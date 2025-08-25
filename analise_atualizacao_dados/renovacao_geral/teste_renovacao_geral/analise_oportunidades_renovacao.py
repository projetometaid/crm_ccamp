#!/usr/bin/env python3
"""
ANÁLISE DE OPORTUNIDADES DE RENOVAÇÃO
Identifica clientes que precisam ser contatados para renovação
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

def analisar_oportunidades_renovacao():
    """Analisa registros sem dados de renovação - oportunidades de negócio"""
    print("🎯 ANÁLISE DE OPORTUNIDADES DE RENOVAÇÃO")
    print("=" * 70)
    print("📞 Clientes que PRECISAM ser contatados para renovação")
    print("⚠️ Campos vazios = Oportunidades de negócio!")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM renovacao_geral")
    total_registros = cursor.fetchone()[0]
    
    # Registros SEM dados de renovação (oportunidades)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM renovacao_geral
        WHERE (nome_da_ar_protocolo_renovacao IS NULL OR nome_da_ar_protocolo_renovacao = '')
        AND (produto_protocolo_renovacao IS NULL OR produto_protocolo_renovacao = '')
        AND status_protocolo_renovacao = 'PENDENTE'
    """)
    
    oportunidades_total = cursor.fetchone()[0]
    
    print(f"📊 RESUMO GERAL:")
    print(f"   📋 Total de registros: {total_registros:,}")
    print(f"   🎯 Oportunidades de renovação: {oportunidades_total:,} ({(oportunidades_total/total_registros)*100:.1f}%)")
    print(f"   ✅ Já processados: {total_registros - oportunidades_total:,} ({((total_registros - oportunidades_total)/total_registros)*100:.1f}%)")
    
    return oportunidades_total

def analisar_por_prazo_vencimento():
    """Analisa oportunidades por prazo de vencimento"""
    print(f"\n⏰ ANÁLISE POR PRAZO DE VENCIMENTO")
    print("-" * 60)
    print("🚨 Priorização por urgência de renovação")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Oportunidades por faixa de prazo
    cursor.execute("""
        SELECT
            CASE
                WHEN prazo <= 0 THEN 'VENCIDO'
                WHEN prazo <= 30 THEN 'CRÍTICO (≤30 dias)'
                WHEN prazo <= 60 THEN 'URGENTE (31-60 dias)'
                WHEN prazo <= 90 THEN 'ATENÇÃO (61-90 dias)'
                WHEN prazo <= 180 THEN 'NORMAL (91-180 dias)'
                ELSE 'FUTURO (>180 dias)'
            END as faixa_prazo,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE (nome_da_ar_protocolo_renovacao IS NULL OR nome_da_ar_protocolo_renovacao = '')
        AND (produto_protocolo_renovacao IS NULL OR produto_protocolo_renovacao = '')
        AND status_protocolo_renovacao = 'PENDENTE'
        GROUP BY CASE
                WHEN prazo <= 0 THEN 'VENCIDO'
                WHEN prazo <= 30 THEN 'CRÍTICO (≤30 dias)'
                WHEN prazo <= 60 THEN 'URGENTE (31-60 dias)'
                WHEN prazo <= 90 THEN 'ATENÇÃO (61-90 dias)'
                WHEN prazo <= 180 THEN 'NORMAL (91-180 dias)'
                ELSE 'FUTURO (>180 dias)'
            END
        ORDER BY
            MIN(CASE
                WHEN prazo <= 0 THEN 1
                WHEN prazo <= 30 THEN 2
                WHEN prazo <= 60 THEN 3
                WHEN prazo <= 90 THEN 4
                WHEN prazo <= 180 THEN 5
                ELSE 6
            END)
    """)
    
    faixas_prazo = cursor.fetchall()
    total_oportunidades = sum(quantidade for _, quantidade in faixas_prazo)
    
    print(f"📊 PRIORIZAÇÃO POR URGÊNCIA ({total_oportunidades:,} oportunidades):")
    
    for faixa, quantidade in faixas_prazo:
        pct = (quantidade / total_oportunidades) * 100
        
        if 'VENCIDO' in faixa:
            emoji = "🚨"
            prioridade = "MÁXIMA"
        elif 'CRÍTICO' in faixa:
            emoji = "🔴"
            prioridade = "ALTA"
        elif 'URGENTE' in faixa:
            emoji = "🟠"
            prioridade = "MÉDIA"
        elif 'ATENÇÃO' in faixa:
            emoji = "🟡"
            prioridade = "BAIXA"
        else:
            emoji = "🟢"
            prioridade = "FUTURA"
        
        print(f"   {emoji} {faixa:20} | {quantidade:,} ({pct:.1f}%) | Prioridade: {prioridade}")
    
    conn.close()

