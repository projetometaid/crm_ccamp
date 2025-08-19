"""
Configuração do Dashboard CRM CCAMP
Configurações de banco de dados e aplicação web
"""

import os
from datetime import timedelta

class Config:
    """Configuração base da aplicação"""
    
    # Configurações do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'crm-ccamp-dashboard-2024'
    
    # Configurações do Banco de Dados PostgreSQL
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5433',
        'database': 'crm_ccamp',
        'user': 'postgres',
        'password': '@Certificado123'
    }
    
    # String de conexão SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configurações de Paginação
    ITEMS_PER_PAGE = 50
    MAX_ITEMS_PER_PAGE = 200
    
    # Configurações de Performance
    DATABASE_QUERY_TIMEOUT = 30  # segundos
    
    # Configurações de Segurança
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    
    # Configurações de segurança para produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuração padrão
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
