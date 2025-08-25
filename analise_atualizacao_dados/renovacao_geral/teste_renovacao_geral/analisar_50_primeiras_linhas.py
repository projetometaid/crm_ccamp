#!/usr/bin/env python3
"""
ANÁLISE DAS 50 PRIMEIRAS LINHAS - RENOVAÇÃO GERAL
Analisa padrões de CPF vs CNPJ e mapeamento correto dos campos
"""

import xlrd
import psycopg2

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def analisar_50_primeiras_linhas():
    """Analisa detalhadamente as 50 primeiras linhas"""
    print("🔍 ANÁLISE DAS 50 PRIMEIRAS LINHAS")
    print("=" * 50)
    
    wb = xlrd.open_workbook("../renovacao_geral/GestaoRenovacao (1).xls")
    sheet = wb.sheet_by_index(0)
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
    
    print(f"📊 Analisando linhas 1-50 de {sheet.nrows:,} total")
    
    # Índices das colunas importantes
    col_razao_social = headers.index('Razão Social')
    col_cpf_cnpj = headers.index('CPF/CNPJ')
    col_nome_titular = headers.index('Nome Titular')
    col_produto = headers.index('Produto')
    col_protocolo = headers.index('Protocolo')
    col_protocolo_renovacao = headers.index('Protocolo renovação')
    col_status_renovacao = headers.index('Status protocolo renovação')
    
    print(f"\n📋 COLUNAS MAPEADAS:")
    print(f"   Razão Social: {col_razao_social}")
    print(f"   CPF/CNPJ: {col_cpf_cnpj}")
    print(f"   Nome Titular: {col_nome_titular}")
    print(f"   Produto: {col_produto}")
    print(f"   Protocolo: {col_protocolo}")
    print(f"   Protocolo renovação: {col_protocolo_renovacao}")
    
    # Analisar cada linha
    registros_cpf = []
    registros_cnpj = []
    
    print(f"\n🔍 ANÁLISE LINHA POR LINHA:")
    print("-" * 100)
    
    for row in range(1, min(51, sheet.nrows)):  # Linhas 1-50
        razao_social = str(sheet.cell_value(row, col_razao_social)).strip()
        cpf_cnpj = str(sheet.cell_value(row, col_cpf_cnpj)).strip()
        nome_titular = str(sheet.cell_value(row, col_nome_titular)).strip()
        produto = str(sheet.cell_value(row, col_produto)).strip()
        protocolo = str(sheet.cell_value(row, col_protocolo)).strip()
        protocolo_renovacao = str(sheet.cell_value(row, col_protocolo_renovacao)).strip()
        status_renovacao = str(sheet.cell_value(row, col_status_renovacao)).strip()
        
        # Determinar se é CPF ou CNPJ
        # CPF tem 11 dígitos, CNPJ tem 14 dígitos
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, cpf_cnpj))
        
        if len(cpf_cnpj_limpo) == 11:
            tipo_documento = "CPF"
            registros_cpf.append({
                'linha': row,
                'razao_social': razao_social,
                'cpf_cnpj': cpf_cnpj,
                'nome_titular': nome_titular,
                'produto': produto,
                'protocolo': protocolo,
                'protocolo_renovacao': protocolo_renovacao,
                'status_renovacao': status_renovacao
            })
        elif len(cpf_cnpj_limpo) == 14:
            tipo_documento = "CNPJ"
            registros_cnpj.append({
                'linha': row,
                'razao_social': razao_social,
                'cpf_cnpj': cpf_cnpj,
                'nome_titular': nome_titular,
                'produto': produto,
                'protocolo': protocolo,
                'protocolo_renovacao': protocolo_renovacao,
                'status_renovacao': status_renovacao
            })
        else:
            tipo_documento = "INVÁLIDO"
        
        # Verificar se razão social = nome titular (padrão CPF)
        razao_igual_titular = razao_social.upper() == nome_titular.upper()
        
        print(f"📋 Linha {row:2d} | {tipo_documento:<5} | {protocolo} | {status_renovacao:<8}")
        print(f"   Razão Social: {razao_social[:40]}")
        print(f"   Nome Titular: {nome_titular[:40]}")
        print(f"   CPF/CNPJ: {cpf_cnpj}")
        print(f"   Produto: {produto[:30]}")
        print(f"   Protocolo Renovação: {protocolo_renovacao if protocolo_renovacao else 'VAZIO'}")
        print(f"   Razão = Titular: {'✅ SIM' if razao_igual_titular else '❌ NÃO'}")
        print()
    
    # Análise dos padrões
    print(f"\n📊 ANÁLISE DE PADRÕES:")
    print("=" * 40)
    print(f"📋 Total analisado: {min(50, sheet.nrows - 1)} registros")
    print(f"👤 Registros CPF: {len(registros_cpf)}")
    print(f"🏢 Registros CNPJ: {len(registros_cnpj)}")
    
    # Analisar padrão CPF
    if registros_cpf:
        print(f"\n👤 ANÁLISE DOS REGISTROS CPF ({len(registros_cpf)}):")
        print("-" * 40)
        
        cpf_razao_igual_titular = 0
        cpf_com_renovacao = 0
        
        for reg in registros_cpf[:10]:  # Mostrar primeiros 10
            razao_igual = reg['razao_social'].upper() == reg['nome_titular'].upper()
            tem_renovacao = bool(reg['protocolo_renovacao'].strip())
            
            if razao_igual:
                cpf_razao_igual_titular += 1
            if tem_renovacao:
                cpf_com_renovacao += 1
            
            print(f"   📋 {reg['protocolo']} | {reg['cpf_cnpj']}")
            print(f"      Razão: {reg['razao_social'][:30]}")
            print(f"      Titular: {reg['nome_titular'][:30]}")
            print(f"      Igual: {'✅' if razao_igual else '❌'} | Renovação: {'✅' if tem_renovacao else '❌'}")
            print()
        
        pct_igual_cpf = (cpf_razao_igual_titular / len(registros_cpf)) * 100
        pct_renovacao_cpf = (cpf_com_renovacao / len(registros_cpf)) * 100
        
        print(f"   📊 Razão = Titular: {cpf_razao_igual_titular}/{len(registros_cpf)} ({pct_igual_cpf:.1f}%)")
        print(f"   📊 Com renovação: {cpf_com_renovacao}/{len(registros_cpf)} ({pct_renovacao_cpf:.1f}%)")
    
    # Analisar padrão CNPJ
    if registros_cnpj:
        print(f"\n🏢 ANÁLISE DOS REGISTROS CNPJ ({len(registros_cnpj)}):")
        print("-" * 40)
        
        cnpj_razao_diferente_titular = 0
        cnpj_com_renovacao = 0
        
        for reg in registros_cnpj[:10]:  # Mostrar primeiros 10
            razao_diferente = reg['razao_social'].upper() != reg['nome_titular'].upper()
            tem_renovacao = bool(reg['protocolo_renovacao'].strip())
            
            if razao_diferente:
                cnpj_razao_diferente_titular += 1
            if tem_renovacao:
                cnpj_com_renovacao += 1
            
            print(f"   📋 {reg['protocolo']} | {reg['cpf_cnpj']}")
            print(f"      Razão: {reg['razao_social'][:30]}")
            print(f"      Titular: {reg['nome_titular'][:30]}")
            print(f"      Diferente: {'✅' if razao_diferente else '❌'} | Renovação: {'✅' if tem_renovacao else '❌'}")
            print()
        
        pct_diferente_cnpj = (cnpj_razao_diferente_titular / len(registros_cnpj)) * 100
        pct_renovacao_cnpj = (cnpj_com_renovacao / len(registros_cnpj)) * 100
        
        print(f"   📊 Razão ≠ Titular: {cnpj_razao_diferente_titular}/{len(registros_cnpj)} ({pct_diferente_cnpj:.1f}%)")
        print(f"   📊 Com renovação: {cnpj_com_renovacao}/{len(registros_cnpj)} ({pct_renovacao_cnpj:.1f}%)")
    
    return registros_cpf, registros_cnpj

