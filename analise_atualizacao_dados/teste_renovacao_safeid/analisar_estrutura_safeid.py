#!/usr/bin/env python3
"""
ANÁLISE DE ESTRUTURA - RENOVAÇÃO SAFEID
Analisa estrutura do arquivo e tipos de dados no banco
"""

import psycopg2
import xlrd

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
    """Analisa estrutura completa do arquivo Excel"""
    print("📖 ANALISANDO ESTRUTURA DO ARQUIVO SAFEID")
    print("=" * 50)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    print(f"📊 Arquivo: {sheet.nrows:,} linhas x {sheet.ncols} colunas")
    
    # Analisar todos os cabeçalhos
    print(f"\n📋 TODAS AS COLUNAS DO ARQUIVO:")
    print("-" * 60)
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
        print(f"   {col:2d}. {header}")
    
    # Identificar colunas específicas do SafeID
    colunas_voucher = []
    colunas_data = []
    colunas_valor = []
    
    for i, header in enumerate(headers):
        if 'voucher' in header.lower():
            colunas_voucher.append((i, header))
        elif 'data' in header.lower():
            colunas_data.append((i, header))
        elif 'valor' in header.lower():
            colunas_valor.append((i, header))
    
    print(f"\n🎫 COLUNAS DE VOUCHER IDENTIFICADAS:")
    for col, nome in colunas_voucher:
        print(f"   Coluna {col:2d}: {nome}")
    
    print(f"\n📅 COLUNAS DE DATA IDENTIFICADAS:")
    for col, nome in colunas_data:
        print(f"   Coluna {col:2d}: {nome}")
    
    print(f"\n💰 COLUNAS DE VALOR IDENTIFICADAS:")
    for col, nome in colunas_valor:
        print(f"   Coluna {col:2d}: {nome}")
    
    # Analisar dados das primeiras linhas
    print(f"\n🔍 ANÁLISE DAS PRIMEIRAS 10 LINHAS:")
    print("-" * 80)
    
    for row in range(1, min(11, sheet.nrows)):
        print(f"\n📋 LINHA {row}:")
        
        # Mostrar colunas principais
        colunas_principais = [0, 1, 2, 4, 5, 6, 7, 8, 9, 14]  # Protocolo, Doc, Nome, Data Pag, Vouchers, Valor, Produto, Status
        
        for col in colunas_principais:
            if col < sheet.ncols:
                header = headers[col]
                valor = sheet.cell_value(row, col)
                tipo = type(valor).__name__
                
                # Formatar valor para exibição
                if isinstance(valor, str):
                    valor_display = f"'{valor[:40]}'" if len(str(valor)) > 40 else f"'{valor}'"
                elif isinstance(valor, float) and valor.is_integer():
                    valor_display = f"{int(valor)}"
                else:
                    valor_display = str(valor)
                
                print(f"   {header:<25}: {valor_display} ({tipo})")
    
    # Analisar especificamente as colunas de voucher
    print(f"\n🎫 ANÁLISE DETALHADA DAS COLUNAS DE VOUCHER:")
    print("-" * 60)
    
    for col, nome in colunas_voucher:
        print(f"\n📋 {nome} (Coluna {col}):")
        
        valores_vazios = 0
        valores_preenchidos = 0
        exemplos_preenchidos = []
        
        for row in range(1, min(51, sheet.nrows)):  # Analisar primeiras 50 linhas
            valor = sheet.cell_value(row, col)
            
            if valor and str(valor).strip():
                valores_preenchidos += 1
                if len(exemplos_preenchidos) < 5:
                    exemplos_preenchidos.append((row, valor))
            else:
                valores_vazios += 1
        
        total_analisado = min(50, sheet.nrows - 1)
        pct_preenchidos = (valores_preenchidos / total_analisado) * 100
        pct_vazios = (valores_vazios / total_analisado) * 100
        
        print(f"   📊 Preenchidos: {valores_preenchidos}/{total_analisado} ({pct_preenchidos:.1f}%)")
        print(f"   📊 Vazios: {valores_vazios}/{total_analisado} ({pct_vazios:.1f}%)")
        
        if exemplos_preenchidos:
            print(f"   ✅ Exemplos preenchidos:")
            for linha, valor in exemplos_preenchidos:
                print(f"      Linha {linha}: {valor}")
    
    return headers

