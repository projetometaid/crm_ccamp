#!/usr/bin/env python3
"""
ANÁLISE APENAS DO SAFEID
Analisa SOMENTE os 160 protocolos do arquivo SafeID e seus campos específicos
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

def obter_protocolos_safeid():
    """Obtém APENAS os 160 protocolos do arquivo SafeID"""
    print("📖 LENDO PROTOCOLOS DO ARQUIVO SAFEID")
    print("=" * 40)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    protocolos = []
    for row in range(1, sheet.nrows):  # Pular cabeçalho
        protocolo = str(sheet.cell_value(row, 0)).strip()  # Coluna 0 = Protocolo
        if protocolo:
            protocolos.append(int(float(protocolo)))
    
    print(f"📊 Total de protocolos SafeID: {len(protocolos)}")
    print(f"🔍 Primeiro: {min(protocolos):,}")
    print(f"🔍 Último: {max(protocolos):,}")
    
    return protocolos

def analisar_campos_safeid_banco(protocolos_safeid):
    """Analisa APENAS os campos dos protocolos SafeID no banco"""
    print(f"\n🔍 ANALISANDO CAMPOS SAFEID NO BANCO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Campos específicos do SafeID que queremos analisar
    campos_safeid = [
        'protocolo', 'nome', 'documento', 'produto', 'status_do_certificado',
        'data_inicio_validade', 'data_fim_validade', 'vouchercodigo', 
        'voucherpercentual', 'vouchervalor', 'periodo_de_uso',
        'e_mail_do_titular', 'telefone_do_titular'
    ]
    
    # Verificar se campo 'renovado' existe
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'emissao' AND column_name = 'renovado'
    """)
    
    campo_renovado_existe = cursor.fetchone() is not None
    if campo_renovado_existe:
        campos_safeid.append('renovado')
    
    print(f"📋 CAMPOS SAFEID ANALISADOS: {len(campos_safeid)}")
    for i, campo in enumerate(campos_safeid, 1):
        status = "✅" if campo != 'renovado' or campo_renovado_existe else "❌"
        print(f"   {i:2d}. {status} {campo}")
    
    if not campo_renovado_existe:
        print(f"\n🚨 CAMPO 'renovado' NÃO EXISTE - Precisa ser criado!")
    
    # Buscar dados dos protocolos SafeID
    protocolos_str = ','.join(map(str, protocolos_safeid[:10]))  # Primeiros 10
    
    campos_select = ', '.join(campos_safeid[:-1] if not campo_renovado_existe else campos_safeid)
    
    cursor.execute(f"""
        SELECT {campos_select}
        FROM emissao 
        WHERE protocolo IN ({protocolos_str})
        ORDER BY protocolo
    """)
    
    registros = cursor.fetchall()
    
    print(f"\n📊 DADOS DOS PRIMEIROS 10 PROTOCOLOS SAFEID:")
    print("-" * 80)
    
    for i, registro in enumerate(registros, 1):
        protocolo = registro[0]
        nome = registro[1][:30] if registro[1] else 'NULL'
        produto = registro[3] if len(registro) > 3 else 'NULL'
        status = registro[4] if len(registro) > 4 else 'NULL'
        
        print(f"{i:2d}. {protocolo} | {nome} | {produto} | {status}")
    
    # Analisar campos específicos
    print(f"\n📊 ANÁLISE DE CAMPOS ESPECÍFICOS:")
    print("-" * 50)
    
    for protocolo in protocolos_safeid[:5]:  # Primeiros 5
        cursor.execute("""
            SELECT vouchercodigo, voucherpercentual, vouchervalor, periodo_de_uso
            FROM emissao WHERE protocolo = %s
        """, (protocolo,))
        
        resultado = cursor.fetchone()
        if resultado:
            voucher_cod, voucher_perc, voucher_val, periodo = resultado
            print(f"   {protocolo}: VoucherCod={voucher_cod}, VoucherPerc={voucher_perc}, Período={periodo}")
    
    conn.close()
    
    return len(campos_safeid), campo_renovado_existe

