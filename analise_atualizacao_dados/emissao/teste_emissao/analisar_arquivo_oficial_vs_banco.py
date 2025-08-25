#!/usr/bin/env python3
"""
ANÁLISE ARQUIVO OFICIAL vs BANCO - EMISSÃO
Analisa o arquivo RelatorioEmissoes (13).xls oficial vs dados do banco
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
    print("📖 ANALISANDO ARQUIVO OFICIAL: RelatorioEmissoes (13).xls")
    print("=" * 60)
    
    wb = xlrd.open_workbook("../RelatorioEmissoes (13).xls")
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
        protocolo = str(sheet.cell_value(row, 0)).strip()
        documento = str(sheet.cell_value(row, 1)).strip()
        nome = str(sheet.cell_value(row, 2)).strip()[:30]
        
        print(f"   {row}. {protocolo} | {documento} | {nome}")
    
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
            FROM emissao 
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
    
    inserts = []
    updates = []
    
    # Processar todos os registros
    for row in range(1, sheet.nrows):
        protocolo_str = str(sheet.cell_value(row, 0)).strip()
        
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
    
    # Mapear colunas importantes do arquivo
    mapeamento_colunas = {
        0: 'protocolo',
        1: 'documento', 
        2: 'nome',
        9: 'produto',
        21: 'status_do_certificado',
        19: 'data_inicio_validade',
        20: 'data_fim_validade',
        15: 'valor_do_boleto'
    }
    
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
        for row in range(1, sheet.nrows):
            if int(float(str(sheet.cell_value(row, 0)).strip())) == protocolo:
                linha_arquivo = row
                break
        
        if linha_arquivo is None:
            continue
        
        # Buscar dados no banco
        cursor.execute("""
            SELECT protocolo, documento, nome, produto, status_do_certificado,
                   data_inicio_validade, data_fim_validade, valor_do_boleto
            FROM emissao WHERE protocolo = %s
        """, (protocolo,))
        
        resultado = cursor.fetchone()
        if not resultado:
            continue
        
        prot_banco, doc_banco, nome_banco, prod_banco, status_banco, \
        data_inicio_banco, data_fim_banco, valor_banco = resultado
        
        print(f"\n📋 PROTOCOLO {protocolo}:")
        
        mudancas_protocolo = []
        
        # Comparar cada campo
        for col, campo in mapeamento_colunas.items():
            if col == 0:  # Protocolo - não muda
                continue
                
            if col >= sheet.ncols:
                continue
            
            valor_arquivo = str(sheet.cell_value(linha_arquivo, col)).strip()
            
            # Buscar valor correspondente no banco
            if campo == 'documento':
                valor_banco = str(doc_banco) if doc_banco else ''
            elif campo == 'nome':
                valor_banco = str(nome_banco) if nome_banco else ''
            elif campo == 'produto':
                valor_banco = str(prod_banco) if prod_banco else ''
            elif campo == 'status_do_certificado':
                valor_banco = str(status_banco) if status_banco else ''
            elif campo == 'valor_do_boleto':
                valor_banco = str(valor_banco) if valor_banco else ''
            else:
                valor_banco = ''  # Datas - análise simplificada
            
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
    
    print(f"📁 ARQUIVO OFICIAL: RelatorioEmissoes (13).xls")
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
    print(f"   1. 🛡️ Fazer backup da tabela emissao")
    print(f"   2. 🔧 Ajustar limites de campos (ex: documento)")
    print(f"   3. 🚀 Executar em lotes pequenos")
    print(f"   4. ✅ Validar resultados após execução")

def main():
    """Função principal"""
    print("🔍 ANÁLISE ARQUIVO OFICIAL vs BANCO - EMISSÃO")
    print("=" * 70)
    print("🎯 Objetivo: Analisar RelatorioEmissoes (13).xls vs banco")
    print("🔑 Chave: Protocolo para identificar INSERT vs UPDATE")
    print()
    
    try:
        # Analisar estrutura do arquivo
        headers, sheet = analisar_estrutura_arquivo()
        
        # Extrair protocolos do arquivo
        protocolos_arquivo = []
        for row in range(1, sheet.nrows):
            protocolo = str(sheet.cell_value(row, 0)).strip()
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
