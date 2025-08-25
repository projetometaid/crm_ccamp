#!/usr/bin/env python3
"""
ANÁLISE 100% DO BANCO DE DADOS - RENOVAÇÃO GERAL
Analisa TODOS os registros da tabela renovacao_geral para verificar estado dos campos
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

def analisar_100_porcento_banco():
    """Analisa 100% dos registros da tabela renovacao_geral"""
    print("🗄️ ANÁLISE 100% DO BANCO DE DADOS - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Analisando TODOS os registros da tabela renovacao_geral")
    print("📊 Verificando estado real dos campos de renovação")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Primeiro, contar total de registros
    cursor.execute("SELECT COUNT(*) FROM renovacao_geral")
    total_registros = cursor.fetchone()[0]
    
    print(f"📊 TOTAL DE REGISTROS NA TABELA: {total_registros:,}")
    print()
    
    # Analisar campo status_protocolo_renovacao
    print("🔍 ANALISANDO CAMPO: status_protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN status_protocolo_renovacao IS NULL THEN 'NULL'
                WHEN status_protocolo_renovacao = '' THEN 'VAZIO'
                ELSE status_protocolo_renovacao
            END as status_valor,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY CASE 
                WHEN status_protocolo_renovacao IS NULL THEN 'NULL'
                WHEN status_protocolo_renovacao = '' THEN 'VAZIO'
                ELSE status_protocolo_renovacao
            END
        ORDER BY quantidade DESC
    """)
    
    for status_valor, quantidade in cursor.fetchall():
        pct = (quantidade / total_registros) * 100
        print(f"   {status_valor:20}: {quantidade:,} registros ({pct:.1f}%)")
    
    # Analisar campo protocolo_renovacao
    print(f"\n🔍 ANALISANDO CAMPO: protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN protocolo_renovacao IS NULL THEN 'NULL'
                ELSE 'PREENCHIDO'
            END as status_valor,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY CASE 
                WHEN protocolo_renovacao IS NULL THEN 'NULL'
                ELSE 'PREENCHIDO'
            END
        ORDER BY quantidade DESC
    """)
    
    for status_valor, quantidade in cursor.fetchall():
        pct = (quantidade / total_registros) * 100
        print(f"   {status_valor:20}: {quantidade:,} registros ({pct:.1f}%)")
    
    # Mostrar alguns valores de protocolo_renovacao preenchidos
    cursor.execute("""
        SELECT protocolo_renovacao, COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE protocolo_renovacao IS NOT NULL
        GROUP BY protocolo_renovacao
        ORDER BY quantidade DESC
        LIMIT 10
    """)
    
    protocolos_preenchidos = cursor.fetchall()
    if protocolos_preenchidos:
        print(f"\n   📋 EXEMPLOS DE PROTOCOLOS_RENOVACAO PREENCHIDOS:")
        for protocolo, quantidade in protocolos_preenchidos:
            print(f"      {protocolo}: {quantidade} registros")
    
    # Analisar campo nome_da_ar_protocolo_renovacao
    print(f"\n🔍 ANALISANDO CAMPO: nome_da_ar_protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN nome_da_ar_protocolo_renovacao IS NULL THEN 'NULL'
                WHEN nome_da_ar_protocolo_renovacao = '' THEN 'VAZIO'
                ELSE nome_da_ar_protocolo_renovacao
            END as ar_valor,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY CASE 
                WHEN nome_da_ar_protocolo_renovacao IS NULL THEN 'NULL'
                WHEN nome_da_ar_protocolo_renovacao = '' THEN 'VAZIO'
                ELSE nome_da_ar_protocolo_renovacao
            END
        ORDER BY quantidade DESC
    """)
    
    for ar_valor, quantidade in cursor.fetchall():
        pct = (quantidade / total_registros) * 100
        ar_display = ar_valor[:30] if len(ar_valor) > 30 else ar_valor
        print(f"   {ar_display:30}: {quantidade:,} registros ({pct:.1f}%)")
    
    # Analisar campo produto_protocolo_renovacao
    print(f"\n🔍 ANALISANDO CAMPO: produto_protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN produto_protocolo_renovacao IS NULL THEN 'NULL'
                WHEN produto_protocolo_renovacao = '' THEN 'VAZIO'
                ELSE produto_protocolo_renovacao
            END as produto_valor,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY CASE 
                WHEN produto_protocolo_renovacao IS NULL THEN 'NULL'
                WHEN produto_protocolo_renovacao = '' THEN 'VAZIO'
                ELSE produto_protocolo_renovacao
            END
        ORDER BY quantidade DESC
    """)
    
    for produto_valor, quantidade in cursor.fetchall():
        pct = (quantidade / total_registros) * 100
        produto_display = produto_valor[:25] if len(produto_valor) > 25 else produto_valor
        print(f"   {produto_display:25}: {quantidade:,} registros ({pct:.1f}%)")
    
    # Análise combinada - registros com dados de renovação
    print(f"\n🔍 ANÁLISE COMBINADA - DADOS DE RENOVAÇÃO")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN protocolo_renovacao IS NOT NULL 
                     AND (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     AND (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     AND (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'COMPLETO'
                WHEN protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PROTOCOLO'
                WHEN (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     OR (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     OR (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'PARCIAL'
                ELSE 'VAZIO_TOTAL'
            END as categoria,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY CASE 
                WHEN protocolo_renovacao IS NOT NULL 
                     AND (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     AND (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     AND (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'COMPLETO'
                WHEN protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PROTOCOLO'
                WHEN (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     OR (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     OR (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'PARCIAL'
                ELSE 'VAZIO_TOTAL'
            END
        ORDER BY quantidade DESC
    """)
    
    for categoria, quantidade in cursor.fetchall():
        pct = (quantidade / total_registros) * 100
        print(f"   {categoria:20}: {quantidade:,} registros ({pct:.1f}%)")
    
    # Verificar especificamente os 1.300 protocolos do arquivo
    print(f"\n🔍 VERIFICANDO OS 1.300 PROTOCOLOS DO ARQUIVO")
    print("-" * 60)
    
    # Ler protocolos do arquivo
    import xlrd
    wb = xlrd.open_workbook("../GestaoRenovacao (1).xls")
    sheet = wb.sheet_by_index(0)
    
    protocolos_arquivo = []
    for row in range(1, sheet.nrows):
        protocolo_str = str(sheet.cell_value(row, 13)).strip()
        try:
            protocolo = int(float(protocolo_str))
            protocolos_arquivo.append(protocolo)
        except:
            continue
    
    placeholders = ','.join(['%s'] * len(protocolos_arquivo))
    
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN protocolo_renovacao IS NOT NULL 
                     AND (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     AND (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     AND (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'COMPLETO'
                WHEN protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PROTOCOLO'
                WHEN (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     OR (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     OR (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'PARCIAL'
                ELSE 'VAZIO_TOTAL'
            END as categoria,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE protocolo IN ({placeholders})
        GROUP BY CASE 
                WHEN protocolo_renovacao IS NOT NULL 
                     AND (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     AND (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     AND (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'COMPLETO'
                WHEN protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PROTOCOLO'
                WHEN (status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '')
                     OR (nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '')
                     OR (produto_protocolo_renovacao IS NOT NULL AND produto_protocolo_renovacao != '')
                THEN 'PARCIAL'
                ELSE 'VAZIO_TOTAL'
            END
        ORDER BY quantidade DESC
    """, protocolos_arquivo)
    
    print(f"📊 ESTADO DOS 1.300 PROTOCOLOS DO ARQUIVO:")
    for categoria, quantidade in cursor.fetchall():
        pct = (quantidade / len(protocolos_arquivo)) * 100
        print(f"   {categoria:20}: {quantidade:,} registros ({pct:.1f}%)")
    
    conn.close()
    
    return total_registros

def main():
    """Função principal"""
    try:
        total = analisar_100_porcento_banco()
        
        print(f"\n🎉 ANÁLISE 100% DO BANCO CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 Total analisado: {total:,} registros")
        print(f"🎯 Escopo: TODA a tabela renovacao_geral")
        print(f"📋 Objetivo: Verificar estado real dos campos")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
