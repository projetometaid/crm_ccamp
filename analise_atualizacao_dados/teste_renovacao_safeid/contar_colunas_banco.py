#!/usr/bin/env python3
"""
SCRIPT SIMPLES - CONTAR COLUNAS NO BANCO
Confirma quantas colunas tem a tabela emissao
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

def contar_colunas():
    """Conta colunas da tabela emissao"""
    print("🔍 CONTANDO COLUNAS DA TABELA EMISSAO")
    print("=" * 40)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Contar total
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'emissao'
    """)
    
    total = cursor.fetchone()[0]
    print(f"📊 TOTAL DE COLUNAS: {total}")
    
    # Listar nomes
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        ORDER BY ordinal_position
    """)
    
    colunas = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📋 LISTA DAS {len(colunas)} COLUNAS:")
    print("-" * 40)
    
    for i, coluna in enumerate(colunas, 1):
        print(f"{i:2d}. {coluna}")
    
    conn.close()
    
    print(f"\n✅ CONFIRMADO: A tabela 'emissao' tem {total} colunas")

if __name__ == "__main__":
    contar_colunas()
