#!/usr/bin/env python3
"""
ANÁLISE FINAL SAFEID - VERIFICAÇÃO COMPLETA
Verifica TODOS os campos do SafeID para confirmar quais realmente precisam ser atualizados
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

def ler_arquivo_safeid_completo():
    """Lê TODOS os dados do arquivo SafeID"""
    print("📖 LENDO ARQUIVO SAFEID COMPLETO")
    print("=" * 40)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    # Obter cabeçalhos
    headers = []
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
    
    print(f"📊 Arquivo: {sheet.nrows-1} linhas x {sheet.ncols} colunas")
    
    # Ler primeiros 20 registros para análise
    registros = []
    for row in range(1, min(21, sheet.nrows)):
        registro = {}
        for col, header in enumerate(headers):
            valor = sheet.cell_value(row, col)
            if isinstance(valor, str):
                valor = valor.strip()
            elif isinstance(valor, float) and valor.is_integer():
                valor = str(int(valor))
            else:
                valor = str(valor) if valor else ''
            
            registro[header] = valor
        registros.append(registro)
    
    print(f"✅ Carregados {len(registros)} registros para análise")
    
    return headers, registros

def verificar_todos_campos_banco(protocolos_amostra):
    """Verifica TODOS os campos possíveis no banco para os protocolos SafeID"""
    print(f"\n🔍 VERIFICANDO TODOS OS CAMPOS NO BANCO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar TODOS os campos de um protocolo SafeID
    protocolo_teste = protocolos_amostra[0]
    
    cursor.execute("SELECT * FROM emissao WHERE protocolo = %s", (int(protocolo_teste),))
    registro = cursor.fetchone()
    
    # Obter nomes das colunas
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        ORDER BY ordinal_position
    """)
    colunas_banco = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Total de colunas no banco: {len(colunas_banco)}")
    
    # Mostrar apenas campos preenchidos para protocolo SafeID
    print(f"\n📋 CAMPOS PREENCHIDOS NO PROTOCOLO {protocolo_teste}:")
    print("-" * 60)
    
    campos_preenchidos = []
    for i, (coluna, valor) in enumerate(zip(colunas_banco, registro)):
        if valor is not None and str(valor).strip():
            valor_str = str(valor)[:40] if len(str(valor)) > 40 else str(valor)
            print(f"   {coluna:<35}: {valor_str}")
            campos_preenchidos.append(coluna)
    
    print(f"\n📊 Campos preenchidos: {len(campos_preenchidos)}/{len(colunas_banco)}")
    
    conn.close()
    
    return colunas_banco, campos_preenchidos

def mapear_arquivo_para_banco_completo(headers, colunas_banco):
    """Mapeia TODOS os campos do arquivo para o banco"""
    print(f"\n🔗 MAPEAMENTO COMPLETO ARQUIVO → BANCO")
    print("=" * 60)
    
    # Mapeamento completo possível
    mapeamento_completo = {
        'Protocolo': 'protocolo',
        'Documento': 'documento',
        'Nome / Razão Social': 'nome',
        'Autoridade de Registro Venda': 'nome_da_autoridade_de_registro',
        'Data de Pagamento': None,  # Não existe campo específico
        'VoucherCodigo': 'vouchercodigo',
        'VoucherPercentual': 'voucherpercentual',
        'VoucherValor': 'vouchervalor',
        'Valor Pagamento': 'valor_do_boleto',
        'Descrição Produto': 'produto',
        'Validade Certificado': 'validade',
        'Período de Uso': 'periodo_de_uso',
        'Data Início do Uso': 'data_inicio_validade',
        'Data Fim do Uso': 'data_fim_validade',
        'Status do Certificado': 'status_do_certificado',
        'Data de Revogação': 'data_de_revogacao',
        'Código de Revogação': 'codigo_revogacao',
        'Descrição da Revogação': 'descricao_revogacao',
        'CNPJ do parceiro': None,  # Não existe campo específico
        'Nome do parceiro': 'nome_do_parceiro',
        'CPF do contador': None,  # Não existe campo específico
        'Consultor comercial': 'nome_contato_comercial',
        'Primeira Emissão': None,  # Não existe campo específico
        'Código do catalogo': 'catalogo_do_contador_parceiro',
        'Data de Faturamento': None,  # Não existe campo específico
        'Nome Catalogo': 'nome_do_catalogo',
        'Email Titular': 'e_mail_do_titular',
        'Telefone Titular': 'telefone_do_titular',
        'Renovado': None,  # CAMPO PRINCIPAL - NÃO EXISTE
        'Status do Período de Uso': None  # Não existe campo específico
    }
    
    print(f"📋 MAPEAMENTO DETALHADO:")
    print("-" * 60)
    
    campos_mapeados = 0
    campos_nao_existem = 0
    campos_sem_mapeamento = 0
    
    for arquivo_col, banco_col in mapeamento_completo.items():
        if banco_col is None:
            if arquivo_col == 'Renovado':
                print(f"   🚨 {arquivo_col:<30} → ❌ CAMPO PRINCIPAL AUSENTE")
                campos_nao_existem += 1
            else:
                print(f"   ❓ {arquivo_col:<30} → ❌ SEM MAPEAMENTO")
                campos_sem_mapeamento += 1
        elif banco_col in colunas_banco:
            print(f"   ✅ {arquivo_col:<30} → {banco_col}")
            campos_mapeados += 1
        else:
            print(f"   ❌ {arquivo_col:<30} → {banco_col} (NÃO EXISTE)")
            campos_nao_existem += 1
    
    print(f"\n📊 RESUMO DO MAPEAMENTO:")
    print(f"   ✅ Campos mapeáveis: {campos_mapeados}")
    print(f"   ❌ Campos não existem: {campos_nao_existem}")
    print(f"   ❓ Sem mapeamento: {campos_sem_mapeamento}")
    print(f"   📊 Total: {len(headers)}")
    
    return campos_mapeados, campos_nao_existem, campos_sem_mapeamento

