#!/usr/bin/env python3
"""
ANÁLISE DE CAMPOS ATUALIZADOS
Analisa quais campos serão alterados nos protocolos existentes
"""

import psycopg2
import xlrd
from collections import defaultdict, Counter

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
    """Lê todos os dados do arquivo Excel"""
    print("📖 LENDO DADOS COMPLETOS DO ARQUIVO...")
    
    wb = xlrd.open_workbook("RelatorioEmissoes.xls")
    sheet = wb.sheet_by_index(0)
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = sheet.cell_value(0, col)
        headers.append(str(header).strip() if header else f"coluna_{col}")
    
    print(f"📋 {len(headers)} colunas encontradas no arquivo")
    
    # Ler dados
    dados_arquivo = {}
    for row in range(1, sheet.nrows):
        protocolo_raw = sheet.cell_value(row, 0)
        if protocolo_raw:
            protocolo = str(int(protocolo_raw))
            
            # Ler todos os campos da linha
            registro = {}
            for col in range(sheet.ncols):
                valor = sheet.cell_value(row, col)
                if valor is not None and valor != '':
                    if isinstance(valor, str):
                        valor = valor.strip()
                    registro[headers[col]] = valor
            
            dados_arquivo[protocolo] = registro
    
    print(f"✅ {len(dados_arquivo)} registros carregados do arquivo")
    return dados_arquivo, headers

def buscar_protocolos_existentes(protocolos_arquivo):
    """Busca dados completos dos protocolos que existem no banco"""
    print("\n🗄️ BUSCANDO DADOS DOS PROTOCOLOS EXISTENTES...")

    conn = conectar_banco()
    cursor = conn.cursor()

    # CORRIGIDO: Buscar apenas protocolos que estão no arquivo
    print(f"🔍 Buscando apenas protocolos do range do arquivo...")

    # Converter protocolos do arquivo para lista de inteiros
    protocolos_int = [int(p) for p in protocolos_arquivo]
    min_protocolo = min(protocolos_int)
    max_protocolo = max(protocolos_int)

    print(f"📊 Range do arquivo: {min_protocolo:,} até {max_protocolo:,}")

    # Buscar dados no range dos protocolos do arquivo
    cursor.execute("""
        SELECT * FROM emissao
        WHERE protocolo >= %s AND protocolo <= %s
    """, (min_protocolo, max_protocolo))

    # Obter nomes das colunas
    colunas = [desc[0] for desc in cursor.description]
    registros = cursor.fetchall()

    # Converter para dicionário por protocolo
    dados_banco = {}
    for registro in registros:
        protocolo_bigint = registro[0]  # protocolo como bigint
        protocolo = str(protocolo_bigint)  # converter para string
        dados_banco[protocolo] = dict(zip(colunas, registro))

        # Debug: verificar se está convertendo corretamente
        if len(dados_banco) <= 3:
            print(f"🔍 Debug conversão: {protocolo_bigint} → '{protocolo}'")

    conn.close()

    print(f"✅ {len(dados_banco)} registros carregados do banco (no range)")
    print(f"📋 {len(colunas)} colunas na tabela do banco")

    # Debug: mostrar alguns protocolos
    if dados_banco:
        exemplos = list(dados_banco.keys())[:5]
        print(f"🔍 Exemplos de protocolos do banco: {exemplos}")

    return dados_banco, colunas

def mapear_colunas(headers_arquivo, colunas_banco):
    """Mapeia colunas do arquivo para colunas do banco"""
    print("\n🔗 MAPEANDO COLUNAS ARQUIVO → BANCO...")
    
    # Mapeamento manual baseado no conhecimento das estruturas
    mapeamento = {
        'Protocolo': 'protocolo',
        'Documento do Titular': 'documento_do_titular',
        'Nome do Titular': 'nome_do_titular',
        'Produto': 'produto',
        'Data Inicio Validade': 'data_inicio_validade',
        'Data Fim Validade': 'data_fim_validade',
        'Status do Certificado': 'status_do_certificado',
        'Valor do Boleto': 'valor_do_boleto',
        'Nome da Cidade': 'nome_da_cidade',
        'Documento': 'documento',
        'Data AVP': 'data_avp'
    }
    
    # Verificar quais colunas do arquivo têm correspondência no banco
    mapeamento_valido = {}
    for col_arquivo, col_banco in mapeamento.items():
        if col_arquivo in headers_arquivo and col_banco in colunas_banco:
            mapeamento_valido[col_arquivo] = col_banco
            print(f"   ✅ {col_arquivo} → {col_banco}")
        else:
            if col_arquivo in headers_arquivo:
                print(f"   ❌ {col_arquivo} → (não encontrada no banco)")
            else:
                print(f"   ❓ {col_arquivo} → (não encontrada no arquivo)")
    
    print(f"\n📊 {len(mapeamento_valido)} colunas mapeadas com sucesso")
    return mapeamento_valido

