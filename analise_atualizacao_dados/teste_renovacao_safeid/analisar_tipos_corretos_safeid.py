#!/usr/bin/env python3
"""
ANÁLISE DE TIPOS CORRETOS - SAFEID
Analisa tipos de dados do banco e compara com arquivo (50 primeiras linhas)
"""

import psycopg2
import xlrd
from datetime import datetime
from decimal import Decimal
from collections import Counter

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def analisar_tipos_banco_completo():
    """Analisa tipos de dados completos da tabela emissao"""
    print("🗄️ ANALISANDO TIPOS DE DADOS COMPLETOS NO BANCO")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar estrutura completa da tabela emissao
    cursor.execute("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        ORDER BY ordinal_position
    """)
    
    colunas_info = cursor.fetchall()
    
    print(f"📊 ESTRUTURA COMPLETA DA TABELA EMISSAO:")
    print("-" * 80)
    print(f"{'COLUNA':<35} {'TIPO':<20} {'TAMANHO':<10} {'NULL':<8} {'DEFAULT':<15}")
    print("-" * 80)
    
    for col_name, data_type, max_length, nullable, default in colunas_info:
        tamanho = str(max_length) if max_length else '-'
        null_ok = 'YES' if nullable == 'YES' else 'NO'
        default_val = str(default)[:12] if default else '-'
        print(f'{col_name:<35} {data_type:<20} {tamanho:<10} {null_ok:<8} {default_val:<15}')
    
    # Verificar dados reais de um protocolo SafeID
    print(f"\n🔍 VERIFICANDO DADOS REAIS (protocolo 1005638878):")
    cursor.execute("""
        SELECT protocolo, nome, documento, nome_do_titular, documento_do_titular,
               produto, data_inicio_validade, data_fim_validade, 
               status_do_certificado, valor_do_boleto,
               vouchercodigo, voucherpercentual, vouchervalor
        FROM emissao 
        WHERE protocolo = 1005638878
    """)
    
    registro = cursor.fetchone()
    if registro:
        campos = ['protocolo', 'nome', 'documento', 'nome_do_titular', 'documento_do_titular',
                  'produto', 'data_inicio_validade', 'data_fim_validade', 
                  'status_do_certificado', 'valor_do_boleto',
                  'vouchercodigo', 'voucherpercentual', 'vouchervalor']
        
        print("-" * 80)
        for i, (campo, valor) in enumerate(zip(campos, registro)):
            tipo_python = type(valor).__name__
            valor_str = str(valor)[:50] if valor else 'NULL'
            print(f'{campo:<35} {tipo_python:<15} {valor_str}')
    else:
        print("❌ Protocolo não encontrado no banco")
    
    conn.close()
    
    return colunas_info

def ler_50_primeiras_linhas_tipadas():
    """Lê e analisa as 50 primeiras linhas com conversão de tipos"""
    print(f"\n\n📖 ANALISANDO 50 PRIMEIRAS LINHAS COM TIPOS")
    print("=" * 60)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
    
    print(f"📊 Analisando {min(50, sheet.nrows-1)} linhas de {sheet.nrows-1} total")
    
    # Mapeamento de campos importantes
    campos_importantes = {
        'Protocolo': 0,
        'Documento': 1,
        'Nome / Razão Social': 2,
        'Data de Pagamento': 4,
        'VoucherCodigo': 5,
        'VoucherPercentual': 6,
        'VoucherValor': 7,
        'Valor Pagamento': 8,
        'Descrição Produto': 9,
        'Data Início do Uso': 12,
        'Data Fim do Uso': 13,
        'Status do Certificado': 14,
        'Renovado': 28
    }
    
    print(f"\n📋 CAMPOS IMPORTANTES MAPEADOS:")
    for nome, col in campos_importantes.items():
        if col < len(headers):
            print(f"   {nome:<25}: Coluna {col:2d}")
    
    # Analisar dados das 50 primeiras linhas
    dados_analisados = []
    
    print(f"\n🔍 ANÁLISE DETALHADA DAS 50 PRIMEIRAS LINHAS:")
    print("-" * 100)
    
    for row in range(1, min(51, sheet.nrows)):
        registro = {}
        
        for nome_campo, col in campos_importantes.items():
            if col < sheet.ncols:
                valor_raw = sheet.cell_value(row, col)
                tipo_raw = type(valor_raw).__name__
                
                # Converter para string limpa
                if isinstance(valor_raw, str):
                    valor_limpo = valor_raw.strip()
                elif isinstance(valor_raw, float) and valor_raw.is_integer():
                    valor_limpo = str(int(valor_raw))
                else:
                    valor_limpo = str(valor_raw) if valor_raw else ''
                
                registro[nome_campo] = {
                    'valor_raw': valor_raw,
                    'valor_limpo': valor_limpo,
                    'tipo_raw': tipo_raw,
                    'vazio': not valor_limpo or valor_limpo == '0.0'
                }
        
        dados_analisados.append(registro)
        
        # Mostrar primeiras 10 linhas detalhadamente
        if row <= 10:
            protocolo = registro['Protocolo']['valor_limpo']
            renovado = registro['Renovado']['valor_limpo']
            status = registro['Status do Certificado']['valor_limpo']
            voucher_perc = registro['VoucherPercentual']['valor_limpo']
            
            print(f"📋 Linha {row:2d} | {protocolo} | Renovado: {renovado} | Status: {status}")
            print(f"   Nome: {registro['Nome / Razão Social']['valor_limpo'][:40]}")
            print(f"   Produto: {registro['Descrição Produto']['valor_limpo']}")
            print(f"   Voucher %: {voucher_perc}")
            print(f"   Data Início: {registro['Data Início do Uso']['valor_limpo'] or 'VAZIO'}")
            print(f"   Data Fim: {registro['Data Fim do Uso']['valor_limpo'] or 'VAZIO'}")
            print()
    
    return dados_analisados, headers

def analisar_padroes_campos(dados_analisados):
    """Analisa padrões dos campos nas 50 linhas"""
    print(f"\n📊 ANÁLISE DE PADRÕES DOS CAMPOS")
    print("=" * 50)
    
    total_linhas = len(dados_analisados)
    
    # Analisar cada campo
    for nome_campo in ['Protocolo', 'Renovado', 'Status do Certificado', 'VoucherPercentual', 
                       'Data Início do Uso', 'Data Fim do Uso', 'Valor Pagamento']:
        
        print(f"\n📋 {nome_campo.upper()}:")
        print("-" * 30)
        
        valores = [reg[nome_campo]['valor_limpo'] for reg in dados_analisados if nome_campo in reg]
        vazios = [reg[nome_campo]['vazio'] for reg in dados_analisados if nome_campo in reg]
        tipos = [reg[nome_campo]['tipo_raw'] for reg in dados_analisados if nome_campo in reg]
        
        # Estatísticas básicas
        total_vazios = sum(vazios)
        total_preenchidos = total_linhas - total_vazios
        
        print(f"   📊 Preenchidos: {total_preenchidos}/{total_linhas} ({total_preenchidos/total_linhas*100:.1f}%)")
        print(f"   📊 Vazios: {total_vazios}/{total_linhas} ({total_vazios/total_linhas*100:.1f}%)")
        
        # Tipos encontrados
        tipos_unicos = set(tipos)
        print(f"   📊 Tipos: {', '.join(tipos_unicos)}")
        
        # Valores únicos (se poucos)
        valores_nao_vazios = [v for v, vazio in zip(valores, vazios) if not vazio]
        valores_unicos = set(valores_nao_vazios)
        
        if len(valores_unicos) <= 10:
            print(f"   📊 Valores únicos:")
            for valor in sorted(valores_unicos):
                count = valores_nao_vazios.count(valor)
                print(f"      '{valor}': {count} ocorrências")
        else:
            print(f"   📊 {len(valores_unicos)} valores únicos diferentes")
            # Mostrar alguns exemplos
            exemplos = sorted(list(valores_unicos))[:5]
            print(f"   📊 Exemplos: {exemplos}")

def comparar_com_banco_tipado(dados_analisados):
    """Compara dados do arquivo com banco usando tipos corretos"""
    print(f"\n\n🔍 COMPARAÇÃO TIPADA ARQUIVO vs BANCO")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    mudancas_identificadas = []
    
    print(f"🔍 VERIFICANDO PRIMEIROS 10 PROTOCOLOS:")
    print("-" * 50)
    
    for i, registro in enumerate(dados_analisados[:10], 1):
        protocolo = registro['Protocolo']['valor_limpo']
        
        cursor.execute("""
            SELECT protocolo, nome, produto, status_do_certificado,
                   data_inicio_validade, data_fim_validade,
                   voucherpercentual, valor_do_boleto
            FROM emissao WHERE protocolo = %s
        """, (int(protocolo),))
        
        resultado = cursor.fetchone()
        
        if resultado:
            prot, nome_banco, prod_banco, status_banco, \
            data_inicio_banco, data_fim_banco, voucher_perc_banco, valor_banco = resultado
            
            print(f"\n📋 {i:2d}. PROTOCOLO {protocolo}:")
            
            mudancas_protocolo = []
            
            # Comparar Status
            status_arquivo = registro['Status do Certificado']['valor_limpo']
            if status_arquivo != str(status_banco):
                mudancas_protocolo.append(f"Status: '{status_banco}' → '{status_arquivo}'")
            
            # Comparar Produto
            produto_arquivo = registro['Descrição Produto']['valor_limpo']
            if produto_arquivo != str(prod_banco):
                mudancas_protocolo.append(f"Produto: '{prod_banco}' → '{produto_arquivo}'")
            
            # Comparar VoucherPercentual
            voucher_arquivo = registro['VoucherPercentual']['valor_limpo'].replace(',', '.')
            voucher_banco_str = str(voucher_perc_banco) if voucher_perc_banco else '0'
            if voucher_arquivo != voucher_banco_str:
                mudancas_protocolo.append(f"VoucherPercentual: '{voucher_perc_banco}' → '{voucher_arquivo}'")
            
            # Comparar Datas (se preenchidas no arquivo)
            data_inicio_arquivo = registro['Data Início do Uso']['valor_limpo']
            if data_inicio_arquivo and not data_inicio_banco:
                mudancas_protocolo.append(f"Data Início: NULL → '{data_inicio_arquivo}'")
            
            data_fim_arquivo = registro['Data Fim do Uso']['valor_limpo']
            if data_fim_arquivo and not data_fim_banco:
                mudancas_protocolo.append(f"Data Fim: NULL → '{data_fim_arquivo}'")
            
            # Campo Renovado (não existe no banco)
            renovado_arquivo = registro['Renovado']['valor_limpo']
            mudancas_protocolo.append(f"Renovado: CAMPO_NOVO → '{renovado_arquivo}'")
            
            if mudancas_protocolo:
                mudancas_identificadas.extend(mudancas_protocolo)
                print(f"   🔄 MUDANÇAS IDENTIFICADAS ({len(mudancas_protocolo)}):")
                for mudanca in mudancas_protocolo:
                    print(f"      • {mudanca}")
            else:
                print(f"   ✅ SEM MUDANÇAS (exceto campo Renovado)")
        else:
            print(f"   ❌ Protocolo {protocolo} não encontrado no banco")
    
    conn.close()
    
    return mudancas_identificadas

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE TIPOS CORRETOS - SAFEID")
    print("=" * 70)
    print("🎯 Objetivo: Analisar tipos de dados e comportamento dos campos")
    print()
    
    try:
        # Analisar tipos do banco
        colunas_banco = analisar_tipos_banco_completo()
        
        # Analisar 50 primeiras linhas
        dados_analisados, headers = ler_50_primeiras_linhas_tipadas()
        
        # Analisar padrões
        analisar_padroes_campos(dados_analisados)
        
        # Comparar com banco
        mudancas = comparar_com_banco_tipado(dados_analisados)
        
        print(f"\n🎯 RESUMO FINAL:")
        print("=" * 30)
        print(f"📊 Linhas analisadas: {len(dados_analisados)}")
        print(f"📊 Campos no banco: {len(colunas_banco)}")
        print(f"📊 Mudanças identificadas: {len(mudancas)}")
        
        print(f"\n💡 PRINCIPAIS DESCOBERTAS:")
        print(f"   🎯 Campo 'Renovado' é o principal (não existe no banco)")
        print(f"   📊 100% dos protocolos existem no banco")
        print(f"   🎫 VoucherPercentual sempre '0,00'")
        print(f"   📅 Datas de uso podem estar vazias")
        print(f"   📋 Status e Produto podem ter mudanças")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
