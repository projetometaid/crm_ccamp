#!/usr/bin/env python3
"""
ANÁLISE SEM CAMPO PRAZO - RENOVAÇÃO GERAL
Compara registros EXCLUINDO o campo 'prazo' que é calculado dinamicamente
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

def normalizar_valor(valor):
    """Normaliza valor para comparação"""
    if valor is None:
        return ""
    
    valor_str = str(valor).strip()
    
    # Remover .0 de números inteiros
    if valor_str.endswith('.0'):
        valor_str = valor_str[:-2]
    
    return valor_str

def normalizar_data(valor):
    """Normaliza datas para comparação"""
    if not valor or valor == "":
        return ""
    
    valor_str = str(valor).strip()
    
    # Converter formato brasileiro para SQL
    try:
        if '/' in valor_str:
            # Formato: dd/mm/yyyy HH:MM:SS ou dd/mm/yyyy
            if ' ' in valor_str:
                dt = datetime.strptime(valor_str, '%d/%m/%Y %H:%M:%S')
            else:
                dt = datetime.strptime(valor_str, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    
    # Se já está em formato SQL, manter
    if '-' in valor_str:
        try:
            dt = datetime.strptime(valor_str, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    return valor_str

def comparar_registro_sem_prazo(protocolo, registro_arquivo, registro_banco):
    """Compara um registro específico campo por campo EXCLUINDO o campo prazo"""
    
    # Mapeamento arquivo → banco (SEM o campo prazo)
    mapeamento = {
        0: ('razao_social', 'Razão Social'),
        1: ('cpfcnpj', 'CPF/CNPJ'),
        2: ('telefone', 'Telefone'),
        3: ('e_mail', 'E-mail'),
        4: ('produto', 'Produto'),
        5: ('nome_titular', 'Nome Titular'),
        6: ('data_inicio_validade', 'Data Início Validade'),
        7: ('data_fim_validade', 'Data Fim Validade'),
        # 8: PRAZO - EXCLUÍDO DA COMPARAÇÃO (campo calculado)
        9: ('ar_solicitacao', 'AR Solicitação'),
        10: ('ar_emissao', 'AR Emissão'),
        11: ('local_de_atendimento', 'Local de Atendimento'),
        12: ('endereco_do_local_de_atendimento', 'Endereço do Local'),
        14: ('status_acao', 'Status Ação'),
        15: ('status_certificado', 'Status Certificado'),
        16: ('nome_contador_parceiro', 'Nome Contador Parceiro'),
        17: ('cpf_contador_parceiro', 'CPF Contador Parceiro'),
        18: ('protocolo_renovacao', 'Protocolo renovação'),
        19: ('status_protocolo_renovacao', 'Status protocolo renovação'),
        20: ('nome_da_ar_protocolo_renovacao', 'Nome da AR protocolo renovação'),
        21: ('produto_protocolo_renovacao', 'Produto protocolo renovação')
    }
    
    mudancas = []
    
    for col_arquivo, (campo_banco, nome_campo) in mapeamento.items():
        # Valor do arquivo
        valor_arquivo = normalizar_valor(registro_arquivo.get(col_arquivo, ''))
        
        # Valor do banco
        valor_banco = normalizar_valor(registro_banco.get(campo_banco, ''))
        
        # Normalizar datas especificamente
        if 'data' in campo_banco.lower():
            valor_arquivo = normalizar_data(valor_arquivo)
            valor_banco = normalizar_data(valor_banco)
        
        # Comparar valores
        if valor_arquivo != valor_banco:
            # Verificar se não é apenas uma mudança de vazio para vazio
            if valor_arquivo != '' or valor_banco != '':
                mudancas.append({
                    'campo': campo_banco,
                    'nome': nome_campo,
                    'valor_banco': valor_banco,
                    'valor_arquivo': valor_arquivo
                })
    
    return mudancas

def analisar_mudancas_sem_prazo():
    """Analisa mudanças reais EXCLUINDO o campo prazo"""
    print("🔍 ANÁLISE SEM CAMPO PRAZO - RENOVAÇÃO GERAL")
    print("=" * 60)
    print("🎯 Comparando registros EXCLUINDO campo 'prazo' (calculado dinamicamente)")
    print("⚠️ Campo 'prazo' ignorado pois muda a cada dia")
    print()
    
    # Ler arquivo
    print("📖 LENDO ARQUIVO...")
    wb = xlrd.open_workbook("../GestaoRenovacao (1).xls")
    sheet = wb.sheet_by_index(0)
    
    # Ler registros do arquivo
    registros_arquivo = {}
    for row in range(1, sheet.nrows):
        protocolo_str = str(sheet.cell_value(row, 13)).strip()  # Col 13 = Protocolo
        
        try:
            protocolo = int(float(protocolo_str))
        except:
            continue
        
        registro = {}
        for col in range(sheet.ncols):
            valor = str(sheet.cell_value(row, col)).strip()
            registro[col] = valor
        
        registros_arquivo[protocolo] = registro
    
    print(f"✅ Arquivo carregado: {len(registros_arquivo):,} registros")
    
    # Buscar registros do banco
    print("🗄️ BUSCANDO REGISTROS NO BANCO...")
    conn = conectar_banco()
    cursor = conn.cursor()
    
    protocolos = list(registros_arquivo.keys())
    placeholders = ','.join(['%s'] * len(protocolos))
    
    cursor.execute(f"""
        SELECT protocolo, razao_social, cpfcnpj, telefone, e_mail, produto, 
               nome_titular, data_inicio_validade, data_fim_validade, prazo,
               ar_solicitacao, ar_emissao, local_de_atendimento, 
               endereco_do_local_de_atendimento, status_acao, status_certificado,
               nome_contador_parceiro, cpf_contador_parceiro, protocolo_renovacao,
               status_protocolo_renovacao, nome_da_ar_protocolo_renovacao,
               produto_protocolo_renovacao
        FROM renovacao_geral
        WHERE protocolo IN ({placeholders})
        ORDER BY protocolo
    """, protocolos)
    
    registros_banco = {}
    for registro in cursor.fetchall():
        protocolo = registro[0]
        registros_banco[protocolo] = {
            'protocolo': registro[0],
            'razao_social': registro[1],
            'cpfcnpj': registro[2],
            'telefone': registro[3],
            'e_mail': registro[4],
            'produto': registro[5],
            'nome_titular': registro[6],
            'data_inicio_validade': registro[7],
            'data_fim_validade': registro[8],
            'prazo': registro[9],  # Incluído mas não usado na comparação
            'ar_solicitacao': registro[10],
            'ar_emissao': registro[11],
            'local_de_atendimento': registro[12],
            'endereco_do_local_de_atendimento': registro[13],
            'status_acao': registro[14],
            'status_certificado': registro[15],
            'nome_contador_parceiro': registro[16],
            'cpf_contador_parceiro': registro[17],
            'protocolo_renovacao': registro[18],
            'status_protocolo_renovacao': registro[19],
            'nome_da_ar_protocolo_renovacao': registro[20],
            'produto_protocolo_renovacao': registro[21]
        }
    
    conn.close()
    
    print(f"✅ Banco consultado: {len(registros_banco):,} registros encontrados")
    
    # Comparar registros SEM o campo prazo
    print(f"\n🔍 COMPARANDO REGISTROS (EXCLUINDO CAMPO PRAZO)...")
    
    registros_novos = []
    registros_com_mudancas = []
    registros_sem_mudancas = []
    estatisticas_campos = {}
    
    for protocolo, registro_arquivo in registros_arquivo.items():
        if protocolo not in registros_banco:
            registros_novos.append(protocolo)
            continue
        
        # Comparar registro SEM o campo prazo
        mudancas = comparar_registro_sem_prazo(protocolo, registro_arquivo, registros_banco[protocolo])
        
        if mudancas:
            registros_com_mudancas.append({
                'protocolo': protocolo,
                'mudancas': mudancas
            })
            
            # Contar mudanças por campo
            for mudanca in mudancas:
                campo = mudanca['campo']
                if campo not in estatisticas_campos:
                    estatisticas_campos[campo] = 0
                estatisticas_campos[campo] += 1
        else:
            registros_sem_mudancas.append(protocolo)
    
    # Mostrar resultados
    print(f"\n📊 RESULTADO DA ANÁLISE (SEM CAMPO PRAZO):")
    print("=" * 60)
    
    total = len(registros_arquivo)
    novos = len(registros_novos)
    com_mudancas = len(registros_com_mudancas)
    sem_mudancas = len(registros_sem_mudancas)
    
    print(f"📁 Total no arquivo: {total:,} registros")
    print(f"🆕 Registros novos: {novos:,} ({novos/total*100:.1f}%)")
    print(f"🔄 Registros COM mudanças: {com_mudancas:,} ({com_mudancas/total*100:.1f}%)")
    print(f"✅ Registros SEM mudanças: {sem_mudancas:,} ({sem_mudancas/total*100:.1f}%)")
    
    print(f"\n⚠️ CAMPO EXCLUÍDO DA ANÁLISE:")
    print(f"   🚫 prazo: Campo calculado dinamicamente (muda a cada dia)")
    
    if estatisticas_campos:
        print(f"\n📋 MUDANÇAS POR CAMPO (EXCLUINDO PRAZO):")
        print("-" * 60)
        for campo, count in sorted(estatisticas_campos.items()):
            pct = (count / (com_mudancas + sem_mudancas)) * 100 if (com_mudancas + sem_mudancas) > 0 else 0
            print(f"   {campo:30}: {count:,} mudanças ({pct:.1f}%)")
    else:
        print(f"\n✅ NENHUMA MUDANÇA IDENTIFICADA (EXCLUINDO PRAZO)")
    
    # Mostrar exemplos de mudanças
    if registros_com_mudancas:
        print(f"\n💡 EXEMPLOS DE MUDANÇAS (primeiros 5 registros):")
        print("-" * 80)
        
        for i, registro in enumerate(registros_com_mudancas[:5]):
            protocolo = registro['protocolo']
            mudancas = registro['mudancas']
            
            print(f"\n📋 PROTOCOLO {protocolo} ({len(mudancas)} mudanças):")
            for mudanca in mudancas[:3]:  # Mostrar apenas 3 primeiras mudanças
                banco = mudanca['valor_banco'][:30] if mudanca['valor_banco'] else 'VAZIO'
                arquivo = mudanca['valor_arquivo'][:30] if mudanca['valor_arquivo'] else 'VAZIO'
                print(f"   • {mudanca['nome']}: '{banco}' → '{arquivo}'")
            
            if len(mudancas) > 3:
                print(f"   ... e mais {len(mudancas) - 3} mudanças")
    
    return {
        'total': total,
        'novos': novos,
        'com_mudancas': com_mudancas,
        'sem_mudancas': sem_mudancas,
        'estatisticas_campos': estatisticas_campos,
        'registros_com_mudancas': registros_com_mudancas
    }

def main():
    """Função principal"""
    try:
        resultado = analisar_mudancas_sem_prazo()
        
        print(f"\n🎉 ANÁLISE SEM CAMPO PRAZO CONCLUÍDA!")
        print("=" * 50)
        print(f"✅ Campo 'prazo' excluído da comparação")
        print(f"📊 {resultado['com_mudancas']:,} registros precisam de UPDATE")
        print(f"✅ {resultado['sem_mudancas']:,} registros estão corretos")
        
        if resultado['com_mudancas'] > 0:
            print(f"\n🎯 PRÓXIMO PASSO:")
            print(f"   Criar script de atualização para {resultado['com_mudancas']:,} registros")
            print(f"   (Excluindo campo 'prazo' da atualização)")
        else:
            print(f"\n✅ NENHUMA ATUALIZAÇÃO NECESSÁRIA!")
            print(f"   Todos os registros já estão corretos no banco")
            print(f"   (Campo 'prazo' é calculado dinamicamente)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
