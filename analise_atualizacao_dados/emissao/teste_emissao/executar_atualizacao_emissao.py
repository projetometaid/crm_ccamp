#!/usr/bin/env python3
"""
EXECUÇÃO DE ATUALIZAÇÕES - EMISSÃO
Executa as atualizações identificadas na análise da emissão
"""

import psycopg2
import xlrd
from datetime import datetime
from decimal import Decimal
import sys

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def converter_data_brasileira(data_str):
    """Converte data brasileira para datetime"""
    if not data_str or data_str.strip() == '':
        return None
    
    try:
        # Formato: dd/mm/yyyy HH:MM:SS
        return datetime.strptime(data_str.strip(), '%d/%m/%Y %H:%M:%S')
    except:
        try:
            # Formato: dd/mm/yyyy
            return datetime.strptime(data_str.strip(), '%d/%m/%Y')
        except:
            return None

def converter_valor(valor_str):
    """Converte valor string para Decimal"""
    if not valor_str or valor_str.strip() == '':
        return None

    try:
        # Remove pontos de milhares e substitui vírgula por ponto
        valor_limpo = str(valor_str).replace('.', '').replace(',', '.')
        return Decimal(valor_limpo)
    except:
        return None

def truncar_campo(valor, tamanho_max):
    """Trunca campo para não exceder limite do banco"""
    if not valor:
        return valor

    valor_str = str(valor).strip()
    if len(valor_str) > tamanho_max:
        return valor_str[:tamanho_max]
    return valor_str

def validar_e_limpar_registro(registro):
    """Valida e limpa registro conforme limites do banco"""
    # Limites dos campos conforme estrutura do banco
    registro['nome'] = truncar_campo(registro['nome'], 500)
    registro['documento'] = truncar_campo(registro['documento'], 20)
    registro['produto'] = truncar_campo(registro['produto'], 255)
    registro['status_do_certificado'] = truncar_campo(registro['status_do_certificado'], 255)

    return registro

def ler_arquivo_emissao():
    """Lê todos os dados do arquivo de emissão com mapeamento correto"""
    print("📖 LENDO ARQUIVO DE EMISSÃO COMPLETO")
    print("=" * 50)

    wb = xlrd.open_workbook("../RelatorioEmissoes (13).xls")
    sheet = wb.sheet_by_index(0)

    print(f"📊 Processando {sheet.nrows-1:,} registros...")

    # MAPEAMENTO CORRETO DAS COLUNAS (baseado na análise)
    print(f"📋 MAPEAMENTO CORRETO:")
    print(f"   Col 0: Protocolo")
    print(f"   Col 1: Nome (CORRIGIDO)")
    print(f"   Col 2: Documento (CORRIGIDO)")
    print(f"   Col 8: Produto")
    print(f"   Col 9: Descrição do Produto")
    print(f"   Col 18: Data Inicio Validade")
    print(f"   Col 19: Data Fim Validade")
    print(f"   Col 20: Status do Certificado")
    print(f"   Col 29: Valor do Boleto")
    print()

    registros = []

    for row in range(1, sheet.nrows):
        # Ler campos principais com mapeamento CORRETO
        protocolo = str(sheet.cell_value(row, 0)).strip()
        nome = str(sheet.cell_value(row, 1)).strip()  # CORRIGIDO: Col 1 = Nome
        documento = str(sheet.cell_value(row, 2)).strip()  # CORRIGIDO: Col 2 = Documento
        produto = str(sheet.cell_value(row, 8)).strip()  # Produto
        descricao_produto = str(sheet.cell_value(row, 9)).strip()  # Descrição do Produto
        status = str(sheet.cell_value(row, 20)).strip()  # Status do Certificado

        # Ler datas
        data_inicio = sheet.cell_value(row, 18)  # Data Inicio Validade
        data_fim = sheet.cell_value(row, 19)     # Data Fim Validade

        # Ler valores
        valor_boleto = sheet.cell_value(row, 29)  # Valor do Boleto

        # Usar descrição do produto se produto estiver vazio
        produto_final = descricao_produto if descricao_produto else produto

        registro = {
            'protocolo': int(float(protocolo)) if protocolo else None,
            'nome': nome,
            'documento': documento,
            'produto': produto_final,
            'status_do_certificado': status,
            'data_inicio_validade': converter_data_brasileira(str(data_inicio)) if data_inicio else None,
            'data_fim_validade': converter_data_brasileira(str(data_fim)) if data_fim else None,
            'valor_do_boleto': converter_valor(str(valor_boleto)) if valor_boleto else None
        }

        # Validar e limpar registro
        registro = validar_e_limpar_registro(registro)

        registros.append(registro)

        # Progresso a cada 100 registros
        if row % 100 == 0:
            print(f"   📋 Processados: {row:,}/{sheet.nrows-1:,}")

    print(f"✅ Total carregado: {len(registros):,} registros")

    return registros