def analisar_mudancas(dados_arquivo, dados_banco, mapeamento):
    """Analisa mudanças campo por campo"""
    print("\n🔍 ANALISANDO MUDANÇAS CAMPO POR CAMPO...")

    # Debug: verificar alguns protocolos
    protocolos_arquivo_exemplo = list(dados_arquivo.keys())[:5]
    protocolos_banco_exemplo = list(dados_banco.keys())[:5]
    print(f"🔍 Debug - Protocolos arquivo: {protocolos_arquivo_exemplo}")
    print(f"🔍 Debug - Protocolos banco: {protocolos_banco_exemplo}")

    # Encontrar protocolos que existem em ambos
    protocolos_existentes = set(dados_arquivo.keys()) & set(dados_banco.keys())
    print(f"📊 Analisando {len(protocolos_existentes)} protocolos existentes")

    # Se não encontrou nenhum, vamos investigar
    if len(protocolos_existentes) == 0:
        print(f"⚠️ PROBLEMA: Nenhum protocolo em comum encontrado!")
        print(f"   Arquivo tem {len(dados_arquivo)} protocolos")
        print(f"   Banco tem {len(dados_banco)} protocolos")

        # Testar alguns protocolos específicos
        protocolos_teste = ['1008563478', '1008570262', '1008632785']
        for protocolo in protocolos_teste:
            no_arquivo = protocolo in dados_arquivo
            no_banco = protocolo in dados_banco
            print(f"   {protocolo}: Arquivo={no_arquivo}, Banco={no_banco}")

        return {
            'total_protocolos_analisados': 0,
            'protocolos_com_mudancas': 0,
            'protocolos_sem_mudancas': 0,
            'mudancas_por_campo': Counter(),
            'mudancas_detalhadas': [],
            'total_mudancas': 0
        }
    
    # Contadores para análise
    mudancas_por_campo = Counter()
    mudancas_detalhadas = []
    protocolos_com_mudancas = set()
    
    for protocolo in protocolos_existentes:
        registro_arquivo = dados_arquivo[protocolo]
        registro_banco = dados_banco[protocolo]
        
        mudancas_protocolo = []
        
        # Comparar cada campo mapeado
        for col_arquivo, col_banco in mapeamento.items():
            valor_arquivo = registro_arquivo.get(col_arquivo)
            valor_banco = registro_banco.get(col_banco)
            
            # Normalizar valores para comparação
            valor_arquivo_str = str(valor_arquivo).strip() if valor_arquivo is not None else ''
            valor_banco_str = str(valor_banco).strip() if valor_banco is not None else ''
            
            # Verificar se há mudança
            if valor_arquivo_str != valor_banco_str and valor_arquivo_str != '':
                tipo_mudanca = 'PREENCHIMENTO' if valor_banco_str == '' else 'ATUALIZACAO'
                
                mudancas_por_campo[col_arquivo] += 1
                mudancas_protocolo.append({
                    'campo': col_arquivo,
                    'valor_atual': valor_banco,
                    'valor_novo': valor_arquivo,
                    'tipo': tipo_mudanca
                })
                
                mudancas_detalhadas.append({
                    'protocolo': protocolo,
                    'campo': col_arquivo,
                    'valor_atual': valor_banco,
                    'valor_novo': valor_arquivo,
                    'tipo': tipo_mudanca
                })
        
        if mudancas_protocolo:
            protocolos_com_mudancas.add(protocolo)
    
    return {
        'total_protocolos_analisados': len(protocolos_existentes),
        'protocolos_com_mudancas': len(protocolos_com_mudancas),
        'protocolos_sem_mudancas': len(protocolos_existentes) - len(protocolos_com_mudancas),
        'mudancas_por_campo': mudancas_por_campo,
        'mudancas_detalhadas': mudancas_detalhadas,
        'total_mudancas': len(mudancas_detalhadas)
    }

