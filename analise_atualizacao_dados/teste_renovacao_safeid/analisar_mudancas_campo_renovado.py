#!/usr/bin/env python3
"""
ANÁLISE DE MUDANÇAS - CAMPO RENOVADO SAFEID
Compara dados existentes no banco com dados do arquivo para identificar mudanças
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

def ler_dados_arquivo():
    """Lê todos os dados do arquivo SafeID"""
    print("📖 LENDO DADOS DO ARQUIVO SAFEID")
    print("=" * 40)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
    
    # Encontrar colunas importantes
    col_protocolo = headers.index('Protocolo')
    col_renovado = headers.index('Renovado')
    col_status = headers.index('Status do Certificado')
    col_produto = headers.index('Descrição Produto')
    
    print(f"📊 Arquivo: {sheet.nrows-1} registros")
    print(f"✅ Coluna Protocolo: {col_protocolo}")
    print(f"✅ Coluna Renovado: {col_renovado}")
    print(f"✅ Coluna Status: {col_status}")
    print(f"✅ Coluna Produto: {col_produto}")
    
    # Ler todos os dados
    dados_arquivo = {}
    
    for row in range(1, sheet.nrows):
        protocolo = str(sheet.cell_value(row, col_protocolo)).strip()
        renovado = str(sheet.cell_value(row, col_renovado)).strip()
        status = str(sheet.cell_value(row, col_status)).strip()
        produto = str(sheet.cell_value(row, col_produto)).strip()
        
        dados_arquivo[protocolo] = {
            'renovado': renovado,
            'status': status,
            'produto': produto
        }
    
    print(f"✅ Carregados {len(dados_arquivo)} protocolos do arquivo")
    
    # Mostrar distribuição do campo Renovado no arquivo
    renovado_sim = sum(1 for dados in dados_arquivo.values() if dados['renovado'].upper() == 'SIM')
    renovado_nao = sum(1 for dados in dados_arquivo.values() if dados['renovado'].upper() == 'NÃO' or dados['renovado'].upper() == 'NAO')
    
    print(f"\n📊 DISTRIBUIÇÃO RENOVADO NO ARQUIVO:")
    print(f"   🔄 Sim: {renovado_sim} ({renovado_sim/len(dados_arquivo)*100:.1f}%)")
    print(f"   ⏳ Não: {renovado_nao} ({renovado_nao/len(dados_arquivo)*100:.1f}%)")
    
    return dados_arquivo

def buscar_dados_banco(protocolos):
    """Busca dados dos protocolos no banco"""
    print(f"\n🗄️ BUSCANDO DADOS NO BANCO")
    print("=" * 40)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar dados dos protocolos
    protocolos_str = ','.join(protocolos)
    
    cursor.execute(f"""
        SELECT protocolo, renovado, status_do_certificado, descricao_produto
        FROM renovacao_safeid 
        WHERE protocolo IN ({protocolos_str})
        ORDER BY protocolo
    """)
    
    resultados = cursor.fetchall()
    
    dados_banco = {}
    for protocolo, renovado, status, produto in resultados:
        dados_banco[str(protocolo)] = {
            'renovado': str(renovado) if renovado else '',
            'status': str(status) if status else '',
            'produto': str(produto) if produto else ''
        }
    
    print(f"✅ Encontrados {len(dados_banco)} protocolos no banco")
    
    # Mostrar distribuição do campo Renovado no banco
    renovado_sim = sum(1 for dados in dados_banco.values() if dados['renovado'].upper() == 'SIM')
    renovado_nao = sum(1 for dados in dados_banco.values() if dados['renovado'].upper() == 'NÃO' or dados['renovado'].upper() == 'NAO')
    renovado_vazio = sum(1 for dados in dados_banco.values() if not dados['renovado'])
    
    print(f"\n📊 DISTRIBUIÇÃO RENOVADO NO BANCO:")
    print(f"   🔄 Sim: {renovado_sim} ({renovado_sim/len(dados_banco)*100:.1f}%)")
    print(f"   ⏳ Não: {renovado_nao} ({renovado_nao/len(dados_banco)*100:.1f}%)")
    print(f"   ⚪ Vazio: {renovado_vazio} ({renovado_vazio/len(dados_banco)*100:.1f}%)")
    
    conn.close()
    
    return dados_banco

def comparar_dados(dados_arquivo, dados_banco):
    """Compara dados do arquivo com banco e identifica mudanças"""
    print(f"\n🔍 COMPARANDO DADOS ARQUIVO vs BANCO")
    print("=" * 50)
    
    mudancas_renovado = []
    mudancas_status = []
    mudancas_produto = []
    sem_mudancas = []
    nao_encontrados = []
    
    print(f"📋 ANÁLISE DETALHADA POR PROTOCOLO:")
    print("-" * 60)
    
    for protocolo, dados_arq in dados_arquivo.items():
        if protocolo in dados_banco:
            dados_bnc = dados_banco[protocolo]
            
            mudancas_protocolo = []
            
            # Comparar campo Renovado
            renovado_arq = dados_arq['renovado'].upper()
            renovado_bnc = dados_bnc['renovado'].upper()
            
            if renovado_arq != renovado_bnc:
                mudancas_renovado.append({
                    'protocolo': protocolo,
                    'banco': renovado_bnc,
                    'arquivo': renovado_arq
                })
                mudancas_protocolo.append(f"Renovado: '{renovado_bnc}' → '{renovado_arq}'")
            
            # Comparar Status
            status_arq = dados_arq['status']
            status_bnc = dados_bnc['status']
            
            if status_arq != status_bnc:
                mudancas_status.append({
                    'protocolo': protocolo,
                    'banco': status_bnc,
                    'arquivo': status_arq
                })
                mudancas_protocolo.append(f"Status: '{status_bnc}' → '{status_arq}'")
            
            # Comparar Produto
            produto_arq = dados_arq['produto']
            produto_bnc = dados_bnc['produto']
            
            if produto_arq != produto_bnc:
                mudancas_produto.append({
                    'protocolo': protocolo,
                    'banco': produto_bnc,
                    'arquivo': produto_arq
                })
                mudancas_protocolo.append(f"Produto: '{produto_bnc}' → '{produto_arq}'")
            
            # Mostrar resultado
            if mudancas_protocolo:
                print(f"🔄 {protocolo}: {len(mudancas_protocolo)} mudanças")
                for mudanca in mudancas_protocolo:
                    print(f"   • {mudanca}")
            else:
                sem_mudancas.append(protocolo)
                print(f"✅ {protocolo}: SEM MUDANÇAS")
        else:
            nao_encontrados.append(protocolo)
            print(f"❌ {protocolo}: NÃO ENCONTRADO NO BANCO")
    
    return mudancas_renovado, mudancas_status, mudancas_produto, sem_mudancas, nao_encontrados

def analisar_padroes_mudancas(mudancas_renovado, mudancas_status, mudancas_produto):
    """Analisa padrões das mudanças identificadas"""
    print(f"\n📊 ANÁLISE DE PADRÕES DAS MUDANÇAS")
    print("=" * 50)
    
    # Análise do campo Renovado
    print(f"🎯 MUDANÇAS NO CAMPO RENOVADO ({len(mudancas_renovado)}):")
    print("-" * 40)
    
    if mudancas_renovado:
        padroes_renovado = {}
        for mudanca in mudancas_renovado:
            padrao = f"{mudanca['banco']} → {mudanca['arquivo']}"
            if padrao not in padroes_renovado:
                padroes_renovado[padrao] = []
            padroes_renovado[padrao].append(mudanca['protocolo'])
        
        for padrao, protocolos in padroes_renovado.items():
            print(f"   📋 {padrao}: {len(protocolos)} protocolos")
            if len(protocolos) <= 5:
                print(f"      Protocolos: {', '.join(protocolos)}")
            else:
                print(f"      Exemplos: {', '.join(protocolos[:3])}...")
    else:
        print(f"   ✅ NENHUMA MUDANÇA NO CAMPO RENOVADO")
    
    # Análise do Status
    print(f"\n📋 MUDANÇAS NO STATUS ({len(mudancas_status)}):")
    print("-" * 30)
    
    if mudancas_status:
        padroes_status = {}
        for mudanca in mudancas_status:
            padrao = f"{mudanca['banco']} → {mudanca['arquivo']}"
            if padrao not in padroes_status:
                padroes_status[padrao] = 0
            padroes_status[padrao] += 1
        
        for padrao, count in padroes_status.items():
            print(f"   📋 {padrao}: {count} protocolos")
    else:
        print(f"   ✅ NENHUMA MUDANÇA NO STATUS")
    
    # Análise do Produto
    print(f"\n📦 MUDANÇAS NO PRODUTO ({len(mudancas_produto)}):")
    print("-" * 30)
    
    if mudancas_produto:
        padroes_produto = {}
        for mudanca in mudancas_produto:
            padrao = f"{mudanca['banco']} → {mudanca['arquivo']}"
            if padrao not in padroes_produto:
                padroes_produto[padrao] = 0
            padroes_produto[padrao] += 1
        
        for padrao, count in padroes_produto.items():
            print(f"   📋 {padrao}: {count} protocolos")
    else:
        print(f"   ✅ NENHUMA MUDANÇA NO PRODUTO")

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE MUDANÇAS - CAMPO RENOVADO SAFEID")
    print("=" * 60)
    print("🎯 Objetivo: Identificar mudanças entre banco e arquivo")
    print()
    
    try:
        # Ler dados do arquivo
        dados_arquivo = ler_dados_arquivo()
        
        # Buscar dados no banco
        protocolos = list(dados_arquivo.keys())
        dados_banco = buscar_dados_banco(protocolos)
        
        # Comparar dados
        mudancas_renovado, mudancas_status, mudancas_produto, sem_mudancas, nao_encontrados = comparar_dados(dados_arquivo, dados_banco)
        
        # Analisar padrões
        analisar_padroes_mudancas(mudancas_renovado, mudancas_status, mudancas_produto)
        
        print(f"\n🎯 RESUMO FINAL:")
        print("=" * 30)
        print(f"📊 Total de protocolos: {len(dados_arquivo)}")
        print(f"✅ Encontrados no banco: {len(dados_banco)}")
        print(f"❌ Não encontrados: {len(nao_encontrados)}")
        print(f"🔄 Mudanças no Renovado: {len(mudancas_renovado)}")
        print(f"📋 Mudanças no Status: {len(mudancas_status)}")
        print(f"📦 Mudanças no Produto: {len(mudancas_produto)}")
        print(f"✅ Sem mudanças: {len(sem_mudancas)}")
        
        total_mudancas = len(mudancas_renovado) + len(mudancas_status) + len(mudancas_produto)
        print(f"\n💡 TOTAL DE MUDANÇAS: {total_mudancas}")
        
        if total_mudancas > 0:
            print(f"🔄 RECOMENDAÇÃO: PROCEDER COM ATUALIZAÇÃO")
        else:
            print(f"✅ RECOMENDAÇÃO: DADOS JÁ ESTÃO ATUALIZADOS")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
