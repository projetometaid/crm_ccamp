#!/usr/bin/env python3
"""
ANÁLISE ESPECÍFICA AGOSTO 2025 - RENOVAÇÃO GERAL
Analisa APENAS os 1.300 registros do arquivo GestaoRenovacao (1).xls
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

def obter_protocolos_agosto_2025():
    """Obtém os protocolos específicos do arquivo de agosto 2025"""
    print("📁 LENDO ARQUIVO AGOSTO 2025...")
    
    wb = xlrd.open_workbook("../GestaoRenovacao (1).xls")
    sheet = wb.sheet_by_index(0)
    
    protocolos = []
    for row in range(1, sheet.nrows):
        protocolo_str = str(sheet.cell_value(row, 13)).strip()
        try:
            protocolo = int(float(protocolo_str))
            protocolos.append(protocolo)
        except:
            continue
    
    print(f"✅ Protocolos de agosto 2025: {len(protocolos):,}")
    return protocolos

def analisar_agosto_2025_especifico():
    """Analisa especificamente os 1.300 registros de agosto 2025"""
    print("🎯 ANÁLISE ESPECÍFICA - AGOSTO 2025")
    print("=" * 60)
    print("📊 Foco: APENAS os 1.300 registros do arquivo atual")
    print()
    
    # Obter protocolos do arquivo
    protocolos_agosto = obter_protocolos_agosto_2025()
    
    if not protocolos_agosto:
        print("❌ Nenhum protocolo encontrado no arquivo!")
        return
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar dados específicos desses protocolos
    placeholders = ','.join(['%s'] * len(protocolos_agosto))
    
    cursor.execute(f"""
        SELECT 
            protocolo,
            razao_social,
            telefone,
            e_mail,
            produto,
            data_fim_validade,
            prazo,
            protocolo_renovacao,
            status_protocolo_renovacao,
            nome_da_ar_protocolo_renovacao,
            produto_protocolo_renovacao
        FROM renovacao_geral
        WHERE protocolo IN ({placeholders})
        ORDER BY protocolo
    """, protocolos_agosto)
    
    registros = cursor.fetchall()
    
    print(f"📊 RESUMO AGOSTO 2025:")
    print(f"   📁 Protocolos no arquivo: {len(protocolos_agosto):,}")
    print(f"   🗄️ Encontrados no banco: {len(registros):,}")
    
    if len(registros) != len(protocolos_agosto):
        print(f"   ⚠️ Diferença: {len(protocolos_agosto) - len(registros)} protocolos não encontrados")
    
    return registros

def analisar_status_renovacao_agosto(registros):
    """Analisa status de renovação dos registros de agosto"""
    print(f"\n📊 STATUS DE RENOVAÇÃO - AGOSTO 2025")
    print("-" * 50)
    
    # Contar por status
    status_count = {}
    for registro in registros:
        status = registro[8]  # status_protocolo_renovacao
        if status not in status_count:
            status_count[status] = 0
        status_count[status] += 1
    
    total = len(registros)
    
    print(f"📋 DISTRIBUIÇÃO POR STATUS ({total:,} registros):")
    for status, count in sorted(status_count.items()):
        pct = (count / total) * 100
        
        if status == 'EMITIDO':
            emoji = "✅"
            descricao = "Renovação concluída"
        elif status == 'PENDENTE':
            emoji = "⏳"
            descricao = "Aguardando renovação"
        elif status == 'CANCELADO':
            emoji = "❌"
            descricao = "Cliente cancelou"
        else:
            emoji = "❓"
            descricao = "Status indefinido"
        
        print(f"   {emoji} {status:15} | {count:,} ({pct:.1f}%) | {descricao}")

def analisar_ars_agosto(registros):
    """Analisa distribuição por ARs nos registros de agosto"""
    print(f"\n🏢 DISTRIBUIÇÃO POR ARs - AGOSTO 2025")
    print("-" * 50)
    
    # Contar por AR
    ar_count = {}
    sem_ar = 0
    
    for registro in registros:
        ar = registro[9]  # nome_da_ar_protocolo_renovacao
        
        if ar and ar.strip():
            if ar not in ar_count:
                ar_count[ar] = 0
            ar_count[ar] += 1
        else:
            sem_ar += 1
    
    total_com_ar = sum(ar_count.values())
    total = len(registros)
    
    print(f"📊 RESUMO ARs ({total:,} registros):")
    print(f"   ✅ Com AR definida: {total_com_ar:,} ({(total_com_ar/total)*100:.1f}%)")
    print(f"   ⚪ Sem AR (oportunidades): {sem_ar:,} ({(sem_ar/total)*100:.1f}%)")
    
    if ar_count:
        print(f"\n📋 DISTRIBUIÇÃO POR AR:")
        
        # Separar AR Campinas dos concorrentes
        campinas_total = 0
        concorrentes_total = 0
        
        for ar, count in sorted(ar_count.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_com_ar) * 100
            
            if 'CERTIFICADO CAMPINAS' in ar.upper():
                campinas_total += count
                status = "🏆 NOSSA AR"
            else:
                concorrentes_total += count
                status = "🔴 CONCORRENTE"
            
            print(f"   {ar[:35]:35} | {count:,} ({pct:.1f}%) | {status}")
        
        print(f"\n🏆 RESUMO COMPETITIVO:")
        print(f"   🏆 AR Certificado Campinas: {campinas_total:,} ({(campinas_total/total_com_ar)*100:.1f}%)")
        print(f"   🔴 Concorrentes: {concorrentes_total:,} ({(concorrentes_total/total_com_ar)*100:.1f}%)")

def analisar_oportunidades_agosto(registros):
    """Analisa oportunidades de negócio nos registros de agosto"""
    print(f"\n🎯 OPORTUNIDADES DE NEGÓCIO - AGOSTO 2025")
    print("-" * 50)
    
    # Identificar oportunidades (sem AR e status PENDENTE)
    oportunidades = []
    processados = []
    
    for registro in registros:
        protocolo = registro[0]
        status = registro[8]  # status_protocolo_renovacao
        ar = registro[9]  # nome_da_ar_protocolo_renovacao
        
        if status == 'PENDENTE' and (not ar or ar.strip() == ''):
            oportunidades.append(registro)
        else:
            processados.append(registro)
    
    total = len(registros)
    oport_count = len(oportunidades)
    proc_count = len(processados)
    
    print(f"📊 RESUMO DE OPORTUNIDADES:")
    print(f"   🎯 Oportunidades (PENDENTE sem AR): {oport_count:,} ({(oport_count/total)*100:.1f}%)")
    print(f"   ✅ Já processados: {proc_count:,} ({(proc_count/total)*100:.1f}%)")
    
    if oportunidades:
        # Analisar por prazo
        print(f"\n⏰ PRIORIZAÇÃO POR PRAZO:")
        
        vencidos = []
        criticos = []
        urgentes = []
        normais = []
        
        for registro in oportunidades:
            prazo = registro[6]  # prazo
            
            if prazo <= 0:
                vencidos.append(registro)
            elif prazo <= 30:
                criticos.append(registro)
            elif prazo <= 60:
                urgentes.append(registro)
            else:
                normais.append(registro)
        
        print(f"   🚨 VENCIDOS: {len(vencidos):,} ({(len(vencidos)/oport_count)*100:.1f}%)")
        print(f"   🔴 CRÍTICOS (≤30 dias): {len(criticos):,} ({(len(criticos)/oport_count)*100:.1f}%)")
        print(f"   🟠 URGENTES (31-60 dias): {len(urgentes):,} ({(len(urgentes)/oport_count)*100:.1f}%)")
        print(f"   🟢 NORMAIS (>60 dias): {len(normais):,} ({(len(normais)/oport_count)*100:.1f}%)")
        
        # Analisar por produto
        print(f"\n🏷️ OPORTUNIDADES POR PRODUTO:")
        
        produto_count = {}
        for registro in oportunidades:
            produto = registro[4]  # produto
            if produto not in produto_count:
                produto_count[produto] = 0
            produto_count[produto] += 1
        
        for produto, count in sorted(produto_count.items(), key=lambda x: x[1], reverse=True):
            pct = (count / oport_count) * 100
            
            # Estimar receita potencial
            if 'e-CNPJ' in produto:
                valor_estimado = 200
                emoji = "💼"
            elif 'e-CPF' in produto:
                valor_estimado = 100
                emoji = "👤"
            else:
                valor_estimado = 150
                emoji = "📄"
            
            receita_potencial = count * valor_estimado
            
            print(f"   {emoji} {produto[:30]:30} | {count:,} ({pct:.1f}%) | R$ {receita_potencial:,.2f}")
        
        # Calcular receita total potencial
        receita_total = sum(count * (200 if 'e-CNPJ' in produto else 100) 
                           for produto, count in produto_count.items())
        
        print(f"\n💰 RECEITA POTENCIAL AGOSTO 2025: R$ {receita_total:,.2f}")

def gerar_lista_contatos_agosto(registros):
    """Gera lista de contatos prioritários para agosto 2025"""
    print(f"\n📞 LISTA DE CONTATOS PRIORITÁRIOS - AGOSTO 2025")
    print("-" * 60)
    
    # Filtrar oportunidades críticas
    contatos_criticos = []
    
    for registro in registros:
        status = registro[8]  # status_protocolo_renovacao
        ar = registro[9]  # nome_da_ar_protocolo_renovacao
        prazo = registro[6]  # prazo
        
        # Oportunidade crítica: PENDENTE, sem AR, prazo <= 30
        if status == 'PENDENTE' and (not ar or ar.strip() == '') and prazo <= 30:
            contatos_criticos.append(registro)
    
    # Ordenar por prazo (mais urgente primeiro)
    contatos_criticos.sort(key=lambda x: x[6])  # ordenar por prazo
    
    if contatos_criticos:
        print(f"🚨 CONTATOS MAIS URGENTES ({len(contatos_criticos)} registros):")
        print("-" * 80)
        print(f"{'Protocolo':12} | {'Razão Social':25} | {'Telefone':15} | {'Produto':12} | {'Prazo':6}")
        print("-" * 80)
        
        for i, registro in enumerate(contatos_criticos[:15]):  # Top 15
            protocolo = registro[0]
            razao = registro[1][:25] if registro[1] else 'N/A'
            telefone = registro[2][:15] if registro[2] else 'N/A'
            produto = registro[4][:12] if registro[4] else 'N/A'
            prazo = registro[6]
            
            if prazo <= 0:
                emoji = "🚨"
            elif prazo <= 15:
                emoji = "🔴"
            else:
                emoji = "🟠"
            
            print(f"{protocolo:12} | {razao:25} | {telefone:15} | {produto:12} | {emoji}{prazo:5}")
    else:
        print("✅ Nenhum contato crítico encontrado para agosto 2025!")

def main():
    """Função principal"""
    try:
        print("🎯 ANÁLISE ESPECÍFICA AGOSTO 2025 - RENOVAÇÃO GERAL")
        print("=" * 70)
        print("📊 Foco: APENAS os 1.300 registros do arquivo atual")
        print()
        
        # Analisar registros específicos de agosto 2025
        registros = analisar_agosto_2025_especifico()
        
        if not registros:
            print("❌ Nenhum registro encontrado!")
            return
        
        # Análises específicas
        analisar_status_renovacao_agosto(registros)
        analisar_ars_agosto(registros)
        analisar_oportunidades_agosto(registros)
        gerar_lista_contatos_agosto(registros)
        
        print(f"\n🎉 ANÁLISE AGOSTO 2025 CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 {len(registros):,} registros analisados")
        print(f"🎯 Foco específico em agosto 2025")
        print(f"📞 Lista de contatos prioritários gerada")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