def exibir_relatorio(resultado):
    """Exibe relatório detalhado das mudanças"""
    print("\n📊 RELATÓRIO DE CAMPOS ATUALIZADOS")
    print("=" * 50)
    
    print(f"📋 Total de protocolos existentes analisados: {resultado['total_protocolos_analisados']:,}")
    print(f"🔄 Protocolos COM mudanças: {resultado['protocolos_com_mudancas']:,}")
    print(f"✅ Protocolos SEM mudanças: {resultado['protocolos_sem_mudancas']:,}")
    print(f"📝 Total de mudanças de campo: {resultado['total_mudancas']:,}")
    
    # Percentuais
    if resultado['total_protocolos_analisados'] > 0:
        pct_com_mudancas = (resultado['protocolos_com_mudancas'] / resultado['total_protocolos_analisados']) * 100
        pct_sem_mudancas = (resultado['protocolos_sem_mudancas'] / resultado['total_protocolos_analisados']) * 100
        print(f"📊 {pct_com_mudancas:.1f}% terão atualizações, {pct_sem_mudancas:.1f}% sem mudanças")
    
    # Campos mais alterados
    if resultado['mudancas_por_campo']:
        print(f"\n📝 CAMPOS MAIS ALTERADOS:")
        print("-" * 40)
        for campo, quantidade in resultado['mudancas_por_campo'].most_common(15):
            pct = (quantidade / resultado['total_protocolos_analisados']) * 100
            print(f"   🔸 {campo}: {quantidade:,} alterações ({pct:.1f}%)")
    
    # Exemplos de mudanças
    if resultado['mudancas_detalhadas']:
        print(f"\n🔍 EXEMPLOS DE MUDANÇAS (primeiras 15):")
        print("-" * 50)
        
        # Agrupar por tipo
        preenchimentos = [m for m in resultado['mudancas_detalhadas'] if m['tipo'] == 'PREENCHIMENTO']
        atualizacoes = [m for m in resultado['mudancas_detalhadas'] if m['tipo'] == 'ATUALIZACAO']
        
        print(f"📝 PREENCHIMENTOS (campo vazio → valor): {len(preenchimentos):,}")
        for mudanca in preenchimentos[:8]:
            valor_novo = str(mudanca['valor_novo'])[:40]
            print(f"   📝 {mudanca['protocolo']} | {mudanca['campo']}")
            print(f"      VAZIO → {valor_novo}")
            print()
        
        print(f"🔄 ATUALIZAÇÕES (valor → novo valor): {len(atualizacoes):,}")
        for mudanca in atualizacoes[:7]:
            valor_atual = str(mudanca['valor_atual'])[:30] if mudanca['valor_atual'] else 'VAZIO'
            valor_novo = str(mudanca['valor_novo'])[:30]
            print(f"   🔄 {mudanca['protocolo']} | {mudanca['campo']}")
            print(f"      {valor_atual} → {valor_novo}")
            print()

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE CAMPOS ATUALIZADOS")
    print("=" * 50)
    print("🎯 Foco: 965 protocolos que JÁ EXISTEM no banco")
    print()
    
    try:
        # Carregar dados
        dados_arquivo, headers_arquivo = ler_dados_arquivo()
        dados_banco, colunas_banco = buscar_protocolos_existentes(list(dados_arquivo.keys()))
        
        # Mapear colunas
        mapeamento = mapear_colunas(headers_arquivo, colunas_banco)
        
        # Analisar mudanças
        resultado = analisar_mudancas(dados_arquivo, dados_banco, mapeamento)
        
        # Exibir relatório
        exibir_relatorio(resultado)
        
        print(f"\n🎯 RESUMO EXECUTIVO:")
        print("=" * 30)
        print(f"   📊 {resultado['protocolos_com_mudancas']:,} protocolos serão atualizados")
        print(f"   📝 {resultado['total_mudancas']:,} campos serão alterados")
        print(f"   ✅ {resultado['protocolos_sem_mudancas']:,} protocolos sem mudanças")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
