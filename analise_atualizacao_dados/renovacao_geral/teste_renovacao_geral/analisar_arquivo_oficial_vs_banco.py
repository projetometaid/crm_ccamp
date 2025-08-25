#!/usr/bin/env python3
"""
ANÁLISE ARQUIVO OFICIAL vs BANCO - RENOVAÇÃO GERAL
Analisa o arquivo GestaoRenovacao (1).xls oficial vs dados do banco
Usa protocolo como chave para identificar INSERT vs UPDATE
"""

import psycopg2
import xlrd
from datetime import datetime
from decimal import Decimal

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def analisar_estrutura_arquivo():
    """Analisa estrutura do arquivo oficial"""
    print("📖 ANALISANDO ARQUIVO OFICIAL: GestaoRenovacao (1).xls")
    print("=" * 60)
    
    wb = xlrd.open_workbook("../GestaoRenovacao (1).xls")
    sheet = wb.sheet_by_index(0)
    
    print(f"📊 Arquivo: {sheet.nrows-1:,} registros x {sheet.ncols} colunas")
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
    
    print(f"\n📋 COLUNAS DO ARQUIVO ({len(headers)}):")
    print("-" * 50)
    for i, header in enumerate(headers):
        print(f"   {i:2d}. {header}")
    
    # Analisar primeiros registros
    print(f"\n🔍 AMOSTRA DOS PRIMEIROS 5 REGISTROS:")
    print("-" * 80)
    
    for row in range(1, min(6, sheet.nrows)):
        # Identificar coluna do protocolo (baseado na análise anterior)
        protocolo_col = None
        for col in range(sheet.ncols):
            if 'protocolo' in headers[col].lower() and 'renovacao' not in headers[col].lower():
                protocolo_col = col
                break
        
        if protocolo_col is not None:
            protocolo = str(sheet.cell_value(row, protocolo_col)).strip()
            razao_social = str(sheet.cell_value(row, 0)).strip()[:30] if sheet.ncols > 0 else ""
            documento = str(sheet.cell_value(row, 1)).strip() if sheet.ncols > 1 else ""
            
            print(f"   {row}. {protocolo} | {razao_social} | {documento}")
        else:
            print(f"   {row}. Protocolo não identificado")
    
    return headers, sheet

def buscar_protocolos_existentes(protocolos_arquivo):
    """Busca quais protocolos já existem no banco"""
    print(f"\n🗄️ VERIFICANDO PROTOCOLOS NO BANCO")
    print("=" * 40)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Converter protocolos para inteiros
    protocolos_int = []
    for p in protocolos_arquivo:
        try:
            protocolos_int.append(int(float(p)))
        except:
            continue
    
    print(f"📊 Protocolos válidos no arquivo: {len(protocolos_int):,}")
    
    # Buscar no banco em lotes
    protocolos_existentes = set()
    lote_size = 1000
    
    for i in range(0, len(protocolos_int), lote_size):
        lote = protocolos_int[i:i+lote_size]
        placeholders = ','.join(['%s'] * len(lote))
        
        cursor.execute(f"""
            SELECT protocolo 
            FROM renovacao_geral 
            WHERE protocolo IN ({placeholders})
        """, lote)
        
        for (protocolo,) in cursor.fetchall():
            protocolos_existentes.add(protocolo)
        
        print(f"   📋 Processado lote {i//lote_size + 1}/{(len(protocolos_int)-1)//lote_size + 1}")
    
    conn.close()
    
    print(f"✅ Protocolos encontrados no banco: {len(protocolos_existentes):,}")
    
    return protocolos_existentes

def analisar_operacoes_necessarias(headers, sheet, protocolos_existentes):
    """Analisa quais operações serão necessárias"""
    print(f"\n🔍 ANALISANDO OPERAÇÕES NECESSÁRIAS")
    print("=" * 50)
    
    # Encontrar coluna do protocolo
    protocolo_col = None
    for col in range(len(headers)):
        if 'protocolo' in headers[col].lower() and 'renovacao' not in headers[col].lower():
            protocolo_col = col
            break
    
    if protocolo_col is None:
        print("❌ Coluna de protocolo não encontrada!")
        return [], []
    
    print(f"📋 Usando coluna {protocolo_col}: '{headers[protocolo_col]}'")
    
    inserts = []
    updates = []
    
    # Processar todos os registros
    for row in range(1, sheet.nrows):
        protocolo_str = str(sheet.cell_value(row, protocolo_col)).strip()
        
        try:
            protocolo = int(float(protocolo_str))
        except:
            continue
        
        if protocolo in protocolos_existentes:
            updates.append(protocolo)
        else:
            inserts.append(protocolo)
    
    print(f"📊 OPERAÇÕES IDENTIFICADAS:")
    print(f"   🆕 INSERT: {len(inserts):,} registros ({len(inserts)/(len(inserts)+len(updates))*100:.1f}%)")
    print(f"   🔄 UPDATE: {len(updates):,} registros ({len(updates)/(len(inserts)+len(updates))*100:.1f}%)")
    
    return inserts, updates

