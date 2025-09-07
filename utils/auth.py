"""
Sistema de autenticação para o MDM
"""
import hashlib
import streamlit as st
from datetime import datetime
from typing import Optional, Dict
import sqlite3

from database.database_manager import DatabaseManager
from database.models import Usuario

class AuthManager:
    """Gerenciador de autenticação"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def hash_password(self, password: str) -> str:
        """Gerar hash da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar senha"""
        return self.hash_password(password) == password_hash
    
    def authenticate(self, username: str, password: str) -> Optional[Usuario]:
        """Autenticar usuário"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM usuarios 
                WHERE username = ? AND ativo = 1
            """, (username,))
            row = cursor.fetchone()
            
            if row and self.verify_password(password, row['password_hash']):
                # Atualizar último login
                conn.execute("""
                    UPDATE usuarios 
                    SET ultimo_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (row['id'],))
                conn.commit()
                
                return Usuario(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    nome=row['nome'],
                    email=row['email'],
                    perfil=row['perfil'],
                    ativo=bool(row['ativo']),
                    data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
                    ultimo_login=datetime.now()
                )
        return None
    
    def create_user(self, username: str, password: str, nome: str, email: str, perfil: str = 'visualizador') -> bool:
        """Criar novo usuário"""
        try:
            password_hash = self.hash_password(password)
            with self.db_manager.get_connection() as conn:
                conn.execute("""
                    INSERT INTO usuarios (username, password_hash, nome, email, perfil)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, password_hash, nome, email, perfil))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username já existe
    
    def get_current_user(self) -> Optional[Usuario]:
        """Obter usuário atual da sessão"""
        if 'user' in st.session_state:
            return st.session_state.user
        return None
    
    def login_user(self, user: Usuario):
        """Fazer login do usuário"""
        st.session_state.user = user
        st.session_state.authenticated = True
    
    def logout_user(self):
        """Fazer logout do usuário"""
        if 'user' in st.session_state:
            del st.session_state.user
        if 'authenticated' in st.session_state:
            del st.session_state.authenticated
    
    def is_authenticated(self) -> bool:
        """Verificar se usuário está autenticado"""
        return st.session_state.get('authenticated', False)
    
    def has_permission(self, action: str) -> bool:
        """Verificar permissões do usuário atual"""
        user = self.get_current_user()
        if not user:
            return False
        
        if user.perfil == 'admin':
            return True
        
        permissions = {
            'visualizador': ['read'],
            'editor': ['read', 'create', 'update'],
            'admin': ['read', 'create', 'update', 'delete', 'manage_users']
        }
        
        return action in permissions.get(user.perfil, [])
    
    def require_auth(func):
        """Decorator para exigir autenticação"""
        def wrapper(*args, **kwargs):
            auth_manager = AuthManager()
            if not auth_manager.is_authenticated():
                st.error("⚠️ Acesso negado. Faça login para continuar.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    
    def require_permission(action: str):
        """Decorator para exigir permissão específica"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                auth_manager = AuthManager()
                if not auth_manager.has_permission(action):
                    st.error("⚠️ Permissão insuficiente para esta ação.")
                    st.stop()
                return func(*args, **kwargs)
            return wrapper
        return decorator

def show_login_page():
    """Exibir página de login"""
    st.title("🔐 Sistema MDM - Login")
    
    with st.form("login_form"):
        st.subheader("Acesso ao Sistema")
        username = st.text_input("Usuário", placeholder="Digite seu usuário")
        password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        submit_button = st.form_submit_button("Entrar")
        
        if submit_button:
            if username and password:
                auth_manager = AuthManager()
                user = auth_manager.authenticate(username, password)
                
                if user:
                    auth_manager.login_user(user)
                    st.success(f"✅ Bem-vindo, {user.nome}!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
            else:
                st.error("❌ Por favor, preencha todos os campos.")
    
    # Informações de acesso padrão
    st.info("""
    **Acesso padrão:**
    - Usuário: admin
    - Senha: admin123
    
    **Perfis de usuário:**
    - **Admin**: Acesso total ao sistema
    - **Editor**: Pode criar e editar registros
    - **Visualizador**: Apenas visualização
    """)

def show_logout_button():
    """Exibir botão de logout na sidebar"""
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 {user.nome}**")
        st.sidebar.markdown(f"*{user.perfil.title()}*")
        
        if st.sidebar.button("🚪 Sair", key="logout_button"):
            auth_manager.logout_user()
            st.rerun()

# Instância global do gerenciador
auth_manager = AuthManager()