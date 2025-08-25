#!/usr/bin/env python3
"""
VERIFICAÇÃO DE FONTE DE DADOS - RENOVAÇÃO GERAL
Confirma que estamos analisando o arquivo correto contra a tabela correta
"""

import psycopg2
import xlrd
import os

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def verificar_arquivo_fonte():
    """Verifica o arquivo que estamos usando"""
    print("📁 VERIFICANDO ARQUIVO FONTE")
    print("=" * 50)
    
    arquivo_path = "../GestaoRenovacao (1).xls"
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_path):
        print(f"❌ Arquivo não encontrado: {arquivo_path}")
        
        # Listar arquivos disponíveis
        print(f"\n📋 Arquivos disponíveis na pasta:")
        pasta = os.path.dirname(arquivo_path) or "."
        for arquivo in os.listdir(pasta):
            if arquivo.endswith('.xls') or arquivo.endswith('.xlsx'):
                print(f"   - {arquivo}")
        return None
    
    # Analisar arquivo
    wb = xlrd.open_workbook(arquivo_path)
    sheet = wb.sheet_by_index(0)
    
    print(f"✅ Arquivo encontrado: GestaoRenovacao (1).xls")
    print(f"📊 Dimensões: {sheet.nrows-1:,} registros x {sheet.ncols} colunas")
    
    # Mostrar cabeçalhos
    print(f"\n📋 CABEÇALHOS DO ARQUIVO:")
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        print(f"   Col {col:2d}: {header}")
    
    # Mostrar amostra de dados
    print(f"\n🔍 AMOSTRA DE DADOS (primeiros 3 registros):")
    for row in range(1, min(4, sheet.nrows)):
        protocolo = str(sheet.cell_value(row, 13)).strip() if sheet.ncols > 13 else "N/A"
        razao = str(sheet.cell_value(row, 0)).strip()[:30] if sheet.ncols > 0 else "N/A"
        print(f"   Linha {row}: Protocolo={protocolo}, Razão={razao}")
    
    return sheet

def verificar_tabela_banco():
    """Verifica a tabela do banco que estamos usando"""
    print(f"\n🗄️ VERIFICANDO TABELA DO BANCO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se tabela existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'renovacao_geral'
        )
    """)
    
    if not cursor.fetchone()[0]:
        print(f"❌ Tabela 'renovacao_geral' não encontrada!")
        
        # Listar tabelas disponíveis
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%renovacao%'
            ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        print(f"\n📋 Tabelas com 'renovacao' encontradas:")
        for (tabela,) in tabelas:
            print(f"   - {tabela}")
        
        conn.close()
        return None
    
    # Analisar tabela
    cursor.execute("""
        SELECT COUNT(*) FROM renovacao_geral
    """)
    total_registros = cursor.fetchone()[0]
    
    print(f"✅ Tabela encontrada: renovacao_geral")
    print(f"📊 Total de registros: {total_registros:,}")
    
    # Mostrar estrutura da tabela
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'renovacao_geral' 
        ORDER BY ordinal_position
    """)
    
    colunas = cursor.fetchall()
    print(f"\n📋 ESTRUTURA DA TABELA ({len(colunas)} campos):")
    for col_name, data_type, max_length in colunas:
        tamanho = f"({max_length})" if max_length else ""
        print(f"   - {col_name}: {data_type}{tamanho}")
    
    # Mostrar amostra de dados
    cursor.execute("""
        SELECT protocolo, razao_social, cpfcnpj
        FROM renovacao_geral 
        ORDER BY protocolo 
        LIMIT 3
    """)
    
    print(f"\n🔍 AMOSTRA DE DADOS (primeiros 3 registros):")
    for protocolo, razao, cpfcnpj in cursor.fetchall():
        razao_str = razao[:30] if razao else "NULL"
        print(f"   Protocolo={protocolo}, Razão={razao_str}, CPF/CNPJ={cpfcnpj}")
    
    conn.close()
    return total_registros

def verificar_compatibilidade(sheet, total_banco):
    """Verifica se arquivo e banco são compatíveis"""
    print(f"\n🔍 VERIFICANDO COMPATIBILIDADE")
    print("=" * 50)
    
    if sheet is None or total_banco is None:
        print(f"❌ Não foi possível verificar compatibilidade")
        return False
    
    # Verificar protocolos do arquivo
    protocolos_arquivo = set()
    for row in range(1, sheet.nrows):
        protocolo_str = str(sheet.cell_value(row, 13)).strip()
        try:
            protocolo = int(float(protocolo_str))
            protocolos_arquivo.add(protocolo)
        except:
            continue
    
    print(f"📊 Protocolos únicos no arquivo: {len(protocolos_arquivo):,}")
    
    # Verificar quantos existem no banco
    conn = conectar_banco()
    cursor = conn.cursor()
    
    protocolos_lista = list(protocolos_arquivo)[:100]  # Testar primeiros 100
    placeholders = ','.join(['%s'] * len(protocolos_lista))
    
    cursor.execute(f"""
        SELECT COUNT(*) 
        FROM renovacao_geral 
        WHERE protocolo IN ({placeholders})
    """, protocolos_lista)
    
    encontrados = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 Protocolos encontrados no banco (amostra 100): {encontrados}")
    
    # Verificar compatibilidade
    if encontrados > 0:
        print(f"✅ COMPATIBILIDADE CONFIRMADA")
        print(f"   📁 Arquivo: GestaoRenovacao (1).xls")
        print(f"   🗄️ Tabela: renovacao_geral")
        print(f"   🔑 Protocolos em comum: {encontrados}/100 testados")
        return True
    else:
        print(f"❌ INCOMPATIBILIDADE DETECTADA")
        print(f"   Nenhum protocolo do arquivo foi encontrado no banco")
        return False

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DE FONTE DE DADOS - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Objetivo: Confirmar arquivo e tabela corretos")
    print()
    
    try:
        # Verificar arquivo
        sheet = verificar_arquivo_fonte()
        
        # Verificar tabela
        total_banco = verificar_tabela_banco()
        
        # Verificar compatibilidade
        compativel = verificar_compatibilidade(sheet, total_banco)
        
        print(f"\n🎉 VERIFICAÇÃO CONCLUÍDA!")
        print("=" * 40)
        
        if compativel:
            print(f"✅ FONTE DE DADOS CONFIRMADA:")
            print(f"   📁 Arquivo: GestaoRenovacao (1).xls")
            print(f"   🗄️ Tabela: renovacao_geral")
            print(f"   🔑 Chave: protocolo")
            print(f"   ✅ Compatibilidade verificada")
            
            print(f"\n🚀 PRÓXIMO PASSO:")
            print(f"   Prosseguir com análise de mudanças")
        else:
            print(f"❌ PROBLEMA NA FONTE DE DADOS:")
            print(f"   Arquivo e tabela não são compatíveis")
            print(f"   Verificar se estão corretos")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
