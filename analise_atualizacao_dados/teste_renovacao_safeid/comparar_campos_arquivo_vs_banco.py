#!/usr/bin/env python3
"""
COMPARAÇÃO ARQUIVO vs BANCO SAFEID
Compara os 30 campos do arquivo com os 33 campos do banco
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

def obter_campos_arquivo():
    """Obtém os 30 campos do arquivo SafeID"""
    print("📖 LENDO CAMPOS DO ARQUIVO SAFEID")
    print("=" * 40)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    campos_arquivo = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        campos_arquivo.append(header)
    
    print(f"📊 ARQUIVO TEM {len(campos_arquivo)} CAMPOS:")
    for i, campo in enumerate(campos_arquivo, 1):
        print(f"   {i:2d}. {campo}")
    
    return campos_arquivo

def obter_campos_banco():
    """Obtém os 33 campos da tabela renovacao_safeid"""
    print(f"\n🗄️ LENDO CAMPOS DA TABELA RENOVACAO_SAFEID")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'renovacao_safeid'
        ORDER BY ordinal_position
    """)
    
    campos_banco = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 BANCO TEM {len(campos_banco)} CAMPOS:")
    for i, campo in enumerate(campos_banco, 1):
        print(f"   {i:2d}. {campo}")
    
    conn.close()
    
    return campos_banco

def mapear_campos(campos_arquivo, campos_banco):
    """Mapeia campos do arquivo para campos do banco"""
    print(f"\n🔗 MAPEAMENTO ARQUIVO → BANCO")
    print("=" * 60)
    
    # Mapeamento direto baseado nos nomes
    mapeamento = {
        'Protocolo': 'protocolo',
        'Documento': 'documento',
        'Nome / Razão Social': 'nome_razao_social',
        'Autoridade de Registro Venda': 'autoridade_de_registro_venda',
        'Data de Pagamento': 'data_de_pagamento',
        'VoucherCodigo': 'vouchercodigo',
        'VoucherPercentual': 'voucherpercentual',
        'VoucherValor': 'vouchervalor',
        'Valor Pagamento': 'valor_pagamento',
        'Descrição Produto': 'descricao_produto',
        'Validade Certificado': 'validade_certificado',
        'Período de Uso': 'periodo_de_uso',
        'Data Início do Uso': 'data_inicio_do_uso',
        'Data Fim do Uso': 'data_fim_do_uso',
        'Status do Certificado': 'status_do_certificado',
        'Data de Revogação': 'data_de_revogacao',
        'Código de Revogação': 'codigo_de_revogacao',
        'Descrição da Revogação': 'descricao_da_revogacao',
        'CNPJ do parceiro': 'cnpj_do_parceiro',
        'Nome do parceiro': 'nome_do_parceiro',
        'CPF do contador': 'cpf_do_contador',
        'Consultor comercial': 'consultor_comercial',
        'Primeira Emissão': 'primeira_emissao',
        'Código do catalogo': 'codigo_do_catalogo',
        'Data de Faturamento': 'data_de_faturamento',
        'Nome Catalogo': 'nome_catalogo',
        'Email Titular': 'email_titular',
        'Telefone Titular': 'telefone_titular',
        'Renovado': 'renovado',
        'Status do Período de Uso': 'status_do_periodo_de_uso'
    }
    
    print(f"📋 MAPEAMENTO DOS 30 CAMPOS DO ARQUIVO:")
    print("-" * 60)
    
    campos_mapeados = []
    campos_nao_mapeados = []
    
    for i, campo_arquivo in enumerate(campos_arquivo, 1):
        if campo_arquivo in mapeamento:
            campo_banco = mapeamento[campo_arquivo]
            if campo_banco in campos_banco:
                print(f"   {i:2d}. ✅ {campo_arquivo:<35} → {campo_banco}")
                campos_mapeados.append(campo_banco)
            else:
                print(f"   {i:2d}. ❌ {campo_arquivo:<35} → {campo_banco} (NÃO EXISTE)")
                campos_nao_mapeados.append(campo_arquivo)
        else:
            print(f"   {i:2d}. ❓ {campo_arquivo:<35} → SEM MAPEAMENTO")
            campos_nao_mapeados.append(campo_arquivo)
    
    return campos_mapeados, campos_nao_mapeados

def identificar_campos_extras(campos_arquivo, campos_banco, campos_mapeados):
    """Identifica os 3 campos extras no banco"""
    print(f"\n🔍 IDENTIFICANDO CAMPOS EXTRAS NO BANCO")
    print("=" * 50)
    
    # Campos do banco que NÃO estão mapeados do arquivo
    campos_extras = []
    
    for campo_banco in campos_banco:
        if campo_banco not in campos_mapeados and campo_banco != 'id':  # id é sempre extra
            campos_extras.append(campo_banco)
    
    print(f"📊 CAMPOS EXTRAS NO BANCO ({len(campos_extras)}):")
    print("-" * 40)
    
    for i, campo in enumerate(campos_extras, 1):
        print(f"   {i}. 🆕 {campo}")
    
    # Verificar se são campos de controle
    print(f"\n💡 ANÁLISE DOS CAMPOS EXTRAS:")
    print("-" * 30)
    
    for campo in campos_extras:
        if 'id' in campo.lower():
            print(f"   🔑 {campo}: Campo de chave primária")
        elif 'data' in campo.lower() and 'atualizacao' in campo.lower():
            print(f"   📅 {campo}: Campo de controle de atualização")
        elif 'observacao' in campo.lower():
            print(f"   📝 {campo}: Campo de observações/logs")
        else:
            print(f"   ❓ {campo}: Campo adicional")
    
    return campos_extras

def main():
    """Função principal"""
    print("🔍 COMPARAÇÃO ARQUIVO vs BANCO SAFEID")
    print("=" * 60)
    print("🎯 Objetivo: Identificar os 3 campos extras no banco")
    print()
    
    try:
        # Obter campos do arquivo
        campos_arquivo = obter_campos_arquivo()
        
        # Obter campos do banco
        campos_banco = obter_campos_banco()
        
        # Mapear campos
        campos_mapeados, campos_nao_mapeados = mapear_campos(campos_arquivo, campos_banco)
        
        # Identificar campos extras
        campos_extras = identificar_campos_extras(campos_arquivo, campos_banco, campos_mapeados)
        
        print(f"\n🎯 RESUMO FINAL:")
        print("=" * 30)
        print(f"📁 Arquivo: {len(campos_arquivo)} campos")
        print(f"🗄️ Banco: {len(campos_banco)} campos")
        print(f"✅ Mapeados: {len(campos_mapeados)} campos")
        print(f"❌ Não mapeados: {len(campos_nao_mapeados)} campos")
        print(f"🆕 Extras no banco: {len(campos_extras)} campos")
        
        print(f"\n💡 EXPLICAÇÃO:")
        print(f"   📊 {len(campos_arquivo)} (arquivo) + {len(campos_extras)} (extras) = {len(campos_banco)} (banco)")
        
        if len(campos_extras) == 3:
            print(f"   ✅ Confirmado: 3 campos extras no banco")
        else:
            print(f"   ⚠️ Encontrados {len(campos_extras)} campos extras (esperado: 3)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