def identificar_operacoes(registros):
    """Identifica quais registros são INSERT vs UPDATE"""
    print(f"\n🔍 IDENTIFICANDO OPERAÇÕES NECESSÁRIAS")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar todos os protocolos existentes no banco
    print("📊 Buscando protocolos existentes no banco...")
    cursor.execute("SELECT protocolo FROM emissao")
    protocolos_existentes = set(row[0] for row in cursor.fetchall())
    
    print(f"✅ Encontrados {len(protocolos_existentes):,} protocolos no banco")
    
    # Separar operações
    inserts = []
    updates = []
    
    for registro in registros:
        protocolo = registro['protocolo']
        
        if protocolo in protocolos_existentes:
            updates.append(registro)
        else:
            inserts.append(registro)
    
    print(f"\n📊 OPERAÇÕES IDENTIFICADAS:")
    print(f"   🆕 INSERT: {len(inserts):,} registros ({len(inserts)/len(registros)*100:.1f}%)")
    print(f"   🔄 UPDATE: {len(updates):,} registros ({len(updates)/len(registros)*100:.1f}%)")
    
    conn.close()
    
    return inserts, updates

def executar_inserts(inserts):
    """Executa inserções de novos registros"""
    if not inserts:
        print("✅ Nenhuma inserção necessária")
        return 0
    
    print(f"\n🆕 EXECUTANDO INSERÇÕES")
    print("=" * 40)
    print(f"📊 Total a inserir: {len(inserts):,}")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    sql_insert = """
        INSERT INTO emissao (
            protocolo, nome, documento, produto, status_do_certificado,
            data_inicio_validade, data_fim_validade, valor_do_boleto
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    
    inseridos = 0
    erros = 0

    for i, registro in enumerate(inserts, 1):
        try:
            cursor.execute(sql_insert, (
                registro['protocolo'],
                registro['nome'],
                registro['documento'],
                registro['produto'],
                registro['status_do_certificado'],
                registro['data_inicio_validade'],
                registro['data_fim_validade'],
                registro['valor_do_boleto']
            ))

            inseridos += 1

            # Commit a cada 50 inserções para evitar rollback total
            if i % 50 == 0:
                conn.commit()
                print(f"   📋 Inseridos: {i:,}/{len(inserts):,}")

        except Exception as e:
            erros += 1
            conn.rollback()  # Rollback apenas desta transação
            print(f"   ❌ Erro no protocolo {registro['protocolo']}: {str(e)[:100]}")

            # Mostrar apenas primeiros 5 erros para não poluir log
            if erros <= 5:
                print(f"      Dados: nome='{registro['nome'][:20]}', doc='{registro['documento']}'")

    # Commit final
    try:
        conn.commit()
    except:
        pass

    conn.close()
    
    print(f"✅ Inserções concluídas: {inseridos:,} sucessos, {erros} erros")
    
    return inseridos

def executar_updates(updates):
    """Executa atualizações de registros existentes"""
    if not updates:
        print("✅ Nenhuma atualização necessária")
        return 0
    
    print(f"\n🔄 EXECUTANDO ATUALIZAÇÕES")
    print("=" * 40)
    print(f"📊 Total a atualizar: {len(updates):,}")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    sql_update = """
        UPDATE emissao SET
            nome = %s,
            documento = %s,
            produto = %s,
            status_do_certificado = %s,
            data_inicio_validade = %s,
            data_fim_validade = %s,
            valor_do_boleto = %s
        WHERE protocolo = %s
    """
    
    atualizados = 0
    erros = 0

    for i, registro in enumerate(updates, 1):
        try:
            cursor.execute(sql_update, (
                registro['nome'],
                registro['documento'],
                registro['produto'],
                registro['status_do_certificado'],
                registro['data_inicio_validade'],
                registro['data_fim_validade'],
                registro['valor_do_boleto'],
                registro['protocolo']
            ))

            if cursor.rowcount > 0:
                atualizados += 1

            # Commit a cada 50 atualizações para evitar rollback total
            if i % 50 == 0:
                conn.commit()
                print(f"   📋 Atualizados: {i:,}/{len(updates):,}")

        except Exception as e:
            erros += 1
            conn.rollback()  # Rollback apenas desta transação
            print(f"   ❌ Erro no protocolo {registro['protocolo']}: {str(e)[:100]}")

            # Mostrar apenas primeiros 5 erros para não poluir log
            if erros <= 5:
                print(f"      Dados: nome='{registro['nome'][:20]}', doc='{registro['documento']}'")

    # Commit final
    try:
        conn.commit()
    except:
        pass

    conn.close()
    
    print(f"✅ Atualizações concluídas: {atualizados:,} sucessos, {erros} erros")
    
    return atualizados

def validar_resultados():
    """Valida os resultados da operação"""
    print(f"\n✅ VALIDANDO RESULTADOS")
    print("=" * 30)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Contar registros totais
    cursor.execute("SELECT COUNT(*) FROM emissao")
    total_registros = cursor.fetchone()[0]
    
    # Contar registros recentes (últimas 24h)
    cursor.execute("""
        SELECT COUNT(*) FROM emissao 
        WHERE protocolo >= 1008000000
    """)
    registros_recentes = cursor.fetchone()[0]
    
    print(f"📊 Total de registros na tabela: {total_registros:,}")
    print(f"📊 Registros recentes (1008+): {registros_recentes:,}")
    
    conn.close()

def main():
    """Função principal"""
    print("🚀 EXECUÇÃO DE ATUALIZAÇÕES - EMISSÃO")
    print("=" * 60)
    print("🎯 Baseado na análise: 562 INSERT + 162 UPDATE")
    print()
    
    inicio = datetime.now()
    
    try:
        # Ler arquivo
        registros = ler_arquivo_emissao()
        
        # Identificar operações
        inserts, updates = identificar_operacoes(registros)
        
        # Confirmar operação
        print(f"\n⚠️ CONFIRMAÇÃO FINAL:")
        print(f"   🆕 {len(inserts):,} inserções")
        print(f"   🔄 {len(updates):,} atualizações")
        
        resposta = input("\n🚀 PROSSEGUIR? (sim/não): ").strip().lower()
        
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada pelo usuário")
            return
        
        # Executar operações
        print(f"\n🚀 INICIANDO EXECUÇÃO...")
        
        inseridos = executar_inserts(inserts)
        atualizados = executar_updates(updates)
        
        # Validar resultados
        validar_resultados()
        
        # Resumo final
        fim = datetime.now()
        duracao = fim - inicio
        
        print(f"\n🎉 OPERAÇÃO CONCLUÍDA!")
        print("=" * 30)
        print(f"⏱️ Duração: {duracao}")
        print(f"🆕 Inseridos: {inseridos:,}")
        print(f"🔄 Atualizados: {atualizados:,}")
        print(f"📊 Total processado: {inseridos + atualizados:,}")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
