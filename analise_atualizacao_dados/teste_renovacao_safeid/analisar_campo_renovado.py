#!/usr/bin/env python3
"""
ANÁLISE DO CAMPO RENOVADO - SAFEID
Foca no campo principal: Renovado (Não/Sim)
"""

import xlrd
import psycopg2

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="crm_ccamp",
        user="postgres",
        password="@Certificado123"
    )

def verificar_campo_renovado_banco():
    """Verifica se existe campo 'renovado' no banco"""
    print("🗄️ VERIFICANDO CAMPO 'RENOVADO' NO BANCO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se existe campo renovado
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        AND column_name ILIKE '%renovado%'
    """)
    
    campo_renovado = cursor.fetchall()
    
    if campo_renovado:
        print(f"✅ CAMPO RENOVADO ENCONTRADO:")
        for col_name, data_type, max_length in campo_renovado:
            tamanho = str(max_length) if max_length else '-'
            print(f"   {col_name}: {data_type} ({tamanho})")
    else:
        print(f"❌ CAMPO 'RENOVADO' NÃO ENCONTRADO NO BANCO")
        
        # Verificar campos similares
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'emissao' 
            AND (column_name ILIKE '%renov%' 
                 OR column_name ILIKE '%status%'
                 OR column_name ILIKE '%flag%')
            ORDER BY column_name
        """)
        
        campos_similares = cursor.fetchall()
        if campos_similares:
            print(f"\n🔍 CAMPOS SIMILARES ENCONTRADOS:")
            for (col_name,) in campos_similares:
                print(f"   {col_name}")
    
    conn.close()
    return len(campo_renovado) > 0

def analisar_campo_renovado_arquivo():
    """Analisa o campo Renovado no arquivo"""
    print(f"\n📖 ANALISANDO CAMPO 'RENOVADO' NO ARQUIVO")
    print("=" * 50)
    
    wb = xlrd.open_workbook("../renovacao_safeid/RelatorioSafeID.xls")
    sheet = wb.sheet_by_index(0)
    
    # Encontrar coluna Renovado
    headers = []
    col_renovado = None
    col_protocolo = None
    
    for col in range(sheet.ncols):
        header = str(sheet.cell_value(0, col)).strip()
        headers.append(header)
        
        if header == 'Renovado':
            col_renovado = col
        elif header == 'Protocolo':
            col_protocolo = col
    
    if col_renovado is None:
        print(f"❌ ERRO: Coluna 'Renovado' não encontrada!")
        return [], []
    
    print(f"✅ Coluna 'Renovado' encontrada: {col_renovado}")
    print(f"✅ Coluna 'Protocolo' encontrada: {col_protocolo}")
    
    # Analisar valores
    valores_renovado = []
    protocolos_sim = []
    protocolos_nao = []
    
    print(f"\n📊 ANALISANDO VALORES DO CAMPO 'RENOVADO':")
    print("-" * 40)
    
    for row in range(1, sheet.nrows):
        protocolo = str(sheet.cell_value(row, col_protocolo)).strip()
        renovado = str(sheet.cell_value(row, col_renovado)).strip()
        
        valores_renovado.append(renovado)
        
        if renovado.upper() == 'SIM':
            protocolos_sim.append(protocolo)
        elif renovado.upper() == 'NÃO' or renovado.upper() == 'NAO':
            protocolos_nao.append(protocolo)
        
        # Mostrar primeiros 20 para debug
        if row <= 20:
            print(f"   Linha {row:2d}: {protocolo} → '{renovado}'")
    
    # Estatísticas
    total = len(valores_renovado)
    count_sim = len(protocolos_sim)
    count_nao = len(protocolos_nao)
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de registros: {total}")
    print(f"   Renovado = 'Sim': {count_sim} ({count_sim/total*100:.1f}%)")
    print(f"   Renovado = 'Não': {count_nao} ({count_nao/total*100:.1f}%)")
    print(f"   Outros valores: {total - count_sim - count_nao}")
    
    # Valores únicos
    valores_unicos = set(valores_renovado)
    print(f"\n🔍 VALORES ÚNICOS ENCONTRADOS:")
    for valor in sorted(valores_unicos):
        count = valores_renovado.count(valor)
        print(f"   '{valor}': {count} ocorrências")
    
    return protocolos_sim, protocolos_nao

