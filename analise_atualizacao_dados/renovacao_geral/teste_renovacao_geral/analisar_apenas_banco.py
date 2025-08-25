#!/usr/bin/env python3
"""
ANÁLISE APENAS DO BANCO DE DADOS - RENOVAÇÃO GERAL
Analisa o estado atual dos dados no banco sem comparar com arquivo
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

def analisar_campos_renovacao_banco():
    """Analisa especificamente os campos de renovação no banco"""
    print("🗄️ ANÁLISE APENAS DO BANCO DE DADOS - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Analisando estado atual dos campos de renovação")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Primeiro, vamos buscar os protocolos do arquivo para focar apenas neles
    print("📖 IDENTIFICANDO PROTOCOLOS DO ARQUIVO...")
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
    
    print(f"✅ Protocolos do arquivo: {len(protocolos_arquivo):,}")
    
    # Analisar campos de renovação no banco para esses protocolos
    placeholders = ','.join(['%s'] * len(protocolos_arquivo))
    
    print(f"\n🔍 ANALISANDO CAMPOS DE RENOVAÇÃO NO BANCO...")
    
    # Análise do campo status_protocolo_renovacao
    cursor.execute(f"""
        SELECT 
            status_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
        GROUP BY status_protocolo_renovacao
        ORDER BY quantidade DESC
    """, protocolos_arquivo)
    
    print(f"\n📊 CAMPO: status_protocolo_renovacao")
    print("-" * 50)
    total_status = 0
    for status, count in cursor.fetchall():
        status_str = status if status else 'NULL/VAZIO'
        pct = 0  # Calcularemos depois
        total_status += count
        print(f"   {status_str:20}: {count:,} registros")
    
    # Recalcular percentuais
    cursor.execute(f"""
        SELECT 
            status_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
        GROUP BY status_protocolo_renovacao
        ORDER BY quantidade DESC
    """, protocolos_arquivo)
    
    print(f"\n📊 CAMPO: status_protocolo_renovacao (com percentuais)")
    print("-" * 60)
    for status, count in cursor.fetchall():
        status_str = status if status else 'NULL/VAZIO'
        pct = (count / total_status) * 100
        print(f"   {status_str:20}: {count:,} registros ({pct:.1f}%)")
    
    # Análise do campo protocolo_renovacao
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN protocolo_renovacao IS NULL THEN 'NULL/VAZIO'
                ELSE 'PREENCHIDO'
            END as status,
            COUNT(*) as quantidade
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
        GROUP BY CASE 
                WHEN protocolo_renovacao IS NULL THEN 'NULL/VAZIO'
                ELSE 'PREENCHIDO'
            END
        ORDER BY quantidade DESC
    """, protocolos_arquivo)
    
    print(f"\n📊 CAMPO: protocolo_renovacao")
    print("-" * 50)
    for status, count in cursor.fetchall():
        pct = (count / total_status) * 100
        print(f"   {status:20}: {count:,} registros ({pct:.1f}%)")
    
    # Análise do campo nome_da_ar_protocolo_renovacao
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN nome_da_ar_protocolo_renovacao IS NULL OR nome_da_ar_protocolo_renovacao = '' THEN 'NULL/VAZIO'
                ELSE nome_da_ar_protocolo_renovacao
            END as ar_nome,
            COUNT(*) as quantidade
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
        GROUP BY CASE 
                WHEN nome_da_ar_protocolo_renovacao IS NULL OR nome_da_ar_protocolo_renovacao = '' THEN 'NULL/VAZIO'
                ELSE nome_da_ar_protocolo_renovacao
            END
        ORDER BY quantidade DESC
    """, protocolos_arquivo)
    
    print(f"\n📊 CAMPO: nome_da_ar_protocolo_renovacao")
    print("-" * 60)
    for ar_nome, count in cursor.fetchall():
        pct = (count / total_status) * 100
        print(f"   {ar_nome:30}: {count:,} registros ({pct:.1f}%)")
    
    # Análise do campo produto_protocolo_renovacao
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN produto_protocolo_renovacao IS NULL OR produto_protocolo_renovacao = '' THEN 'NULL/VAZIO'
                ELSE produto_protocolo_renovacao
            END as produto,
            COUNT(*) as quantidade
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
        GROUP BY CASE 
                WHEN produto_protocolo_renovacao IS NULL OR produto_protocolo_renovacao = '' THEN 'NULL/VAZIO'
                ELSE produto_protocolo_renovacao
            END
        ORDER BY quantidade DESC
    """, protocolos_arquivo)
    
    print(f"\n📊 CAMPO: produto_protocolo_renovacao")
    print("-" * 50)
    for produto, count in cursor.fetchall():
        pct = (count / total_status) * 100
        print(f"   {produto:25}: {count:,} registros ({pct:.1f}%)")
    
    # Análise combinada - registros com dados de renovação
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN protocolo_renovacao IS NOT NULL THEN 'COM_PROTOCOLO_RENOVACAO'
                WHEN nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '' THEN 'COM_AR_SEM_PROTOCOLO'
                WHEN status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '' THEN 'APENAS_STATUS'
                ELSE 'SEM_DADOS_RENOVACAO'
            END as categoria,
            COUNT(*) as quantidade
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
        GROUP BY CASE 
                WHEN protocolo_renovacao IS NOT NULL THEN 'COM_PROTOCOLO_RENOVACAO'
                WHEN nome_da_ar_protocolo_renovacao IS NOT NULL AND nome_da_ar_protocolo_renovacao != '' THEN 'COM_AR_SEM_PROTOCOLO'
                WHEN status_protocolo_renovacao IS NOT NULL AND status_protocolo_renovacao != '' THEN 'APENAS_STATUS'
                ELSE 'SEM_DADOS_RENOVACAO'
            END
        ORDER BY quantidade DESC
    """, protocolos_arquivo)
    
    print(f"\n📊 ANÁLISE COMBINADA - DADOS DE RENOVAÇÃO")
    print("-" * 60)
    for categoria, count in cursor.fetchall():
        pct = (count / total_status) * 100
        print(f"   {categoria:25}: {count:,} registros ({pct:.1f}%)")
    
    # Mostrar alguns exemplos de registros
    cursor.execute(f"""
        SELECT protocolo, status_protocolo_renovacao, protocolo_renovacao, 
               nome_da_ar_protocolo_renovacao, produto_protocolo_renovacao
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
        ORDER BY protocolo
        LIMIT 10
    """, protocolos_arquivo)
    
    print(f"\n💡 EXEMPLOS DE REGISTROS NO BANCO (primeiros 10):")
    print("-" * 100)
    print(f"{'Protocolo':12} | {'Status':15} | {'Prot.Renov':12} | {'AR':20} | {'Produto':15}")
    print("-" * 100)
    
    for protocolo, status, prot_ren, ar, produto in cursor.fetchall():
        status_str = status[:15] if status else 'NULL'
        prot_ren_str = str(prot_ren) if prot_ren else 'NULL'
        ar_str = ar[:20] if ar else 'NULL'
        produto_str = produto[:15] if produto else 'NULL'
        
        print(f"{protocolo:12} | {status_str:15} | {prot_ren_str:12} | {ar_str:20} | {produto_str:15}")
    
    conn.close()
    
    return total_status

def main():
    """Função principal"""
    try:
        total = analisar_campos_renovacao_banco()
        
        print(f"\n🎉 ANÁLISE DO BANCO CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 Total de registros analisados: {total:,}")
        print(f"🎯 Foco: Campos de renovação no banco")
        print(f"📋 Objetivo: Entender estado atual dos dados")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
