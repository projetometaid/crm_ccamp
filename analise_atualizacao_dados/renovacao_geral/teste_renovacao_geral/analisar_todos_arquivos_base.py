#!/usr/bin/env python3
"""
ANÁLISE DE TODOS OS ARQUIVOS DA BASE - RENOVAÇÃO GERAL
Analisa todos os arquivos XLS da pasta base_renovacao_geral para verificar dados
"""

import os
import xlrd
from collections import defaultdict

def encontrar_todos_arquivos_xls():
    """Encontra todos os arquivos XLS na pasta base_renovacao_geral"""
    print("📁 PROCURANDO TODOS OS ARQUIVOS XLS...")
    print("=" * 50)
    
    base_path = "../base_renovacao_geral"
    arquivos_encontrados = []
    
    # Percorrer todas as pastas e subpastas
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xls') or file.endswith('.xlsx'):
                caminho_completo = os.path.join(root, file)
                arquivos_encontrados.append(caminho_completo)
    
    print(f"✅ Encontrados {len(arquivos_encontrados)} arquivos XLS")
    
    # Organizar por ano
    arquivos_por_ano = defaultdict(list)
    for arquivo in arquivos_encontrados:
        if '2024' in arquivo:
            arquivos_por_ano['2024'].append(arquivo)
        elif '2025' in arquivo:
            arquivos_por_ano['2025'].append(arquivo)
        elif '2026' in arquivo:
            arquivos_por_ano['2026'].append(arquivo)
        elif '2027' in arquivo:
            arquivos_por_ano['2027'].append(arquivo)
        elif '2028' in arquivo:
            arquivos_por_ano['2028'].append(arquivo)
        elif '2029' in arquivo:
            arquivos_por_ano['2029'].append(arquivo)
        else:
            arquivos_por_ano['outros'].append(arquivo)
    
    print(f"\n📊 DISTRIBUIÇÃO POR ANO:")
    for ano, arquivos in sorted(arquivos_por_ano.items()):
        print(f"   {ano}: {len(arquivos)} arquivos")
    
    return arquivos_encontrados, arquivos_por_ano

def analisar_estrutura_arquivo(arquivo_path):
    """Analisa a estrutura de um arquivo específico"""
    try:
        wb = xlrd.open_workbook(arquivo_path)
        sheet = wb.sheet_by_index(0)
        
        # Obter cabeçalhos
        headers = []
        for col in range(sheet.ncols):
            header = str(sheet.cell_value(0, col)).strip()
            headers.append(header)
        
        return {
            'arquivo': os.path.basename(arquivo_path),
            'caminho': arquivo_path,
            'registros': sheet.nrows - 1,
            'colunas': sheet.ncols,
            'headers': headers,
            'sucesso': True
        }
    
    except Exception as e:
        return {
            'arquivo': os.path.basename(arquivo_path),
            'caminho': arquivo_path,
            'erro': str(e),
            'sucesso': False
        }