def comparar_arquivo_vs_banco_safeid():
    """Compara APENAS os campos do SafeID: arquivo vs banco"""
    print(f"\n🔍 COMPARAÇÃO SAFEID: ARQUIVO vs BANCO")
    print("=" * 50)
    
    # 30 colunas do arquivo SafeID
    colunas_arquivo_safeid = [
        'Protocolo', 'Documento', 'Nome / Razão Social', 'Autoridade de Registro Venda',
        'Data de Pagamento', 'VoucherCodigo', 'VoucherPercentual', 'VoucherValor',
        'Valor Pagamento', 'Descrição Produto', 'Validade Certificado', 'Período de Uso',
        'Data Início do Uso', 'Data Fim do Uso', 'Status do Certificado', 'Data de Revogação',
        'Código de Revogação', 'Descrição da Revogação', 'CNPJ do parceiro', 'Nome do parceiro',
        'CPF do contador', 'Consultor comercial', 'Primeira Emissão', 'Código do catalogo',
        'Data de Faturamento', 'Nome Catalogo', 'Email Titular', 'Telefone Titular',
        'Renovado', 'Status do Período de Uso'
    ]
    
    print(f"📁 ARQUIVO SAFEID: {len(colunas_arquivo_safeid)} colunas")
    
    # Mapeamento específico para SafeID
    mapeamento_safeid = {
        'Protocolo': 'protocolo',
        'Documento': 'documento',
        'Nome / Razão Social': 'nome',
        'VoucherCodigo': 'vouchercodigo',
        'VoucherPercentual': 'voucherpercentual', 
        'VoucherValor': 'vouchervalor',
        'Descrição Produto': 'produto',
        'Período de Uso': 'periodo_de_uso',
        'Data Início do Uso': 'data_inicio_validade',
        'Data Fim do Uso': 'data_fim_validade',
        'Status do Certificado': 'status_do_certificado',
        'Email Titular': 'e_mail_do_titular',
        'Telefone Titular': 'telefone_do_titular',
        'Renovado': 'renovado'  # Campo principal
    }
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    print(f"\n✅ MAPEAMENTO SAFEID:")
    print("-" * 40)
    
    campos_mapeados = 0
    campo_principal_existe = False
    
    for arquivo_col, banco_col in mapeamento_safeid.items():
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'emissao' AND column_name = %s
        """, (banco_col,))
        
        existe = cursor.fetchone() is not None
        
        if existe:
            status = "✅"
            campos_mapeados += 1
            if banco_col == 'renovado':
                campo_principal_existe = True
        else:
            status = "❌"
        
        print(f"   {status} {arquivo_col:<25} → {banco_col}")
    
    conn.close()
    
    print(f"\n📊 RESUMO SAFEID:")
    print(f"   📁 Colunas no arquivo: {len(colunas_arquivo_safeid)}")
    print(f"   ✅ Campos mapeáveis: {campos_mapeados}")
    print(f"   ❌ Campos sem mapeamento: {len(colunas_arquivo_safeid) - campos_mapeados}")
    
    if not campo_principal_existe:
        print(f"\n🚨 CAMPO PRINCIPAL AUSENTE:")
        print(f"   ❌ 'renovado' NÃO EXISTE")
        print(f"   🔧 AÇÃO: ALTER TABLE emissao ADD COLUMN renovado VARCHAR(10);")
    
    return campos_mapeados, campo_principal_existe

def main():
    """Função principal"""
    print("🔍 ANÁLISE APENAS DO SAFEID")
    print("=" * 50)
    print("🎯 Foco: SOMENTE os 160 protocolos do SafeID")
    print()
    
    try:
        # Obter protocolos do SafeID
        protocolos_safeid = obter_protocolos_safeid()
        
        # Analisar campos no banco
        total_campos, renovado_existe = analisar_campos_safeid_banco(protocolos_safeid)
        
        # Comparar arquivo vs banco
        campos_mapeados, campo_principal = comparar_arquivo_vs_banco_safeid()
        
        print(f"\n🎯 CONCLUSÃO SAFEID:")
        print("=" * 30)
        print(f"📊 Protocolos SafeID: {len(protocolos_safeid)}")
        print(f"📊 Campos analisados: {total_campos}")
        print(f"📊 Campos mapeáveis: {campos_mapeados}")
        print(f"🎯 Campo 'renovado': {'✅ EXISTE' if renovado_existe else '❌ CRIAR'}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