def analisar_por_produto():
    """Analisa oportunidades por tipo de produto"""
    print(f"\n🏷️ ANÁLISE POR TIPO DE PRODUTO")
    print("-" * 60)
    print("💰 Potencial de receita por produto")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            produto,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE (nome_da_ar_protocolo_renovacao IS NULL OR nome_da_ar_protocolo_renovacao = '')
        AND (produto_protocolo_renovacao IS NULL OR produto_protocolo_renovacao = '')
        AND status_protocolo_renovacao = 'PENDENTE'
        GROUP BY produto
        ORDER BY quantidade DESC
    """)
    
    produtos = cursor.fetchall()
    total_produtos = sum(quantidade for _, quantidade in produtos)
    
    print(f"📊 OPORTUNIDADES POR PRODUTO ({total_produtos:,} total):")
    
    for produto, quantidade in produtos:
        pct = (quantidade / total_produtos) * 100
        
        # Estimar valor médio por produto (valores aproximados)
        if 'e-CNPJ' in produto:
            valor_estimado = 200  # R$ 200 por e-CNPJ
            emoji = "💼"
        elif 'e-CPF' in produto:
            valor_estimado = 100  # R$ 100 por e-CPF
            emoji = "👤"
        else:
            valor_estimado = 150  # Valor médio
            emoji = "📄"
        
        receita_potencial = quantidade * valor_estimado
        
        print(f"   {emoji} {produto:25} | {quantidade:,} ({pct:.1f}%) | Potencial: R$ {receita_potencial:,.2f}")
    
    # Calcular receita total potencial
    receita_total = sum(quantidade * (200 if 'e-CNPJ' in produto else 100) 
                       for produto, quantidade in produtos)
    
    print(f"\n💰 RECEITA POTENCIAL TOTAL: R$ {receita_total:,.2f}")
    
    conn.close()

def analisar_por_regiao():
    """Analisa oportunidades por região (baseado no local de atendimento)"""
    print(f"\n🗺️ ANÁLISE POR REGIÃO")
    print("-" * 60)
    print("📍 Distribuição geográfica das oportunidades")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN local_de_atendimento IS NULL OR local_de_atendimento = '' THEN 'NÃO INFORMADO'
                ELSE local_de_atendimento
            END as regiao,
            COUNT(*) as quantidade
        FROM renovacao_geral
        WHERE (nome_da_ar_protocolo_renovacao IS NULL OR nome_da_ar_protocolo_renovacao = '')
        AND (produto_protocolo_renovacao IS NULL OR produto_protocolo_renovacao = '')
        AND status_protocolo_renovacao = 'PENDENTE'
        GROUP BY CASE 
                WHEN local_de_atendimento IS NULL OR local_de_atendimento = '' THEN 'NÃO INFORMADO'
                ELSE local_de_atendimento
            END
        ORDER BY quantidade DESC
        LIMIT 15
    """)
    
    regioes = cursor.fetchall()
    total_regioes = sum(quantidade for _, quantidade in regioes)
    
    print(f"📊 TOP 15 REGIÕES COM OPORTUNIDADES ({total_regioes:,} total):")
    
    for regiao, quantidade in regioes:
        pct = (quantidade / total_regioes) * 100
        print(f"   📍 {regiao[:35]:35} | {quantidade:,} ({pct:.1f}%)")
    
    conn.close()

