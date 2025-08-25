#!/usr/bin/env python3
"""
ANÁLISE SIMPLES DE PROTOCOLOS - FOCO TOTAL
Apenas verificar se protocolos do arquivo existem no banco
"""

import psycopg2
import xlrd

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def ler_protocolos_arquivo():
    """Lê APENAS os protocolos do arquivo Excel"""
    print("📖 LENDO PROTOCOLOS DO ARQUIVO...")
    
    wb = xlrd.open_workbook("RelatorioEmissoes.xls")
    sheet = wb.sheet_by_index(0)
    
    protocolos = []
    for row in range(1, sheet.nrows):  # Pular cabeçalho
        protocolo_raw = sheet.cell_value(row, 0)  # Primeira coluna
        if protocolo_raw:
            protocolo = str(int(protocolo_raw))  # Converter para string limpa
            protocolos.append(protocolo)
    
    print(f"✅ {len(protocolos)} protocolos carregados do arquivo")
    print(f"🔍 Primeiro protocolo: {protocolos[0]}")
    print(f"🔍 Último protocolo: {protocolos[-1]}")
    
    return protocolos

def buscar_protocolos_banco():
    """Busca TODOS os protocolos do banco"""
    print("\n🗄️ BUSCANDO PROTOCOLOS DO BANCO...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("SELECT protocolo FROM emissao")
    resultados = cursor.fetchall()
    
    protocolos_banco = set()
    for (protocolo,) in resultados:
        protocolo_str = str(protocolo)  # Converter para string
        protocolos_banco.add(protocolo_str)
    
    conn.close()
    
    print(f"✅ {len(protocolos_banco)} protocolos carregados do banco")
    
    # Mostrar alguns exemplos
    exemplos = sorted(list(protocolos_banco))[:10]
    print(f"🔍 Primeiros 10 protocolos do banco: {exemplos}")
    
    return protocolos_banco

def testar_protocolos_especificos():
    """Testa protocolos específicos que sabemos que existem"""
    print("\n🔍 TESTE DIRETO DE PROTOCOLOS ESPECÍFICOS...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Protocolos que sabemos que existem (dos testes anteriores)
    protocolos_teste = [
        '1008563478',  # 01/08/2025
        '1008570262',  # 04/08/2025  
        '1008632785',  # 12/08/2025
        '1008704422'   # 22/08/2025 (pode não existir)
    ]
    
    for protocolo in protocolos_teste:
        # Teste como string
        cursor.execute("SELECT COUNT(*) FROM emissao WHERE protocolo = %s", (protocolo,))
        existe_str = cursor.fetchone()[0] > 0
        
        # Teste como int
        cursor.execute("SELECT COUNT(*) FROM emissao WHERE protocolo = %s", (int(protocolo),))
        existe_int = cursor.fetchone()[0] > 0
        
        print(f"   {protocolo}: String={existe_str}, Int={existe_int}")
    
    conn.close()

def comparar_protocolos():
    """Compara protocolos do arquivo com banco"""
    print("\n🔍 COMPARAÇÃO ARQUIVO vs BANCO...")
    
    # Carregar dados
    protocolos_arquivo = ler_protocolos_arquivo()
    protocolos_banco = buscar_protocolos_banco()
    
    # Testar protocolos específicos primeiro
    testar_protocolos_especificos()
    
    print(f"\n📊 ANÁLISE DE INTERSECÇÃO...")
    
    # Encontrar intersecção
    protocolos_existentes = []
    protocolos_novos = []
    
    for protocolo in protocolos_arquivo:
        if protocolo in protocolos_banco:
            protocolos_existentes.append(protocolo)
        else:
            protocolos_novos.append(protocolo)
    
    print(f"✅ Protocolos que JÁ EXISTEM: {len(protocolos_existentes)}")
    print(f"🆕 Protocolos NOVOS: {len(protocolos_novos)}")
    
    # Mostrar alguns exemplos de cada
    if protocolos_existentes:
        print(f"\n📋 EXEMPLOS DE PROTOCOLOS EXISTENTES:")
        for i, protocolo in enumerate(protocolos_existentes[:10], 1):
            print(f"   {i:2d}. {protocolo}")
        if len(protocolos_existentes) > 10:
            print(f"   ... e mais {len(protocolos_existentes) - 10}")
    
    if protocolos_novos:
        print(f"\n📋 EXEMPLOS DE PROTOCOLOS NOVOS:")
        for i, protocolo in enumerate(protocolos_novos[:10], 1):
            print(f"   {i:2d}. {protocolo}")
        if len(protocolos_novos) > 10:
            print(f"   ... e mais {len(protocolos_novos) - 10}")
    
    # Verificar ranges
    print(f"\n📊 ANÁLISE DE RANGES:")
    
    if protocolos_banco:
        protocolos_banco_int = [int(p) for p in protocolos_banco]
        min_banco = min(protocolos_banco_int)
        max_banco = max(protocolos_banco_int)
        print(f"   🗄️ Banco: {min_banco:,} até {max_banco:,}")
    
    if protocolos_arquivo:
        protocolos_arquivo_int = [int(p) for p in protocolos_arquivo]
        min_arquivo = min(protocolos_arquivo_int)
        max_arquivo = max(protocolos_arquivo_int)
        print(f"   📁 Arquivo: {min_arquivo:,} até {max_arquivo:,}")
    
    # Verificar sobreposição de ranges
    if protocolos_banco and protocolos_arquivo:
        if min_arquivo <= max_banco and max_arquivo >= min_banco:
            print(f"   🔄 HÁ SOBREPOSIÇÃO DE RANGES!")
        else:
            print(f"   ❌ NÃO HÁ SOBREPOSIÇÃO DE RANGES")
    
    return len(protocolos_existentes), len(protocolos_novos)

def main():
    """Função principal"""
    print("🔍 ANÁLISE SIMPLES DE PROTOCOLOS")
    print("=" * 50)
    print("🎯 Objetivo: Identificar erro na comparação de protocolos")
    print()
    
    try:
        existentes, novos = comparar_protocolos()
        
        print(f"\n🎯 RESULTADO FINAL:")
        print("=" * 30)
        print(f"✅ Protocolos existentes: {existentes:,}")
        print(f"🆕 Protocolos novos: {novos:,}")
        print(f"📊 Total analisado: {existentes + novos:,}")
        
        if existentes > 0:
            print(f"\n⚠️ CONFIRMADO: Há protocolos que JÁ EXISTEM no banco!")
            print(f"   O script anterior tinha um erro na comparação.")
        else:
            print(f"\n✅ CONFIRMADO: Todos os protocolos são realmente novos.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
