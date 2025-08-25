#!/usr/bin/env python3
"""
VERIFICAÇÃO DIRETA DOS DADOS SAFEID NO BANCO
Busca apenas protocolos do SafeID no banco para ver campos reais
"""

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

def buscar_protocolos_safeid_banco():
    """Busca protocolos específicos do SafeID no banco"""
    print("🔍 BUSCANDO PROTOCOLOS SAFEID DIRETAMENTE NO BANCO")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Protocolos do arquivo SafeID (range conhecido)
    protocolos_safeid = [
        1005638878, 1005659099, 1005887636, 1005937323, 1006072460,
        1006221874, 1006260907, 1006286653, 1006294040, 1006298029
    ]
    
    print(f"🔍 Verificando {len(protocolos_safeid)} protocolos específicos do SafeID...")
    
    # Buscar dados completos desses protocolos
    for i, protocolo in enumerate(protocolos_safeid, 1):
        print(f"\n📋 {i:2d}. PROTOCOLO {protocolo}:")
        print("-" * 50)
        
        cursor.execute("SELECT * FROM emissao WHERE protocolo = %s", (protocolo,))
        resultado = cursor.fetchone()
        
        if resultado:
            # Obter nomes das colunas
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'emissao' 
                ORDER BY ordinal_position
            """)
            colunas = [row[0] for row in cursor.fetchall()]
            
            # Mostrar apenas campos preenchidos
            print(f"   ✅ ENCONTRADO - Campos preenchidos:")
            for j, (coluna, valor) in enumerate(zip(colunas, resultado)):
                if valor is not None and str(valor).strip():
                    valor_str = str(valor)[:50] if len(str(valor)) > 50 else str(valor)
                    print(f"      {coluna:<35}: {valor_str}")
            
            # Contar campos preenchidos vs vazios
            preenchidos = sum(1 for valor in resultado if valor is not None and str(valor).strip())
            vazios = len(resultado) - preenchidos
            print(f"   📊 Preenchidos: {preenchidos}/{len(resultado)} | Vazios: {vazios}")
            
        else:
            print(f"   ❌ NÃO ENCONTRADO")
    
    conn.close()

def verificar_campos_especificos():
    """Verifica campos específicos que podem existir"""
    print(f"\n\n🔍 VERIFICANDO CAMPOS ESPECÍFICOS DO SAFEID")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Campos que podem existir relacionados ao SafeID
    campos_verificar = [
        'renovado', 'safeid', 'periodo_de_uso', 'vouchercodigo', 
        'voucherpercentual', 'vouchervalor', 'data_inicio_validade',
        'data_fim_validade', 'status_do_certificado', 'produto'
    ]
    
    print(f"🔍 Verificando existência de campos específicos:")
    print("-" * 40)
    
    for campo in campos_verificar:
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'emissao' 
            AND column_name = %s
        """, (campo,))
        
        resultado = cursor.fetchone()
        if resultado:
            col_name, data_type, max_length = resultado
            tamanho = str(max_length) if max_length else '-'
            print(f"   ✅ {campo:<25}: {data_type} ({tamanho})")
        else:
            print(f"   ❌ {campo:<25}: NÃO EXISTE")
    
    conn.close()