def comparar_dados_reais(registros_arquivo):
    """Compara dados reais do arquivo com banco"""
    print(f"\n🔍 COMPARAÇÃO DADOS REAIS (PRIMEIROS 5)")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    mudancas_por_protocolo = []
    
    for i, registro in enumerate(registros_arquivo[:5], 1):
        protocolo = registro['Protocolo']
        
        cursor.execute("""
            SELECT protocolo, nome, produto, status_do_certificado,
                   data_inicio_validade, data_fim_validade,
                   vouchercodigo, voucherpercentual, vouchervalor,
                   periodo_de_uso, e_mail_do_titular, telefone_do_titular
            FROM emissao WHERE protocolo = %s
        """, (int(protocolo),))
        
        resultado = cursor.fetchone()
        
        if resultado:
            prot, nome_banco, prod_banco, status_banco, \
            data_inicio_banco, data_fim_banco, voucher_cod_banco, \
            voucher_perc_banco, voucher_val_banco, periodo_banco, \
            email_banco, telefone_banco = resultado
            
            print(f"\n📋 {i}. PROTOCOLO {protocolo}:")
            
            mudancas = []
            
            # Verificar mudanças campo por campo
            if registro['Descrição Produto'] != str(prod_banco):
                mudancas.append(f"Produto: '{prod_banco}' → '{registro['Descrição Produto']}'")
            
            if registro['Status do Certificado'] != str(status_banco):
                mudancas.append(f"Status: '{status_banco}' → '{registro['Status do Certificado']}'")
            
            # VoucherPercentual
            voucher_perc_arquivo = registro['VoucherPercentual'].replace(',', '.') if registro['VoucherPercentual'] else '0'
            voucher_perc_banco_str = str(voucher_perc_banco) if voucher_perc_banco else '0'
            if voucher_perc_arquivo != voucher_perc_banco_str:
                mudancas.append(f"VoucherPercentual: '{voucher_perc_banco}' → '{voucher_perc_arquivo}'")
            
            # Datas
            if registro['Data Início do Uso'] and not data_inicio_banco:
                mudancas.append(f"Data Início: NULL → '{registro['Data Início do Uso']}'")
            
            if registro['Data Fim do Uso'] and not data_fim_banco:
                mudancas.append(f"Data Fim: NULL → '{registro['Data Fim do Uso']}'")
            
            # Campo Renovado (sempre mudança pois não existe)
            mudancas.append(f"Renovado: CAMPO_NOVO → '{registro['Renovado']}'")
            
            if mudancas:
                print(f"   🔄 MUDANÇAS ({len(mudancas)}):")
                for mudanca in mudancas:
                    print(f"      • {mudanca}")
                mudancas_por_protocolo.append(len(mudancas))
            else:
                print(f"   ✅ SEM MUDANÇAS")
                mudancas_por_protocolo.append(0)
        else:
            print(f"   ❌ Protocolo não encontrado")
    
    conn.close()
    
    return mudancas_por_protocolo

def main():
    """Função principal"""
    print("🔍 ANÁLISE FINAL SAFEID - VERIFICAÇÃO COMPLETA")
    print("=" * 70)
    print("🎯 Objetivo: Confirmar EXATAMENTE quantos campos precisam ser atualizados")
    print()
    
    try:
        # Ler arquivo completo
        headers, registros = ler_arquivo_safeid_completo()
        
        # Extrair protocolos para teste
        protocolos_amostra = [reg['Protocolo'] for reg in registros]
        
        # Verificar campos no banco
        colunas_banco, campos_preenchidos = verificar_todos_campos_banco(protocolos_amostra)
        
        # Mapear campos
        mapeados, nao_existem, sem_mapeamento = mapear_arquivo_para_banco_completo(headers, colunas_banco)
        
        # Comparar dados reais
        mudancas = comparar_dados_reais(registros)
        
        print(f"\n🎯 CONCLUSÃO FINAL:")
        print("=" * 40)
        print(f"📁 Arquivo SafeID: {len(headers)} colunas")
        print(f"🗄️ Banco: {len(colunas_banco)} colunas")
        print(f"✅ Campos mapeáveis: {mapeados}")
        print(f"❌ Campos não existem: {nao_existem}")
        print(f"❓ Sem mapeamento: {sem_mapeamento}")
        
        if mudancas:
            media_mudancas = sum(mudancas) / len(mudancas)
            print(f"\n📊 MUDANÇAS POR PROTOCOLO:")
            print(f"   Média: {media_mudancas:.1f} mudanças por protocolo")
            print(f"   Total estimado: {media_mudancas * 160:.0f} mudanças nos 160 protocolos")
        
        print(f"\n💡 RECOMENDAÇÃO:")
        if mapeados >= 10:
            print(f"   ✅ VALE A PENA ATUALIZAR - {mapeados} campos mapeáveis")
            print(f"   🔧 Criar campo 'renovado' e processar atualizações")
        else:
            print(f"   ⚠️ POUCOS CAMPOS MAPEÁVEIS - Avaliar necessidade")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
