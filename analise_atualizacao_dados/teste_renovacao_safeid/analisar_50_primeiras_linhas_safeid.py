#!/usr/bin/env python3
"""
ANÁLISE DAS 50 PRIMEIRAS LINHAS - RENOVAÇÃO SAFEID
Analisa quais campos serão atualizados nos protocolos existentes
"""

import xlrd
import psycopg2
from datetime import datetime

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def analisar_50_primeiras_linhas():
    """Analisa detalhadamente as 50 primeiras linhas"""
    print("🔍 ANÁLISE DAS 50 PRIMEIRAS LINHAS - SAFEID")
    print("=" * 50)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
    
    print(f"📊 Analisando linhas 1-50 de {sheet.nrows:,} total")
    
    # Índices das colunas importantes
    col_protocolo = headers.index('Protocolo')
    col_documento = headers.index('Documento')
    col_nome = headers.index('Nome / Razão Social')
    col_produto = headers.index('Descrição Produto')
    col_status = headers.index('Status do Certificado')
    col_data_inicio = headers.index('Data Início do Uso')
    col_data_fim = headers.index('Data Fim do Uso')
    col_voucher_codigo = headers.index('VoucherCodigo')
    col_voucher_percentual = headers.index('VoucherPercentual')
    col_voucher_valor = headers.index('VoucherValor')
    
    print(f"\n📋 COLUNAS PRINCIPAIS MAPEADAS:")
    print(f"   Protocolo: {col_protocolo}")
    print(f"   Status: {col_status}")
    print(f"   Produto: {col_produto}")
    print(f"   VoucherPercentual: {col_voucher_percentual}")
    
    # Analisar cada linha
    registros_analisados = []
    
    print(f"\n🔍 ANÁLISE LINHA POR LINHA:")
    print("-" * 100)
    
    for row in range(1, min(51, sheet.nrows)):  # Linhas 1-50
        protocolo = str(sheet.cell_value(row, col_protocolo)).strip()
        documento = str(sheet.cell_value(row, col_documento)).strip()
        nome = str(sheet.cell_value(row, col_nome)).strip()
        produto = str(sheet.cell_value(row, col_produto)).strip()
        status = str(sheet.cell_value(row, col_status)).strip()
        data_inicio = str(sheet.cell_value(row, col_data_inicio)).strip()
        data_fim = str(sheet.cell_value(row, col_data_fim)).strip()
        voucher_codigo = str(sheet.cell_value(row, col_voucher_codigo)).strip()
        voucher_percentual = str(sheet.cell_value(row, col_voucher_percentual)).strip()
        voucher_valor = str(sheet.cell_value(row, col_voucher_valor)).strip()
        
        registro = {
            'linha': row,
            'protocolo': protocolo,
            'documento': documento,
            'nome': nome,
            'produto': produto,
            'status': status,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'voucher_codigo': voucher_codigo,
            'voucher_percentual': voucher_percentual,
            'voucher_valor': voucher_valor
        }
        
        registros_analisados.append(registro)
        
        print(f"📋 Linha {row:2d} | {protocolo} | {status}")
        print(f"   Nome: {nome[:40]}")
        print(f"   Produto: {produto}")
        print(f"   Voucher %: {voucher_percentual}")
        print(f"   Data Início: {data_inicio if data_inicio else 'VAZIO'}")
        print(f"   Data Fim: {data_fim if data_fim else 'VAZIO'}")
        print()
    
    return registros_analisados

