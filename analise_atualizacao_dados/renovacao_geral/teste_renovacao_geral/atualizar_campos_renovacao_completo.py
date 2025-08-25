#!/usr/bin/env python3
"""
ATUALIZAÇÃO COMPLETA DOS CAMPOS DE RENOVAÇÃO
Lê TODOS os arquivos da base e atualiza campos vazios no banco
"""

import os
import xlrd
import psycopg2
from datetime import datetime

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def encontrar_todos_arquivos():
    """Encontra todos os arquivos XLS da base"""
    print("📁 PROCURANDO TODOS OS ARQUIVOS XLS...")
    
    base_path = "../base_renovacao_geral"
    arquivos = []
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xls') or file.endswith('.xlsx'):
                caminho_completo = os.path.join(root, file)
                arquivos.append(caminho_completo)
    
    print(f"✅ Encontrados {len(arquivos)} arquivos")
    return arquivos

def ler_dados_renovacao_arquivo(arquivo_path):
    """Lê dados de renovação de um arquivo específico"""
    try:
        wb = xlrd.open_workbook(arquivo_path)
        sheet = wb.sheet_by_index(0)
        
        # Mapear colunas (baseado na análise anterior)
        col_protocolo = 13  # Protocolo
        col_protocolo_renovacao = 18  # Protocolo renovação
        col_status_renovacao = 19  # Status protocolo renovação
        col_ar_renovacao = 20  # Nome da AR protocolo renovação
        col_produto_renovacao = 21  # Produto protocolo renovação
        
        dados_renovacao = {}
        
        for row in range(1, sheet.nrows):
            # Protocolo principal (chave)
            protocolo_str = str(sheet.cell_value(row, col_protocolo)).strip()
            try:
                protocolo = int(float(protocolo_str))
            except:
                continue
            
            # Dados de renovação
            protocolo_renovacao = str(sheet.cell_value(row, col_protocolo_renovacao)).strip()
            status_renovacao = str(sheet.cell_value(row, col_status_renovacao)).strip()
            ar_renovacao = str(sheet.cell_value(row, col_ar_renovacao)).strip()
            produto_renovacao = str(sheet.cell_value(row, col_produto_renovacao)).strip()
            
            # Normalizar valores vazios
            if protocolo_renovacao in ['0', '0.0', '', 'None']:
                protocolo_renovacao = None
            else:
                try:
                    protocolo_renovacao = int(float(protocolo_renovacao))
                except:
                    protocolo_renovacao = None
            
            if status_renovacao in ['', 'None']:
                status_renovacao = None
            
            if ar_renovacao in ['', 'None']:
                ar_renovacao = None
            
            if produto_renovacao in ['', 'None']:
                produto_renovacao = None
            
            # Armazenar dados se pelo menos um campo está preenchido
            if any([protocolo_renovacao, status_renovacao, ar_renovacao, produto_renovacao]):
                dados_renovacao[protocolo] = {
                    'protocolo_renovacao': protocolo_renovacao,
                    'status_protocolo_renovacao': status_renovacao,
                    'nome_da_ar_protocolo_renovacao': ar_renovacao,
                    'produto_protocolo_renovacao': produto_renovacao
                }
        
        return dados_renovacao, None
        
    except Exception as e:
        return {}, str(e)

def consolidar_dados_todos_arquivos(arquivos):
    """Consolida dados de renovação de todos os arquivos"""
    print(f"\n📊 CONSOLIDANDO DADOS DE {len(arquivos)} ARQUIVOS...")
    
    dados_consolidados = {}
    arquivos_processados = 0
    arquivos_com_erro = 0
    
    for i, arquivo in enumerate(arquivos):
        print(f"   📋 Processando: {os.path.basename(arquivo)} ({i+1}/{len(arquivos)})")
        
        dados_arquivo, erro = ler_dados_renovacao_arquivo(arquivo)
        
        if erro:
            print(f"      ❌ Erro: {erro}")
            arquivos_com_erro += 1
            continue
        
        arquivos_processados += 1
        
        # Consolidar dados (arquivo mais recente sobrescreve)
        for protocolo, dados in dados_arquivo.items():
            dados_consolidados[protocolo] = dados
        
        print(f"      ✅ {len(dados_arquivo)} registros com dados de renovação")
    
    print(f"\n📊 CONSOLIDAÇÃO CONCLUÍDA:")
    print(f"   ✅ Arquivos processados: {arquivos_processados}")
    print(f"   ❌ Arquivos com erro: {arquivos_com_erro}")
    print(f"   📊 Total de protocolos com dados: {len(dados_consolidados):,}")
    
    return dados_consolidados

