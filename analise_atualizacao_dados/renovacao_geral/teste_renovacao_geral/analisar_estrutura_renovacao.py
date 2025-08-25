#!/usr/bin/env python3
"""
ANÁLISE DE ESTRUTURA - RENOVAÇÃO GERAL
Analisa estrutura do arquivo e tipos de dados no banco
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

def analisar_estrutura_arquivo():
    """Analisa estrutura completa do arquivo Excel"""
    print("📖 ANALISANDO ESTRUTURA DO ARQUIVO RENOVAÇÃO")
    print("=" * 50)
    
    wb = xlrd.open_workbook("../renovacao_geral/GestaoRenovacao (1).xls")
    sheet = wb.sheet_by_index(0)
    
    print(f"📊 Arquivo: {sheet.nrows:,} linhas x {sheet.ncols} colunas")
    
    # Analisar todos os cabeçalhos
    print(f"\n📋 TODAS AS COLUNAS DO ARQUIVO:")
    print("-" * 60)
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
        print(f"   {col:2d}. {header}")
    
    # Identificar colunas de protocolo
    colunas_protocolo = []
    for i, header in enumerate(headers):
        if 'protocolo' in header.lower():
            colunas_protocolo.append((i, header))
    
    print(f"\n🔍 COLUNAS DE PROTOCOLO IDENTIFICADAS:")
    for col, nome in colunas_protocolo:
        print(f"   Coluna {col:2d}: {nome}")
    
    # Analisar dados das primeiras linhas
    print(f"\n🔍 ANÁLISE DAS PRIMEIRAS 10 LINHAS:")
    print("-" * 80)
    
    for row in range(1, min(11, sheet.nrows)):
        print(f"\n📋 LINHA {row}:")
        
        # Mostrar apenas colunas importantes
        colunas_importantes = [0, 1, 4, 5, 6, 7] + [col for col, _ in colunas_protocolo]
        
        for col in colunas_importantes:
            if col < sheet.ncols:
                header = headers[col]
                valor = sheet.cell_value(row, col)
                tipo = type(valor).__name__
                
                # Formatar valor para exibição
                if isinstance(valor, str):
                    valor_display = f"'{valor[:30]}'" if len(str(valor)) > 30 else f"'{valor}'"
                elif isinstance(valor, float) and valor.is_integer():
                    valor_display = f"{int(valor)}"
                else:
                    valor_display = str(valor)
                
                print(f"   {header:<25}: {valor_display} ({tipo})")
    
    # Analisar especificamente as colunas de protocolo
    if colunas_protocolo:
        print(f"\n🔍 ANÁLISE DETALHADA DAS COLUNAS DE PROTOCOLO:")
        print("-" * 60)
        
        for col, nome in colunas_protocolo:
            print(f"\n📋 {nome} (Coluna {col}):")
            
            valores_vazios = 0
            valores_preenchidos = 0
            exemplos_preenchidos = []
            exemplos_vazios = []
            
            for row in range(1, min(101, sheet.nrows)):  # Analisar primeiras 100 linhas
                valor = sheet.cell_value(row, col)
                
                if valor and str(valor).strip():
                    valores_preenchidos += 1
                    if len(exemplos_preenchidos) < 5:
                        exemplos_preenchidos.append((row, valor))
                else:
                    valores_vazios += 1
                    if len(exemplos_vazios) < 5:
                        exemplos_vazios.append(row)
            
            total_analisado = min(100, sheet.nrows - 1)
            pct_preenchidos = (valores_preenchidos / total_analisado) * 100
            pct_vazios = (valores_vazios / total_analisado) * 100
            
            print(f"   📊 Preenchidos: {valores_preenchidos}/{total_analisado} ({pct_preenchidos:.1f}%)")
            print(f"   📊 Vazios: {valores_vazios}/{total_analisado} ({pct_vazios:.1f}%)")
            
            if exemplos_preenchidos:
                print(f"   ✅ Exemplos preenchidos:")
                for linha, valor in exemplos_preenchidos:
                    print(f"      Linha {linha}: {valor}")
            
            if exemplos_vazios:
                print(f"   ⚪ Exemplos vazios (linhas): {exemplos_vazios}")
    
    return headers, colunas_protocolo

def analisar_tipos_banco():
    """Analisa tipos de dados da tabela emissao no banco"""
    print(f"\n\n🗄️ ANALISANDO TIPOS DE DADOS NO BANCO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar estrutura da tabela emissao
    cursor.execute("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        ORDER BY ordinal_position
    """)
    
    colunas_info = cursor.fetchall()
    
    print(f"📊 ESTRUTURA DA TABELA EMISSAO:")
    print("-" * 80)
    print(f"{'COLUNA':<30} {'TIPO':<15} {'TAMANHO':<10} {'NULL':<8} {'DEFAULT':<15}")
    print("-" * 80)
    
    for col_name, data_type, max_length, nullable, default in colunas_info:
        tamanho = str(max_length) if max_length else '-'
        null_ok = 'YES' if nullable == 'YES' else 'NO'
        default_val = str(default)[:12] if default else '-'
        print(f'{col_name:<30} {data_type:<15} {tamanho:<10} {null_ok:<8} {default_val:<15}')
    
    # Verificar alguns dados reais para entender os tipos
    print(f"\n🔍 VERIFICANDO DADOS REAIS (protocolo 1006315733):")
    cursor.execute("""
        SELECT protocolo, nome, documento, nome_do_titular, documento_do_titular,
               produto, data_inicio_validade, data_fim_validade,
               status_do_certificado, valor_do_boleto, protocolo_renovacao
        FROM emissao
        WHERE protocolo = 1006315733
    """)
    
    registro = cursor.fetchone()
    if registro:
        campos = ['protocolo', 'nome', 'documento', 'nome_do_titular', 'documento_do_titular',
                  'produto', 'data_inicio_validade', 'data_fim_validade',
                  'status_do_certificado', 'valor_do_boleto', 'protocolo_renovacao']
        
        print("-" * 70)
        for i, (campo, valor) in enumerate(zip(campos, registro)):
            tipo_python = type(valor).__name__
            valor_str = str(valor)[:40] if valor else 'NULL'
            print(f'{campo:<30} {tipo_python:<12} {valor_str}')
    else:
        print("❌ Protocolo não encontrado no banco")
    
    conn.close()
    
    return colunas_info