def gerar_lista_contatos_prioritarios():
    """Gera lista de contatos prioritários para renovação"""
    print(f"\n📞 LISTA DE CONTATOS PRIORITÁRIOS")
    print("-" * 60)
    print("🎯 Clientes que devem ser contatados IMEDIATAMENTE")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar registros críticos (vencidos ou vencendo em até 30 dias)
    cursor.execute("""
        SELECT 
            protocolo,
            razao_social,
            telefone,
            e_mail,
            produto,
            data_fim_validade,
            prazo,
            local_de_atendimento
        FROM renovacao_geral
        WHERE (nome_da_ar_protocolo_renovacao IS NULL OR nome_da_ar_protocolo_renovacao = '')
        AND (produto_protocolo_renovacao IS NULL OR produto_protocolo_renovacao = '')
        AND status_protocolo_renovacao = 'PENDENTE'
        AND prazo <= 30
        ORDER BY prazo ASC, produto DESC
        LIMIT 20
    """)
    
    contatos_prioritarios = cursor.fetchall()
    
    if contatos_prioritarios:
        print(f"🚨 TOP 20 CONTATOS MAIS URGENTES:")
        print("-" * 100)
        print(f"{'Protocolo':12} | {'Razão Social':25} | {'Telefone':15} | {'Produto':10} | {'Prazo':6} | {'Status':8}")
        print("-" * 100)
        
        for protocolo, razao, telefone, email, produto, data_fim, prazo, local in contatos_prioritarios:
            razao_short = razao[:25] if razao else 'N/A'
            telefone_short = telefone[:15] if telefone else 'N/A'
            produto_short = produto[:10] if produto else 'N/A'
            
            if prazo <= 0:
                status = "VENCIDO"
                emoji = "🚨"
            elif prazo <= 15:
                status = "CRÍTICO"
                emoji = "🔴"
            else:
                status = "URGENTE"
                emoji = "🟠"
            
            print(f"{protocolo:12} | {razao_short:25} | {telefone_short:15} | {produto_short:10} | {prazo:6} | {emoji}{status}")
    else:
        print("✅ Nenhum contato crítico encontrado!")
    
    conn.close()

def analisar_historico_renovacoes():
    """Analisa histórico de renovações para identificar padrões"""
    print(f"\n📈 ANÁLISE DE PADRÕES DE RENOVAÇÃO")
    print("-" * 60)
    print("🔍 Identificando tendências e oportunidades")
    print()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Taxa de conversão por status
    cursor.execute("""
        SELECT 
            status_protocolo_renovacao,
            COUNT(*) as quantidade
        FROM renovacao_geral
        GROUP BY status_protocolo_renovacao
        ORDER BY quantidade DESC
    """)
    
    status_distribuicao = cursor.fetchall()
    total_status = sum(quantidade for _, quantidade in status_distribuicao)
    
    print(f"📊 DISTRIBUIÇÃO POR STATUS ({total_status:,} total):")
    
    for status, quantidade in status_distribuicao:
        pct = (quantidade / total_status) * 100
        
        if status == 'EMITIDO':
            emoji = "✅"
            descricao = "Renovação concluída"
        elif status == 'PENDENTE':
            emoji = "⏳"
            descricao = "Aguardando contato/renovação"
        elif status == 'CANCELADO':
            emoji = "❌"
            descricao = "Cliente cancelou"
        elif status == 'REVOGADO':
            emoji = "🚫"
            descricao = "Certificado revogado"
        else:
            emoji = "❓"
            descricao = "Status indefinido"
        
        print(f"   {emoji} {status:15} | {quantidade:,} ({pct:.1f}%) | {descricao}")
    
    # Taxa de sucesso da AR Certificado Campinas
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status_protocolo_renovacao = 'EMITIDO' THEN 1 END) as emitidos,
            COUNT(*) as total
        FROM renovacao_geral
        WHERE nome_da_ar_protocolo_renovacao = 'AR CERTIFICADO CAMPINAS'
    """)
    
    emitidos_campinas, total_campinas = cursor.fetchone()
    
    if total_campinas > 0:
        taxa_sucesso = (emitidos_campinas / total_campinas) * 100
        print(f"\n🏆 PERFORMANCE AR CERTIFICADO CAMPINAS:")
        print(f"   ✅ Taxa de sucesso: {taxa_sucesso:.1f}% ({emitidos_campinas:,}/{total_campinas:,})")
    
    conn.close()

def main():
    """Função principal"""
    try:
        print("🎯 ANÁLISE DE OPORTUNIDADES DE RENOVAÇÃO")
        print("=" * 70)
        print("💼 Identificando clientes para contato comercial")
        print()
        
        # Análise geral de oportunidades
        total_oportunidades = analisar_oportunidades_renovacao()
        
        if total_oportunidades == 0:
            print("✅ Não há oportunidades pendentes!")
            return
        
        # Análises específicas
        analisar_por_prazo_vencimento()
        analisar_por_produto()
        analisar_por_regiao()
        gerar_lista_contatos_prioritarios()
        analisar_historico_renovacoes()
        
        print(f"\n🎉 ANÁLISE DE OPORTUNIDADES CONCLUÍDA!")
        print("=" * 50)
        print(f"🎯 {total_oportunidades:,} oportunidades identificadas")
        print(f"📞 Lista de contatos prioritários gerada")
        print(f"💰 Potencial de receita calculado")
        print(f"📊 Estratégia de abordagem definida")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