def analisar_mudancas_updates(headers, sheet, protocolos_updates):
    """Analisa que campos serão atualizados nos UPDATEs"""
    print(f"\n🔄 ANALISANDO MUDANÇAS NOS UPDATES")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Mapear colunas importantes do arquivo baseado na estrutura do banco
    mapeamento_colunas = {}
    
    # Identificar colunas automaticamente
    for i, header in enumerate(headers):
        header_lower = header.lower()
        if 'razao' in header_lower or 'social' in header_lower:
            mapeamento_colunas[i] = 'razao_social'
        elif 'cpf' in header_lower or 'cnpj' in header_lower:
            mapeamento_colunas[i] = 'cpfcnpj'
        elif 'telefone' in header_lower:
            mapeamento_colunas[i] = 'telefone'
        elif 'email' in header_lower or 'e_mail' in header_lower:
            mapeamento_colunas[i] = 'e_mail'
        elif 'produto' in header_lower and 'renovacao' not in header_lower:
            mapeamento_colunas[i] = 'produto'
        elif 'titular' in header_lower:
            mapeamento_colunas[i] = 'nome_titular'
        elif 'protocolo' in header_lower and 'renovacao' in header_lower:
            mapeamento_colunas[i] = 'protocolo_renovacao'
        elif 'protocolo' in header_lower and 'renovacao' not in header_lower:
            mapeamento_colunas[i] = 'protocolo'
    
    print(f"📋 CAMPOS QUE SERÃO ANALISADOS:")
    for col, campo in mapeamento_colunas.items():
        if col < len(headers):
            print(f"   Col {col:2d}: {headers[col]} → {campo}")
    
    # Analisar primeiros 10 UPDATEs
    protocolos_teste = list(protocolos_updates)[:10]
    mudancas_por_campo = {}
    
    print(f"\n🔍 ANÁLISE DETALHADA (primeiros 10 UPDATEs):")
    print("-" * 70)
    
    for protocolo in protocolos_teste:
        # Encontrar linha no arquivo
        linha_arquivo = None
        protocolo_col = None
        for col, campo in mapeamento_colunas.items():
            if campo == 'protocolo':
                protocolo_col = col
                break
        
        if protocolo_col is None:
            continue
            
        for row in range(1, sheet.nrows):
            try:
                if int(float(str(sheet.cell_value(row, protocolo_col)).strip())) == protocolo:
                    linha_arquivo = row
                    break
            except:
                continue
        
        if linha_arquivo is None:
            continue
        
        # Buscar dados no banco
        cursor.execute("""
            SELECT protocolo, razao_social, cpfcnpj, telefone, e_mail, produto, 
                   nome_titular, protocolo_renovacao
            FROM renovacao_geral WHERE protocolo = %s
        """, (protocolo,))
        
        resultado = cursor.fetchone()
        if not resultado:
            continue
        
        prot_banco, razao_banco, cpfcnpj_banco, tel_banco, email_banco, \
        prod_banco, titular_banco, prot_ren_banco = resultado
        
        print(f"\n📋 PROTOCOLO {protocolo}:")
        
        mudancas_protocolo = []
        
        # Comparar cada campo
        for col, campo in mapeamento_colunas.items():
            if campo == 'protocolo':  # Protocolo - não muda
                continue
                
            if col >= sheet.ncols:
                continue
            
            valor_arquivo = str(sheet.cell_value(linha_arquivo, col)).strip()
            
            # Buscar valor correspondente no banco
            if campo == 'razao_social':
                valor_banco = str(razao_banco) if razao_banco else ''
            elif campo == 'cpfcnpj':
                valor_banco = str(cpfcnpj_banco) if cpfcnpj_banco else ''
            elif campo == 'telefone':
                valor_banco = str(tel_banco) if tel_banco else ''
            elif campo == 'e_mail':
                valor_banco = str(email_banco) if email_banco else ''
            elif campo == 'produto':
                valor_banco = str(prod_banco) if prod_banco else ''
            elif campo == 'nome_titular':
                valor_banco = str(titular_banco) if titular_banco else ''
            elif campo == 'protocolo_renovacao':
                valor_banco = str(prot_ren_banco) if prot_ren_banco else ''
            else:
                valor_banco = ''
            
            # Verificar mudança
            if valor_arquivo != valor_banco and valor_arquivo:
                mudancas_protocolo.append(f"{campo}: '{valor_banco}' → '{valor_arquivo}'")
                
                if campo not in mudancas_por_campo:
                    mudancas_por_campo[campo] = 0
                mudancas_por_campo[campo] += 1
        
        if mudancas_protocolo:
            print(f"   🔄 MUDANÇAS ({len(mudancas_protocolo)}):")
            for mudanca in mudancas_protocolo:
                print(f"      • {mudanca}")
        else:
            print(f"   ✅ SEM MUDANÇAS")
    
    conn.close()
    
    # Resumo das mudanças
    print(f"\n📊 RESUMO DAS MUDANÇAS (amostra 10 protocolos):")
    print("-" * 50)
    for campo, count in sorted(mudancas_por_campo.items()):
        print(f"   {campo}: {count} mudanças")
    
    return mudancas_por_campo