def comparar_com_banco(protocolos_sim, protocolos_nao):
    """Compara valores do arquivo com banco"""
    print(f"\n\n🔍 COMPARAÇÃO ARQUIVO vs BANCO")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se campo renovado existe no banco
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        AND column_name = 'renovado'
    """)
    
    campo_existe = cursor.fetchone()
    
    if not campo_existe:
        print(f"❌ CAMPO 'renovado' NÃO EXISTE NO BANCO")
        print(f"   Será necessário criar o campo ou usar outro campo existente")
        
        # Verificar alguns protocolos para ver dados atuais
        print(f"\n🔍 VERIFICANDO DADOS ATUAIS (primeiros 5 'Sim'):")
        for i, protocolo in enumerate(protocolos_sim[:5], 1):
            cursor.execute("""
                SELECT protocolo, status_do_certificado, produto
                FROM emissao WHERE protocolo = %s
            """, (int(protocolo),))
            
            resultado = cursor.fetchone()
            if resultado:
                prot, status, produto = resultado
                print(f"   {i}. {protocolo}: Status='{status}', Produto='{produto}'")
        
        conn.close()
        return
    
    print(f"✅ CAMPO 'renovado' EXISTE NO BANCO")
    
    # Comparar valores
    mudancas_identificadas = []
    
    print(f"\n🔍 VERIFICANDO MUDANÇAS (amostra):")
    print("-" * 40)
    
    # Verificar protocolos que estão como 'Sim' no arquivo
    print(f"\n📋 PROTOCOLOS COM 'Renovado = Sim' NO ARQUIVO:")
    for i, protocolo in enumerate(protocolos_sim[:10], 1):  # Primeiros 10
        cursor.execute("""
            SELECT protocolo, renovado
            FROM emissao WHERE protocolo = %s
        """, (int(protocolo),))
        
        resultado = cursor.fetchone()
        if resultado:
            prot, renovado_banco = resultado
            renovado_banco_str = str(renovado_banco) if renovado_banco else 'NULL'
            
            if renovado_banco_str.upper() != 'SIM':
                mudancas_identificadas.append({
                    'protocolo': protocolo,
                    'banco': renovado_banco_str,
                    'arquivo': 'Sim'
                })
                print(f"   {i:2d}. {protocolo}: '{renovado_banco_str}' → 'Sim' ✅ MUDANÇA")
            else:
                print(f"   {i:2d}. {protocolo}: '{renovado_banco_str}' → 'Sim' ⚪ SEM MUDANÇA")
    
    # Verificar protocolos que estão como 'Não' no arquivo
    print(f"\n📋 PROTOCOLOS COM 'Renovado = Não' NO ARQUIVO:")
    for i, protocolo in enumerate(protocolos_nao[:10], 1):  # Primeiros 10
        cursor.execute("""
            SELECT protocolo, renovado
            FROM emissao WHERE protocolo = %s
        """, (int(protocolo),))
        
        resultado = cursor.fetchone()
        if resultado:
            prot, renovado_banco = resultado
            renovado_banco_str = str(renovado_banco) if renovado_banco else 'NULL'
            
            if renovado_banco_str.upper() != 'NÃO' and renovado_banco_str.upper() != 'NAO':
                mudancas_identificadas.append({
                    'protocolo': protocolo,
                    'banco': renovado_banco_str,
                    'arquivo': 'Não'
                })
                print(f"   {i:2d}. {protocolo}: '{renovado_banco_str}' → 'Não' ✅ MUDANÇA")
            else:
                print(f"   {i:2d}. {protocolo}: '{renovado_banco_str}' → 'Não' ⚪ SEM MUDANÇA")
    
    conn.close()
    
    print(f"\n📊 RESUMO DAS MUDANÇAS:")
    print(f"   Total de mudanças identificadas: {len(mudancas_identificadas)}")
    
    if mudancas_identificadas:
        print(f"\n🔍 EXEMPLOS DE MUDANÇAS:")
        for mudanca in mudancas_identificadas[:5]:
            print(f"   {mudanca['protocolo']}: '{mudanca['banco']}' → '{mudanca['arquivo']}'")
    
    return mudancas_identificadas

def main():
    """Função principal"""
    print("🔍 ANÁLISE DO CAMPO RENOVADO - SAFEID")
    print("=" * 60)
    print("🎯 Foco: Campo 'Renovado' (Não/Sim) - CAMPO CHAVE")
    print()
    
    try:
        # Verificar se campo existe no banco
        campo_existe = verificar_campo_renovado_banco()
        
        # Analisar arquivo
        protocolos_sim, protocolos_nao = analisar_campo_renovado_arquivo()
        
        # Comparar com banco
        mudancas = comparar_com_banco(protocolos_sim, protocolos_nao)
        
        print(f"\n🎯 CONCLUSÕES FINAIS:")
        print("=" * 30)
        print(f"📊 Protocolos 'Renovado = Sim': {len(protocolos_sim)}")
        print(f"📊 Protocolos 'Renovado = Não': {len(protocolos_nao)}")
        
        if campo_existe:
            print(f"📝 Mudanças identificadas: {len(mudancas)}")
            print(f"🎯 Campo principal de atualização: 'renovado'")
        else:
            print(f"⚠️ Campo 'renovado' não existe no banco")
            print(f"   Será necessário criar ou mapear para outro campo")
        
        print(f"\n💡 INTERPRETAÇÃO:")
        print(f"   'Não' → 'Sim': Certificado foi renovado")
        print(f"   'Sim' → 'Sim': Já estava renovado")
        print(f"   'Não' → 'Não': Ainda não renovado")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