def analisar_campos_renovacao_arquivo(arquivo_path):
    """Analisa especificamente os campos de renovação em um arquivo"""
    try:
        wb = xlrd.open_workbook(arquivo_path)
        sheet = wb.sheet_by_index(0)
        
        # Encontrar colunas dos campos de renovação
        headers = []
        for col in range(sheet.ncols):
            header = str(sheet.cell_value(0, col)).strip()
            headers.append(header)
        
        # Mapear colunas importantes
        col_protocolo = None
        col_protocolo_renovacao = None
        col_status_renovacao = None
        col_ar_renovacao = None
        col_produto_renovacao = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'protocolo' in header_lower and 'renovacao' not in header_lower:
                col_protocolo = i
            elif 'protocolo' in header_lower and 'renovacao' in header_lower:
                col_protocolo_renovacao = i
            elif 'status' in header_lower and 'protocolo' in header_lower and 'renovacao' in header_lower:
                col_status_renovacao = i
            elif 'ar' in header_lower and 'protocolo' in header_lower and 'renovacao' in header_lower:
                col_ar_renovacao = i
            elif 'produto' in header_lower and 'protocolo' in header_lower and 'renovacao' in header_lower:
                col_produto_renovacao = i
        
        # Analisar dados dos campos de renovação
        stats = {
            'total_registros': sheet.nrows - 1,
            'protocolo_renovacao_preenchidos': 0,
            'status_renovacao_preenchidos': 0,
            'ar_renovacao_preenchidos': 0,
            'produto_renovacao_preenchidos': 0,
            'exemplos_protocolo_renovacao': set(),
            'exemplos_status_renovacao': set(),
            'exemplos_ar_renovacao': set(),
            'exemplos_produto_renovacao': set()
        }
        
        for row in range(1, min(sheet.nrows, 1001)):  # Analisar até 1000 registros
            # Protocolo renovação
            if col_protocolo_renovacao is not None:
                valor = str(sheet.cell_value(row, col_protocolo_renovacao)).strip()
                if valor and valor != '' and valor != '0' and valor != '0.0':
                    stats['protocolo_renovacao_preenchidos'] += 1
                    if len(stats['exemplos_protocolo_renovacao']) < 5:
                        stats['exemplos_protocolo_renovacao'].add(valor)
            
            # Status renovação
            if col_status_renovacao is not None:
                valor = str(sheet.cell_value(row, col_status_renovacao)).strip()
                if valor and valor != '':
                    stats['status_renovacao_preenchidos'] += 1
                    if len(stats['exemplos_status_renovacao']) < 5:
                        stats['exemplos_status_renovacao'].add(valor)
            
            # AR renovação
            if col_ar_renovacao is not None:
                valor = str(sheet.cell_value(row, col_ar_renovacao)).strip()
                if valor and valor != '':
                    stats['ar_renovacao_preenchidos'] += 1
                    if len(stats['exemplos_ar_renovacao']) < 5:
                        stats['exemplos_ar_renovacao'].add(valor)
            
            # Produto renovação
            if col_produto_renovacao is not None:
                valor = str(sheet.cell_value(row, col_produto_renovacao)).strip()
                if valor and valor != '':
                    stats['produto_renovacao_preenchidos'] += 1
                    if len(stats['exemplos_produto_renovacao']) < 5:
                        stats['exemplos_produto_renovacao'].add(valor)
        
        return {
            'arquivo': os.path.basename(arquivo_path),
            'mapeamento': {
                'protocolo': col_protocolo,
                'protocolo_renovacao': col_protocolo_renovacao,
                'status_renovacao': col_status_renovacao,
                'ar_renovacao': col_ar_renovacao,
                'produto_renovacao': col_produto_renovacao
            },
            'stats': stats,
            'sucesso': True
        }
    
    except Exception as e:
        return {
            'arquivo': os.path.basename(arquivo_path),
            'erro': str(e),
            'sucesso': False
        }

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE TODOS OS ARQUIVOS DA BASE - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Objetivo: Verificar se arquivos contêm dados de renovação")
    print()
    
    try:
        # Encontrar todos os arquivos
        arquivos, arquivos_por_ano = encontrar_todos_arquivos_xls()
        
        if not arquivos:
            print("❌ Nenhum arquivo XLS encontrado!")
            return
        
        # Analisar estrutura de alguns arquivos
        print(f"\n📊 ANALISANDO ESTRUTURA DOS ARQUIVOS...")
        print("-" * 60)
        
        estruturas = []
        for i, arquivo in enumerate(arquivos[:5]):  # Analisar primeiros 5
            print(f"   📋 Analisando: {os.path.basename(arquivo)}")
            estrutura = analisar_estrutura_arquivo(arquivo)
            estruturas.append(estrutura)
        
        # Mostrar estruturas
        print(f"\n📋 ESTRUTURAS ENCONTRADAS:")
        print("-" * 60)
        for estrutura in estruturas:
            if estrutura['sucesso']:
                print(f"\n   📁 {estrutura['arquivo']}")
                print(f"      📊 {estrutura['registros']:,} registros x {estrutura['colunas']} colunas")
                print(f"      📋 Colunas: {', '.join(estrutura['headers'][:5])}...")
            else:
                print(f"\n   ❌ {estrutura['arquivo']}: {estrutura['erro']}")
        
        # Analisar campos de renovação
        print(f"\n🔍 ANALISANDO CAMPOS DE RENOVAÇÃO...")
        print("-" * 60)
        
        total_com_dados_renovacao = 0
        total_registros_analisados = 0
        
        for ano, arquivos_ano in sorted(arquivos_por_ano.items()):
            print(f"\n📅 ANO {ano} ({len(arquivos_ano)} arquivos):")
            
            for arquivo in arquivos_ano:
                analise = analisar_campos_renovacao_arquivo(arquivo)
                
                if analise['sucesso']:
                    stats = analise['stats']
                    total_registros_analisados += stats['total_registros']
                    
                    tem_dados = (stats['protocolo_renovacao_preenchidos'] > 0 or 
                               stats['status_renovacao_preenchidos'] > 0 or
                               stats['ar_renovacao_preenchidos'] > 0 or
                               stats['produto_renovacao_preenchidos'] > 0)
                    
                    if tem_dados:
                        total_com_dados_renovacao += 1
                        print(f"   ✅ {analise['arquivo']}")
                        print(f"      📊 {stats['total_registros']:,} registros")
                        print(f"      🔄 Protocolo renovação: {stats['protocolo_renovacao_preenchidos']} preenchidos")
                        print(f"      📊 Status renovação: {stats['status_renovacao_preenchidos']} preenchidos")
                        print(f"      🏢 AR renovação: {stats['ar_renovacao_preenchidos']} preenchidos")
                        print(f"      🏷️ Produto renovação: {stats['produto_renovacao_preenchidos']} preenchidos")
                        
                        if stats['exemplos_status_renovacao']:
                            print(f"      💡 Status exemplos: {', '.join(list(stats['exemplos_status_renovacao'])[:3])}")
                        if stats['exemplos_ar_renovacao']:
                            print(f"      💡 AR exemplos: {', '.join(list(stats['exemplos_ar_renovacao'])[:2])}")
                    else:
                        print(f"   ⚪ {analise['arquivo']}: Sem dados de renovação")
                else:
                    print(f"   ❌ {analise['arquivo']}: {analise['erro']}")
        
        # Resumo final
        print(f"\n🎉 ANÁLISE CONCLUÍDA!")
        print("=" * 50)
        print(f"📁 Total de arquivos: {len(arquivos)}")
        print(f"✅ Arquivos com dados de renovação: {total_com_dados_renovacao}")
        print(f"📊 Total de registros analisados: {total_registros_analisados:,}")
        
        if total_com_dados_renovacao > 0:
            print(f"\n🎯 DESCOBERTA IMPORTANTE:")
            print(f"   ✅ Encontrados dados de renovação nos arquivos!")
            print(f"   📊 {total_com_dados_renovacao} arquivos contêm dados que faltam no banco")
            print(f"   🚀 Recomendação: Recriar tabela com todos os arquivos")
        else:
            print(f"\n⚠️ ATENÇÃO:")
            print(f"   📊 Nenhum arquivo contém dados de renovação preenchidos")
            print(f"   🤔 Verificar se estrutura está correta")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