def gerar_relatorio_final(headers, total_registros, inserts, updates, mudancas_por_campo):
    """Gera relatório final da análise"""
    print(f"\n📊 RELATÓRIO FINAL DA ANÁLISE")
    print("=" * 50)
    
    print(f"📁 ARQUIVO OFICIAL: GestaoRenovacao (1).xls")
    print(f"   📊 Total de registros: {total_registros:,}")
    print(f"   📊 Total de colunas: {len(headers)}")
    
    print(f"\n🎯 OPERAÇÕES NECESSÁRIAS:")
    print(f"   🆕 INSERT: {len(inserts):,} registros ({len(inserts)/total_registros*100:.1f}%)")
    print(f"   🔄 UPDATE: {len(updates):,} registros ({len(updates)/total_registros*100:.1f}%)")
    
    print(f"\n📋 CAMPOS COM MUDANÇAS (amostra):")
    if mudancas_por_campo:
        for campo, count in sorted(mudancas_por_campo.items()):
            print(f"   • {campo}: {count}/10 protocolos testados")
    else:
        print(f"   ✅ Nenhuma mudança identificada na amostra")
    
    print(f"\n🛡️ AVALIAÇÃO DE RISCO:")
    pct_updates = len(updates) / total_registros * 100
    if pct_updates > 70:
        print(f"   🔴 ALTO: {pct_updates:.1f}% são atualizações")
    elif pct_updates > 30:
        print(f"   🟡 MÉDIO: {pct_updates:.1f}% são atualizações")
    else:
        print(f"   🟢 BAIXO: {pct_updates:.1f}% são atualizações")
    
    print(f"\n💡 RECOMENDAÇÕES:")
    print(f"   1. 🛡️ Fazer backup da tabela renovacao_geral")
    print(f"   2. 🔧 Validar mapeamento de campos")
    print(f"   3. 🚀 Executar em lotes pequenos")
    print(f"   4. ✅ Validar resultados após execução")

def main():
    """Função principal"""
    print("🔍 ANÁLISE ARQUIVO OFICIAL vs BANCO - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Objetivo: Analisar GestaoRenovacao (1).xls vs banco")
    print("🔑 Chave: Protocolo para identificar INSERT vs UPDATE")
    print()
    
    try:
        # Analisar estrutura do arquivo
        headers, sheet = analisar_estrutura_arquivo()
        
        # Extrair protocolos do arquivo
        protocolos_arquivo = []
        protocolo_col = None
        for col in range(len(headers)):
            if 'protocolo' in headers[col].lower() and 'renovacao' not in headers[col].lower():
                protocolo_col = col
                break
        
        if protocolo_col is not None:
            for row in range(1, sheet.nrows):
                protocolo = str(sheet.cell_value(row, protocolo_col)).strip()
                protocolos_arquivo.append(protocolo)
        
        # Verificar protocolos existentes no banco
        protocolos_existentes = buscar_protocolos_existentes(protocolos_arquivo)
        
        # Analisar operações necessárias
        inserts, updates = analisar_operacoes_necessarias(headers, sheet, protocolos_existentes)
        
        # Analisar mudanças nos UPDATEs
        mudancas_por_campo = analisar_mudancas_updates(headers, sheet, updates)
        
        # Gerar relatório final
        gerar_relatorio_final(headers, sheet.nrows-1, inserts, updates, mudancas_por_campo)
        
        print(f"\n🎉 ANÁLISE CONCLUÍDA!")
        print("=" * 30)
        print(f"✅ Arquivo oficial analisado")
        print(f"📊 Operações identificadas")
        print(f"🔍 Mudanças mapeadas")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
