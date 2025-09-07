"""
Configurações da aplicação MDM
"""
import os
from pathlib import Path

# Configurações do banco de dados
DATABASE_PATH = "data/mdm_database.db"
DATABASE_DIR = "data"

# Configurações de autenticação
SECRET_KEY = os.getenv("SECRET_KEY", "mdm_secret_key_2024")
SESSION_TIMEOUT = 3600  # 1 hora em segundos

# Configurações da aplicação
APP_TITLE = "Sistema MDM - Gerenciamento de Dados Mestres"
APP_VERSION = "1.0.0"
PAGE_ICON = "📊"

# Configurações de upload
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

# Configurações de detecção de duplicatas
SIMILARITY_THRESHOLD = 0.85  # 85% de similaridade
DUPLICATE_CHECK_FIELDS = {
    'clientes': ['nome', 'cpf_cnpj', 'email'],
    'produtos': ['nome', 'codigo', 'categoria'],
    'fornecedores': ['nome', 'cnpj', 'email']
}

# Configurações de paginação
ITEMS_PER_PAGE = 20

# Configurações de auditoria
AUDIT_RETENTION_DAYS = 365  # Manter logs por 1 ano

# Criar diretórios necessários
def create_directories():
    """Criar diretórios necessários se não existirem"""
    Path(DATABASE_DIR).mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    Path("pages").mkdir(exist_ok=True)
    Path("utils").mkdir(exist_ok=True)
    Path("database").mkdir(exist_ok=True)

# Configurações de deploy
STREAMLIT_CONFIG = {
    'page_title': APP_TITLE,
    'page_icon': PAGE_ICON,
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}