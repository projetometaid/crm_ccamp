#!/usr/bin/env python3
"""
Aplicação Flask para Dashboard CRM CCAMP
Interface web para análise e atualização de dados
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import psycopg2
import os
import hashlib
from datetime import datetime
import json
import openpyxl

app = Flask(__name__)
app.config['SECRET_KEY'] = 'crm-ccamp-dashboard-2024'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'port': '5433',
    'database': 'crm_ccamp',
    'user': 'postgres',
    'password': '@Certificado123'
}

def get_db_connection():
    """Obtém conexão com banco de dados"""
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    """Página principal do dashboard"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir arquivos estáticos"""
    return send_from_directory('static', filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_files():
    """Analisa arquivos enviados e compara com dados existentes"""
    try:
        files = request.files
        analysis_results = {}
        
        for table_name in ['emissao', 'renovacao-geral', 'renovacao-safeid']:
            file_key = f'file-{table_name}'
            if file_key in files:
                file = files[file_key]
                if file.filename:
                    # Processar arquivo Excel
                    data = read_excel_file(file)

                    # Analisar diferenças com banco
                    analysis = analyze_table_differences(table_name.replace('-', '_'), data)
                    analysis_results[table_name] = analysis
        
        return jsonify({
            'status': 'success',
            'results': analysis_results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def analyze_table_differences(table_name, new_data_df):
    """Analisa diferenças entre dados novos e existentes"""
    
    # Mapear nomes de tabelas
    table_mapping = {
        'renovacao_geral': 'renovacao_geral',
        'renovacao_safeid': 'renovacao_safeid',
        'emissao': 'emissao'
    }
    
    db_table = table_mapping.get(table_name, table_name)
    
    try:
        conn = get_db_connection()
        
        # Buscar dados existentes
        existing_query = f"SELECT * FROM {db_table}"
        existing_df = pd.read_sql(existing_query, conn)
        
        conn.close()
        
        # Análise de diferenças
        analysis = {
            'total_new_records': len(new_data_df),
            'existing_records': len(existing_df),
            'new_protocols': [],
            'updated_protocols': [],
            'field_changes': []
        }
        
        # Verificar protocolos novos e atualizações
        for _, new_row in new_data_df.iterrows():
            protocol = str(new_row.get('protocolo', ''))
            
            if not protocol:
                continue
                
            # Verificar se protocolo existe
            existing_row = existing_df[existing_df['protocolo'].astype(str) == protocol]
            
            if existing_row.empty:
                # Protocolo novo
                analysis['new_protocols'].append({
                    'protocol': protocol,
                    'table': table_name
                })
            else:
                # Verificar campos alterados
                existing_record = existing_row.iloc[0]
                changes = []
                
                for column in new_data_df.columns:
                    if column in existing_record.index:
                        new_value = new_row[column]
                        existing_value = existing_record[column]
                        
                        # Comparar valores (considerando NaN)
                        if pd.isna(new_value) and pd.isna(existing_value):
                            continue
                        elif pd.isna(new_value) or pd.isna(existing_value):
                            if not pd.isna(new_value):  # Só considerar mudança se novo valor não for NaN
                                changes.append({
                                    'field': column,
                                    'old_value': str(existing_value) if not pd.isna(existing_value) else '',
                                    'new_value': str(new_value)
                                })
                        elif str(new_value).strip() != str(existing_value).strip():
                            changes.append({
                                'field': column,
                                'old_value': str(existing_value),
                                'new_value': str(new_value)
                            })
                
                if changes:
                    analysis['updated_protocols'].append({
                        'protocol': protocol,
                        'table': table_name,
                        'changes': changes
                    })
                    
                    # Adicionar às mudanças de campo
                    for change in changes:
                        analysis['field_changes'].append({
                            'protocol': protocol,
                            'table': table_name,
                            'field': change['field'],
                            'old_value': change['old_value'],
                            'new_value': change['new_value']
                        })
        
        return analysis
        
    except Exception as e:
        print(f"Erro na análise da tabela {table_name}: {e}")
        return {
            'error': str(e),
            'total_new_records': len(new_data_df),
            'existing_records': 0,
            'new_protocols': [],
            'updated_protocols': [],
            'field_changes': []
        }

@app.route('/api/process', methods=['POST'])
def process_updates():
    """Processa atualizações no banco de dados"""
    try:
        files = request.files
        results = {}
        
        conn = get_db_connection()
        conn.autocommit = False
        
        try:
            for table_name in ['emissao', 'renovacao-geral', 'renovacao-safeid']:
                file_key = f'file-{table_name}'
                if file_key in files:
                    file = files[file_key]
                    if file.filename:
                        # Processar arquivo
                        df = pd.read_excel(file)
                        result = process_table_updates(conn, table_name.replace('-', '_'), df)
                        results[table_name] = result
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'results': results
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def process_table_updates(conn, table_name, df):
    """Processa atualizações para uma tabela específica"""
    
    cursor = conn.cursor()
    
    # Contadores
    new_records = 0
    updated_records = 0
    errors = 0
    
    for _, row in df.iterrows():
        try:
            protocol = str(row.get('protocolo', ''))
            if not protocol:
                continue
            
            # Verificar se registro existe
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE protocolo = %s", (protocol,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Atualizar registro existente
                update_fields = []
                update_values = []
                
                for column in df.columns:
                    if column != 'protocolo' and not pd.isna(row[column]):
                        update_fields.append(f"{column} = %s")
                        update_values.append(row[column])
                
                if update_fields:
                    update_values.append(protocol)
                    update_query = f"""
                        UPDATE {table_name} 
                        SET {', '.join(update_fields)}, 
                            data_ultima_atualizacao = CURRENT_TIMESTAMP
                        WHERE protocolo = %s
                    """
                    cursor.execute(update_query, update_values)
                    updated_records += 1
            else:
                # Inserir novo registro
                columns = [col for col in df.columns if not pd.isna(row[col])]
                values = [row[col] for col in columns if not pd.isna(row[col])]
                
                placeholders = ', '.join(['%s'] * len(values))
                columns_str = ', '.join(columns)
                
                insert_query = f"""
                    INSERT INTO {table_name} ({columns_str}, data_ultima_atualizacao) 
                    VALUES ({placeholders}, CURRENT_TIMESTAMP)
                """
                cursor.execute(insert_query, values)
                new_records += 1
                
        except Exception as e:
            print(f"Erro ao processar protocolo {protocol}: {e}")
            errors += 1
            continue
    
    return {
        'new_records': new_records,
        'updated_records': updated_records,
        'errors': errors,
        'total_processed': len(df)
    }

@app.route('/api/status')
def get_status():
    """Obtém status atual do banco de dados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar registros por tabela
        tables = ['emissao', 'renovacao_geral', 'renovacao_safeid']
        status = {}
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status[table] = count
        
        # Última atualização
        cursor.execute("""
            SELECT MAX(data_processamento) 
            FROM controle_atualizacoes 
            WHERE status = 'CONCLUIDO'
        """)
        last_update = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'table_counts': status,
            'last_update': last_update.isoformat() if last_update else None
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Iniciando Dashboard CRM CCAMP...")
    print("📊 Acesse: http://localhost:5000")
    print("🔧 Configuração do banco: PostgreSQL localhost:5433")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
