#!/usr/bin/env python3
"""
ANÁLISE DOS 74 CAMPOS DA TABELA EMISSAO
Gera relatório completo de todos os campos do banco
"""

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

def analisar_estrutura_completa():
    """Analisa estrutura completa da tabela emissao"""
    print("🔍 ANALISANDO ESTRUTURA COMPLETA DA TABELA EMISSAO")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Obter estrutura completa
    cursor.execute("""
        SELECT 
            ordinal_position,
            column_name, 
            data_type, 
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        ORDER BY ordinal_position
    """)
    
    colunas = cursor.fetchall()
    
    print(f"📊 TOTAL DE CAMPOS: {len(colunas)}")
    print()
    
    # Gerar relatório detalhado
    relatorio = []
    relatorio.append("# 📊 Estrutura Completa da Tabela EMISSAO")
    relatorio.append("")
    relatorio.append(f"## 📋 Resumo")
    relatorio.append(f"- **Total de campos:** {len(colunas)}")
    relatorio.append(f"- **Tabela:** `emissao`")
    relatorio.append(f"- **Banco:** `crm_ccamp`")
    relatorio.append("")
    
    # Agrupar por tipos
    tipos_campos = {}
    for pos, col_name, data_type, max_length, precision, scale, nullable, default in colunas:
        if data_type not in tipos_campos:
            tipos_campos[data_type] = []
        tipos_campos[data_type].append(col_name)
    
    relatorio.append("## 📊 Distribuição por Tipos")
    relatorio.append("")
    for tipo, campos in sorted(tipos_campos.items()):
        relatorio.append(f"- **{tipo}:** {len(campos)} campos")
    relatorio.append("")
    
    # Lista completa de campos
    relatorio.append("## 📋 Lista Completa dos Campos")
    relatorio.append("")
    relatorio.append("| # | Campo | Tipo | Tamanho | NULL | Default |")
    relatorio.append("|---|-------|------|---------|------|---------|")
    
    for pos, col_name, data_type, max_length, precision, scale, nullable, default in colunas:
        # Formatar tamanho
        if max_length:
            tamanho = str(max_length)
        elif precision and scale:
            tamanho = f"{precision},{scale}"
        elif precision:
            tamanho = str(precision)
        else:
            tamanho = "-"
        
        # Formatar nullable
        null_str = "✅" if nullable == "YES" else "❌"
        
        # Formatar default
        default_str = str(default)[:20] if default else "-"
        
        relatorio.append(f"| {pos} | `{col_name}` | {data_type} | {tamanho} | {null_str} | {default_str} |")
    
    relatorio.append("")
    
    # Campos por categoria
    relatorio.append("## 🏷️ Campos por Categoria")
    relatorio.append("")
    
    # Identificação
    campos_id = [col for pos, col, *_ in colunas if any(x in col.lower() for x in ['id', 'protocolo', 'codigo'])]
    relatorio.append(f"### 🔑 Identificação ({len(campos_id)} campos)")
    for campo in campos_id:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Dados pessoais
    campos_pessoais = [col for pos, col, *_ in colunas if any(x in col.lower() for x in ['nome', 'documento', 'cpf', 'cnpj', 'email', 'telefone'])]
    relatorio.append(f"### 👤 Dados Pessoais ({len(campos_pessoais)} campos)")
    for campo in campos_pessoais:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Datas
    campos_datas = [col for pos, col, *_ in colunas if 'data' in col.lower()]
    relatorio.append(f"### 📅 Datas ({len(campos_datas)} campos)")
    for campo in campos_datas:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Valores
    campos_valores = [col for pos, col, *_ in colunas if any(x in col.lower() for x in ['valor', 'preco', 'custo'])]
    relatorio.append(f"### 💰 Valores ({len(campos_valores)} campos)")
    for campo in campos_valores:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Status e controle
    campos_status = [col for pos, col, *_ in colunas if any(x in col.lower() for x in ['status', 'situacao', 'ativo'])]
    relatorio.append(f"### 📊 Status e Controle ({len(campos_status)} campos)")
    for campo in campos_status:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Certificado
    campos_cert = [col for pos, col, *_ in colunas if any(x in col.lower() for x in ['certificado', 'validade', 'emissao', 'produto'])]
    relatorio.append(f"### 🏆 Certificado ({len(campos_cert)} campos)")
    for campo in campos_cert:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Outros
    todos_categorizados = set(campos_id + campos_pessoais + campos_datas + campos_valores + campos_status + campos_cert)
    campos_outros = [col for pos, col, *_ in colunas if col not in todos_categorizados]
    relatorio.append(f"### 📋 Outros ({len(campos_outros)} campos)")
    for campo in campos_outros:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Análise de constraints
    relatorio.append("## 🔒 Análise de Constraints")
    relatorio.append("")
    
    # Campos obrigatórios
    campos_obrigatorios = [col for pos, col, *_, nullable, default in colunas if nullable == "NO"]
    relatorio.append(f"### ❌ Campos Obrigatórios (NOT NULL) - {len(campos_obrigatorios)} campos")
    for campo in campos_obrigatorios:
        relatorio.append(f"- `{campo}`")
    relatorio.append("")
    
    # Campos com default
    campos_default = [col for pos, col, *_, nullable, default in colunas if default is not None]
    relatorio.append(f"### 🔧 Campos com Default - {len(campos_default)} campos")
    for pos, col, *_, nullable, default in colunas:
        if default is not None:
            relatorio.append(f"- `{col}`: {default}")
    relatorio.append("")
    
    conn.close()
    
    return relatorio

def salvar_relatorio(relatorio):
    """Salva relatório no README"""
    print("💾 SALVANDO RELATÓRIO NO README")
    print("=" * 40)
    
    # Ler README atual
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme_atual = f.read()
    except:
        readme_atual = ""
    
    # Adicionar relatório
    novo_readme = readme_atual + "\n\n" + "\n".join(relatorio)
    
    # Salvar
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(novo_readme)
    
    print(f"✅ Relatório adicionado ao README.md")
    print(f"📊 {len(relatorio)} linhas adicionadas")

def main():
    """Função principal"""
    print("🔍 ANÁLISE DOS 74 CAMPOS DA TABELA EMISSAO")
    print("=" * 60)
    print("🎯 Objetivo: Gerar relatório completo para o README")
    print()
    
    try:
        # Analisar estrutura
        relatorio = analisar_estrutura_completa()
        
        # Salvar no README
        salvar_relatorio(relatorio)
        
        print(f"\n🎉 RELATÓRIO GERADO COM SUCESSO!")
        print("=" * 40)
        print(f"📁 Arquivo: README.md")
        print(f"📊 Estrutura completa da tabela emissao documentada")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
