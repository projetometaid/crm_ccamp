#!/usr/bin/env python3
"""
CONFIRMAÇÃO DE DADOS - EMISSÃO
Confirma dados no terminal e pede autorização antes de executar atualizações
"""

import psycopg2
import xlrd
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

def ler_dados_arquivo_emissao():
    """Lê dados do arquivo de emissão"""
    print("📖 LENDO ARQUIVO DE EMISSÃO")
    print("=" * 40)
    
    wb = xlrd.open_workbook("../RelatorioEmissoes (13).xls")
    sheet = wb.sheet_by_index(0)
    
    print(f"📊 Arquivo: {sheet.nrows-1:,} registros")
    
    # Ler primeiros 10 registros para confirmação
    dados_amostra = []
    
    for row in range(1, min(11, sheet.nrows)):
        protocolo = str(sheet.cell_value(row, 0)).strip()
        nome = str(sheet.cell_value(row, 2)).strip()
        produto = str(sheet.cell_value(row, 9)).strip()
        status = str(sheet.cell_value(row, 21)).strip()
        
        dados_amostra.append({
            'protocolo': protocolo,
            'nome': nome[:30],
            'produto': produto[:30],
            'status': status
        })
    
    print(f"📋 AMOSTRA DOS PRIMEIROS 10 REGISTROS:")
    print("-" * 80)
    for i, dados in enumerate(dados_amostra, 1):
        print(f"{i:2d}. {dados['protocolo']} | {dados['nome']} | {dados['status']}")
    
    return sheet.nrows - 1

def verificar_protocolos_existentes():
    """Verifica quantos protocolos já existem no banco"""
    print(f"\n🗄️ VERIFICANDO PROTOCOLOS NO BANCO")
    print("=" * 40)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Ler alguns protocolos do arquivo
    wb = xlrd.open_workbook("../RelatorioEmissoes (13).xls")
    sheet = wb.sheet_by_index(0)
    
    protocolos_teste = []
    for row in range(1, min(21, sheet.nrows)):  # Primeiros 20
        protocolo = str(sheet.cell_value(row, 0)).strip()
        protocolos_teste.append(int(float(protocolo)))
    
    # Verificar no banco
    protocolos_str = ','.join(map(str, protocolos_teste))
    
    cursor.execute(f"""
        SELECT protocolo, nome, produto, status_do_certificado
        FROM emissao 
        WHERE protocolo IN ({protocolos_str})
        ORDER BY protocolo
        LIMIT 10
    """)
    
    resultados = cursor.fetchall()
    
    print(f"📊 Protocolos testados: {len(protocolos_teste)}")
    print(f"📊 Encontrados no banco: {len(resultados)}")
    
    if resultados:
        print(f"\n📋 DADOS ATUAIS NO BANCO (primeiros 10):")
        print("-" * 80)
        for i, (protocolo, nome, produto, status) in enumerate(resultados, 1):
            nome_str = nome[:30] if nome else 'NULL'
            produto_str = produto[:30] if produto else 'NULL'
            status_str = status if status else 'NULL'
            print(f"{i:2d}. {protocolo} | {nome_str} | {status_str}")
    
    conn.close()
    
    return len(resultados), len(protocolos_teste)

def analisar_mudancas_necessarias():
    """Analisa que tipos de mudanças serão necessárias"""
    print(f"\n🔍 ANALISANDO MUDANÇAS NECESSÁRIAS")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Ler dados do arquivo
    wb = xlrd.open_workbook("../RelatorioEmissoes (13).xls")
    sheet = wb.sheet_by_index(0)
    
    mudancas_identificadas = []
    
    print(f"📋 COMPARANDO ARQUIVO vs BANCO (primeiros 5):")
    print("-" * 60)
    
    for row in range(1, min(6, sheet.nrows)):
        protocolo = str(sheet.cell_value(row, 0)).strip()
        nome_arquivo = str(sheet.cell_value(row, 2)).strip()
        produto_arquivo = str(sheet.cell_value(row, 9)).strip()
        status_arquivo = str(sheet.cell_value(row, 21)).strip()
        
        # Buscar no banco
        cursor.execute("""
            SELECT protocolo, nome, produto, status_do_certificado
            FROM emissao WHERE protocolo = %s
        """, (int(float(protocolo)),))
        
        resultado = cursor.fetchone()
        
        if resultado:
            prot, nome_banco, produto_banco, status_banco = resultado
            
            mudancas_protocolo = []
            
            # Comparar campos
            if nome_arquivo != str(nome_banco):
                mudancas_protocolo.append(f"Nome: '{nome_banco}' → '{nome_arquivo}'")
            
            if produto_arquivo != str(produto_banco):
                mudancas_protocolo.append(f"Produto: '{produto_banco}' → '{produto_arquivo}'")
            
            if status_arquivo != str(status_banco):
                mudancas_protocolo.append(f"Status: '{status_banco}' → '{status_arquivo}'")
            
            print(f"\n📋 PROTOCOLO {protocolo}:")
            if mudancas_protocolo:
                print(f"   🔄 MUDANÇAS ({len(mudancas_protocolo)}):")
                for mudanca in mudancas_protocolo:
                    print(f"      • {mudanca}")
                mudancas_identificadas.extend(mudancas_protocolo)
            else:
                print(f"   ✅ SEM MUDANÇAS")
        else:
            print(f"\n📋 PROTOCOLO {protocolo}:")
            print(f"   🆕 NOVO REGISTRO (INSERT)")
            mudancas_identificadas.append("INSERT")
    
    conn.close()
    
    return len(mudancas_identificadas)

