#!/usr/bin/env python3
"""
ANÁLISE DETALHADA DE MUDANÇAS REAIS - RENOVAÇÃO GERAL
Compara campo por campo respeitando a lógica de negócio
Exclui campo 'prazo' que é calculado dinamicamente
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

def normalizar_valor_para_comparacao(valor):
    """Normaliza valor para comparação exata"""
    if valor is None:
        return ""
    
    valor_str = str(valor).strip()
    
    # Remover .0 de números inteiros
    if valor_str.endswith('.0'):
        valor_str = valor_str[:-2]
    
    # Normalizar valores vazios
    if valor_str.lower() in ['none', 'null', '']:
        return ""
    
    return valor_str

def normalizar_data_para_comparacao(valor_arquivo, valor_banco):
    """Normaliza datas para comparação considerando formatos diferentes"""
    
    def converter_para_timestamp(valor):
        if not valor or valor == "":
            return ""
        
        valor_str = str(valor).strip()
        
        try:
            # Formato brasileiro: dd/mm/yyyy HH:MM:SS
            if '/' in valor_str:
                if ' ' in valor_str:
                    dt = datetime.strptime(valor_str, '%d/%m/%Y %H:%M:%S')
                else:
                    dt = datetime.strptime(valor_str, '%d/%m/%Y')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Formato SQL: yyyy-mm-dd HH:MM:SS
            elif '-' in valor_str:
                if ' ' in valor_str:
                    dt = datetime.strptime(valor_str, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.strptime(valor_str, '%Y-%m-%d')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        return valor_str
    
    arquivo_norm = converter_para_timestamp(valor_arquivo)
    banco_norm = converter_para_timestamp(valor_banco)
    
    return arquivo_norm, banco_norm

def comparar_registro_detalhado(protocolo, registro_arquivo, registro_banco):
    """Compara um registro detalhadamente campo por campo"""
    
    # Mapeamento arquivo → banco (EXCLUINDO campo prazo)
    mapeamento = {
        0: ('razao_social', 'Razão Social', 'texto'),
        1: ('cpfcnpj', 'CPF/CNPJ', 'texto'),
        2: ('telefone', 'Telefone', 'texto'),
        3: ('e_mail', 'E-mail', 'texto'),
        4: ('produto', 'Produto', 'texto'),
        5: ('nome_titular', 'Nome Titular', 'texto'),
        6: ('data_inicio_validade', 'Data Início Validade', 'data'),
        7: ('data_fim_validade', 'Data Fim Validade', 'data'),
        # 8: PRAZO - EXCLUÍDO (campo calculado dinamicamente)
        9: ('ar_solicitacao', 'AR Solicitação', 'texto'),
        10: ('ar_emissao', 'AR Emissão', 'texto'),
        11: ('local_de_atendimento', 'Local de Atendimento', 'texto'),
        12: ('endereco_do_local_de_atendimento', 'Endereço do Local', 'texto'),
        14: ('status_acao', 'Status Ação', 'texto'),
        15: ('status_certificado', 'Status Certificado', 'texto'),
        16: ('nome_contador_parceiro', 'Nome Contador Parceiro', 'texto'),
        17: ('cpf_contador_parceiro', 'CPF Contador Parceiro', 'texto'),
        18: ('protocolo_renovacao', 'Protocolo renovação', 'numero'),
        19: ('status_protocolo_renovacao', 'Status protocolo renovação', 'texto'),
        20: ('nome_da_ar_protocolo_renovacao', 'Nome da AR protocolo renovação', 'texto'),
        21: ('produto_protocolo_renovacao', 'Produto protocolo renovação', 'texto')
    }
    
    mudancas = []
    
    for col_arquivo, (campo_banco, nome_campo, tipo) in mapeamento.items():
        # Valor do arquivo
        valor_arquivo = normalizar_valor_para_comparacao(registro_arquivo.get(col_arquivo, ''))
        
        # Valor do banco
        valor_banco = normalizar_valor_para_comparacao(registro_banco.get(campo_banco, ''))
        
        # Tratamento especial para datas
        if tipo == 'data':
            valor_arquivo_norm, valor_banco_norm = normalizar_data_para_comparacao(valor_arquivo, valor_banco)
            valor_arquivo = valor_arquivo_norm
            valor_banco = valor_banco_norm
        
        # Comparar valores
        if valor_arquivo != valor_banco:
            mudancas.append({
                'campo': campo_banco,
                'nome': nome_campo,
                'tipo': tipo,
                'valor_banco': valor_banco,
                'valor_arquivo': valor_arquivo
            })
    
    return mudancas

def analisar_mudancas_reais_detalhada():
    """Analisa mudanças reais com detalhamento completo"""
    print("🔍 ANÁLISE DETALHADA DE MUDANÇAS REAIS - RENOVAÇÃO GERAL")
    print("=" * 70)
    print("🎯 Comparação campo por campo respeitando lógica de negócio")
    print("⚠️ Campo 'prazo' excluído (calculado dinamicamente)")
    print()
    
    # Ler arquivo
    print("📖 LENDO ARQUIVO GestaoRenovacao (1).xls...")
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
    print("🗄️ BUSCANDO REGISTROS NO BANCO renovacao_geral...")
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
            'prazo': registro[9],
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
    
    # Comparar registros detalhadamente
    print(f"\n🔍 COMPARANDO REGISTROS DETALHADAMENTE...")
    
    registros_novos = []
    registros_com_mudancas = []
    registros_sem_mudancas = []
    estatisticas_campos = {}
    
    contador = 0
    for protocolo, registro_arquivo in registros_arquivo.items():
        contador += 1
        
        if protocolo not in registros_banco:
            registros_novos.append(protocolo)
            continue
        
        # Comparar registro detalhadamente
        mudancas = comparar_registro_detalhado(protocolo, registro_arquivo, registros_banco[protocolo])
        
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
        
        # Progresso a cada 100 registros
        if contador % 100 == 0:
            print(f"   📋 Analisados: {contador:,}/{len(registros_arquivo):,}")
    
    # Mostrar resultados detalhados
    print(f"\n📊 RESULTADO DA ANÁLISE DETALHADA:")
    print("=" * 60)
    
    total = len(registros_arquivo)
    novos = len(registros_novos)
    com_mudancas = len(registros_com_mudancas)
    sem_mudancas = len(registros_sem_mudancas)
    
    print(f"📁 Total no arquivo: {total:,} registros")
    print(f"🆕 Registros novos (INSERT): {novos:,} ({novos/total*100:.1f}%)")
    print(f"🔄 Registros COM mudanças (UPDATE): {com_mudancas:,} ({com_mudancas/total*100:.1f}%)")
    print(f"✅ Registros SEM mudanças (NENHUMA AÇÃO): {sem_mudancas:,} ({sem_mudancas/total*100:.1f}%)")
    
    print(f"\n⚠️ CAMPO EXCLUÍDO DA ANÁLISE:")
    print(f"   🚫 prazo: Campo calculado dinamicamente (muda diariamente)")
    
    if estatisticas_campos:
        print(f"\n📋 MUDANÇAS POR CAMPO (ANÁLISE REAL):")
        print("-" * 60)
        total_existentes = com_mudancas + sem_mudancas
        for campo, count in sorted(estatisticas_campos.items()):
            pct = (count / total_existentes) * 100 if total_existentes > 0 else 0
            print(f"   {campo:35}: {count:,} mudanças ({pct:.1f}%)")
    
    # Mostrar exemplos detalhados
    if registros_com_mudancas:
        print(f"\n💡 EXEMPLOS DETALHADOS DE MUDANÇAS:")
        print("-" * 80)
        
        for i, registro in enumerate(registros_com_mudancas[:5]):
            protocolo = registro['protocolo']
            mudancas = registro['mudancas']
            
            print(f"\n📋 PROTOCOLO {protocolo} ({len(mudancas)} mudanças):")
            for mudanca in mudancas:
                banco = mudanca['valor_banco'][:40] if mudanca['valor_banco'] else 'VAZIO'
                arquivo = mudanca['valor_arquivo'][:40] if mudanca['valor_arquivo'] else 'VAZIO'
                print(f"   • {mudanca['nome']}: '{banco}' → '{arquivo}'")
    
    # Mostrar alguns registros sem mudanças
    if registros_sem_mudancas:
        print(f"\n✅ EXEMPLOS DE REGISTROS SEM MUDANÇAS:")
        print("-" * 50)
        for protocolo in registros_sem_mudancas[:5]:
            print(f"   📋 PROTOCOLO {protocolo}: Dados idênticos")
    
    return {
        'total': total,
        'novos': novos,
        'com_mudancas': com_mudancas,
        'sem_mudancas': sem_mudancas,
        'estatisticas_campos': estatisticas_campos,
        'registros_com_mudancas': registros_com_mudancas,
        'registros_sem_mudancas': registros_sem_mudancas
    }

def main():
    """Função principal"""
    try:
        resultado = analisar_mudancas_reais_detalhada()
        
        print(f"\n🎉 ANÁLISE DETALHADA CONCLUÍDA!")
        print("=" * 50)
        
        if resultado['com_mudancas'] > 0:
            print(f"🔄 ATUALIZAÇÕES NECESSÁRIAS:")
            print(f"   📊 {resultado['com_mudancas']:,} registros precisam de UPDATE")
            print(f"   ✅ {resultado['sem_mudancas']:,} registros já estão corretos")
            
            pct_atualizacao = (resultado['com_mudancas'] / resultado['total']) * 100
            print(f"   📈 Taxa de atualização: {pct_atualizacao:.1f}%")
            
            print(f"\n🎯 PRÓXIMO PASSO:")
            print(f"   Criar script de atualização para {resultado['com_mudancas']:,} registros")
        else:
            print(f"✅ NENHUMA ATUALIZAÇÃO NECESSÁRIA!")
            print(f"   Todos os {resultado['total']:,} registros já estão corretos")
        
        if resultado['novos'] > 0:
            print(f"\n🆕 INSERÇÕES NECESSÁRIAS:")
            print(f"   📊 {resultado['novos']:,} registros novos para INSERT")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
