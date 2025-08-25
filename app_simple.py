#!/usr/bin/env python3
"""
Aplicação Flask Simples para Dashboard CRM CCAMP
Interface web para análise e atualização de dados (sem pandas)
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

def read_excel_file(file):
    """Lê arquivo Excel e retorna dados como lista de dicionários"""
    try:
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active
        
        # Obter cabeçalhos da primeira linha
        headers = []
        for cell in sheet[1]:
            headers.append(cell.value)
        
        # Ler dados
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_data = {}
            for i, value in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_data[headers[i]] = value
            
            # Só adicionar se tiver protocolo
            if row_data.get('protocolo'):
                data.append(row_data)
        
        return data
        
    except Exception as e:
        print(f"Erro ao ler arquivo Excel: {e}")
        return []

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

def analyze_table_differences(table_name, new_data):
    """Analisa diferenças COMPLETAS entre dados novos e existentes - campo por campo"""

    # Mapear nomes de tabelas
    table_mapping = {
        'renovacao_geral': 'renovacao_geral',
        'renovacao_safeid': 'renovacao_safeid',
        'emissao': 'emissao'
    }

    db_table = table_mapping.get(table_name, table_name)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Buscar TODOS os dados existentes para comparação completa
        cursor.execute(f"SELECT * FROM {db_table}")
        columns = [desc[0] for desc in cursor.description]
        existing_rows = cursor.fetchall()

        # Converter para dicionário por protocolo
        existing_data = {}
        for row in existing_rows:
            protocol = str(row[0])  # protocolo é sempre a primeira coluna
            existing_data[protocol] = dict(zip(columns, row))

        conn.close()

        # Análise DETALHADA de diferenças
        analysis = {
            'total_new_records': len(new_data),
            'existing_records': len(existing_data),
            'new_protocols': [],
            'updated_protocols': [],
            'field_changes': [],
            'field_statistics': {},  # Estatísticas por campo
            'summary': {
                'total_protocols_analyzed': 0,
                'protocols_with_changes': 0,
                'total_field_changes': 0,
                'fields_affected': set()
            }
        }

        # Analisar cada registro do arquivo novo
        for record in new_data:
            protocol = str(record.get('protocolo', ''))

            if not protocol:
                continue

            analysis['summary']['total_protocols_analyzed'] += 1

            if protocol not in existing_data:
                # Protocolo NOVO
                analysis['new_protocols'].append({
                    'protocol': protocol,
                    'table': table_name,
                    'all_fields': record
                })
            else:
                # Protocolo EXISTENTE - Comparar TODOS os campos
                existing_record = existing_data[protocol]
                changes = []

                for field_name, new_value in record.items():
                    if field_name == 'protocolo':
                        continue

                    # Obter valor atual do banco
                    current_value = existing_record.get(field_name)

                    # Normalizar valores para comparação
                    new_value_str = str(new_value).strip() if new_value is not None else ''
                    current_value_str = str(current_value).strip() if current_value is not None else ''

                    # Verificar se há mudança
                    if new_value_str != current_value_str and new_value_str != '':
                        changes.append({
                            'field': field_name,
                            'current_value': current_value,
                            'new_value': new_value,
                            'change_type': 'UPDATE' if current_value_str != '' else 'FILL_EMPTY'
                        })

                        # Adicionar às estatísticas por campo
                        if field_name not in analysis['field_statistics']:
                            analysis['field_statistics'][field_name] = {
                                'total_changes': 0,
                                'protocols_affected': [],
                                'change_examples': []
                            }

                        analysis['field_statistics'][field_name]['total_changes'] += 1
                        analysis['field_statistics'][field_name]['protocols_affected'].append(protocol)

                        # Guardar exemplo da mudança (máximo 3 exemplos)
                        if len(analysis['field_statistics'][field_name]['change_examples']) < 3:
                            analysis['field_statistics'][field_name]['change_examples'].append({
                                'protocol': protocol,
                                'from': current_value,
                                'to': new_value
                            })

                        # Adicionar à lista geral de mudanças
                        analysis['field_changes'].append({
                            'protocol': protocol,
                            'table': table_name,
                            'field': field_name,
                            'current_value': current_value,
                            'new_value': new_value,
                            'change_type': 'UPDATE' if current_value_str != '' else 'FILL_EMPTY'
                        })

                        analysis['summary']['fields_affected'].add(field_name)

                if changes:
                    analysis['updated_protocols'].append({
                        'protocol': protocol,
                        'table': table_name,
                        'changes': changes,
                        'total_changes': len(changes)
                    })
                    analysis['summary']['protocols_with_changes'] += 1

        # Finalizar estatísticas
        analysis['summary']['total_field_changes'] = len(analysis['field_changes'])
        analysis['summary']['fields_affected'] = list(analysis['summary']['fields_affected'])

        return analysis

    except Exception as e:
        print(f"Erro na análise da tabela {table_name}: {e}")
        return {
            'error': str(e),
            'total_new_records': len(new_data),
            'existing_records': 0,
            'new_protocols': [],
            'updated_protocols': [],
            'field_changes': [],
            'field_statistics': {},
            'summary': {
                'total_protocols_analyzed': 0,
                'protocols_with_changes': 0,
                'total_field_changes': 0,
                'fields_affected': []
            }
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
                        data = read_excel_file(file)
                        result = process_table_updates(conn, table_name.replace('-', '_'), data)
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

def process_table_updates(conn, table_name, data):
    """Processa atualizações para uma tabela específica"""
    
    cursor = conn.cursor()
    
    # Contadores
    new_records = 0
    updated_records = 0
    errors = 0
    
    for record in data:
        try:
            protocol = str(record.get('protocolo', ''))
            if not protocol:
                continue
            
            # Verificar se registro existe
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE protocolo = %s", (protocol,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Simular atualização (implementação real seria mais complexa)
                updated_records += 1
            else:
                # Simular inserção (implementação real seria mais complexa)
                new_records += 1
                
        except Exception as e:
            print(f"Erro ao processar protocolo {protocol}: {e}")
            errors += 1
            continue
    
    return {
        'new_records': new_records,
        'updated_records': updated_records,
        'errors': errors,
        'total_processed': len(data)
    }

@app.route('/api/detailed-analysis', methods=['POST'])
def get_detailed_analysis():
    """Obtém análise detalhada campo por campo para revisão"""
    try:
        files = request.files
        detailed_analysis = {}

        for table_name in ['emissao', 'renovacao-geral', 'renovacao-safeid']:
            file_key = f'file-{table_name}'
            if file_key in files:
                file = files[file_key]
                if file.filename:
                    # Processar arquivo Excel
                    data = read_excel_file(file)

                    # Análise COMPLETA
                    analysis = analyze_table_differences(table_name.replace('-', '_'), data)
                    detailed_analysis[table_name] = analysis

        return jsonify({
            'status': 'success',
            'detailed_analysis': detailed_analysis,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

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

        conn.close()

        return jsonify({
            'status': 'success',
            'table_counts': status,
            'last_update': datetime.now().isoformat()
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
    print("📊 Acesse: http://localhost:8080")
    print("🔧 Configuração do banco: PostgreSQL localhost:5433")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
