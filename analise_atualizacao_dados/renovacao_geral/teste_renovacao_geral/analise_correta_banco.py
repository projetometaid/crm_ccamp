#!/usr/bin/env python3
"""
ANÁLISE CORRETA DO BANCO DE DADOS - RENOVAÇÃO GERAL
Analisa CORRETAMENTE os dados do banco, especialmente campos de renovação
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

def analisar_banco_corretamente():
    """Analisa o banco de dados corretamente"""
    print("🗄️ ANÁLISE CORRETA DO BANCO DE DADOS - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Analisando CORRETAMENTE os dados do banco")
    print("🔍 Foco especial nos campos de renovação")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM renovacao_geral")
    total_registros = cursor.fetchone()[0]
    
    print(f"📊 TOTAL DE REGISTROS: {total_registros:,}")
    print()
    
    # Analisar campo protocolo_renovacao CORRETAMENTE
    print("🔍 ANÁLISE CORRETA: protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(protocolo_renovacao) as preenchidos,
            COUNT(*) - COUNT(protocolo_renovacao) as nulos
        FROM renovacao_geral
    """)
    
    total, preenchidos, nulos = cursor.fetchone()
    pct_preenchidos = (preenchidos / total) * 100
    pct_nulos = (nulos / total) * 100
    
    print(f"   📊 Total: {total:,}")
    print(f"   ✅ Preenchidos: {preenchidos:,} ({pct_preenchidos:.1f}%)")
    print(f"   ⚪ NULL/Vazios: {nulos:,} ({pct_nulos:.1f}%)")
    
    # Mostrar alguns exemplos de protocolos de renovação
    if preenchidos > 0:
        cursor.execute("""
            SELECT protocolo_renovacao, COUNT(*) as quantidade
            FROM renovacao_geral
            WHERE protocolo_renovacao IS NOT NULL
            GROUP BY protocolo_renovacao
            ORDER BY quantidade DESC
            LIMIT 10
        """)
        
        print(f"\n   💡 EXEMPLOS DE PROTOCOLOS DE RENOVAÇÃO:")
        for protocolo, quantidade in cursor.fetchall():
            print(f"      {protocolo}: {quantidade} registros")
    
    # Analisar campo status_protocolo_renovacao CORRETAMENTE
    print(f"\n🔍 ANÁLISE CORRETA: status_protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            status_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY status_protocolo_renovacao
        ORDER BY quantidade DESC
    """)
    
    for status, quantidade in cursor.fetchall():
        pct = (quantidade / total_registros) * 100
        status_display = status if status else 'NULL'
        print(f"   {status_display:15}: {quantidade:,} registros ({pct:.1f}%)")
    
    # Analisar campo nome_da_ar_protocolo_renovacao CORRETAMENTE
    print(f"\n🔍 ANÁLISE CORRETA: nome_da_ar_protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(nome_da_ar_protocolo_renovacao) as preenchidos,
            COUNT(*) - COUNT(nome_da_ar_protocolo_renovacao) as nulos
        FROM renovacao_geral
        WHERE nome_da_ar_protocolo_renovacao IS NOT NULL 
        AND nome_da_ar_protocolo_renovacao != ''
    """)
    
    total_ar, preenchidos_ar, nulos_ar = cursor.fetchone()
    
    cursor.execute("""
        SELECT 
            nome_da_ar_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE nome_da_ar_protocolo_renovacao IS NOT NULL 
        AND nome_da_ar_protocolo_renovacao != ''
        GROUP BY nome_da_ar_protocolo_renovacao
        ORDER BY quantidade DESC
        LIMIT 10
    """)
    
    ars_encontradas = cursor.fetchall()
    
    if ars_encontradas:
        print(f"   ✅ ARs encontradas no banco:")
        for ar, quantidade in ars_encontradas:
            pct = (quantidade / total_registros) * 100
            print(f"      {ar[:30]:30}: {quantidade:,} registros ({pct:.1f}%)")
    else:
        print(f"   ⚪ Nenhuma AR encontrada (todos NULL/vazios)")
    
    # Analisar campo produto_protocolo_renovacao CORRETAMENTE
    print(f"\n🔍 ANÁLISE CORRETA: produto_protocolo_renovacao")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            produto_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE produto_protocolo_renovacao IS NOT NULL 
        AND produto_protocolo_renovacao != ''
        GROUP BY produto_protocolo_renovacao
        ORDER BY quantidade DESC
        LIMIT 10
    """)
    
    produtos_encontrados = cursor.fetchall()
    
    if produtos_encontrados:
        print(f"   ✅ Produtos encontrados no banco:")
        for produto, quantidade in produtos_encontrados:
            pct = (quantidade / total_registros) * 100
            print(f"      {produto[:25]:25}: {quantidade:,} registros ({pct:.1f}%)")
    else:
        print(f"   ⚪ Nenhum produto encontrado (todos NULL/vazios)")
    
    # Análise combinada CORRETA
    print(f"\n🔍 ANÁLISE COMBINADA CORRETA")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN protocolo_renovacao IS NOT NULL 
                     AND status_protocolo_renovacao IS NOT NULL 
                     AND nome_da_ar_protocolo_renovacao IS NOT NULL 
                     AND produto_protocolo_renovacao IS NOT NULL 
                THEN 'DADOS_COMPLETOS'
                WHEN protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PROTOCOLO'
                WHEN status_protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_STATUS'
                WHEN nome_da_ar_protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_AR'
                WHEN produto_protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PRODUTO'
                ELSE 'TODOS_VAZIOS'
            END as categoria,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY CASE 
                WHEN protocolo_renovacao IS NOT NULL 
                     AND status_protocolo_renovacao IS NOT NULL 
                     AND nome_da_ar_protocolo_renovacao IS NOT NULL 
                     AND produto_protocolo_renovacao IS NOT NULL 
                THEN 'DADOS_COMPLETOS'
                WHEN protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PROTOCOLO'
                WHEN status_protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_STATUS'
                WHEN nome_da_ar_protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_AR'
                WHEN produto_protocolo_renovacao IS NOT NULL 
                THEN 'APENAS_PRODUTO'
                ELSE 'TODOS_VAZIOS'
            END
        ORDER BY quantidade DESC
    """)
    
    for categoria, quantidade in cursor.fetchall():
        pct = (quantidade / total_registros) * 100
        print(f"   {categoria:15}: {quantidade:,} registros ({pct:.1f}%)")
    
    # Mostrar alguns registros REAIS com dados de renovação
    print(f"\n💡 EXEMPLOS REAIS DE REGISTROS COM DADOS DE RENOVAÇÃO:")
    print("-" * 80)
    
    cursor.execute("""
        SELECT protocolo, protocolo_renovacao, status_protocolo_renovacao,
               nome_da_ar_protocolo_renovacao, produto_protocolo_renovacao
        FROM renovacao_geral
        WHERE protocolo_renovacao IS NOT NULL
        ORDER BY protocolo
        LIMIT 10
    """)
    
    registros_com_dados = cursor.fetchall()
    
    if registros_com_dados:
        print(f"{'Protocolo':12} | {'Prot.Renov':12} | {'Status':15} | {'AR':20} | {'Produto':15}")
        print("-" * 80)
        
        for protocolo, prot_ren, status, ar, produto in registros_com_dados:
            status_str = status[:15] if status else 'NULL'
            ar_str = ar[:20] if ar else 'NULL'
            produto_str = produto[:15] if produto else 'NULL'
            
            print(f"{protocolo:12} | {prot_ren:12} | {status_str:15} | {ar_str:20} | {produto_str:15}")
    else:
        print("   ⚪ Nenhum registro com dados de renovação encontrado")
    
    # Verificar especificamente os 1.300 protocolos do arquivo atual
    print(f"\n🔍 VERIFICANDO OS 1.300 PROTOCOLOS DO ARQUIVO ATUAL")
    print("-" * 60)
    
    # Ler protocolos do arquivo atual
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
            COUNT(*) as total,
            COUNT(protocolo_renovacao) as com_protocolo,
            COUNT(CASE WHEN status_protocolo_renovacao IS NOT NULL THEN 1 END) as com_status,
            COUNT(CASE WHEN nome_da_ar_protocolo_renovacao IS NOT NULL THEN 1 END) as com_ar,
            COUNT(CASE WHEN produto_protocolo_renovacao IS NOT NULL THEN 1 END) as com_produto
        FROM renovacao_geral
        WHERE protocolo IN ({placeholders})
    """, protocolos_arquivo)
    
    total_1300, com_prot, com_status, com_ar, com_produto = cursor.fetchone()
    
    print(f"📊 ESTADO DOS 1.300 PROTOCOLOS DO ARQUIVO:")
    print(f"   📊 Total encontrado no banco: {total_1300:,}")
    print(f"   🔄 Com protocolo_renovacao: {com_prot:,} ({com_prot/total_1300*100:.1f}%)")
    print(f"   📊 Com status_protocolo_renovacao: {com_status:,} ({com_status/total_1300*100:.1f}%)")
    print(f"   🏢 Com nome_da_ar_protocolo_renovacao: {com_ar:,} ({com_ar/total_1300*100:.1f}%)")
    print(f"   🏷️ Com produto_protocolo_renovacao: {com_produto:,} ({com_produto/total_1300*100:.1f}%)")
    
    conn.close()
    
    return total_registros

def main():
    """Função principal"""
    try:
        total = analisar_banco_corretamente()
        
        print(f"\n🎉 ANÁLISE CORRETA DO BANCO CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 Total analisado: {total:,} registros")
        print(f"🎯 Análise CORRETA dos campos de renovação")
        print(f"🔍 Agora sabemos a VERDADE sobre o banco")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
