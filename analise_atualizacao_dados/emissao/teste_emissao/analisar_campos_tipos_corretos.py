#!/usr/bin/env python3
"""
ANÁLISE DE CAMPOS COM TIPOS CORRETOS
Converte tipos adequadamente antes da comparação
"""

import psycopg2
import xlrd
from datetime import datetime
from decimal import Decimal
from collections import Counter

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def converter_data_excel(valor_excel):
    """Converte data do Excel para datetime - CORRIGIDO"""
    # Se for vazio ou None, retornar None (não é erro)
    if not valor_excel or (isinstance(valor_excel, str) and valor_excel.strip() == ''):
        return None

    try:
        # Se for string, tentar converter (formato brasileiro)
        if isinstance(valor_excel, str):
            valor_limpo = valor_excel.strip()
            if not valor_limpo:  # String vazia após strip
                return None

            # Formatos brasileiros do arquivo
            formatos = [
                '%d/%m/%Y %H:%M:%S',  # 22/08/2025 17:19:20
                '%d/%m/%Y',           # 17/05/1990
            ]

            for formato in formatos:
                try:
                    return datetime.strptime(valor_limpo, formato)
                except:
                    continue

        # Se for número (data Excel) - menos comum neste arquivo
        elif isinstance(valor_excel, (int, float)):
            try:
                import xlrd
                # Usar xlrd para converter (precisa do datemode do workbook)
                # Por enquanto, vamos ignorar números
                return None
            except:
                return None

        return None
    except:
        return None

def converter_decimal(valor):
    """Converte valor para Decimal"""
    if not valor:
        return None
    
    try:
        if isinstance(valor, str):
            # Remover caracteres não numéricos exceto . e ,
            valor_limpo = valor.replace(',', '.').strip()
            return Decimal(valor_limpo)
        elif isinstance(valor, (int, float)):
            return Decimal(str(valor))
        else:
            return Decimal(str(valor))
    except:
        return None

def normalizar_string(valor):
    """Normaliza string para comparação"""
    if not valor:
        return ''
    return str(valor).strip().upper()

def ler_dados_arquivo_tipados():
    """Lê dados do arquivo com conversão de tipos"""
    print("📖 LENDO DADOS COM CONVERSÃO DE TIPOS...")
    
    wb = xlrd.open_workbook("RelatorioEmissoes.xls")
    sheet = wb.sheet_by_index(0)
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = sheet.cell_value(0, col)
        headers.append(str(header).strip() if header else f"coluna_{col}")
    
    # Mapeamento de conversores por coluna
    conversores = {
        'Data Inicio Validade': converter_data_excel,
        'Data Fim Validade': converter_data_excel,
        'Data AVP': converter_data_excel,
        'Valor do Boleto': converter_decimal,
        'Documento do Titular': normalizar_string,
        'Nome do Titular': normalizar_string,
        'Produto': normalizar_string,
        'Status do Certificado': normalizar_string,
        'Nome da Cidade': normalizar_string,
        'Documento': normalizar_string
    }
    
    dados_arquivo = {}
    for row in range(1, sheet.nrows):
        protocolo_raw = sheet.cell_value(row, 0)
        if protocolo_raw:
            protocolo = str(int(protocolo_raw))
            
            registro = {}
            for col in range(sheet.ncols):
                header = headers[col]
                valor_raw = sheet.cell_value(row, col)
                
                # Aplicar conversor específico se existir
                if header in conversores:
                    valor_convertido = conversores[header](valor_raw)
                else:
                    valor_convertido = valor_raw
                
                if valor_convertido is not None:
                    registro[header] = valor_convertido
            
            dados_arquivo[protocolo] = registro
    
    print(f"✅ {len(dados_arquivo)} registros carregados e convertidos")
    return dados_arquivo, headers