def verificar_campos_banco_safeid():
    """Verifica se há campos específicos do SafeID no banco"""
    print(f"\n\n🗄️ VERIFICANDO CAMPOS SAFEID NO BANCO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se existem campos relacionados a voucher/safeid
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        AND (column_name ILIKE '%voucher%' 
             OR column_name ILIKE '%safeid%'
             OR column_name ILIKE '%codigo%'
             OR column_name ILIKE '%percentual%')
        ORDER BY column_name
    """)
    
    campos_voucher = cursor.fetchall()
    
    if campos_voucher:
        print(f"✅ CAMPOS RELACIONADOS A VOUCHER/SAFEID ENCONTRADOS:")
        print("-" * 50)
        for col_name, data_type, max_length in campos_voucher:
            tamanho = str(max_length) if max_length else '-'
            print(f"   {col_name:<30} {data_type:<15} {tamanho}")
    else:
        print(f"❌ NENHUM CAMPO RELACIONADO A VOUCHER/SAFEID ENCONTRADO")
    
    # Verificar alguns dados reais
    print(f"\n🔍 VERIFICANDO DADOS REAIS (protocolo 1005638878):")
    cursor.execute("""
        SELECT protocolo, nome, documento, nome_do_titular, documento_do_titular,
               produto, data_inicio_validade, data_fim_validade, 
               status_do_certificado, valor_do_boleto
        FROM emissao 
        WHERE protocolo = 1005638878
    """)
    
    registro = cursor.fetchone()
    if registro:
        campos = ['protocolo', 'nome', 'documento', 'nome_do_titular', 'documento_do_titular',
                  'produto', 'data_inicio_validade', 'data_fim_validade', 
                  'status_do_certificado', 'valor_do_boleto']
        
        print("-" * 70)
        for i, (campo, valor) in enumerate(zip(campos, registro)):
            tipo_python = type(valor).__name__
            valor_str = str(valor)[:40] if valor else 'NULL'
            print(f'{campo:<30} {tipo_python:<12} {valor_str}')
    else:
        print("❌ Protocolo não encontrado no banco")
    
    conn.close()
    
    return campos_voucher

def mapear_colunas_arquivo_banco(headers):
    """Mapeia colunas do arquivo para colunas do banco"""
    print(f"\n\n🔗 MAPEAMENTO ARQUIVO → BANCO")
    print("=" * 50)
    
    # Mapeamento baseado nos nomes das colunas
    mapeamento_possivel = {
        'Protocolo': 'protocolo',
        'Documento': 'documento',
        'Nome / Razão Social': 'nome',
        'Descrição Produto': 'produto',
        'Data Início do Uso': 'data_inicio_validade',
        'Data Fim do Uso': 'data_fim_validade',
        'Status do Certificado': 'status_do_certificado',
        'Valor Pagamento': 'valor_do_boleto'
    }
    
    # Campos específicos do SafeID (podem não existir no banco)
    campos_safeid = {
        'VoucherCodigo': 'voucher_codigo',
        'VoucherPercentual': 'voucher_percentual', 
        'VoucherValor': 'voucher_valor',
        'Data de Pagamento': 'data_pagamento',
        'Autoridade de Registro Venda': 'ar_venda',
        'Validade Certificado': 'validade_certificado',
        'Período de Uso': 'periodo_uso'
    }
    
    mapeamento_encontrado = {}
    campos_safeid_encontrados = {}
    colunas_nao_mapeadas = []
    
    print(f"📋 MAPEAMENTO PADRÃO IDENTIFICADO:")
    print("-" * 40)
    
    for header in headers:
        if header in mapeamento_possivel:
            coluna_banco = mapeamento_possivel[header]
            mapeamento_encontrado[header] = coluna_banco
            print(f"   ✅ {header:<30} → {coluna_banco}")
        elif header in campos_safeid:
            coluna_banco = campos_safeid[header]
            campos_safeid_encontrados[header] = coluna_banco
            print(f"   🎫 {header:<30} → {coluna_banco} (SafeID)")
        else:
            colunas_nao_mapeadas.append(header)
    
    if colunas_nao_mapeadas:
        print(f"\n📋 COLUNAS NÃO MAPEADAS:")
        print("-" * 30)
        for header in colunas_nao_mapeadas:
            print(f"   ❓ {header}")
    
    print(f"\n📊 RESUMO:")
    print(f"   ✅ Mapeadas (padrão): {len(mapeamento_encontrado)}")
    print(f"   🎫 Mapeadas (SafeID): {len(campos_safeid_encontrados)}")
    print(f"   ❓ Não mapeadas: {len(colunas_nao_mapeadas)}")
    
    return mapeamento_encontrado, campos_safeid_encontrados

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE ESTRUTURA - RENOVAÇÃO SAFEID")
    print("=" * 60)
    print("🎯 Objetivo: Entender estrutura do arquivo e campos específicos")
    print()
    
    try:
        # Analisar arquivo
        headers = analisar_estrutura_arquivo()
        
        # Verificar campos no banco
        campos_voucher_banco = verificar_campos_banco_safeid()
        
        # Mapear colunas
        mapeamento_padrao, mapeamento_safeid = mapear_colunas_arquivo_banco(headers)
        
        print(f"\n🎯 CONCLUSÕES PRELIMINARES:")
        print("=" * 40)
        print(f"📁 Arquivo tem {len(headers)} colunas")
        print(f"🎫 {len(mapeamento_safeid)} campos específicos do SafeID")
        print(f"✅ {len(mapeamento_padrao)} campos padrão mapeados")
        print(f"🗄️ {len(campos_voucher_banco)} campos voucher no banco")
        
        if len(campos_voucher_banco) == 0:
            print(f"\n⚠️ ATENÇÃO: Campos específicos do SafeID podem não existir no banco!")
            print(f"   Será necessário verificar se devem ser criados ou ignorados.")
        
        print(f"\n🎯 CARACTERÍSTICAS DO SAFEID:")
        print(f"   🎫 Sistema de vouchers (código, percentual, valor)")
        print(f"   📅 Controle de período de uso")
        print(f"   💰 Valores de pagamento específicos")
        print(f"   📋 100% dos protocolos já existem (apenas atualizações)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
