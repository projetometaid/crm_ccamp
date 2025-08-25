#!/usr/bin/env python3
"""
ANÁLISE DE OPORTUNIDADES - RENOVACAO_SAFEID
Identifica padrões, oportunidades e insights do produto SafeID e-CPF
"""

import psycopg2
from datetime import datetime, timedelta

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def analisar_distribuicao_produtos():
    """Analisa distribuição por validade e período de uso"""
    print("📊 ANÁLISE DE DISTRIBUIÇÃO - SAFEID E-CPF")
    print("=" * 60)
    print("🎯 Padrões de validade e período de uso")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Distribuição por validade do certificado
    cursor.execute("""
        SELECT 
            validade_certificado,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY validade_certificado
        ORDER BY quantidade DESC
    """)
    
    print("📋 DISTRIBUIÇÃO POR VALIDADE DO CERTIFICADO:")
    validades = cursor.fetchall()
    total = sum(qtd for _, qtd in validades)
    
    for validade, quantidade in validades:
        pct = (quantidade / total) * 100
        print(f"   📅 {validade:10}: {quantidade:,} ({pct:.1f}%)")
    
    # Distribuição por período de uso
    cursor.execute("""
        SELECT 
            periodo_de_uso,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY periodo_de_uso
        ORDER BY quantidade DESC
    """)
    
    print(f"\n📋 DISTRIBUIÇÃO POR PERÍODO DE USO:")
    periodos = cursor.fetchall()
    
    for periodo, quantidade in periodos:
        pct = (quantidade / total) * 100
        print(f"   ⏰ {periodo:12}: {quantidade:,} ({pct:.1f}%)")
    
    # Combinação validade x período
    cursor.execute("""
        SELECT 
            validade_certificado,
            periodo_de_uso,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY validade_certificado, periodo_de_uso
        ORDER BY quantidade DESC
    """)
    
    print(f"\n📊 COMBINAÇÕES MAIS POPULARES:")
    combinacoes = cursor.fetchall()
    
    for validade, periodo, quantidade in combinacoes[:5]:
        pct = (quantidade / total) * 100
        print(f"   🎯 {validade} + {periodo}: {quantidade:,} ({pct:.1f}%)")
    
    conn.close()

def analisar_renovacoes():
    """Analisa padrões de renovação"""
    print(f"\n🔄 ANÁLISE DE RENOVAÇÕES")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Status de renovação
    cursor.execute("""
        SELECT 
            renovado,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY renovado
        ORDER BY quantidade DESC
    """)
    
    renovacoes = cursor.fetchall()
    total = sum(qtd for _, qtd in renovacoes)
    
    print("📊 STATUS DE RENOVAÇÃO:")
    for status, quantidade in renovacoes:
        pct = (quantidade / total) * 100
        emoji = "🔄" if status == 'Sim' else "🆕"
        print(f"   {emoji} {status:3}: {quantidade:,} ({pct:.1f}%)")
    
    # Primeira emissão
    cursor.execute("""
        SELECT 
            primeira_emissao,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY primeira_emissao
        ORDER BY quantidade DESC
    """)
    
    print(f"\n📊 PRIMEIRA EMISSÃO:")
    for status, quantidade in cursor.fetchall():
        pct = (quantidade / total) * 100
        emoji = "🆕" if status == 'Sim' else "🔄"
        print(f"   {emoji} {status:3}: {quantidade:,} ({pct:.1f}%)")
    
    # Análise de renovações por período
    cursor.execute("""
        SELECT 
            periodo_de_uso,
            COUNT(CASE WHEN renovado = 'Sim' THEN 1 END) as renovados,
            COUNT(*) as total
        FROM renovacao_safeid
        GROUP BY periodo_de_uso
        ORDER BY total DESC
    """)
    
    print(f"\n📊 TAXA DE RENOVAÇÃO POR PERÍODO:")
    for periodo, renovados, total_periodo in cursor.fetchall():
        taxa = (renovados / total_periodo) * 100 if total_periodo > 0 else 0
        print(f"   ⏰ {periodo:12}: {renovados:,}/{total_periodo:,} ({taxa:.1f}%)")
    
    conn.close()