def buscar_protocolos_existentes_banco(protocolos):
    """Busca quais protocolos existem no banco"""
    print(f"\n🗄️ VERIFICANDO PROTOCOLOS NO BANCO...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar em lotes
    protocolos_existentes = {}
    lote_size = 1000
    
    for i in range(0, len(protocolos), lote_size):
        lote = protocolos[i:i+lote_size]
        placeholders = ','.join(['%s'] * len(lote))
        
        cursor.execute(f"""
            SELECT protocolo, protocolo_renovacao, status_protocolo_renovacao,
                   nome_da_ar_protocolo_renovacao, produto_protocolo_renovacao
            FROM renovacao_geral
            WHERE protocolo IN ({placeholders})
        """, lote)
        
        for protocolo, prot_ren, status, ar, produto in cursor.fetchall():
            protocolos_existentes[protocolo] = {
                'protocolo_renovacao': prot_ren,
                'status_protocolo_renovacao': status,
                'nome_da_ar_protocolo_renovacao': ar,
                'produto_protocolo_renovacao': produto
            }
        
        print(f"   📋 Processado lote {i//lote_size + 1}/{(len(protocolos)-1)//lote_size + 1}")
    
    conn.close()
    
    print(f"✅ Protocolos encontrados no banco: {len(protocolos_existentes):,}")
    
    return protocolos_existentes

def identificar_atualizacoes_necessarias(dados_consolidados, protocolos_banco):
    """Identifica quais registros precisam ser atualizados"""
    print(f"\n🔍 IDENTIFICANDO ATUALIZAÇÕES NECESSÁRIAS...")
    
    atualizacoes = []
    
    for protocolo, dados_arquivo in dados_consolidados.items():
        if protocolo not in protocolos_banco:
            continue  # Protocolo não existe no banco
        
        dados_banco = protocolos_banco[protocolo]
        mudancas = {}
        
        # Verificar cada campo
        for campo in ['protocolo_renovacao', 'status_protocolo_renovacao', 
                     'nome_da_ar_protocolo_renovacao', 'produto_protocolo_renovacao']:
            
            valor_banco = dados_banco[campo]
            valor_arquivo = dados_arquivo[campo]
            
            # Atualizar se banco está vazio e arquivo tem dados
            if valor_banco is None and valor_arquivo is not None:
                mudancas[campo] = valor_arquivo
        
        if mudancas:
            atualizacoes.append({
                'protocolo': protocolo,
                'mudancas': mudancas
            })
    
    print(f"📊 RESULTADO:")
    print(f"   🔄 Registros que precisam de atualização: {len(atualizacoes):,}")
    
    # Estatísticas por campo
    stats_campos = {}
    for atualizacao in atualizacoes:
        for campo in atualizacao['mudancas'].keys():
            if campo not in stats_campos:
                stats_campos[campo] = 0
            stats_campos[campo] += 1
    
    print(f"\n📋 ATUALIZAÇÕES POR CAMPO:")
    for campo, count in sorted(stats_campos.items()):
        print(f"   {campo:35}: {count:,} atualizações")
    
    return atualizacoes

def executar_atualizacoes(atualizacoes):
    """Executa as atualizações no banco"""
    print(f"\n🚀 EXECUTANDO ATUALIZAÇÕES...")
    
    if not atualizacoes:
        print("✅ Nenhuma atualização necessária!")
        return
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    atualizados = 0
    erros = 0
    
    for i, atualizacao in enumerate(atualizacoes):
        protocolo = atualizacao['protocolo']
        mudancas = atualizacao['mudancas']
        
        # Construir SQL dinamicamente
        set_clauses = []
        valores = []
        
        for campo, valor in mudancas.items():
            set_clauses.append(f"{campo} = %s")
            valores.append(valor)
        
        valores.append(protocolo)  # Para o WHERE
        
        sql = f"""
            UPDATE renovacao_geral 
            SET {', '.join(set_clauses)}
            WHERE protocolo = %s
        """
        
        try:
            cursor.execute(sql, valores)
            atualizados += 1
            
            # Commit a cada 50 registros
            if (i + 1) % 50 == 0:
                conn.commit()
                print(f"   📋 Atualizados: {i+1:,}/{len(atualizacoes):,}")
        
        except Exception as e:
            erros += 1
            conn.rollback()
            print(f"   ❌ Erro no protocolo {protocolo}: {str(e)[:100]}")
    
    # Commit final
    try:
        conn.commit()
    except:
        pass
    
    conn.close()
    
    print(f"\n📊 RESULTADO DA EXECUÇÃO:")
    print(f"   ✅ Registros atualizados: {atualizados:,}")
    print(f"   ❌ Erros: {erros:,}")
    print(f"   📈 Taxa de sucesso: {(atualizados/(atualizados+erros))*100:.1f}%")

def main():
    """Função principal"""
    print("🚀 ATUALIZAÇÃO COMPLETA DOS CAMPOS DE RENOVAÇÃO")
    print("=" * 70)
    print("🎯 Objetivo: Atualizar campos vazios com dados dos arquivos")
    print()
    
    try:
        # Encontrar todos os arquivos
        arquivos = encontrar_todos_arquivos()
        
        if not arquivos:
            print("❌ Nenhum arquivo encontrado!")
            return
        
        # Consolidar dados de todos os arquivos
        dados_consolidados = consolidar_dados_todos_arquivos(arquivos)
        
        if not dados_consolidados:
            print("❌ Nenhum dado de renovação encontrado!")
            return
        
        # Buscar protocolos existentes no banco
        protocolos = list(dados_consolidados.keys())
        protocolos_banco = buscar_protocolos_existentes_banco(protocolos)
        
        # Identificar atualizações necessárias
        atualizacoes = identificar_atualizacoes_necessarias(dados_consolidados, protocolos_banco)
        
        if not atualizacoes:
            print("\n✅ NENHUMA ATUALIZAÇÃO NECESSÁRIA!")
            print("   Todos os campos já estão preenchidos corretamente")
            return
        
        # Confirmar execução
        print(f"\n🚨 CONFIRMAÇÃO NECESSÁRIA")
        print(f"   🔄 {len(atualizacoes):,} registros serão atualizados")
        print(f"   📊 Apenas campos vazios serão preenchidos")
        print(f"   🔑 Protocolo será usado como chave")
        
        resposta = input("\n🚀 DESEJA EXECUTAR AS ATUALIZAÇÕES? (sim/não): ").strip().lower()
        
        if resposta in ['sim', 's', 'yes', 'y']:
            # Executar atualizações
            executar_atualizacoes(atualizacoes)
            
            print(f"\n🎉 ATUALIZAÇÃO CONCLUÍDA!")
            print("=" * 40)
            print(f"✅ Campos de renovação atualizados com sucesso")
        else:
            print(f"\n❌ OPERAÇÃO CANCELADA")
            print(f"   Nenhuma alteração foi feita no banco")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