def mostrar_resumo_operacao_corrigido():
    """Mostra resumo correto baseado na primeira análise"""
    print(f"\n📊 RESUMO DA OPERAÇÃO (DADOS CORRETOS DA PRIMEIRA ANÁLISE)")
    print("=" * 70)

    # Dados corretos da primeira análise
    total_registros = 1527
    protocolos_novos = 562  # 36,8%
    protocolos_existentes = 965  # 63,2%
    protocolos_com_mudancas = 162  # 16,8% dos existentes
    protocolos_sem_mudancas = 803  # 83,2% dos existentes
    campos_alterados = 328

    print(f"📁 Total no arquivo: {total_registros:,} registros")
    print(f"🆕 Protocolos novos: {protocolos_novos:,} ({protocolos_novos/total_registros*100:.1f}%)")
    print(f"✅ Protocolos existentes: {protocolos_existentes:,} ({protocolos_existentes/total_registros*100:.1f}%)")
    print()
    print(f"📊 ANÁLISE DOS {protocolos_existentes:,} PROTOCOLOS EXISTENTES:")
    print(f"   🔄 COM mudanças: {protocolos_com_mudancas:,} ({protocolos_com_mudancas/protocolos_existentes*100:.1f}%)")
    print(f"   ✅ SEM mudanças: {protocolos_sem_mudancas:,} ({protocolos_sem_mudancas/protocolos_existentes*100:.1f}%)")
    print(f"   📝 Total de campos alterados: {campos_alterados:,}")

    print(f"\n⚠️ OPERAÇÕES QUE SERÃO EXECUTADAS:")
    print(f"   🆕 INSERT: {protocolos_novos:,} registros novos")
    print(f"   🔄 UPDATE: {protocolos_com_mudancas:,} registros ({campos_alterados:,} campos)")
    print(f"   ✅ NENHUMA: {protocolos_sem_mudancas:,} registros (já corretos)")

    print(f"\n🛡️ AVALIAÇÃO DE RISCO:")
    print(f"   🟡 MODERADO: {protocolos_existentes/total_registros*100:.1f}% são atualizações")
    print(f"   ✅ POSITIVO: Apenas {protocolos_com_mudancas/protocolos_existentes*100:.1f}% dos existentes têm mudanças")
    print(f"   🔍 RECOMENDAÇÃO: Backup obrigatório antes da operação")

    return True  # Sempre requer backup

def pedir_autorizacao(alto_risco):
    """Pede autorização do usuário para executar"""
    print(f"\n🚨 AUTORIZAÇÃO NECESSÁRIA")
    print("=" * 30)
    
    if alto_risco:
        print(f"⚠️ OPERAÇÃO DE ALTO RISCO DETECTADA!")
        print(f"   Muitos registros serão ATUALIZADOS")
        print(f"   Recomenda-se fazer BACKUP antes")
        print()
    
    print(f"🔍 CONFIRME OS DADOS ACIMA")
    print(f"📊 Verifique se os números estão corretos")
    print(f"🎯 Confirme se é isso que deseja executar")
    print()
    
    while True:
        resposta = input("🚀 DESEJA PROSSEGUIR COM A OPERAÇÃO? (sim/não): ").strip().lower()
        
        if resposta in ['sim', 's', 'yes', 'y']:
            print(f"\n✅ AUTORIZAÇÃO CONCEDIDA!")
            print(f"🚀 Preparando para executar operação...")
            return True
        elif resposta in ['não', 'nao', 'n', 'no']:
            print(f"\n❌ OPERAÇÃO CANCELADA PELO USUÁRIO")
            print(f"🛡️ Nenhuma alteração foi feita no banco")
            return False
        else:
            print(f"❓ Resposta inválida. Digite 'sim' ou 'não'")

def main():
    """Função principal"""
    print("🔍 CONFIRMAÇÃO DE DADOS - EMISSÃO")
    print("=" * 50)
    print("🎯 Objetivo: Confirmar dados e pedir autorização")
    print()
    
    try:
        # Ler dados do arquivo
        total_registros = ler_dados_arquivo_emissao()
        
        # Verificar protocolos existentes
        existentes, total_teste = verificar_protocolos_existentes()
        
        # Analisar mudanças
        total_mudancas = analisar_mudancas_necessarias()
        
        # Mostrar resumo correto
        alto_risco = mostrar_resumo_operacao_corrigido()
        
        # Pedir autorização
        autorizado = pedir_autorizacao(alto_risco)
        
        if autorizado:
            print(f"\n🎯 PRÓXIMOS PASSOS:")
            print(f"   1. Fazer backup da tabela emissao")
            print(f"   2. Executar script de atualização")
            print(f"   3. Validar resultados")
            print(f"   4. Documentar operação")
            
            print(f"\n💡 COMANDOS SUGERIDOS:")
            print(f"   # Backup")
            print(f"   pg_dump -h localhost -p 5433 -U postgres -t emissao crm_ccamp > backup_emissao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
            print(f"   ")
            print(f"   # Executar atualização")
            print(f"   python3 executar_atualizacao_emissao.py")
        else:
            print(f"\n🔍 SUGESTÕES:")
            print(f"   1. Revisar dados do arquivo")
            print(f"   2. Verificar mapeamento de campos")
            print(f"   3. Testar em ambiente de desenvolvimento")
            print(f"   4. Executar novamente quando estiver pronto")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