def analisar_vencimentos_proximos():
    """Analisa certificados com vencimento próximo"""
    print(f"\n⏰ ANÁLISE DE VENCIMENTOS PRÓXIMOS")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Data atual
    hoje = datetime.now()
    
    # Certificados vencendo nos próximos 30, 60 e 90 dias
    for dias in [30, 60, 90]:
        data_limite = hoje + timedelta(days=dias)
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM renovacao_safeid
            WHERE data_fim_do_uso <= %s
            AND data_fim_do_uso >= %s
            AND status_do_certificado = 'Emitido'
            AND status_do_periodo_de_uso = 'Habilitado'
        """, (data_limite, hoje))
        
        quantidade = cursor.fetchone()[0]
        
        if dias == 30:
            emoji = "🚨"
            urgencia = "CRÍTICO"
        elif dias == 60:
            emoji = "🟠"
            urgencia = "URGENTE"
        else:
            emoji = "🟡"
            urgencia = "ATENÇÃO"
        
        print(f"   {emoji} Próximos {dias:2} dias ({urgencia:8}): {quantidade:,} certificados")
    
    # Certificados já vencidos
    cursor.execute("""
        SELECT COUNT(*) 
        FROM renovacao_safeid
        WHERE data_fim_do_uso < %s
        AND status_do_certificado = 'Emitido'
        AND status_do_periodo_de_uso = 'Habilitado'
    """, (hoje,))
    
    vencidos = cursor.fetchone()[0]
    print(f"   🚨 Já vencidos (IMEDIATO): {vencidos:,} certificados")
    
    # Lista de contatos urgentes
    cursor.execute("""
        SELECT 
            protocolo,
            nome_razao_social,
            email_titular,
            telefone_titular,
            data_fim_do_uso,
            periodo_de_uso
        FROM renovacao_safeid
        WHERE data_fim_do_uso <= %s
        AND status_do_certificado = 'Emitido'
        AND status_do_periodo_de_uso = 'Habilitado'
        ORDER BY data_fim_do_uso ASC
        LIMIT 10
    """, (hoje + timedelta(days=30),))
    
    contatos_urgentes = cursor.fetchall()
    
    if contatos_urgentes:
        print(f"\n📞 TOP 10 CONTATOS MAIS URGENTES:")
        print("-" * 80)
        print(f"{'Protocolo':12} | {'Nome':25} | {'Telefone':15} | {'Vencimento':12} | {'Período':10}")
        print("-" * 80)
        
        for protocolo, nome, email, telefone, vencimento, periodo in contatos_urgentes:
            nome_short = nome[:25] if nome else 'N/A'
            telefone_short = telefone[:15] if telefone else 'N/A'
            venc_str = vencimento.strftime('%d/%m/%Y') if vencimento else 'N/A'
            periodo_short = periodo[:10] if periodo else 'N/A'
            
            dias_restantes = (vencimento - hoje).days if vencimento else 0
            
            if dias_restantes <= 0:
                emoji = "🚨"
            elif dias_restantes <= 15:
                emoji = "🔴"
            else:
                emoji = "🟠"
            
            print(f"{protocolo:12} | {nome_short:25} | {telefone_short:15} | {venc_str:12} | {periodo_short:10} {emoji}")
    
    conn.close()

def analisar_revogacoes():
    """Analisa padrões de revogação"""
    print(f"\n❌ ANÁLISE DE REVOGAÇÕES")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Total de revogações
    cursor.execute("""
        SELECT 
            status_do_certificado,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        GROUP BY status_do_certificado
        ORDER BY quantidade DESC
    """)
    
    status_dist = cursor.fetchall()
    total = sum(qtd for _, qtd in status_dist)
    
    print("📊 STATUS DOS CERTIFICADOS:")
    for status, quantidade in status_dist:
        pct = (quantidade / total) * 100
        emoji = "✅" if status == 'Emitido' else "❌"
        print(f"   {emoji} {status:10}: {quantidade:,} ({pct:.1f}%)")
    
    # Análise temporal das revogações
    cursor.execute("""
        SELECT 
            EXTRACT(YEAR FROM data_de_revogacao) as ano,
            EXTRACT(MONTH FROM data_de_revogacao) as mes,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        WHERE data_de_revogacao IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM data_de_revogacao), EXTRACT(MONTH FROM data_de_revogacao)
        ORDER BY ano, mes
    """)
    
    revogacoes_tempo = cursor.fetchall()
    
    if revogacoes_tempo:
        print(f"\n📊 REVOGAÇÕES POR PERÍODO:")
        for ano, mes, quantidade in revogacoes_tempo:
            print(f"   📅 {int(ano):4}/{int(mes):02d}: {quantidade:,} revogações")
    
    # Motivos de revogação (se disponível)
    cursor.execute("""
        SELECT 
            codigo_de_revogacao,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        WHERE codigo_de_revogacao IS NOT NULL
        GROUP BY codigo_de_revogacao
        ORDER BY quantidade DESC
    """)
    
    motivos = cursor.fetchall()
    
    if motivos:
        print(f"\n📊 CÓDIGOS DE REVOGAÇÃO:")
        for codigo, quantidade in motivos:
            print(f"   🔢 Código {codigo}: {quantidade:,} casos")
    
    conn.close()

def analisar_performance_temporal():
    """Analisa performance ao longo do tempo"""
    print(f"\n📈 ANÁLISE DE PERFORMANCE TEMPORAL")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Emissões por ano
    cursor.execute("""
        SELECT 
            EXTRACT(YEAR FROM data_inicio_do_uso) as ano,
            COUNT(*) as emissoes
        FROM renovacao_safeid
        GROUP BY EXTRACT(YEAR FROM data_inicio_do_uso)
        ORDER BY ano
    """)
    
    emissoes_ano = cursor.fetchall()
    
    print("📊 EMISSÕES POR ANO:")
    for ano, emissoes in emissoes_ano:
        print(f"   📅 {int(ano):4}: {emissoes:,} emissões")
    
    # Faturamento por ano
    cursor.execute("""
        SELECT 
            EXTRACT(YEAR FROM data_de_faturamento) as ano,
            COUNT(*) as faturamentos
        FROM renovacao_safeid
        GROUP BY EXTRACT(YEAR FROM data_de_faturamento)
        ORDER BY ano
    """)
    
    print(f"\n📊 FATURAMENTOS POR ANO:")
    for ano, faturamentos in cursor.fetchall():
        print(f"   💰 {int(ano):4}: {faturamentos:,} faturamentos")
    
    # Crescimento mensal (2024 e 2025)
    cursor.execute("""
        SELECT 
            EXTRACT(YEAR FROM data_inicio_do_uso) as ano,
            EXTRACT(MONTH FROM data_inicio_do_uso) as mes,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        WHERE EXTRACT(YEAR FROM data_inicio_do_uso) IN (2024, 2025)
        GROUP BY EXTRACT(YEAR FROM data_inicio_do_uso), EXTRACT(MONTH FROM data_inicio_do_uso)
        ORDER BY ano, mes
    """)
    
    print(f"\n📊 CRESCIMENTO MENSAL (2024-2025):")
    for ano, mes, quantidade in cursor.fetchall():
        print(f"   📅 {int(ano):4}/{int(mes):02d}: {quantidade:,} emissões")
    
    conn.close()

def calcular_receita_potencial():
    """Calcula receita potencial baseada em renovações"""
    print(f"\n💰 ANÁLISE DE RECEITA POTENCIAL")
    print("-" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Certificados ativos que podem renovar
    hoje = datetime.now()
    
    cursor.execute("""
        SELECT 
            periodo_de_uso,
            COUNT(*) as quantidade
        FROM renovacao_safeid
        WHERE status_do_certificado = 'Emitido'
        AND status_do_periodo_de_uso = 'Habilitado'
        AND data_fim_do_uso > %s
        GROUP BY periodo_de_uso
        ORDER BY quantidade DESC
    """, (hoje,))
    
    ativos = cursor.fetchall()
    
    # Valores estimados por período (valores aproximados)
    valores_periodo = {
        '12 Meses': 150,
        '24 Meses': 250,
        '36 Meses': 350
    }
    
    print("💰 RECEITA POTENCIAL DE RENOVAÇÕES:")
    receita_total = 0
    
    for periodo, quantidade in ativos:
        valor_unitario = valores_periodo.get(periodo, 200)
        receita_periodo = quantidade * valor_unitario
        receita_total += receita_periodo
        
        print(f"   💼 {periodo:12}: {quantidade:,} ativos × R$ {valor_unitario} = R$ {receita_periodo:,.2f}")
    
    print(f"\n🎯 RECEITA TOTAL POTENCIAL: R$ {receita_total:,.2f}")
    
    # Taxa de conversão estimada
    taxa_conversao = 0.3  # 30% estimado
    receita_realista = receita_total * taxa_conversao
    
    print(f"📊 RECEITA REALISTA (30% conversão): R$ {receita_realista:,.2f}")
    
    conn.close()

def main():
    """Função principal"""
    try:
        print("🔍 ANÁLISE DE OPORTUNIDADES - SAFEID E-CPF")
        print("=" * 70)
        print("🎯 Identificando padrões e oportunidades de negócio")
        print()
        
        # Análises específicas
        analisar_distribuicao_produtos()
        analisar_renovacoes()
        analisar_vencimentos_proximos()
        analisar_revogacoes()
        analisar_performance_temporal()
        calcular_receita_potencial()
        
        print(f"\n🎉 ANÁLISE DE OPORTUNIDADES CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 Produto SafeID e-CPF analisado")
        print(f"🎯 Oportunidades de renovação identificadas")
        print(f"💰 Receita potencial calculada")
        print(f"📞 Lista de contatos urgentes gerada")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