def buscar_por_range_safeid():
    """Busca protocolos no range do SafeID"""
    print(f"\n\n📊 BUSCANDO POR RANGE DO SAFEID")
    print("=" * 50)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Range dos protocolos SafeID
    min_protocolo = 1005638878
    max_protocolo = 1006489801
    
    print(f"🔍 Buscando protocolos entre {min_protocolo:,} e {max_protocolo:,}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM emissao 
        WHERE protocolo >= %s AND protocolo <= %s
    """, (min_protocolo, max_protocolo))
    
    total_range = cursor.fetchone()[0]
    print(f"📊 Total de protocolos no range: {total_range:,}")
    
    # Buscar alguns exemplos
    cursor.execute("""
        SELECT protocolo, nome, produto, status_do_certificado,
               data_inicio_validade, data_fim_validade,
               vouchercodigo, voucherpercentual, vouchervalor,
               periodo_de_uso
        FROM emissao 
        WHERE protocolo >= %s AND protocolo <= %s
        ORDER BY protocolo
        LIMIT 10
    """, (min_protocolo, max_protocolo))
    
    registros = cursor.fetchall()
    
    print(f"\n📋 PRIMEIROS 10 REGISTROS NO RANGE:")
    print("-" * 80)
    
    for i, registro in enumerate(registros, 1):
        protocolo, nome, produto, status, data_inicio, data_fim, \
        voucher_cod, voucher_perc, voucher_val, periodo_uso = registro
        
        print(f"\n{i:2d}. {protocolo} | {nome[:30]}")
        print(f"    Produto: {produto}")
        print(f"    Status: {status}")
        print(f"    Data Início: {data_inicio}")
        print(f"    Data Fim: {data_fim}")
        print(f"    Voucher Código: {voucher_cod}")
        print(f"    Voucher Percentual: {voucher_perc}")
        print(f"    Voucher Valor: {voucher_val}")
        print(f"    Período de Uso: {periodo_uso}")
    
    conn.close()

def verificar_campo_renovado_detalhado():
    """Verifica especificamente o campo renovado"""
    print(f"\n\n🎯 VERIFICAÇÃO DETALHADA DO CAMPO 'RENOVADO'")
    print("=" * 60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se campo renovado existe
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'emissao' 
        AND column_name ILIKE '%renovado%'
    """)
    
    campos_renovado = cursor.fetchall()
    
    if campos_renovado:
        print(f"✅ CAMPOS RELACIONADOS A 'RENOVADO' ENCONTRADOS:")
        for col_name, data_type, max_length, nullable in campos_renovado:
            tamanho = str(max_length) if max_length else '-'
            print(f"   {col_name}: {data_type}({tamanho}) - NULL: {nullable}")
        
        # Verificar valores existentes
        for col_name, _, _, _ in campos_renovado:
            cursor.execute(f"""
                SELECT {col_name}, COUNT(*) 
                FROM emissao 
                WHERE protocolo >= 1005638878 AND protocolo <= 1006489801
                AND {col_name} IS NOT NULL
                GROUP BY {col_name}
                ORDER BY COUNT(*) DESC
            """)
            
            valores = cursor.fetchall()
            if valores:
                print(f"\n   📊 Valores em '{col_name}':")
                for valor, count in valores:
                    print(f"      '{valor}': {count} ocorrências")
            else:
                print(f"\n   📊 '{col_name}': Todos os valores são NULL")
    else:
        print(f"❌ NENHUM CAMPO RELACIONADO A 'RENOVADO' ENCONTRADO")
        
        # Verificar campos similares
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'emissao' 
            AND (column_name ILIKE '%renov%' 
                 OR column_name ILIKE '%status%'
                 OR column_name ILIKE '%flag%'
                 OR column_name ILIKE '%ativo%')
            ORDER BY column_name
        """)
        
        campos_similares = cursor.fetchall()
        if campos_similares:
            print(f"\n🔍 CAMPOS SIMILARES ENCONTRADOS:")
            for (col_name,) in campos_similares:
                print(f"   {col_name}")
    
    conn.close()

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DIRETA DOS DADOS SAFEID NO BANCO")
    print("=" * 70)
    print("🎯 Objetivo: Ver exatamente quais campos existem para protocolos SafeID")
    print()
    
    try:
        # Buscar protocolos específicos
        buscar_protocolos_safeid_banco()
        
        # Verificar campos específicos
        verificar_campos_especificos()
        
        # Buscar por range
        buscar_por_range_safeid()
        
        # Verificar campo renovado
        verificar_campo_renovado_detalhado()
        
        print(f"\n🎯 CONCLUSÃO:")
        print("=" * 30)
        print(f"✅ Verificação direta dos dados SafeID concluída")
        print(f"📊 Dados reais do banco analisados")
        print(f"🔍 Campos existentes identificados")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