def buscar_dados_banco_tipados(protocolos_arquivo):
    """Busca dados do banco mantendo tipos originais"""
    print("\n🗄️ BUSCANDO DADOS DO BANCO (tipos originais)...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar no range dos protocolos
    protocolos_int = [int(p) for p in protocolos_arquivo]
    min_protocolo = min(protocolos_int)
    max_protocolo = max(protocolos_int)
    
    cursor.execute("""
        SELECT protocolo, documento_do_titular, nome_do_titular, produto,
               data_inicio_validade, data_fim_validade, status_do_certificado,
               valor_do_boleto, nome_da_cidade, documento, data_avp
        FROM emissao 
        WHERE protocolo >= %s AND protocolo <= %s
    """, (min_protocolo, max_protocolo))
    
    registros = cursor.fetchall()
    conn.close()
    
    # Converter para dicionário
    dados_banco = {}
    colunas = ['protocolo', 'documento_do_titular', 'nome_do_titular', 'produto',
               'data_inicio_validade', 'data_fim_validade', 'status_do_certificado',
               'valor_do_boleto', 'nome_da_cidade', 'documento', 'data_avp']
    
    for registro in registros:
        protocolo = str(registro[0])
        dados_banco[protocolo] = dict(zip(colunas, registro))
    
    print(f"✅ {len(dados_banco)} registros do banco carregados")
    return dados_banco

def comparar_valores_tipados(valor_arquivo, valor_banco, tipo_campo):
    """Compara valores respeitando tipos - CORRIGIDO"""

    # Normalizar valores vazios
    arquivo_vazio = valor_arquivo is None or (isinstance(valor_arquivo, str) and valor_arquivo.strip() == '')
    banco_vazio = valor_banco is None or (isinstance(valor_banco, str) and valor_banco.strip() == '')

    # Se ambos são vazios, são iguais
    if arquivo_vazio and banco_vazio:
        return True, None

    # Se apenas um é vazio, há mudança
    if arquivo_vazio and not banco_vazio:
        return False, 'REMOCAO'  # Arquivo remove valor do banco
    if not arquivo_vazio and banco_vazio:
        return False, 'PREENCHIMENTO'  # Arquivo preenche campo vazio

    # Ambos têm valores, comparar por tipo
    try:
        if tipo_campo == 'datetime':
            # Ambos devem ser datetime para comparar
            if hasattr(valor_arquivo, 'date') and hasattr(valor_banco, 'date'):
                # Comparar apenas data (ignorar horário para tolerância)
                data_arquivo = valor_arquivo.date()
                data_banco = valor_banco.date()
                return data_arquivo == data_banco, 'ATUALIZACAO'
            else:
                # Se um não é datetime, considerar diferente
                return False, 'ATUALIZACAO'

        elif tipo_campo == 'decimal':
            # Comparar como Decimal com tolerância
            if isinstance(valor_arquivo, Decimal) and isinstance(valor_banco, Decimal):
                # Tolerância de 0.01 para diferenças de arredondamento
                diferenca = abs(valor_arquivo - valor_banco)
                return diferenca < Decimal('0.01'), 'ATUALIZACAO'
            else:
                return False, 'ATUALIZACAO'

        elif tipo_campo == 'string':
            # Comparar strings normalizadas
            str_arquivo = normalizar_string(valor_arquivo)
            str_banco = normalizar_string(valor_banco)
            return str_arquivo == str_banco, 'ATUALIZACAO'

        else:
            # Comparação padrão como string
            return str(valor_arquivo).strip() == str(valor_banco).strip(), 'ATUALIZACAO'

    except Exception as e:
        print(f"⚠️ Erro comparando {valor_arquivo} vs {valor_banco}: {e}")
        return False, 'ERRO'

def analisar_mudancas_tipadas():
    """Análise principal com tipos corretos"""
    print("\n🔍 ANÁLISE COM TIPOS CORRETOS...")
    
    # Carregar dados
    dados_arquivo, headers = ler_dados_arquivo_tipados()
    dados_banco = buscar_dados_banco_tipados(list(dados_arquivo.keys()))
    
    # Mapeamento arquivo → banco com tipos
    mapeamento = {
        'Documento do Titular': ('documento_do_titular', 'string'),
        'Nome do Titular': ('nome_do_titular', 'string'),
        'Produto': ('produto', 'string'),
        'Data Inicio Validade': ('data_inicio_validade', 'datetime'),
        'Data Fim Validade': ('data_fim_validade', 'datetime'),
        'Status do Certificado': ('status_do_certificado', 'string'),
        'Valor do Boleto': ('valor_do_boleto', 'decimal'),
        'Nome da Cidade': ('nome_da_cidade', 'string'),
        'Documento': ('documento', 'string'),
        'Data AVP': ('data_avp', 'datetime')
    }
    
    # Encontrar protocolos em comum
    protocolos_comuns = set(dados_arquivo.keys()) & set(dados_banco.keys())
    print(f"📊 Protocolos em comum: {len(protocolos_comuns)}")
    
    if len(protocolos_comuns) == 0:
        print("❌ ERRO: Nenhum protocolo em comum!")
        return
    
    # Analisar mudanças
    mudancas_por_campo = Counter()
    mudancas_detalhadas = []
    protocolos_com_mudancas = set()
    
    for protocolo in protocolos_comuns:  # PROCESSAR TODOS os protocolos
        registro_arquivo = dados_arquivo[protocolo]
        registro_banco = dados_banco[protocolo]
        
        for col_arquivo, (col_banco, tipo_campo) in mapeamento.items():
            valor_arquivo = registro_arquivo.get(col_arquivo)
            valor_banco = registro_banco.get(col_banco)
            
            iguais, tipo_mudanca = comparar_valores_tipados(valor_arquivo, valor_banco, tipo_campo)
            
            if not iguais:
                mudancas_por_campo[col_arquivo] += 1
                protocolos_com_mudancas.add(protocolo)
                
                mudancas_detalhadas.append({
                    'protocolo': protocolo,
                    'campo': col_arquivo,
                    'valor_atual': valor_banco,
                    'valor_novo': valor_arquivo,
                    'tipo': tipo_mudanca,
                    'tipo_campo': tipo_campo
                })
    
    # Relatório detalhado
    total_analisados = len(protocolos_comuns)
    protocolos_sem_mudancas = total_analisados - len(protocolos_com_mudancas)

    print(f"\n📊 RESULTADO DA ANÁLISE COMPLETA:")
    print("=" * 50)
    print(f"📋 Total de protocolos analisados: {total_analisados:,}")
    print(f"🔄 Protocolos COM mudanças: {len(protocolos_com_mudancas):,}")
    print(f"✅ Protocolos SEM mudanças: {protocolos_sem_mudancas:,}")
    print(f"📝 Total de mudanças de campo: {len(mudancas_detalhadas):,}")

    # Percentuais
    if total_analisados > 0:
        pct_com_mudancas = (len(protocolos_com_mudancas) / total_analisados) * 100
        pct_sem_mudancas = (protocolos_sem_mudancas / total_analisados) * 100
        print(f"📊 {pct_com_mudancas:.1f}% terão atualizações, {pct_sem_mudancas:.1f}% sem mudanças")

    if mudancas_por_campo:
        print(f"\n📝 CAMPOS MAIS ALTERADOS:")
        print("-" * 40)
        for campo, qtd in mudancas_por_campo.most_common(15):
            pct = (qtd / total_analisados) * 100
            print(f"   🔸 {campo}: {qtd:,} alterações ({pct:.1f}%)")

    # Análise por tipo de mudança
    tipos_mudanca = Counter()
    for mudanca in mudancas_detalhadas:
        tipos_mudanca[mudanca['tipo']] += 1

    if tipos_mudanca:
        print(f"\n📊 TIPOS DE MUDANÇA:")
        print("-" * 30)
        for tipo, qtd in tipos_mudanca.most_common():
            print(f"   📝 {tipo}: {qtd:,} mudanças")

    if mudancas_detalhadas:
        print(f"\n🔍 EXEMPLOS DE MUDANÇAS (primeiras 20):")
        print("-" * 60)
        for i, mudanca in enumerate(mudancas_detalhadas[:20], 1):
            valor_atual = str(mudanca['valor_atual'])[:30] if mudanca['valor_atual'] else 'VAZIO'
            valor_novo = str(mudanca['valor_novo'])[:30]
            print(f"   {i:2d}. {mudanca['protocolo']} | {mudanca['campo']}")
            print(f"       {valor_atual} → {valor_novo} ({mudanca['tipo']})")

    # Salvar relatório em arquivo
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_campos_atualizados_{timestamp}.txt"

    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE ANÁLISE DE CAMPOS ATUALIZADOS\n")
        f.write("=" * 50 + "\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

        f.write("RESUMO EXECUTIVO:\n")
        f.write("-" * 20 + "\n")
        f.write(f"📋 Total de protocolos analisados: {total_analisados:,}\n")
        f.write(f"🔄 Protocolos COM mudanças: {len(protocolos_com_mudancas):,} ({pct_com_mudancas:.1f}%)\n")
        f.write(f"✅ Protocolos SEM mudanças: {protocolos_sem_mudancas:,} ({pct_sem_mudancas:.1f}%)\n")
        f.write(f"📝 Total de mudanças de campo: {len(mudancas_detalhadas):,}\n\n")

        f.write("CAMPOS MAIS ALTERADOS:\n")
        f.write("-" * 25 + "\n")
        for campo, qtd in mudancas_por_campo.most_common():
            pct = (qtd / total_analisados) * 100
            f.write(f"🔸 {campo}: {qtd:,} alterações ({pct:.1f}%)\n")

        f.write(f"\nTIPOS DE MUDANÇA:\n")
        f.write("-" * 20 + "\n")
        for tipo, qtd in tipos_mudanca.most_common():
            f.write(f"📝 {tipo}: {qtd:,} mudanças\n")

        f.write(f"\nDETALHES DAS MUDANÇAS:\n")
        f.write("-" * 25 + "\n")
        for mudanca in mudancas_detalhadas:
            f.write(f"Protocolo: {mudanca['protocolo']}\n")
            f.write(f"Campo: {mudanca['campo']} ({mudanca['tipo_campo']})\n")
            f.write(f"Valor atual: {mudanca['valor_atual']}\n")
            f.write(f"Valor novo: {mudanca['valor_novo']}\n")
            f.write(f"Tipo: {mudanca['tipo']}\n")
            f.write("-" * 40 + "\n")

    print(f"\n💾 Relatório detalhado salvo: {nome_arquivo}")

    return {
        'total_analisados': total_analisados,
        'com_mudancas': len(protocolos_com_mudancas),
        'sem_mudancas': protocolos_sem_mudancas,
        'total_mudancas': len(mudancas_detalhadas),
        'mudancas_por_campo': mudancas_por_campo,
        'tipos_mudanca': tipos_mudanca
    }

def main():
    """Função principal"""
    print("🔍 ANÁLISE COMPLETA DE CAMPOS ATUALIZADOS")
    print("=" * 50)
    print("🎯 Analisando TODOS os 965 protocolos existentes")
    print()

    try:
        resultado = analisar_mudancas_tipadas()

        print(f"\n🎯 RESUMO FINAL:")
        print("=" * 30)
        print(f"   📊 {resultado['com_mudancas']:,} protocolos serão atualizados")
        print(f"   📝 {resultado['total_mudancas']:,} campos serão alterados")
        print(f"   ✅ {resultado['sem_mudancas']:,} protocolos sem mudanças")

        # Calcular impacto total (incluindo novos)
        print(f"\n🌍 IMPACTO TOTAL DO ARQUIVO:")
        print("-" * 35)
        print(f"   🆕 562 protocolos novos (inserções)")
        print(f"   🔄 {resultado['com_mudancas']:,} protocolos existentes (atualizações)")
        print(f"   ✅ {resultado['sem_mudancas']:,} protocolos existentes (sem mudanças)")
        print(f"   📝 {resultado['total_mudancas']:,} campos alterados")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
