#!/usr/bin/env python3
"""
ANÁLISE PÓS-ATUALIZAÇÃO - RENOVAÇÃO GERAL
Verifica se os dados foram atualizados corretamente e analisa distribuição por ARs
"""

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

def analisar_dados_pos_atualizacao():
    """Analisa os dados após a atualização"""
    print("🔍 ANÁLISE PÓS-ATUALIZAÇÃO - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Verificando se os campos foram atualizados corretamente")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM renovacao_geral")
    total_registros = cursor.fetchone()[0]
    
    print(f"📊 TOTAL DE REGISTROS: {total_registros:,}")
    print()
    
    # Verificar status dos campos após atualização
    print("🔍 STATUS DOS CAMPOS APÓS ATUALIZAÇÃO:")
    print("-" * 60)
    
    # Campo status_protocolo_renovacao
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(status_protocolo_renovacao) as preenchidos,
            COUNT(*) - COUNT(status_protocolo_renovacao) as nulos
        FROM renovacao_geral
    """)
    
    total, preenchidos, nulos = cursor.fetchone()
    pct_preenchidos = (preenchidos / total) * 100
    
    print(f"📊 status_protocolo_renovacao:")
    print(f"   ✅ Preenchidos: {preenchidos:,} ({pct_preenchidos:.1f}%)")
    print(f"   ⚪ NULL/Vazios: {nulos:,} ({(nulos/total)*100:.1f}%)")
    
    # Campo nome_da_ar_protocolo_renovacao
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
        SELECT COUNT(*) 
        FROM renovacao_geral
        WHERE nome_da_ar_protocolo_renovacao IS NOT NULL 
        AND nome_da_ar_protocolo_renovacao != ''
    """)
    
    preenchidos_ar_real = cursor.fetchone()[0]
    nulos_ar_real = total_registros - preenchidos_ar_real
    
    print(f"\n🏢 nome_da_ar_protocolo_renovacao:")
    print(f"   ✅ Preenchidos: {preenchidos_ar_real:,} ({(preenchidos_ar_real/total_registros)*100:.1f}%)")
    print(f"   ⚪ NULL/Vazios: {nulos_ar_real:,} ({(nulos_ar_real/total_registros)*100:.1f}%)")
    
    # Campo produto_protocolo_renovacao
    cursor.execute("""
        SELECT COUNT(*) 
        FROM renovacao_geral
        WHERE produto_protocolo_renovacao IS NOT NULL 
        AND produto_protocolo_renovacao != ''
    """)
    
    preenchidos_produto = cursor.fetchone()[0]
    nulos_produto = total_registros - preenchidos_produto
    
    print(f"\n🏷️ produto_protocolo_renovacao:")
    print(f"   ✅ Preenchidos: {preenchidos_produto:,} ({(preenchidos_produto/total_registros)*100:.1f}%)")
    print(f"   ⚪ NULL/Vazios: {nulos_produto:,} ({(nulos_produto/total_registros)*100:.1f}%)")
    
    conn.close()

def analisar_agosto_2025():
    """Analisa especificamente dados de agosto de 2025"""
    print(f"\n📅 ANÁLISE ESPECÍFICA - AGOSTO 2025")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar registros de agosto de 2025
    cursor.execute("""
        SELECT COUNT(*) 
        FROM renovacao_geral
        WHERE (data_inicio_validade >= '2025-08-01' AND data_inicio_validade < '2025-09-01')
        OR (data_fim_validade >= '2025-08-01' AND data_fim_validade < '2025-09-01')
    """)
    
    total_agosto = cursor.fetchone()[0]
    
    if total_agosto == 0:
        print("⚪ Nenhum registro encontrado para agosto de 2025")
        print("🔍 Verificando outros meses de 2025...")
        
        cursor.execute("""
            SELECT 
                EXTRACT(MONTH FROM data_inicio_validade) as mes,
                COUNT(*) as quantidade
            FROM renovacao_geral
            WHERE EXTRACT(YEAR FROM data_inicio_validade) = 2025
            GROUP BY EXTRACT(MONTH FROM data_inicio_validade)
            ORDER BY mes
        """)
        
        meses_2025 = cursor.fetchall()
        
        if meses_2025:
            print(f"\n📊 REGISTROS POR MÊS EM 2025:")
            meses_nomes = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                          7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
            
            for mes, quantidade in meses_2025:
                mes_nome = meses_nomes.get(int(mes), f'Mês {int(mes)}')
                print(f"   {mes_nome} 2025: {quantidade:,} registros")
        else:
            print("⚪ Nenhum registro encontrado para 2025")
    else:
        print(f"📊 Total de registros em agosto 2025: {total_agosto:,}")
        
        # Analisar campos de renovação para agosto 2025
        cursor.execute("""
            SELECT 
                COUNT(status_protocolo_renovacao) as com_status,
                COUNT(nome_da_ar_protocolo_renovacao) as com_ar,
                COUNT(produto_protocolo_renovacao) as com_produto
            FROM renovacao_geral
            WHERE (data_inicio_validade >= '2025-08-01' AND data_inicio_validade < '2025-09-01')
            OR (data_fim_validade >= '2025-08-01' AND data_fim_validade < '2025-09-01')
        """)
        
        com_status, com_ar, com_produto = cursor.fetchone()
        
        print(f"   📊 Com status_protocolo_renovacao: {com_status:,} ({(com_status/total_agosto)*100:.1f}%)")
        print(f"   🏢 Com nome_da_ar_protocolo_renovacao: {com_ar:,} ({(com_ar/total_agosto)*100:.1f}%)")
        print(f"   🏷️ Com produto_protocolo_renovacao: {com_produto:,} ({(com_produto/total_agosto)*100:.1f}%)")
    
    conn.close()

