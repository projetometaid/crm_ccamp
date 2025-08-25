#!/usr/bin/env python3
"""
ANÁLISE SIMPLES DE PROTOCOLOS - RENOVAÇÃO SAFEID
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
    print("📖 LENDO PROTOCOLOS DO ARQUIVO SAFEID...")
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    # Verificar estrutura do arquivo
    print(f"📋 Arquivo tem {sheet.nrows} linhas e {sheet.ncols} colunas")
    
    # Mostrar cabeçalhos
    print(f"🔍 CABEÇALHOS DO ARQUIVO:")
    for col in range(min(15, sheet.ncols)):  # Mostrar primeiros 15
        header = sheet.cell_value(0, col)
        print(f"   Coluna {col:2d}: {header}")
    
    # Identificar coluna do protocolo
    protocolo_col = None
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).lower()
        if 'protocolo' in header:
            protocolo_col = col
            print(f"✅ Coluna do protocolo encontrada: {col} ({sheet.cell_value(0, col)})")
            break
    
    if protocolo_col is None:
        print("❌ ERRO: Coluna do protocolo não encontrada!")
        return []
    
    protocolos = []
    for row in range(1, sheet.nrows):  # Pular cabeçalho
        protocolo_raw = sheet.cell_value(row, protocolo_col)
        if protocolo_raw:
            try:
                if isinstance(protocolo_raw, str):
                    # Remover espaços e caracteres especiais
                    protocolo_limpo = protocolo_raw.strip().replace('.', '').replace(',', '')
                    protocolo = str(int(float(protocolo_limpo)))
                else:
                    protocolo = str(int(protocolo_raw))
                protocolos.append(protocolo)
            except (ValueError, TypeError):
                print(f"⚠️ Protocolo inválido na linha {row}: {protocolo_raw}")
                continue
    
    print(f"✅ {len(protocolos)} protocolos carregados do arquivo")
    if protocolos:
        print(f"🔍 Primeiro protocolo: {protocolos[0]}")
        print(f"🔍 Último protocolo: {protocolos[-1]}")
        
        # Mostrar alguns exemplos
        print(f"🔍 Primeiros 10 protocolos: {protocolos[:10]}")
    
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
    
    # Mostrar range do banco
    if protocolos_banco:
        protocolos_int = [int(p) for p in protocolos_banco]
        min_banco = min(protocolos_int)
        max_banco = max(protocolos_int)
        print(f"📊 Range do banco: {min_banco:,} até {max_banco:,}")
    
    return protocolos_banco

def testar_protocolos_especificos(protocolos_arquivo):
    """Testa alguns protocolos específicos do arquivo"""
    print("\n🔍 TESTE DIRETO DE PROTOCOLOS ESPECÍFICOS...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Testar primeiros protocolos do arquivo
    protocolos_teste = protocolos_arquivo[:5] if len(protocolos_arquivo) >= 5 else protocolos_arquivo
    
    for protocolo in protocolos_teste:
        # Teste como int
        cursor.execute("SELECT COUNT(*) FROM emissao WHERE protocolo = %s", (int(protocolo),))
        existe = cursor.fetchone()[0] > 0
        
        print(f"   {protocolo}: {'✅ EXISTE' if existe else '❌ NÃO EXISTE'}")
    
    conn.close()

def comparar_protocolos():
    """Compara protocolos do arquivo com banco"""
    print("\n🔍 COMPARAÇÃO ARQUIVO vs BANCO...")
    
    # Carregar dados
    protocolos_arquivo = ler_protocolos_arquivo()
    if not protocolos_arquivo:
        print("❌ Nenhum protocolo válido encontrado no arquivo!")
        return 0, 0
    
    protocolos_banco = buscar_protocolos_banco()
    
    # Testar protocolos específicos primeiro
    testar_protocolos_especificos(protocolos_arquivo)
    
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
    print("🔍 ANÁLISE DE PROTOCOLOS - RENOVAÇÃO SAFEID")
    print("=" * 50)
    print("🎯 Arquivo: RelatorioSafeID.xls")
    print("🎯 Objetivo: Identificar protocolos novos vs existentes")
    print()
    
    try:
        existentes, novos = comparar_protocolos()
        
        print(f"\n🎯 RESULTADO FINAL:")
        print("=" * 30)
        print(f"✅ Protocolos existentes: {existentes:,}")
        print(f"🆕 Protocolos novos: {novos:,}")
        print(f"📊 Total analisado: {existentes + novos:,}")
        
        if existentes > 0:
            pct_existentes = (existentes / (existentes + novos)) * 100
            pct_novos = (novos / (existentes + novos)) * 100
            print(f"📊 {pct_existentes:.1f}% existem, {pct_novos:.1f}% são novos")
            
            print(f"\n⚠️ ATENÇÃO: Há protocolos que JÁ EXISTEM no banco!")
            print(f"   Será necessário analisar quais campos serão atualizados.")
        else:
            print(f"\n✅ TODOS os protocolos são novos - operação de INSERT simples.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
