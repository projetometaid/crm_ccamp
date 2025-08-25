#!/usr/bin/env python3
"""
ANÁLISE DETALHADA DOS ARQUIVOS - RENOVAÇÃO GERAL
Analisa detalhadamente o conteúdo real dos arquivos XLS
"""

import os
import xlrd

def analisar_arquivo_detalhado(arquivo_path):
    """Analisa um arquivo específico mostrando TODOS os dados"""
    print(f"📁 ANALISANDO: {os.path.basename(arquivo_path)}")
    print("=" * 80)
    
    try:
        wb = xlrd.open_workbook(arquivo_path)
        sheet = wb.sheet_by_index(0)
        
        print(f"📊 Dimensões: {sheet.nrows-1:,} registros x {sheet.ncols} colunas")
        print()
        
        # Mostrar TODOS os cabeçalhos
        print("📋 TODOS OS CABEÇALHOS:")
        print("-" * 80)
        for col in range(sheet.ncols):
            header = str(sheet.cell_value(0, col)).strip()
            print(f"   Col {col:2d}: {header}")
        
        print()
        
        # Mostrar dados dos primeiros 5 registros COMPLETOS
        print("🔍 PRIMEIROS 5 REGISTROS COMPLETOS:")
        print("-" * 80)
        
        for row in range(1, min(6, sheet.nrows)):
            print(f"\n📋 REGISTRO {row}:")
            for col in range(sheet.ncols):
                header = str(sheet.cell_value(0, col)).strip()
                valor = str(sheet.cell_value(row, col)).strip()
                
                # Destacar campos de renovação
                if any(x in header.lower() for x in ['renovacao', 'protocolo', 'status', 'ar']):
                    if valor and valor != '' and valor != '0' and valor != '0.0':
                        print(f"   🔄 Col {col:2d} ({header}): '{valor}'")
                    else:
                        print(f"   ⚪ Col {col:2d} ({header}): VAZIO")
                else:
                    if len(valor) > 50:
                        valor = valor[:50] + "..."
                    print(f"   📋 Col {col:2d} ({header}): '{valor}'")
        
        # Analisar especificamente campos que podem ser de renovação
        print(f"\n🔍 ANÁLISE ESPECÍFICA DE CAMPOS DE RENOVAÇÃO:")
        print("-" * 80)
        
        campos_renovacao_encontrados = []
        
        for col in range(sheet.ncols):
            header = str(sheet.cell_value(0, col)).strip()
            header_lower = header.lower()
            
            # Verificar se é campo relacionado a renovação
            if any(x in header_lower for x in ['renovacao', 'protocolo', 'status', 'ar', 'produto']):
                # Contar quantos registros têm dados neste campo
                preenchidos = 0
                exemplos = set()
                
                for row in range(1, min(101, sheet.nrows)):  # Verificar primeiros 100
                    valor = str(sheet.cell_value(row, col)).strip()
                    if valor and valor != '' and valor != '0' and valor != '0.0' and valor.lower() != 'none':
                        preenchidos += 1
                        if len(exemplos) < 5:
                            exemplos.add(valor)
                
                if preenchidos > 0 or 'protocolo' in header_lower or 'renovacao' in header_lower:
                    campos_renovacao_encontrados.append({
                        'col': col,
                        'header': header,
                        'preenchidos': preenchidos,
                        'exemplos': list(exemplos)
                    })
        
        if campos_renovacao_encontrados:
            print("✅ CAMPOS DE RENOVAÇÃO ENCONTRADOS:")
            for campo in campos_renovacao_encontrados:
                print(f"   Col {campo['col']:2d}: {campo['header']}")
                print(f"      📊 Preenchidos: {campo['preenchidos']}/100 verificados")
                if campo['exemplos']:
                    print(f"      💡 Exemplos: {', '.join(campo['exemplos'][:3])}")
                else:
                    print(f"      ⚪ Todos vazios")
                print()
        else:
            print("❌ NENHUM CAMPO DE RENOVAÇÃO ENCONTRADO")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 ANÁLISE DETALHADA DOS ARQUIVOS - RENOVAÇÃO GERAL")
    print("=" * 80)
    print("🎯 Objetivo: Ver EXATAMENTE o que está nos arquivos")
    print()
    
    # Analisar alguns arquivos específicos de diferentes anos
    arquivos_para_analisar = [
        "../base_renovacao_geral/2025/GestaoRenovacao (1).xls",
        "../base_renovacao_geral/2025/GestaoRenovacao (2).xls",
        "../base_renovacao_geral/2024/GestaoRenovacao (1).xls",
        "../base_renovacao_geral/2026/GestaoRenovacao (1).xls"
    ]
    
    for arquivo in arquivos_para_analisar:
        if os.path.exists(arquivo):
            print(f"\n" + "="*100)
            sucesso = analisar_arquivo_detalhado(arquivo)
            if sucesso:
                print("✅ Análise concluída")
            else:
                print("❌ Falha na análise")
            print("="*100)
        else:
            print(f"❌ Arquivo não encontrado: {arquivo}")
    
    print(f"\n🎉 ANÁLISE DETALHADA CONCLUÍDA!")
    print("🎯 Agora podemos ver exatamente o que está nos arquivos")

if __name__ == "__main__":
    main()
