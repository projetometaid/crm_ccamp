#!/usr/bin/env python3
"""
VERIFICAÇÃO DO TOTAL DE COLUNAS NO BANCO
Conta exatamente quantas colunas existem na tabela emissao
"""

import psycopg2

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def contar_colunas_banco():
    """Conta total de colunas na tabela emissao"""
    print("🔍 CONTANDO COLUNAS NA TABELA EMISSAO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Contar total de colunas
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'emissao'
    """)
    
    total_colunas = cursor.fetchone()[0]
    print(f"📊 TOTAL DE COLUNAS NA TABELA EMISSAO: {total_colunas}")
    
    # Listar todas as colunas
    cursor.execute("""
        SELECT 
            ordinal_position,
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        ORDER BY ordinal_position
    """)
    
    colunas = cursor.fetchall()
    
    print(f"\n📋 LISTA COMPLETA DAS {len(colunas)} COLUNAS:")
    print("-" * 80)
    print(f"{'POS':<4} {'NOME DA COLUNA':<40} {'TIPO':<20} {'TAMANHO':<10} {'NULL'}")
    print("-" * 80)
    
    for pos, col_name, data_type, max_length, nullable in colunas:
        tamanho = str(max_length) if max_length else '-'
        null_ok = 'YES' if nullable == 'YES' else 'NO'
        print(f'{pos:<4} {col_name:<40} {data_type:<20} {tamanho:<10} {null_ok}')
    
    conn.close()
    
    return total_colunas, colunas

def verificar_arquivo_vs_banco():
    """Compara colunas do arquivo SafeID com banco"""
    print(f"\n\n🔍 COMPARAÇÃO ARQUIVO SAFEID vs BANCO")
    print("=" * 50)
    
    # Colunas do arquivo SafeID (30 colunas)
    colunas_arquivo = [
        'Protocolo', 'Documento', 'Nome / Razão Social', 'Autoridade de Registro Venda',
        'Data de Pagamento', 'VoucherCodigo', 'VoucherPercentual', 'VoucherValor',
        'Valor Pagamento', 'Descrição Produto', 'Validade Certificado', 'Período de Uso',
        'Data Início do Uso', 'Data Fim do Uso', 'Status do Certificado', 'Data de Revogação',
        'Código de Revogação', 'Descrição da Revogação', 'CNPJ do parceiro', 'Nome do parceiro',
        'CPF do contador', 'Consultor comercial', 'Primeira Emissão', 'Código do catalogo',
        'Data de Faturamento', 'Nome Catalogo', 'Email Titular', 'Telefone Titular',
        'Renovado', 'Status do Período de Uso'
    ]
    
    print(f"📁 ARQUIVO SAFEID: {len(colunas_arquivo)} colunas")
    
    # Buscar colunas do banco
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        ORDER BY ordinal_position
    """)
    
    colunas_banco = [row[0] for row in cursor.fetchall()]
    
    print(f"🗄️ BANCO EMISSAO: {len(colunas_banco)} colunas")
    
    print(f"\n📊 DIFERENÇA: Banco tem {len(colunas_banco) - len(colunas_arquivo)} colunas a mais que o arquivo")
    
    # Verificar mapeamento possível
    mapeamento_possivel = {
        'Protocolo': 'protocolo',
        'Documento': 'documento', 
        'Nome / Razão Social': 'nome',
        'VoucherCodigo': 'vouchercodigo',
        'VoucherPercentual': 'voucherpercentual',
        'VoucherValor': 'vouchervalor',
        'Descrição Produto': 'produto',
        'Data Início do Uso': 'data_inicio_validade',
        'Data Fim do Uso': 'data_fim_validade',
        'Status do Certificado': 'status_do_certificado',
        'Email Titular': 'e_mail_do_titular',
        'Telefone Titular': 'telefone_do_titular',
        'Período de Uso': 'periodo_de_uso'
    }
    
    print(f"\n✅ CAMPOS QUE PODEM SER MAPEADOS:")
    print("-" * 40)
    
    campos_mapeados = 0
    for arquivo_col, banco_col in mapeamento_possivel.items():
        if banco_col in colunas_banco:
            print(f"   {arquivo_col:<30} → {banco_col}")
            campos_mapeados += 1
        else:
            print(f"   {arquivo_col:<30} → ❌ {banco_col} (NÃO EXISTE)")
    
    print(f"\n📊 RESUMO DO MAPEAMENTO:")
    print(f"   ✅ Campos mapeáveis: {campos_mapeados}")
    print(f"   ❌ Campos sem mapeamento: {len(colunas_arquivo) - campos_mapeados}")
    
    # Campo principal ausente
    print(f"\n🚨 CAMPO PRINCIPAL AUSENTE:")
    if 'renovado' not in colunas_banco:
        print(f"   ❌ 'renovado' NÃO EXISTE no banco")
        print(f"   🔧 Será necessário criar: ALTER TABLE emissao ADD COLUMN renovado VARCHAR(10);")
    else:
        print(f"   ✅ 'renovado' EXISTE no banco")
    
    conn.close()

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO TOTAL DE COLUNAS - BANCO vs ARQUIVO")
    print("=" * 70)
    print("🎯 Objetivo: Confirmar quantas colunas existem no banco")
    print()
    
    try:
        # Contar colunas do banco
        total_colunas, colunas_info = contar_colunas_banco()
        
        # Comparar com arquivo
        verificar_arquivo_vs_banco()
        
        print(f"\n🎯 CONCLUSÃO:")
        print("=" * 30)
        print(f"🗄️ Banco tem {total_colunas} colunas")
        print(f"📁 Arquivo SafeID tem 30 colunas")
        print(f"📊 Diferença: {total_colunas - 30} colunas a mais no banco")
        print(f"✅ Banco tem muito mais campos que o arquivo")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