def verificar_no_banco(registros):
    """Verifica como os dados estão armazenados no banco"""
    print(f"\n\n🗄️ VERIFICAÇÃO NO BANCO DE DADOS")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    mudancas_identificadas = []
    
    print(f"\n🔍 COMPARANDO ARQUIVO vs BANCO (primeiros 10):")
    print("-" * 60)
    
    for reg in registros[:10]:  # Verificar primeiros 10
        protocolo = reg['protocolo']
        
        cursor.execute("""
            SELECT protocolo, nome, documento, produto, status_do_certificado,
                   data_inicio_validade, data_fim_validade,
                   vouchercodigo, voucherpercentual, vouchervalor
            FROM emissao WHERE protocolo = %s
        """, (int(protocolo),))
        
        resultado = cursor.fetchone()
        
        if resultado:
            prot, nome_banco, doc_banco, prod_banco, status_banco, \
            data_inicio_banco, data_fim_banco, voucher_cod_banco, \
            voucher_perc_banco, voucher_val_banco = resultado
            
            print(f"   📋 PROTOCOLO {protocolo}:")
            
            # Comparar campos
            mudancas_protocolo = []
            
            # Status
            if reg['status'] != str(status_banco):
                mudancas_protocolo.append(f"Status: '{status_banco}' → '{reg['status']}'")
            
            # Produto
            if reg['produto'] != str(prod_banco):
                mudancas_protocolo.append(f"Produto: '{prod_banco}' → '{reg['produto']}'")
            
            # Voucher Percentual
            voucher_perc_arquivo = reg['voucher_percentual'].replace(',', '.')
            voucher_perc_banco_str = str(voucher_perc_banco) if voucher_perc_banco else '0'
            if voucher_perc_arquivo != voucher_perc_banco_str:
                mudancas_protocolo.append(f"VoucherPercentual: '{voucher_perc_banco}' → '{voucher_perc_arquivo}'")
            
            # Datas (se preenchidas no arquivo)
            if reg['data_inicio'] and not data_inicio_banco:
                mudancas_protocolo.append(f"Data Início: NULL → '{reg['data_inicio']}'")
            
            if reg['data_fim'] and not data_fim_banco:
                mudancas_protocolo.append(f"Data Fim: NULL → '{reg['data_fim']}'")
            
            if mudancas_protocolo:
                mudancas_identificadas.extend(mudancas_protocolo)
                print(f"      🔄 MUDANÇAS IDENTIFICADAS:")
                for mudanca in mudancas_protocolo:
                    print(f"         • {mudanca}")
            else:
                print(f"      ✅ SEM MUDANÇAS")
            
            print()
        else:
            print(f"   ❌ Protocolo {protocolo} não encontrado no banco")
    
    conn.close()
    
    return mudancas_identificadas

def analisar_padroes_mudancas(registros):
    """Analisa padrões das mudanças identificadas"""
    print(f"\n📊 ANÁLISE DE PADRÕES - SAFEID")
    print("=" * 40)
    
    # Analisar status
    status_arquivo = [reg['status'] for reg in registros]
    status_unicos = set(status_arquivo)
    
    print(f"📋 STATUS NO ARQUIVO:")
    for status in status_unicos:
        count = status_arquivo.count(status)
        pct = (count / len(registros)) * 100
        print(f"   {status}: {count} ({pct:.1f}%)")
    
    # Analisar produtos
    produtos_arquivo = [reg['produto'] for reg in registros]
    produtos_unicos = set(produtos_arquivo)
    
    print(f"\n📋 PRODUTOS NO ARQUIVO:")
    for produto in produtos_unicos:
        count = produtos_arquivo.count(produto)
        pct = (count / len(registros)) * 100
        print(f"   {produto}: {count} ({pct:.1f}%)")
    
    # Analisar vouchers
    vouchers_preenchidos = [reg for reg in registros if reg['voucher_percentual'] and reg['voucher_percentual'] != '0,00']
    vouchers_zerados = [reg for reg in registros if reg['voucher_percentual'] == '0,00']
    
    print(f"\n🎫 ANÁLISE DE VOUCHERS:")
    print(f"   Vouchers zerados (0,00): {len(vouchers_zerados)} ({len(vouchers_zerados)/len(registros)*100:.1f}%)")
    print(f"   Vouchers preenchidos: {len(vouchers_preenchidos)} ({len(vouchers_preenchidos)/len(registros)*100:.1f}%)")
    
    # Analisar datas
    datas_inicio_preenchidas = [reg for reg in registros if reg['data_inicio']]
    datas_fim_preenchidas = [reg for reg in registros if reg['data_fim']]
    
    print(f"\n📅 ANÁLISE DE DATAS:")
    print(f"   Data Início preenchida: {len(datas_inicio_preenchidas)} ({len(datas_inicio_preenchidas)/len(registros)*100:.1f}%)")
    print(f"   Data Fim preenchida: {len(datas_fim_preenchidas)} ({len(datas_fim_preenchidas)/len(registros)*100:.1f}%)")

def main():
    """Função principal"""
    print("🔍 ANÁLISE DAS 50 PRIMEIRAS LINHAS - SAFEID")
    print("=" * 60)
    print("🎯 Objetivo: Identificar campos que serão atualizados")
    print()
    
    try:
        # Analisar arquivo
        registros = analisar_50_primeiras_linhas()
        
        # Verificar no banco
        mudancas = verificar_no_banco(registros)
        
        # Analisar padrões
        analisar_padroes_mudancas(registros)
        
        print(f"\n🎯 CONCLUSÕES:")
        print("=" * 30)
        print(f"📊 {len(mudancas)} mudanças identificadas na amostra")
        print(f"🎫 Foco principal: Status e produtos SafeID")
        print(f"📅 Datas de uso podem ser preenchidas")
        print(f"💰 Vouchers principalmente zerados")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
