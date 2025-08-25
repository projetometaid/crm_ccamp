#!/usr/bin/env python3
"""
ANÁLISE ESTRUTURA RENOVACAO_SAFEID
Analisa a estrutura completa da tabela renovacao_safeid
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

def analisar_estrutura_tabela():
    """Analisa a estrutura completa da tabela renovacao_safeid"""
    print("🔍 ANÁLISE ESTRUTURA - RENOVACAO_SAFEID")
    print("=" * 60)
    print("🎯 Mapeando estrutura completa da tabela")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se tabela existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'renovacao_safeid'
        )
    """)
    
    if not cursor.fetchone()[0]:
        print("❌ Tabela 'renovacao_safeid' não encontrada!")
        conn.close()
        return
    
    # Obter estrutura da tabela
    cursor.execute("""
        SELECT 
            ordinal_position,
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'renovacao_safeid' 
        ORDER BY ordinal_position
    """)
    
    colunas = cursor.fetchall()
    
    print(f"📊 ESTRUTURA DA TABELA renovacao_safeid:")
    print("-" * 80)
    print(f"{'#':3} | {'Campo':35} | {'Tipo':20} | {'Tamanho':8} | {'Nulo':5} | {'Padrão':15}")
    print("-" * 80)
    
    for pos, nome, tipo, tamanho, nulo, padrao in colunas:
        tamanho_str = str(tamanho) if tamanho else '-'
        nulo_str = 'SIM' if nulo == 'YES' else 'NÃO'
        padrao_str = str(padrao)[:15] if padrao else '-'
        
        print(f"{pos:3} | {nome:35} | {tipo:20} | {tamanho_str:8} | {nulo_str:5} | {padrao_str:15}")
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM renovacao_safeid")
    total_registros = cursor.fetchone()[0]
    
    print(f"\n📊 RESUMO:")
    print(f"   📋 Total de campos: {len(colunas)}")
    print(f"   📊 Total de registros: {total_registros:,}")
    
    conn.close()
    
    return colunas, total_registros

