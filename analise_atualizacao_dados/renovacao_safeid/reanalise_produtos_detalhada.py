#!/usr/bin/env python3
"""
REANÁLISE DETALHADA DOS PRODUTOS - RENOVACAO_SAFEID
Analisa TODOS os produtos para identificar variações além do SafeID e-CPF
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

def analisar_produtos_detalhado():
    """Analisa todos os produtos de forma detalhada"""
    print("🔍 REANÁLISE DETALHADA DOS PRODUTOS - RENOVACAO_SAFEID")
    print("=" * 70)
    print("🎯 Verificando TODOS os tipos de produtos")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Analisar TODOS os produtos únicos
    cursor.execute("""
        SELECT 
            descricao_produto,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY descricao_produto
        ORDER BY quantidade DESC
    """)
    
    produtos = cursor.fetchall()
    total = sum(qtd for _, qtd in produtos)
    
    print(f"📊 TODOS OS PRODUTOS ENCONTRADOS ({total:,} registros):")
    print("-" * 70)
    
    for produto, quantidade in produtos:
        pct = (quantidade / total) * 100
        
        # Identificar tipo de produto
        if 'e-CPF' in produto.upper():
            emoji = "👤"
            tipo = "PESSOA FÍSICA"
        elif 'e-CNPJ' in produto.upper() or 'CNPJ' in produto.upper():
            emoji = "🏢"
            tipo = "PESSOA JURÍDICA"
        elif 'SAFEID' in produto.upper():
            emoji = "🔐"
            tipo = "SAFEID"
        else:
            emoji = "❓"
            tipo = "OUTRO"
        
        print(f"   {emoji} {produto:40} | {quantidade:,} ({pct:.1f}%) | {tipo}")
    
    conn.close()
    
    return produtos

def analisar_documentos_por_produto():
    """Analisa os documentos (CPF/CNPJ) por tipo de produto"""
    print(f"\n📋 ANÁLISE DE DOCUMENTOS POR PRODUTO")
    print("-" * 70)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Analisar documentos por produto
    cursor.execute("""
        SELECT 
            descricao_produto,
            LENGTH(documento) as tamanho_doc,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY descricao_produto, LENGTH(documento)
        ORDER BY descricao_produto, tamanho_doc
    """)
    
    docs_por_produto = cursor.fetchall()
    
    print(f"📊 TAMANHO DOS DOCUMENTOS POR PRODUTO:")
    print("-" * 70)
    
    for produto, tamanho, quantidade in docs_por_produto:
        if tamanho == 11:
            doc_tipo = "CPF"
            emoji = "👤"
        elif tamanho == 14:
            doc_tipo = "CNPJ"
            emoji = "🏢"
        else:
            doc_tipo = f"OUTRO ({tamanho} dígitos)"
            emoji = "❓"
        
        print(f"   {emoji} {produto:40} | {doc_tipo:15} | {quantidade:,} registros")
    
    conn.close()

def analisar_amostras_por_produto():
    """Mostra amostras de registros por tipo de produto"""
    print(f"\n🔍 AMOSTRAS DE REGISTROS POR PRODUTO")
    print("-" * 70)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar produtos únicos
    cursor.execute("""
        SELECT DISTINCT descricao_produto
        FROM renovacao_safeid
        ORDER BY descricao_produto
    """)
    
    produtos_unicos = [row[0] for row in cursor.fetchall()]
    
    for produto in produtos_unicos:
        print(f"\n📋 PRODUTO: {produto}")
        print("-" * 50)
        
        # Buscar amostra de registros deste produto
        cursor.execute("""
            SELECT 
                protocolo,
                documento,
                nome_razao_social,
                LENGTH(documento) as tamanho_doc
            FROM renovacao_safeid
            WHERE descricao_produto = %s
            ORDER BY RANDOM()
            LIMIT 5
        """, (produto,))
        
        amostras = cursor.fetchall()
        
        print(f"{'Protocolo':12} | {'Documento':15} | {'Nome':30} | {'Tipo':5}")
        print("-" * 70)
        
        for protocolo, documento, nome, tamanho in amostras:
            doc_tipo = "CPF" if tamanho == 11 else "CNPJ" if tamanho == 14 else "?"
            nome_short = nome[:30] if nome else 'N/A'
            
            print(f"{protocolo:12} | {documento:15} | {nome_short:30} | {doc_tipo:5}")
    
    conn.close()

def analisar_combinacoes_produto_validade():
    """Analisa combinações de produto com validade e período"""
    print(f"\n📊 COMBINAÇÕES PRODUTO × VALIDADE × PERÍODO")
    print("-" * 70)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            descricao_produto,
            validade_certificado,
            periodo_de_uso,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY descricao_produto, validade_certificado, periodo_de_uso
        ORDER BY descricao_produto, quantidade DESC
    """)
    
    combinacoes = cursor.fetchall()
    
    produto_atual = None
    
    for produto, validade, periodo, quantidade in combinacoes:
        if produto != produto_atual:
            print(f"\n🔐 {produto}:")
            produto_atual = produto
        
        print(f"   📅 {validade} + {periodo}: {quantidade:,} registros")
    
    conn.close()