def mapear_colunas_arquivo_banco(headers):
    """Mapeia colunas do arquivo para colunas do banco"""
    print(f"\n\n🔗 MAPEAMENTO ARQUIVO → BANCO")
    print("=" * 50)
    
    # Mapeamento baseado nos nomes das colunas
    mapeamento_possivel = {
        'Razão Social': 'razao_social',
        'CPF/CNPJ': 'cpf_cnpj', 
        'Telefone': 'telefone',
        'E-mail': 'email',
        'Produto': 'produto',
        'Nome Titular': 'nome_titular',
        'Data Início Validade': 'data_inicio_validade',
        'Data Fim Validade': 'data_fim_validade',
        'Prazo': 'prazo',
        'AR Solicitação': 'ar_solicitacao',
        'Protocolo': 'protocolo',
        'Status do Certificado': 'status_do_certificado',
        'Valor do Boleto': 'valor_do_boleto'
    }
    
    mapeamento_encontrado = {}
    colunas_nao_mapeadas = []
    
    print(f"📋 MAPEAMENTO IDENTIFICADO:")
    print("-" * 40)
    
    for header in headers:
        if header in mapeamento_possivel:
            coluna_banco = mapeamento_possivel[header]
            mapeamento_encontrado[header] = coluna_banco
            print(f"   ✅ {header:<25} → {coluna_banco}")
        else:
            colunas_nao_mapeadas.append(header)
    
    if colunas_nao_mapeadas:
        print(f"\n📋 COLUNAS NÃO MAPEADAS:")
        print("-" * 30)
        for header in colunas_nao_mapeadas:
            print(f"   ❓ {header}")
    
    print(f"\n📊 RESUMO:")
    print(f"   ✅ Mapeadas: {len(mapeamento_encontrado)}")
    print(f"   ❓ Não mapeadas: {len(colunas_nao_mapeadas)}")
    
    return mapeamento_encontrado

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE ESTRUTURA - RENOVAÇÃO GERAL")
    print("=" * 60)
    print("🎯 Objetivo: Entender estrutura do arquivo e tipos do banco")
    print()
    
    try:
        # Analisar arquivo
        headers, colunas_protocolo = analisar_estrutura_arquivo()
        
        # Analisar banco
        colunas_banco = analisar_tipos_banco()
        
        # Mapear colunas
        mapeamento = mapear_colunas_arquivo_banco(headers)
        
        print(f"\n🎯 CONCLUSÕES PRELIMINARES:")
        print("=" * 40)
        print(f"📁 Arquivo tem {len(headers)} colunas")
        print(f"🗄️ Banco tem {len(colunas_banco)} colunas")
        print(f"🔗 {len(mapeamento)} colunas mapeadas")
        print(f"📋 {len(colunas_protocolo)} colunas de protocolo identificadas")
        
        if len(colunas_protocolo) > 1:
            print(f"\n⚠️ ATENÇÃO: Múltiplas colunas de protocolo!")
            print(f"   Isso confirma a lógica de renovação:")
            print(f"   - Protocolo original (a ser renovado)")
            print(f"   - Protocolo novo (renovação gerada)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
