#!/usr/bin/env python3
"""
SISTEMA DE ATUALIZAÇÃO INCREMENTAL CRM CCAMP
Processa novos relatórios e atualiza apenas registros existentes baseado no protocolo
"""

import pandas as pd
import psycopg2
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('atualizacao_incremental.log'),
        logging.StreamHandler()
    ]
)

class AtualizadorIncremental:
    def __init__(self):
        """Inicializa conexão com banco de dados"""
        self.conn = psycopg2.connect(
            host="localhost",
            port="5433",
            database="crm_ccamp",
            user="postgres",
            password="@Certificado123"
        )
        self.conn.autocommit = False
        
        # Mapeamento de colunas por tabela
        self.mapeamento_colunas = {
            'emissao': {
                'protocolo': 'protocolo',
                'documento_do_titular': 'documento_do_titular',
                'nome_do_titular': 'nome_do_titular',
                'produto': 'produto',
                'data_inicio_validade': 'data_inicio_validade',
                'data_fim_validade': 'data_fim_validade',
                'status_do_certificado': 'status_do_certificado',
                'valor_do_boleto': 'valor_do_boleto',
                'nome_da_cidade': 'nome_da_cidade',
                'documento': 'documento'
            },
            'renovacao_geral': {
                'protocolo': 'protocolo',
                'cpfcnpj': 'cpfcnpj',
                'nome_titular': 'nome_titular',
                'produto': 'produto',
                'data_inicio_validade': 'data_inicio_validade',
                'data_fim_validade': 'data_fim_validade',
                'status_certificado': 'status_certificado',
                'local_de_atendimento': 'local_de_atendimento',
                'protocolo_renovacao': 'protocolo_renovacao',
                'status_protocolo_renovacao': 'status_protocolo_renovacao'
            },
            'renovacao_safeid': {
                'protocolo': 'protocolo',
                'documento': 'documento',
                'nome_razao_social': 'nome_razao_social',
                'descricao_produto': 'descricao_produto',
                'data_inicio_do_uso': 'data_inicio_do_uso',
                'data_fim_do_uso': 'data_fim_do_uso',
                'status_do_certificado': 'status_do_certificado',
                'valor_pagamento': 'valor_pagamento',
                'primeira_emissao': 'primeira_emissao',
                'renovado': 'renovado'
            }
        }
    
    def calcular_hash_arquivo(self, caminho_arquivo: str) -> str:
        """Calcula hash MD5 do arquivo para evitar reprocessamento"""
        hash_md5 = hashlib.md5()
        with open(caminho_arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def verificar_arquivo_ja_processado(self, hash_arquivo: str, tabela_destino: str) -> bool:
        """Verifica se arquivo já foi processado"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM controle_atualizacoes 
                WHERE hash_arquivo = %s AND tabela_destino = %s AND status = 'CONCLUIDO'
            """, (hash_arquivo, tabela_destino))
            return cursor.fetchone()[0] > 0
    
    def processar_arquivo_emissao(self, caminho_arquivo: str, observacao: str = None) -> Dict:
        """Processa arquivo de atualização da tabela emissao"""
        return self._processar_arquivo_generico(
            caminho_arquivo=caminho_arquivo,
            tabela_destino='emissao',
            funcao_sql='atualizar_emissao_incremental',
            observacao=observacao
        )
    
    def processar_arquivo_renovacao_geral(self, caminho_arquivo: str, observacao: str = None) -> Dict:
        """Processa arquivo de atualização da tabela renovacao_geral"""
        return self._processar_arquivo_generico(
            caminho_arquivo=caminho_arquivo,
            tabela_destino='renovacao_geral',
            funcao_sql='atualizar_renovacao_geral_incremental',
            observacao=observacao
        )
    
    def processar_arquivo_renovacao_safeid(self, caminho_arquivo: str, observacao: str = None) -> Dict:
        """Processa arquivo de atualização da tabela renovacao_safeid"""
        return self._processar_arquivo_generico(
            caminho_arquivo=caminho_arquivo,
            tabela_destino='renovacao_safeid',
            funcao_sql='atualizar_renovacao_safeid_incremental',
            observacao=observacao
        )
    
    def _processar_arquivo_generico(self, caminho_arquivo: str, tabela_destino: str, 
                                  funcao_sql: str, observacao: str = None) -> Dict:
        """Processa arquivo genérico de atualização"""
        
        logging.info(f"Iniciando processamento: {caminho_arquivo} -> {tabela_destino}")
        
        # Calcular hash do arquivo
        hash_arquivo = self.calcular_hash_arquivo(caminho_arquivo)
        
        # Verificar se já foi processado
        if self.verificar_arquivo_ja_processado(hash_arquivo, tabela_destino):
            logging.warning(f"Arquivo já processado anteriormente: {caminho_arquivo}")
            return {
                'status': 'JA_PROCESSADO',
                'arquivo': caminho_arquivo,
                'hash': hash_arquivo
            }
        
        try:
            # Ler arquivo Excel
            df = pd.read_excel(caminho_arquivo)
            total_registros = len(df)
            
            logging.info(f"Arquivo carregado: {total_registros} registros")
            
            # Obter mapeamento de colunas
            mapeamento = self.mapeamento_colunas[tabela_destino]
            
            # Contadores
            registros_novos = 0
            registros_atualizados = 0
            registros_ignorados = 0
            
            # Processar cada linha
            with self.conn.cursor() as cursor:
                for index, row in df.iterrows():
                    try:
                        # Preparar parâmetros baseado no mapeamento
                        parametros = self._preparar_parametros(row, mapeamento, observacao)
                        
                        # Executar função de atualização
                        cursor.execute(f"SELECT {funcao_sql}({parametros})")
                        resultado = cursor.fetchone()[0]
                        
                        if resultado == 'INSERIDO':
                            registros_novos += 1
                        elif resultado == 'ATUALIZADO':
                            registros_atualizados += 1
                        
                        # Commit a cada 100 registros
                        if (index + 1) % 100 == 0:
                            self.conn.commit()
                            logging.info(f"Processados {index + 1}/{total_registros} registros")
                    
                    except Exception as e:
                        logging.error(f"Erro no registro {index}: {e}")
                        registros_ignorados += 1
                        continue
                
                # Commit final
                self.conn.commit()
                
                # Registrar processamento
                cursor.execute("""
                    SELECT registrar_processamento(%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    tabela_destino,
                    os.path.basename(caminho_arquivo),
                    total_registros,
                    registros_novos,
                    registros_atualizados,
                    registros_ignorados,
                    hash_arquivo,
                    observacao
                ))
                
                processamento_id = cursor.fetchone()[0]
                self.conn.commit()
            
            resultado = {
                'status': 'SUCESSO',
                'processamento_id': processamento_id,
                'arquivo': caminho_arquivo,
                'total_registros': total_registros,
                'registros_novos': registros_novos,
                'registros_atualizados': registros_atualizados,
                'registros_ignorados': registros_ignorados,
                'hash': hash_arquivo
            }
            
            logging.info(f"Processamento concluído: {resultado}")
            return resultado
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro no processamento: {e}")
            raise
    
    def _preparar_parametros(self, row: pd.Series, mapeamento: Dict, observacao: str) -> str:
        """Prepara string de parâmetros para função SQL"""
        parametros = []
        
        for campo_sql, campo_excel in mapeamento.items():
            valor = row.get(campo_excel)
            
            if pd.isna(valor) or valor is None:
                parametros.append('NULL')
            elif isinstance(valor, str):
                # Escapar aspas simples
                valor_escapado = valor.replace("'", "''")
                parametros.append(f"'{valor_escapado}'")
            elif isinstance(valor, (int, float)):
                parametros.append(str(valor))
            elif isinstance(valor, datetime):
                parametros.append(f"'{valor.isoformat()}'::timestamp")
            else:
                parametros.append(f"'{str(valor)}'")
        
        # Adicionar observação
        if observacao:
            observacao_escapada = observacao.replace("'", "''")
            parametros.append(f"'{observacao_escapada}'")
        else:
            parametros.append('NULL')
        
        return ', '.join(parametros)
    
    def obter_historico_atualizacoes(self, tabela: str = None, limite: int = 50) -> List[Dict]:
        """Obtém histórico de atualizações"""
        with self.conn.cursor() as cursor:
            if tabela:
                cursor.execute("""
                    SELECT * FROM vw_historico_atualizacoes 
                    WHERE tabela_destino = %s 
                    ORDER BY data_processamento DESC 
                    LIMIT %s
                """, (tabela, limite))
            else:
                cursor.execute("""
                    SELECT * FROM vw_historico_atualizacoes 
                    ORDER BY data_processamento DESC 
                    LIMIT %s
                """, (limite,))
            
            colunas = [desc[0] for desc in cursor.description]
            resultados = cursor.fetchall()
            
            return [dict(zip(colunas, row)) for row in resultados]
    
    def verificar_protocolos_duplicados(self, tabela: str) -> List[Dict]:
        """Verifica se existem protocolos duplicados"""
        with self.conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT protocolo, COUNT(*) as quantidade
                FROM {tabela}
                GROUP BY protocolo
                HAVING COUNT(*) > 1
                ORDER BY quantidade DESC
            """)
            
            resultados = cursor.fetchall()
            return [{'protocolo': row[0], 'quantidade': row[1]} for row in resultados]
    
    def __del__(self):
        """Fechar conexão ao destruir objeto"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Exemplo de uso do sistema"""
    atualizador = AtualizadorIncremental()
    
    print("🔄 SISTEMA DE ATUALIZAÇÃO INCREMENTAL CRM CCAMP")
    print("=" * 50)
    
    # Exemplo de processamento
    # resultado = atualizador.processar_arquivo_emissao(
    #     'novo_relatorio_emissao.xlsx',
    #     'Atualização mensal - Janeiro 2024'
    # )
    
    # Mostrar histórico
    print("\n📊 HISTÓRICO DE ATUALIZAÇÕES:")
    historico = atualizador.obter_historico_atualizacoes(limite=10)
    
    for item in historico:
        print(f"📅 {item['data_processamento']} | {item['tabela_destino']} | "
              f"Novos: {item['registros_novos']} | Atualizados: {item['registros_atualizados']}")
    
    # Verificar duplicados
    print("\n🔍 VERIFICAÇÃO DE DUPLICADOS:")
    for tabela in ['emissao', 'renovacao_geral', 'renovacao_safeid']:
        duplicados = atualizador.verificar_protocolos_duplicados(tabela)
        if duplicados:
            print(f"⚠️  {tabela}: {len(duplicados)} protocolos duplicados")
        else:
            print(f"✅ {tabela}: Sem duplicados")

if __name__ == "__main__":
    main()