def analisar_dados_amostra():
    """Analisa uma amostra dos dados para entender o conteúdo"""
    print(f"\n🔍 ANÁLISE DE DADOS - AMOSTRA")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar amostra de dados
    cursor.execute("""
        SELECT * FROM renovacao_safeid 
        ORDER BY RANDOM()
        LIMIT 5
    """)
    
    registros = cursor.fetchall()
    
    # Obter nomes das colunas
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'renovacao_safeid' 
        ORDER BY ordinal_position
    """)
    
    colunas = [row[0] for row in cursor.fetchall()]
    
    print(f"📋 AMOSTRA DE DADOS (5 registros aleatórios):")
    print("-" * 100)
    
    for i, registro in enumerate(registros, 1):
        print(f"\n📋 REGISTRO {i}:")
        for j, valor in enumerate(registro):
            campo = colunas[j]
            valor_str = str(valor)[:50] if valor else 'NULL'
            print(f"   {campo:30}: {valor_str}")
    
    conn.close()

def analisar_preenchimento_campos():
    """Analisa o preenchimento de cada campo"""
    print(f"\n📊 ANÁLISE DE PREENCHIMENTO DOS CAMPOS")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM renovacao_safeid")
    total = cursor.fetchone()[0]
    
    # Obter nomes das colunas
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'renovacao_safeid' 
        ORDER BY ordinal_position
    """)
    
    colunas = [row[0] for row in cursor.fetchall()]
    
    print(f"📋 TAXA DE PREENCHIMENTO ({total:,} registros):")
    print("-" * 70)
    print(f"{'Campo':35} | {'Preenchidos':12} | {'%':6} | {'Vazios':8}")
    print("-" * 70)
    
    for campo in colunas:
        # Contar registros não nulos e não vazios
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM renovacao_safeid 
            WHERE {campo} IS NOT NULL 
            AND TRIM(CAST({campo} AS TEXT)) != ''
        """)
        
        preenchidos = cursor.fetchone()[0]
        vazios = total - preenchidos
        pct = (preenchidos / total) * 100
        
        status = "✅" if pct > 90 else "⚠️" if pct > 50 else "❌"
        
        print(f"{campo:35} | {preenchidos:12,} | {pct:5.1f}% | {vazios:8,} {status}")
    
    conn.close()

def analisar_campos_chave():
    """Analisa campos que podem ser chaves ou identificadores"""
    print(f"\n🔑 ANÁLISE DE CAMPOS CHAVE")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Campos que podem ser chaves (protocolo, id, etc.)
    campos_chave = []
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'renovacao_safeid' 
        AND (column_name LIKE '%protocolo%' 
             OR column_name LIKE '%id%'
             OR column_name LIKE '%codigo%'
             OR column_name LIKE '%numero%')
        ORDER BY ordinal_position
    """)
    
    campos_chave = [row[0] for row in cursor.fetchall()]
    
    if campos_chave:
        print(f"📋 CAMPOS IDENTIFICADORES ENCONTRADOS:")
        
        for campo in campos_chave:
            # Verificar unicidade
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT {campo}) as unicos
                FROM renovacao_safeid
                WHERE {campo} IS NOT NULL
            """)
            
            total, unicos = cursor.fetchone()
            
            if total > 0:
                unicidade = (unicos / total) * 100
                status = "🔑 CHAVE" if unicidade == 100 else f"📊 {unicidade:.1f}% único"
                
                print(f"   {campo:30}: {total:,} registros | {unicos:,} únicos | {status}")
                
                # Mostrar alguns exemplos
                cursor.execute(f"""
                    SELECT DISTINCT {campo} 
                    FROM renovacao_safeid 
                    WHERE {campo} IS NOT NULL 
                    LIMIT 5
                """)
                
                exemplos = [str(row[0]) for row in cursor.fetchall()]
                print(f"      💡 Exemplos: {', '.join(exemplos)}")
                print()
    else:
        print("⚠️ Nenhum campo identificador óbvio encontrado")
    
    conn.close()

def analisar_campos_data():
    """Analisa campos de data"""
    print(f"\n📅 ANÁLISE DE CAMPOS DE DATA")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar campos de data
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns 
        WHERE table_name = 'renovacao_safeid' 
        AND (data_type LIKE '%date%' 
             OR data_type LIKE '%time%'
             OR column_name LIKE '%data%'
             OR column_name LIKE '%date%')
        ORDER BY ordinal_position
    """)
    
    campos_data = cursor.fetchall()
    
    if campos_data:
        print(f"📋 CAMPOS DE DATA ENCONTRADOS:")
        
        for campo, tipo in campos_data:
            # Analisar range de datas
            cursor.execute(f"""
                SELECT 
                    MIN({campo}) as data_min,
                    MAX({campo}) as data_max,
                    COUNT({campo}) as total_preenchidos
                FROM renovacao_safeid
                WHERE {campo} IS NOT NULL
            """)
            
            data_min, data_max, total = cursor.fetchone()
            
            if total > 0:
                print(f"   📅 {campo} ({tipo}):")
                print(f"      📊 Registros: {total:,}")
                print(f"      📅 Período: {data_min} até {data_max}")
                
                # Distribuição por ano
                cursor.execute(f"""
                    SELECT 
                        EXTRACT(YEAR FROM {campo}) as ano,
                        COUNT(*) as quantidade
                    FROM renovacao_safeid
                    WHERE {campo} IS NOT NULL
                    GROUP BY EXTRACT(YEAR FROM {campo})
                    ORDER BY ano
                """)
                
                anos = cursor.fetchall()
                if anos:
                    print(f"      📊 Por ano: {', '.join([f'{int(ano)}({qtd})' for ano, qtd in anos])}")
                print()
    else:
        print("⚠️ Nenhum campo de data encontrado")
    
    conn.close()

def main():
    """Função principal"""
    try:
        print("🔍 ANÁLISE COMPLETA - RENOVACAO_SAFEID")
        print("=" * 70)
        print("🎯 Mapeando estrutura, dados e características")
        print()
        
        # Análise da estrutura
        colunas, total = analisar_estrutura_tabela()
        
        if not colunas:
            return
        
        # Análise de dados
        analisar_dados_amostra()
        analisar_preenchimento_campos()
        analisar_campos_chave()
        analisar_campos_data()
        
        print(f"\n🎉 ANÁLISE COMPLETA CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 {len(colunas)} campos analisados")
        print(f"📋 {total:,} registros na tabela")
        print(f"🎯 Estrutura mapeada para documentação")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