def verificar_inconsistencias():
    """Verifica possíveis inconsistências entre produto e documento"""
    print(f"\n⚠️ VERIFICAÇÃO DE INCONSISTÊNCIAS")
    print("-" * 70)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar produtos e-CPF com CNPJ
    cursor.execute("""
        SELECT COUNT(*) 
        FROM renovacao_safeid
        WHERE descricao_produto LIKE '%e-CPF%'
        AND LENGTH(documento) = 14
    """)
    
    cpf_com_cnpj = cursor.fetchone()[0]
    
    # Verificar produtos e-CNPJ com CPF
    cursor.execute("""
        SELECT COUNT(*) 
        FROM renovacao_safeid
        WHERE descricao_produto LIKE '%e-CNPJ%'
        AND LENGTH(documento) = 11
    """)
    
    cnpj_com_cpf = cursor.fetchone()[0]
    
    # Verificar SafeID com CNPJ
    cursor.execute("""
        SELECT COUNT(*) 
        FROM renovacao_safeid
        WHERE descricao_produto LIKE '%SafeID%'
        AND LENGTH(documento) = 14
    """)
    
    safeid_com_cnpj = cursor.fetchone()[0]
    
    print(f"🔍 POSSÍVEIS INCONSISTÊNCIAS:")
    print(f"   ⚠️ Produtos e-CPF com CNPJ: {cpf_com_cnpj:,} registros")
    print(f"   ⚠️ Produtos e-CNPJ com CPF: {cnpj_com_cpf:,} registros")
    print(f"   ⚠️ SafeID com CNPJ: {safeid_com_cnpj:,} registros")
    
    if safeid_com_cnpj > 0:
        print(f"\n🔍 AMOSTRAS DE SAFEID COM CNPJ:")
        cursor.execute("""
            SELECT 
                protocolo,
                documento,
                nome_razao_social,
                descricao_produto
            FROM renovacao_safeid
            WHERE descricao_produto LIKE '%SafeID%'
            AND LENGTH(documento) = 14
            LIMIT 10
        """)
        
        amostras = cursor.fetchall()
        
        print(f"{'Protocolo':12} | {'CNPJ':15} | {'Razão Social':35} | {'Produto':15}")
        print("-" * 85)
        
        for protocolo, documento, nome, produto in amostras:
            nome_short = nome[:35] if nome else 'N/A'
            produto_short = produto[:15] if produto else 'N/A'
            
            print(f"{protocolo:12} | {documento:15} | {nome_short:35} | {produto_short:15}")
    
    conn.close()

def main():
    """Função principal"""
    try:
        print("🔍 REANÁLISE DETALHADA DOS PRODUTOS - RENOVACAO_SAFEID")
        print("=" * 70)
        print("🎯 Verificando se há outros produtos além do SafeID e-CPF")
        print()
        
        # Análises detalhadas
        produtos = analisar_produtos_detalhado()
        analisar_documentos_por_produto()
        analisar_amostras_por_produto()
        analisar_combinacoes_produto_validade()
        verificar_inconsistencias()
        
        print(f"\n🎉 REANÁLISE DETALHADA CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 {len(produtos)} tipos de produtos identificados")
        print(f"🔍 Inconsistências verificadas")
        print(f"📋 Amostras analisadas por produto")
        
        # Resumo final
        print(f"\n📋 RESUMO FINAL:")
        for produto, quantidade in produtos:
            if 'e-CPF' in produto.upper():
                tipo = "👤 PESSOA FÍSICA"
            elif 'e-CNPJ' in produto.upper() or 'CNPJ' in produto.upper():
                tipo = "🏢 PESSOA JURÍDICA"
            elif 'SAFEID' in produto.upper():
                tipo = "🔐 SAFEID"
            else:
                tipo = "❓ OUTRO"
            
            print(f"   {produto}: {quantidade:,} registros ({tipo})")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