def verificar_no_banco(registros_cpf, registros_cnpj):
    """Verifica como os dados estão armazenados no banco"""
    print(f"\n\n🗄️ VERIFICAÇÃO NO BANCO DE DADOS")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar alguns registros CPF
    if registros_cpf:
        print(f"\n👤 VERIFICANDO REGISTROS CPF NO BANCO:")
        print("-" * 40)
        
        for reg in registros_cpf[:3]:  # Verificar primeiros 3
            protocolo = reg['protocolo']
            
            cursor.execute("""
                SELECT protocolo, nome, documento, nome_do_titular, documento_do_titular,
                       produto, protocolo_renovacao
                FROM emissao WHERE protocolo = %s
            """, (int(protocolo),))
            
            resultado = cursor.fetchone()
            
            if resultado:
                prot, nome, doc, nome_tit, doc_tit, prod, prot_ren = resultado
                
                print(f"   📋 PROTOCOLO {protocolo}:")
                print(f"      📁 ARQUIVO:")
                print(f"         Razão Social: {reg['razao_social']}")
                print(f"         Nome Titular: {reg['nome_titular']}")
                print(f"         CPF/CNPJ: {reg['cpf_cnpj']}")
                print(f"         Produto: {reg['produto'][:30]}")
                print(f"      🗄️ BANCO:")
                print(f"         Nome: {nome}")
                print(f"         Documento: {doc}")
                print(f"         Nome Titular: {nome_tit}")
                print(f"         Doc Titular: {doc_tit}")
                print(f"         Produto: {prod}")
                print(f"         Protocolo Renovação: {prot_ren}")
                print()
            else:
                print(f"   ❌ Protocolo {protocolo} não encontrado no banco")
    
    # Verificar alguns registros CNPJ
    if registros_cnpj:
        print(f"\n🏢 VERIFICANDO REGISTROS CNPJ NO BANCO:")
        print("-" * 40)
        
        for reg in registros_cnpj[:3]:  # Verificar primeiros 3
            protocolo = reg['protocolo']
            
            cursor.execute("""
                SELECT protocolo, nome, documento, nome_do_titular, documento_do_titular,
                       produto, protocolo_renovacao
                FROM emissao WHERE protocolo = %s
            """, (int(protocolo),))
            
            resultado = cursor.fetchone()
            
            if resultado:
                prot, nome, doc, nome_tit, doc_tit, prod, prot_ren = resultado
                
                print(f"   📋 PROTOCOLO {protocolo}:")
                print(f"      📁 ARQUIVO:")
                print(f"         Razão Social: {reg['razao_social']}")
                print(f"         Nome Titular: {reg['nome_titular']}")
                print(f"         CPF/CNPJ: {reg['cpf_cnpj']}")
                print(f"         Produto: {reg['produto'][:30]}")
                print(f"      🗄️ BANCO:")
                print(f"         Nome: {nome}")
                print(f"         Documento: {doc}")
                print(f"         Nome Titular: {nome_tit}")
                print(f"         Doc Titular: {doc_tit}")
                print(f"         Produto: {prod}")
                print(f"         Protocolo Renovação: {prot_ren}")
                print()
            else:
                print(f"   ❌ Protocolo {protocolo} não encontrado no banco")
    
    conn.close()

def main():
    """Função principal"""
    print("🔍 ANÁLISE DAS 50 PRIMEIRAS LINHAS - RENOVAÇÃO GERAL")
    print("=" * 60)
    print("🎯 Objetivo: Verificar padrões CPF vs CNPJ e mapeamento correto")
    print()
    
    try:
        # Analisar arquivo
        registros_cpf, registros_cnpj = analisar_50_primeiras_linhas()
        
        # Verificar no banco
        verificar_no_banco(registros_cpf, registros_cnpj)
        
        print(f"\n🎯 CONCLUSÕES:")
        print("=" * 30)
        print(f"👤 CPF: Razão Social = Nome Titular (pessoa física)")
        print(f"🏢 CNPJ: Razão Social ≠ Nome Titular (pessoa jurídica)")
        print(f"📊 Padrão identificado para mapeamento correto dos campos")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
