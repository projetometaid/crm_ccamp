#!/usr/bin/env python3
"""
INVESTIGAÇÃO DO PROBLEMA DAS DATAS
Analisa como as datas estão sendo lidas do Excel
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

def investigar_datas_excel():
    """Investiga como as datas aparecem no Excel"""
    print("🔍 INVESTIGANDO DATAS NO ARQUIVO EXCEL")
    print("=" * 50)
    
    wb = xlrd.open_workbook("RelatorioEmissoes.xls")
    sheet = wb.sheet_by_index(0)
    
    # Identificar colunas de data
    headers = []
    colunas_data = {}
    
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
        
        # Identificar colunas que podem ser datas
        if any(palavra in header.lower() for palavra in ['data', 'validade', 'avp']):
            colunas_data[col] = header
    
    print(f"📋 COLUNAS DE DATA IDENTIFICADAS:")
    for col, nome in colunas_data.items():
        print(f"   Coluna {col:2d}: {nome}")
    
    print(f"\n🔍 ANALISANDO PRIMEIRAS 10 LINHAS:")
    print("-" * 80)
    
    for row in range(1, min(11, sheet.nrows)):
        protocolo = sheet.cell_value(row, 0)
        print(f"\n📋 Linha {row} - Protocolo: {int(protocolo) if protocolo else 'N/A'}")
        
        for col, nome_coluna in colunas_data.items():
            valor_raw = sheet.cell_value(row, col)
            tipo_valor = type(valor_raw).__name__
            
            print(f"   {nome_coluna}:")
            print(f"      Valor raw: {repr(valor_raw)}")
            print(f"      Tipo: {tipo_valor}")
            
            # Tentar diferentes interpretações
            if valor_raw:
                if isinstance(valor_raw, (int, float)):
                    try:
                        # Converter data Excel
                        data_excel = xlrd.xldate_as_datetime(valor_raw, wb.datemode)
                        print(f"      Como data Excel: {data_excel}")
                    except:
                        print(f"      ❌ Não é data Excel válida")
                
                elif isinstance(valor_raw, str):
                    print(f"      Como string: '{valor_raw}'")
                    
                    # Tentar converter string para data
                    formatos = [
                        '%d/%m/%Y %H:%M:%S',
                        '%d/%m/%Y',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d',
                        '%m/%d/%Y %H:%M:%S',
                        '%m/%d/%Y'
                    ]
                    
                    for formato in formatos:
                        try:
                            data_convertida = datetime.strptime(valor_raw.strip(), formato)
                            print(f"      ✅ Formato {formato}: {data_convertida}")
                            break
                        except:
                            continue
                    else:
                        print(f"      ❌ Não conseguiu converter string para data")
            else:
                print(f"      ⚠️ Valor vazio/None")

def comparar_com_banco():
    """Compara datas do arquivo com banco"""
    print(f"\n\n🔍 COMPARANDO DATAS ARQUIVO vs BANCO")
    print("=" * 50)
    
    # Ler algumas datas do arquivo
    wb = xlrd.open_workbook("RelatorioEmissoes.xls")
    sheet = wb.sheet_by_index(0)
    
    # Encontrar colunas de data
    headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
    
    col_data_avp = None
    col_data_inicio = None
    col_data_fim = None
    
    for i, header in enumerate(headers):
        if 'Data AVP' in header:
            col_data_avp = i
        elif 'Data Inicio Validade' in header:
            col_data_inicio = i
        elif 'Data Fim Validade' in header:
            col_data_fim = i
    
    print(f"📊 Colunas encontradas:")
    print(f"   Data AVP: coluna {col_data_avp}")
    print(f"   Data Inicio: coluna {col_data_inicio}")
    print(f"   Data Fim: coluna {col_data_fim}")
    
    # Pegar alguns protocolos para comparar
    protocolos_teste = []
    for row in range(1, min(6, sheet.nrows)):
        protocolo_raw = sheet.cell_value(row, 0)
        if protocolo_raw:
            protocolo = str(int(protocolo_raw))
            
            # Ler datas do arquivo
            data_avp_raw = sheet.cell_value(row, col_data_avp) if col_data_avp else None
            data_inicio_raw = sheet.cell_value(row, col_data_inicio) if col_data_inicio else None
            data_fim_raw = sheet.cell_value(row, col_data_fim) if col_data_fim else None
            
            protocolos_teste.append({
                'protocolo': protocolo,
                'data_avp_raw': data_avp_raw,
                'data_inicio_raw': data_inicio_raw,
                'data_fim_raw': data_fim_raw
            })
    
    # Buscar no banco
    conn = conectar_banco()
    cursor = conn.cursor()
    
    for dados in protocolos_teste:
        protocolo = dados['protocolo']
        
        cursor.execute("""
            SELECT data_avp, data_inicio_validade, data_fim_validade
            FROM emissao WHERE protocolo = %s
        """, (int(protocolo),))
        
        resultado = cursor.fetchone()
        
        print(f"\n📋 PROTOCOLO {protocolo}:")
        print("-" * 40)
        
        if resultado:
            data_avp_banco, data_inicio_banco, data_fim_banco = resultado
            
            print(f"🗄️ BANCO:")
            print(f"   Data AVP: {data_avp_banco}")
            print(f"   Data Início: {data_inicio_banco}")
            print(f"   Data Fim: {data_fim_banco}")
            
            print(f"\n📁 ARQUIVO (raw):")
            print(f"   Data AVP: {repr(dados['data_avp_raw'])} ({type(dados['data_avp_raw']).__name__})")
            print(f"   Data Início: {repr(dados['data_inicio_raw'])} ({type(dados['data_inicio_raw']).__name__})")
            print(f"   Data Fim: {repr(dados['data_fim_raw'])} ({type(dados['data_fim_raw']).__name__})")
            
            # Tentar converter datas do arquivo
            print(f"\n📁 ARQUIVO (convertido):")
            
            for nome, valor_raw in [
                ('Data AVP', dados['data_avp_raw']),
                ('Data Início', dados['data_inicio_raw']),
                ('Data Fim', dados['data_fim_raw'])
            ]:
                if valor_raw:
                    if isinstance(valor_raw, (int, float)):
                        try:
                            data_convertida = xlrd.xldate_as_datetime(valor_raw, wb.datemode)
                            print(f"   {nome}: {data_convertida} ✅")
                        except Exception as e:
                            print(f"   {nome}: ERRO - {e} ❌")
                    elif isinstance(valor_raw, str):
                        print(f"   {nome}: '{valor_raw}' (string)")
                    else:
                        print(f"   {nome}: {valor_raw} (tipo: {type(valor_raw).__name__})")
                else:
                    print(f"   {nome}: VAZIO ⚠️")
        else:
            print(f"❌ Protocolo não encontrado no banco")
    
    conn.close()

def testar_xldate():
    """Testa especificamente a função xldate"""
    print(f"\n\n🔍 TESTE ESPECÍFICO DE xlrd.xldate")
    print("=" * 50)
    
    wb = xlrd.open_workbook("RelatorioEmissoes.xls")
    sheet = wb.sheet_by_index(0)
    
    print(f"📊 Informações do workbook:")
    print(f"   Date mode: {wb.datemode}")
    print(f"   (0=1900, 1=1904)")
    
    # Testar alguns valores
    print(f"\n🔍 Testando valores específicos:")
    
    for row in range(1, 4):
        for col in range(sheet.ncols):
            valor = sheet.cell_value(row, col)
            
            if isinstance(valor, (int, float)) and valor > 40000:  # Possível data Excel
                header = str(sheet.cell_value(0, col))
                
                print(f"\n   Linha {row}, Coluna {col} ({header}):")
                print(f"      Valor: {valor}")
                
                try:
                    data_convertida = xlrd.xldate_as_datetime(valor, wb.datemode)
                    print(f"      Data: {data_convertida} ✅")
                except Exception as e:
                    print(f"      Erro: {e} ❌")

def main():
    """Função principal"""
    try:
        investigar_datas_excel()
        comparar_com_banco()
        testar_xldate()
        
        print(f"\n\n💡 PRÓXIMOS PASSOS:")
        print("   1. Verificar se datas estão em formato correto no Excel")
        print("   2. Ajustar função de conversão de datas")
        print("   3. Testar com diferentes formatos de data")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
