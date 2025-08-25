#!/usr/bin/env python3
"""
EXEMPLO DE USO DO SISTEMA DE ATUALIZAÇÃO INCREMENTAL
Demonstra como processar novos relatórios sem duplicar dados
"""

from atualizador_incremental import AtualizadorIncremental
import pandas as pd
import os
from datetime import datetime

def criar_arquivo_exemplo_emissao():
    """Cria arquivo de exemplo para teste de atualização"""
    
    # Dados de exemplo (protocolos que já existem no banco)
    dados_exemplo = [
        {
            'protocolo': '1000001234',
            'documento_do_titular': '12345678901',
            'nome_do_titular': 'JOÃO DA SILVA ATUALIZADO',
            'produto': 'e-CPF A3 (PSC) 4 Anos',
            'data_inicio_validade': '2024-01-15 10:30:00',
            'data_fim_validade': '2028-01-15 10:30:00',  # Campo que pode não existir inicialmente
            'status_do_certificado': 'Emitido',
            'valor_do_boleto': 180.00,  # Valor atualizado
            'nome_da_cidade': 'São Paulo',
            'documento': '12345678901'
        },
        {
            'protocolo': '1000001235',
            'documento_do_titular': '98765432100',
            'nome_do_titular': 'MARIA SANTOS',
            'produto': 'e-CNPJ A1 (Arquivo) 1 Ano',
            'data_inicio_validade': '2024-02-01 14:00:00',
            'data_fim_validade': '2025-02-01 14:00:00',
            'status_do_certificado': 'Instalado',  # Status atualizado
            'valor_do_boleto': 220.00,
            'nome_da_cidade': 'Rio de Janeiro',
            'documento': '12345678000123'
        }
    ]
    
    df = pd.DataFrame(dados_exemplo)
    arquivo = 'exemplo_atualizacao_emissao.xlsx'
    df.to_excel(arquivo, index=False)
    
    print(f"✅ Arquivo de exemplo criado: {arquivo}")
    return arquivo

def demonstrar_atualizacao_incremental():
    """Demonstra o processo completo de atualização incremental"""
    
    print("🔄 DEMONSTRAÇÃO DO SISTEMA DE ATUALIZAÇÃO INCREMENTAL")
    print("=" * 60)
    
    # Inicializar atualizador
    atualizador = AtualizadorIncremental()
    
    # 1. Verificar estado inicial
    print("\n1️⃣ VERIFICANDO ESTADO INICIAL:")
    historico_inicial = atualizador.obter_historico_atualizacoes(limite=5)
    print(f"📊 Últimas {len(historico_inicial)} atualizações no histórico")
    
    # 2. Criar arquivo de exemplo
    print("\n2️⃣ CRIANDO ARQUIVO DE EXEMPLO:")
    arquivo_exemplo = criar_arquivo_exemplo_emissao()
    
    # 3. Processar arquivo
    print("\n3️⃣ PROCESSANDO ARQUIVO DE ATUALIZAÇÃO:")
    try:
        resultado = atualizador.processar_arquivo_emissao(
            arquivo_exemplo,
            f'Teste de atualização incremental - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )
        
        print(f"✅ Status: {resultado['status']}")
        print(f"📁 Arquivo: {resultado['arquivo']}")
        print(f"📊 Total de registros: {resultado['total_registros']}")
        print(f"🆕 Registros novos: {resultado['registros_novos']}")
        print(f"🔄 Registros atualizados: {resultado['registros_atualizados']}")
        print(f"⚠️ Registros ignorados: {resultado['registros_ignorados']}")
        print(f"🔑 Hash do arquivo: {resultado['hash'][:16]}...")
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return
    
    # 4. Tentar processar o mesmo arquivo novamente
    print("\n4️⃣ TESTANDO PROTEÇÃO CONTRA REPROCESSAMENTO:")
    try:
        resultado_duplicado = atualizador.processar_arquivo_emissao(
            arquivo_exemplo,
            'Tentativa de reprocessamento'
        )
        
        print(f"✅ Status: {resultado_duplicado['status']}")
        if resultado_duplicado['status'] == 'JA_PROCESSADO':
            print("🛡️ Sistema protegeu contra reprocessamento do mesmo arquivo!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 5. Verificar histórico atualizado
    print("\n5️⃣ VERIFICANDO HISTÓRICO ATUALIZADO:")
    historico_final = atualizador.obter_historico_atualizacoes('emissao', limite=3)
    
    for item in historico_final:
        print(f"📅 {item['data_processamento']} | {item['arquivo_origem']}")
        print(f"   📊 Novos: {item['registros_novos']} | Atualizados: {item['registros_atualizados']} | Tipo: {item['tipo_processamento']}")
    
    # 6. Verificar integridade
    print("\n6️⃣ VERIFICANDO INTEGRIDADE DOS DADOS:")
    duplicados = atualizador.verificar_protocolos_duplicados('emissao')
    
    if duplicados:
        print(f"⚠️ Encontrados {len(duplicados)} protocolos duplicados:")
        for dup in duplicados[:5]:  # Mostrar apenas os primeiros 5
            print(f"   🔄 Protocolo {dup['protocolo']}: {dup['quantidade']} ocorrências")
    else:
        print("✅ Nenhum protocolo duplicado encontrado - Integridade mantida!")
    
    # 7. Limpeza
    print("\n7️⃣ LIMPEZA:")
    if os.path.exists(arquivo_exemplo):
        os.remove(arquivo_exemplo)
        print(f"🗑️ Arquivo de exemplo removido: {arquivo_exemplo}")
    
    print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")

def exemplo_uso_producao():
    """Exemplo de como usar em produção"""
    
    print("\n" + "="*60)
    print("📋 EXEMPLO DE USO EM PRODUÇÃO")
    print("="*60)
    
    codigo_exemplo = '''
# EXEMPLO DE USO EM PRODUÇÃO

from atualizador_incremental import AtualizadorIncremental

# Inicializar sistema
atualizador = AtualizadorIncremental()

# Processar relatório de emissão atualizado
resultado_emissao = atualizador.processar_arquivo_emissao(
    'relatorio_emissao_janeiro_2024.xlsx',
    'Relatório mensal de emissão - Janeiro 2024'
)

# Processar relatório de renovação geral
resultado_renovacao = atualizador.processar_arquivo_renovacao_geral(
    'relatorio_renovacao_geral_janeiro_2024.xlsx',
    'Relatório mensal de renovação geral - Janeiro 2024'
)

# Processar relatório SafeID
resultado_safeid = atualizador.processar_arquivo_renovacao_safeid(
    'relatorio_safeid_janeiro_2024.xlsx',
    'Relatório mensal SafeID - Janeiro 2024'
)

# Verificar resultados
for resultado in [resultado_emissao, resultado_renovacao, resultado_safeid]:
    print(f"Arquivo: {resultado['arquivo']}")
    print(f"Novos: {resultado['registros_novos']}")
    print(f"Atualizados: {resultado['registros_atualizados']}")
    print("-" * 40)

# Obter histórico de atualizações
historico = atualizador.obter_historico_atualizacoes(limite=20)
for item in historico:
    print(f"{item['data_processamento']} - {item['tabela_destino']} - {item['tipo_processamento']}")
'''
    
    print(codigo_exemplo)

def main():
    """Função principal"""
    demonstrar_atualizacao_incremental()
    exemplo_uso_producao()

if __name__ == "__main__":
    main()
