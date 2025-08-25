#!/usr/bin/env python3
"""
ANÁLISE DE CONSISTÊNCIA - RENOVAÇÃO GERAL
Verifica consistência entre campos de renovação e identifica apenas mudanças reais
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

def analisar_consistencia_renovacao():
    """Analisa consistência entre campos de renovação"""
    print("🔍 ANÁLISE DE CONSISTÊNCIA - RENOVAÇÃO GERAL")
    print("=" * 60)
    print("🎯 Verificando consistência entre campos de renovação")
    print("📋 Lógica: Se tem protocolo_renovacao → deve ter status, AR e produto")
    print()
    
    # Ler arquivo
    print("📖 LENDO ARQUIVO...")
    wb = xlrd.open_workbook("../GestaoRenovacao (1).xls")
    sheet = wb.sheet_by_index(0)
    
    registros_arquivo = {}
    for row in range(1, sheet.nrows):
        protocolo_str = str(sheet.cell_value(row, 13)).strip()
        try:
            protocolo = int(float(protocolo_str))
        except:
            continue
        
        registro = {
            'protocolo_renovacao': str(sheet.cell_value(row, 18)).strip(),
            'status_protocolo_renovacao': str(sheet.cell_value(row, 19)).strip(),
            'nome_da_ar_protocolo_renovacao': str(sheet.cell_value(row, 20)).strip(),
            'produto_protocolo_renovacao': str(sheet.cell_value(row, 21)).strip()
        }
        
        registros_arquivo[protocolo] = registro
    
    print(f"✅ Arquivo carregado: {len(registros_arquivo):,} registros")
    
    # Buscar dados do banco
    print("🗄️ BUSCANDO DADOS DO BANCO...")
    conn = conectar_banco()
    cursor = conn.cursor()
    
    protocolos = list(registros_arquivo.keys())
    placeholders = ','.join(['%s'] * len(protocolos))
    
    cursor.execute(f"""
        SELECT protocolo, protocolo_renovacao, status_protocolo_renovacao,
               nome_da_ar_protocolo_renovacao, produto_protocolo_renovacao
        FROM renovacao_geral
        WHERE protocolo IN ({placeholders})
        ORDER BY protocolo
    """, protocolos)
    
    registros_banco = {}
    for protocolo, prot_ren, status, ar, produto in cursor.fetchall():
        registros_banco[protocolo] = {
            'protocolo_renovacao': str(prot_ren) if prot_ren else '',
            'status_protocolo_renovacao': str(status) if status else '',
            'nome_da_ar_protocolo_renovacao': str(ar) if ar else '',
            'produto_protocolo_renovacao': str(produto) if produto else ''
        }
    
    conn.close()
    
    print(f"✅ Banco consultado: {len(registros_banco):,} registros")
    
    # Analisar consistência
    print(f"\n🔍 ANALISANDO CONSISTÊNCIA DOS CAMPOS...")
    
    # Categorizar registros do arquivo
    arquivo_com_protocolo = []
    arquivo_sem_protocolo = []
    
    for protocolo, dados in registros_arquivo.items():
        prot_ren = dados['protocolo_renovacao']
        
        # Verificar se protocolo_renovacao está preenchido
        if prot_ren and prot_ren != '' and prot_ren != '0' and prot_ren != '0.0':
            arquivo_com_protocolo.append(protocolo)
        else:
            arquivo_sem_protocolo.append(protocolo)
    
    # Categorizar registros do banco
    banco_com_protocolo = []
    banco_sem_protocolo = []
    
    for protocolo, dados in registros_banco.items():
        prot_ren = dados['protocolo_renovacao']
        
        if prot_ren and prot_ren != '' and prot_ren != '0' and prot_ren != '0.0':
            banco_com_protocolo.append(protocolo)
        else:
            banco_sem_protocolo.append(protocolo)
    
    print(f"\n📊 CATEGORIZAÇÃO DOS REGISTROS:")
    print("-" * 50)
    print(f"📁 ARQUIVO:")
    print(f"   🔄 COM protocolo_renovacao: {len(arquivo_com_protocolo):,} registros")
    print(f"   ⏸️ SEM protocolo_renovacao: {len(arquivo_sem_protocolo):,} registros")
    
    print(f"\n🗄️ BANCO:")
    print(f"   🔄 COM protocolo_renovacao: {len(banco_com_protocolo):,} registros")
    print(f"   ⏸️ SEM protocolo_renovacao: {len(banco_sem_protocolo):,} registros")
    
    # Comparar apenas registros que realmente mudaram
    print(f"\n🔍 IDENTIFICANDO MUDANÇAS REAIS...")
    
    mudancas_reais = []
    sem_mudancas = []
    
    for protocolo in registros_arquivo.keys():
        if protocolo not in registros_banco:
            continue
        
        arquivo = registros_arquivo[protocolo]
        banco = registros_banco[protocolo]
        
        mudancas_protocolo = []
        
        # Comparar cada campo
        for campo in ['protocolo_renovacao', 'status_protocolo_renovacao', 
                     'nome_da_ar_protocolo_renovacao', 'produto_protocolo_renovacao']:
            
            valor_arquivo = arquivo[campo].strip()
            valor_banco = banco[campo].strip()
            
            # Normalizar valores vazios
            if valor_arquivo in ['0', '0.0', 'None', 'null']:
                valor_arquivo = ''
            if valor_banco in ['0', '0.0', 'None', 'null']:
                valor_banco = ''
            
            if valor_arquivo != valor_banco:
                mudancas_protocolo.append({
                    'campo': campo,
                    'banco': valor_banco,
                    'arquivo': valor_arquivo
                })
        
        if mudancas_protocolo:
            mudancas_reais.append({
                'protocolo': protocolo,
                'mudancas': mudancas_protocolo
            })
        else:
            sem_mudancas.append(protocolo)
    
    print(f"\n📊 RESULTADO DA ANÁLISE DE CONSISTÊNCIA:")
    print("=" * 60)
    
    total = len(registros_arquivo)
    com_mudancas = len(mudancas_reais)
    sem_mudancas_count = len(sem_mudancas)
    
    print(f"📁 Total no arquivo: {total:,} registros")
    print(f"🔄 Registros COM mudanças REAIS: {com_mudancas:,} ({com_mudancas/total*100:.1f}%)")
    print(f"✅ Registros SEM mudanças: {sem_mudancas_count:,} ({sem_mudancas_count/total*100:.1f}%)")
    
    # Analisar tipos de mudanças
    if mudancas_reais:
        print(f"\n📋 TIPOS DE MUDANÇAS IDENTIFICADAS:")
        print("-" * 50)
        
        mudancas_por_campo = {}
        for registro in mudancas_reais:
            for mudanca in registro['mudancas']:
                campo = mudanca['campo']
                if campo not in mudancas_por_campo:
                    mudancas_por_campo[campo] = 0
                mudancas_por_campo[campo] += 1
        
        for campo, count in sorted(mudancas_por_campo.items()):
            pct = (count / com_mudancas) * 100
            print(f"   {campo:35}: {count:,} mudanças ({pct:.1f}%)")
        
        # Mostrar exemplos
        print(f"\n💡 EXEMPLOS DE MUDANÇAS REAIS (primeiros 5):")
        print("-" * 80)
        
        for i, registro in enumerate(mudancas_reais[:5]):
            protocolo = registro['protocolo']
            mudancas = registro['mudancas']
            
            print(f"\n📋 PROTOCOLO {protocolo} ({len(mudancas)} mudanças):")
            for mudanca in mudancas:
                banco = mudanca['banco'][:30] if mudanca['banco'] else 'VAZIO'
                arquivo = mudanca['arquivo'][:30] if mudanca['arquivo'] else 'VAZIO'
                print(f"   • {mudanca['campo']}: '{banco}' → '{arquivo}'")
    
    # Mostrar alguns registros sem mudanças
    if sem_mudancas:
        print(f"\n✅ EXEMPLOS DE REGISTROS SEM MUDANÇAS (primeiros 10):")
        print("-" * 60)
        for protocolo in sem_mudancas[:10]:
            banco = registros_banco[protocolo]
            prot_ren = banco['protocolo_renovacao'][:15] if banco['protocolo_renovacao'] else 'VAZIO'
            status = banco['status_protocolo_renovacao'][:15] if banco['status_protocolo_renovacao'] else 'VAZIO'
            print(f"   📋 {protocolo}: Prot.Ren={prot_ren}, Status={status}")
    
    return {
        'total': total,
        'com_mudancas': com_mudancas,
        'sem_mudancas': sem_mudancas_count,
        'mudancas_reais': mudancas_reais
    }

def main():
    """Função principal"""
    try:
        resultado = analisar_consistencia_renovacao()
        
        print(f"\n🎉 ANÁLISE DE CONSISTÊNCIA CONCLUÍDA!")
        print("=" * 50)
        
        if resultado['com_mudancas'] > 0:
            print(f"🔄 ATUALIZAÇÕES NECESSÁRIAS:")
            print(f"   📊 {resultado['com_mudancas']:,} registros precisam de UPDATE")
            print(f"   ✅ {resultado['sem_mudancas']:,} registros já estão corretos")
            
            pct_atualizacao = (resultado['com_mudancas'] / resultado['total']) * 100
            print(f"   📈 Taxa de atualização REAL: {pct_atualizacao:.1f}%")
            
            print(f"\n🎯 PRÓXIMO PASSO:")
            print(f"   Criar script de atualização para {resultado['com_mudancas']:,} registros")
            print(f"   (Excluindo campo 'prazo' que é calculado dinamicamente)")
        else:
            print(f"✅ NENHUMA ATUALIZAÇÃO NECESSÁRIA!")
            print(f"   Todos os {resultado['total']:,} registros já estão corretos")
            print(f"   (Apenas campo 'prazo' muda dinamicamente)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