def analisar_distribuicao_ars():
    """Analisa distribuição por ARs (AR Certificado Campinas vs Concorrentes)"""
    print(f"\n🏢 ANÁLISE DE DISTRIBUIÇÃO POR ARs")
    print("=" * 60)
    print("🎯 AR Certificado Campinas vs Concorrentes")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Distribuição geral por AR
    cursor.execute("""
        SELECT 
            nome_da_ar_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE nome_da_ar_protocolo_renovacao IS NOT NULL 
        AND nome_da_ar_protocolo_renovacao != ''
        GROUP BY nome_da_ar_protocolo_renovacao
        ORDER BY quantidade DESC
    """)
    
    ars_distribuicao = cursor.fetchall()
    
    if not ars_distribuicao:
        print("⚪ Nenhuma AR encontrada nos dados")
        conn.close()
        return
    
    # Calcular totais
    total_com_ar = sum(quantidade for _, quantidade in ars_distribuicao)
    
    print(f"📊 DISTRIBUIÇÃO GERAL POR AR ({total_com_ar:,} registros com AR):")
    print("-" * 70)
    
    ar_campinas_total = 0
    concorrentes_total = 0
    
    for ar, quantidade in ars_distribuicao:
        pct = (quantidade / total_com_ar) * 100
        
        if 'CERTIFICADO CAMPINAS' in ar.upper():
            ar_campinas_total += quantidade
            status = "🏆 NOSSA AR"
        else:
            concorrentes_total += quantidade
            status = "🔴 CONCORRENTE"
        
        print(f"   {ar[:40]:40} | {quantidade:,} ({pct:.1f}%) | {status}")
    
    # Resumo
    print(f"\n📊 RESUMO COMPETITIVO:")
    print("-" * 50)
    
    pct_campinas = (ar_campinas_total / total_com_ar) * 100
    pct_concorrentes = (concorrentes_total / total_com_ar) * 100
    
    print(f"🏆 AR CERTIFICADO CAMPINAS: {ar_campinas_total:,} ({pct_campinas:.1f}%)")
    print(f"🔴 CONCORRENTES: {concorrentes_total:,} ({pct_concorrentes:.1f}%)")
    
    # Análise por status
    print(f"\n📊 ANÁLISE POR STATUS DE RENOVAÇÃO:")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            status_protocolo_renovacao,
            CASE 
                WHEN nome_da_ar_protocolo_renovacao LIKE '%CERTIFICADO CAMPINAS%' THEN 'AR_CAMPINAS'
                WHEN nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '' THEN 'CONCORRENTES'
                ELSE 'SEM_AR'
            END as categoria_ar,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE status_protocolo_renovacao IS NOT NULL
        GROUP BY status_protocolo_renovacao, categoria_ar
        ORDER BY status_protocolo_renovacao, categoria_ar
    """)
    
    status_ar = cursor.fetchall()
    
    for status, categoria, quantidade in status_ar:
        if categoria == 'AR_CAMPINAS':
            emoji = "🏆"
        elif categoria == 'CONCORRENTES':
            emoji = "🔴"
        else:
            emoji = "⚪"
        
        print(f"   {status:15} | {categoria:15} | {emoji} {quantidade:,}")
    
    # Top 5 concorrentes
    print(f"\n🔴 TOP 5 CONCORRENTES:")
    print("-" * 50)
    
    concorrentes = [(ar, qtd) for ar, qtd in ars_distribuicao 
                   if 'CERTIFICADO CAMPINAS' not in ar.upper()]
    
    for i, (ar, quantidade) in enumerate(concorrentes[:5], 1):
        pct = (quantidade / total_com_ar) * 100
        print(f"   {i}. {ar[:35]:35} | {quantidade:,} ({pct:.1f}%)")
    
    conn.close()

def analisar_produtos_renovacao():
    """Analisa distribuição por produtos de renovação"""
    print(f"\n🏷️ ANÁLISE DE PRODUTOS DE RENOVAÇÃO")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            produto_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE produto_protocolo_renovacao IS NOT NULL 
        AND produto_protocolo_renovacao != ''
        GROUP BY produto_protocolo_renovacao
        ORDER BY quantidade DESC
    """)
    
    produtos = cursor.fetchall()
    
    if produtos:
        total_produtos = sum(quantidade for _, quantidade in produtos)
        
        print(f"📊 DISTRIBUIÇÃO POR PRODUTO ({total_produtos:,} registros):")
        for produto, quantidade in produtos:
            pct = (quantidade / total_produtos) * 100
            print(f"   {produto:25} | {quantidade:,} ({pct:.1f}%)")
    else:
        print("⚪ Nenhum produto de renovação encontrado")
    
    conn.close()

def main():
    """Função principal"""
    try:
        # Análise geral pós-atualização
        analisar_dados_pos_atualizacao()
        
        # Análise específica de agosto 2025
        analisar_agosto_2025()
        
        # Análise de distribuição por ARs
        analisar_distribuicao_ars()
        
        # Análise de produtos
        analisar_produtos_renovacao()
        
        print(f"\n🎉 ANÁLISE PÓS-ATUALIZAÇÃO CONCLUÍDA!")
        print("=" * 50)
        print(f"✅ Dados verificados e analisados")
        print(f"📊 Distribuição por ARs mapeada")
        print(f"🏆 Posição competitiva identificada")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
