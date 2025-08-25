#!/usr/bin/env python3
"""
ANÁLISE DA TABELA SAFEID NO BANCO
Analisa SOMENTE a tabela SafeID no banco de dados
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

def verificar_tabela_safeid():
    """Verifica se existe tabela SafeID no banco"""
    print("🔍 VERIFICANDO TABELA SAFEID NO BANCO")
    print("=" * 40)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se tabela SafeID existe
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name ILIKE '%safeid%'
    """)
    
    tabelas_safeid = cursor.fetchall()
    
    if tabelas_safeid:
        print(f"✅ TABELAS SAFEID ENCONTRADAS:")
        for (tabela,) in tabelas_safeid:
            print(f"   📋 {tabela}")
    else:
        print(f"❌ NENHUMA TABELA SAFEID ENCONTRADA")
        
        # Verificar todas as tabelas disponíveis
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        todas_tabelas = cursor.fetchall()
        print(f"\n📋 TODAS AS TABELAS DISPONÍVEIS:")
        for (tabela,) in todas_tabelas:
            print(f"   📋 {tabela}")
    
    conn.close()
    
    return tabelas_safeid

def analisar_estrutura_safeid(nome_tabela):
    """Analisa estrutura da tabela SafeID"""
    print(f"\n🔍 ANALISANDO ESTRUTURA DA TABELA {nome_tabela.upper()}")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Contar campos
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = %s
    """, (nome_tabela,))
    
    total_campos = cursor.fetchone()[0]
    print(f"📊 TOTAL DE CAMPOS NA TABELA {nome_tabela}: {total_campos}")
    
    # Listar todos os campos
    cursor.execute("""
        SELECT 
            ordinal_position,
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (nome_tabela,))
    
    colunas = cursor.fetchall()
    
    print(f"\n📋 ESTRUTURA COMPLETA DA TABELA {nome_tabela.upper()}:")
    print("-" * 80)
    print(f"{'POS':<4} {'CAMPO':<35} {'TIPO':<20} {'TAMANHO':<10} {'NULL':<8}")
    print("-" * 80)
    
    for pos, col_name, data_type, max_length, nullable, default in colunas:
        tamanho = str(max_length) if max_length else '-'
        null_ok = 'YES' if nullable == 'YES' else 'NO'
        print(f'{pos:<4} {col_name:<35} {data_type:<20} {tamanho:<10} {null_ok:<8}')
    
    conn.close()
    
    return total_campos, colunas

def verificar_dados_safeid(nome_tabela):
    """Verifica dados na tabela SafeID"""
    print(f"\n🔍 VERIFICANDO DADOS NA TABELA {nome_tabela.upper()}")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
    total_registros = cursor.fetchone()[0]
    
    print(f"📊 TOTAL DE REGISTROS: {total_registros:,}")
    
    if total_registros > 0:
        # Mostrar primeiros registros
        cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 5")
        registros = cursor.fetchall()
        
        # Obter nomes das colunas
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (nome_tabela,))
        colunas = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 PRIMEIROS 5 REGISTROS:")
        print("-" * 80)
        
        for i, registro in enumerate(registros, 1):
            print(f"\n📋 REGISTRO {i}:")
            for coluna, valor in zip(colunas, registro):
                if valor is not None and str(valor).strip():
                    valor_str = str(valor)[:50] if len(str(valor)) > 50 else str(valor)
                    print(f"   {coluna:<35}: {valor_str}")
    else:
        print(f"⚪ TABELA VAZIA")
    
    conn.close()
    
    return total_registros

def main():
    """Função principal"""
    print("🔍 ANÁLISE DA TABELA SAFEID NO BANCO")
    print("=" * 50)
    print("🎯 Objetivo: Analisar SOMENTE a tabela SafeID")
    print()
    
    try:
        # Verificar se tabela SafeID existe
        tabelas_safeid = verificar_tabela_safeid()
        
        if tabelas_safeid:
            for (nome_tabela,) in tabelas_safeid:
                # Analisar estrutura
                total_campos, colunas = analisar_estrutura_safeid(nome_tabela)
                
                # Verificar dados
                total_registros = verificar_dados_safeid(nome_tabela)
                
                print(f"\n🎯 RESUMO DA TABELA {nome_tabela.upper()}:")
                print("=" * 40)
                print(f"📊 Campos: {total_campos}")
                print(f"📊 Registros: {total_registros:,}")
        else:
            print(f"\n❌ CONCLUSÃO:")
            print("=" * 20)
            print(f"❌ Não existe tabela específica do SafeID")
            print(f"💡 Os dados do SafeID podem estar em outra tabela")
            print(f"🔍 Verificar se dados estão na tabela 'emissao' ou similar")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
