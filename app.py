"""
Aplicação principal do Sistema MDM (Master Data Management)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Configurações da página
from config import STREAMLIT_CONFIG, create_directories
st.set_page_config(**STREAMLIT_CONFIG)

# Importações dos módulos
from utils.auth import AuthManager, show_login_page, show_logout_button
from utils.duplicate_detector import duplicate_detector
from database.database_manager import db_manager
from utils.search_engine import search_engine
from utils.audit_manager import audit_manager

# Aplicar CSS customizado
def load_css():
    """Carregar CSS customizado"""
    css_file = "static/style.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_dashboard():
    """Exibir dashboard principal"""
    st.title("📊 Dashboard - Sistema MDM")
    
    # Obter métricas
    metrics = db_manager.get_dashboard_metrics()
    duplicate_counts = duplicate_detector.get_duplicate_count()
    
    # Primeira linha de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total de Clientes",
            value=metrics['total_clientes'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="📦 Total de Produtos",
            value=metrics['total_produtos'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="🏢 Total de Fornecedores",
            value=metrics['total_fornecedores'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="⚠️ Duplicatas Detectadas",
            value=duplicate_counts['total'],
            delta=None
        )
    
    # Linha de separação
    st.divider()
    
    # Segunda linha - Gráficos e informações
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribuição de Registros")
        
        # Gráfico de pizza
        data = {
            'Tipo': ['Clientes', 'Produtos', 'Fornecedores'],
            'Quantidade': [metrics['total_clientes'], metrics['total_produtos'], metrics['total_fornecedores']]
        }
        
        if sum(data['Quantidade']) > 0:
            fig = px.pie(
                values=data['Quantidade'],
                names=data['Tipo'],
                title="Distribuição de Registros por Tipo",
                color_discrete_map={
                    'Clientes': '#007bff',
                    'Produtos': '#28a745',
                    'Fornecedores': '#ffc107'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum registro encontrado. Comece cadastrando dados!")
    
    with col2:
        st.subheader("🔄 Atividades Recentes")
        
        # Obter atividades recentes
        recent_activities = audit_manager.get_activity_summary(dias=7)
        
        if recent_activities['por_operacao']:
            operations_df = pd.DataFrame(recent_activities['por_operacao'])
            
            fig = px.bar(
                operations_df,
                x='operacao',
                y='total',
                title="Operações dos Últimos 7 Dias",
                color='operacao',
                color_discrete_map={
                    'INSERT': '#28a745',
                    'UPDATE': '#ffc107',
                    'DELETE': '#dc3545'
                }
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma atividade recente registrada.")
    
    # Terceira linha - Alertas e informações importantes
    st.divider()
    
    # Alertas de duplicatas
    if duplicate_counts['total'] > 0:
        st.error(f"""
        ⚠️ **Atenção: {duplicate_counts['total']} grupos de duplicatas detectados!**
        
        - Clientes: {duplicate_counts['clientes']} grupos
        - Produtos: {duplicate_counts['produtos']} grupos  
        - Fornecedores: {duplicate_counts['fornecedores']} grupos
        
        📌 Acesse a seção "Duplicatas" para revisar e resolver.
        """)
    
    # Informações do sistema
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🔐 Sistema de Autenticação**
        - Controle de acesso por usuário
        - Perfis: Admin, Editor, Visualizador
        - Log completo de atividades
        """)
    
    with col2:
        st.info("""
        **📊 Funcionalidades Principais**
        - Cadastro de Clientes, Produtos e Fornecedores
        - Detecção automática de duplicatas
        - Busca avançada com filtros
        """)
    
    with col3:
        st.info("""
        **🔄 Importação/Exportação**
        - Import/Export CSV e Excel
        - Templates de importação
        - Validação automática de dados
        """)
    
    # Registros recentes
    st.divider()
    st.subheader("📋 Registros Recentes")
    
    recent_records = search_engine.get_recent_records(limit=10)
    
    tab1, tab2, tab3 = st.tabs(["👥 Clientes", "📦 Produtos", "🏢 Fornecedores"])
    
    with tab1:
        if recent_records['clientes']:
            for cliente in recent_records['clientes']:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{cliente['nome']}**")
                        st.write(f"📧 {cliente['email']}")
                    with col2:
                        st.write(f"🆔 {cliente['cpf_cnpj']}")
                    with col3:
                        st.write(f"📅 {cliente['data_criacao'][:10] if cliente['data_criacao'] else 'N/A'}")
                st.divider()
        else:
            st.info("Nenhum cliente cadastrado ainda.")
    
    with tab2:
        if recent_records['produtos']:
            for produto in recent_records['produtos']:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{produto['nome']}**")
                        st.write(f"🏷️ {produto['categoria']}")
                    with col2:
                        st.write(f"🔢 {produto['codigo']}")
                    with col3:
                        st.write(f"📅 {produto['data_criacao'][:10] if produto['data_criacao'] else 'N/A'}")
                st.divider()
        else:
            st.info("Nenhum produto cadastrado ainda.")
    
    with tab3:
        if recent_records['fornecedores']:
            for fornecedor in recent_records['fornecedores']:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{fornecedor['nome']}**")
                        st.write(f"📧 {fornecedor['email']}")
                    with col2:
                        st.write(f"🏢 {fornecedor['cnpj']}")
                    with col3:
                        st.write(f"📅 {fornecedor['data_criacao'][:10] if fornecedor['data_criacao'] else 'N/A'}")
                st.divider()
        else:
            st.info("Nenhum fornecedor cadastrado ainda.")

def show_sidebar_navigation():
    """Mostrar navegação lateral"""
    with st.sidebar:
        st.title("🏠 Navegação")
        
        # Menu principal
        menu_options = {
            "📊 Dashboard": "dashboard",
            "👥 Clientes": "clientes", 
            "📦 Produtos": "produtos",
            "🏢 Fornecedores": "fornecedores",
            "🔍 Buscar": "busca",
            "⚠️ Duplicatas": "duplicatas",
            "📈 Auditoria": "auditoria",
            "📤 Import/Export": "import_export"
        }
        
        # Verificar permissões do usuário
        auth_manager = AuthManager()
        user = auth_manager.get_current_user()
        
        selected_page = st.radio("Selecione uma opção:", list(menu_options.keys()))
        page_key = menu_options[selected_page]
        
        # Informações do usuário
        show_logout_button()
        
        st.divider()
        
        # Informações de status
        if user:
            if user.perfil == 'admin':
                st.success("🔐 Acesso Administrativo")
            elif user.perfil == 'editor':
                st.info("✏️ Acesso de Editor")
            else:
                st.warning("👁️ Acesso de Visualizador")
        
        # Métricas rápidas na sidebar
        st.divider()
        st.subheader("📊 Resumo")
        
        try:
            metrics = db_manager.get_dashboard_metrics()
            st.metric("Clientes", metrics['total_clientes'])
            st.metric("Produtos", metrics['total_produtos'])  
            st.metric("Fornecedores", metrics['total_fornecedores'])
        except Exception as e:
            st.error("Erro ao carregar métricas")
        
        return page_key

def main():
    """Função principal da aplicação"""
    # Criar diretórios necessários
    create_directories()
    
    # Carregar CSS
    load_css()
    
    # Verificar autenticação
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        show_login_page()
        return
    
    # Usuário autenticado - mostrar aplicação
    try:
        # Navegação lateral
        current_page = show_sidebar_navigation()
        
        # Roteamento de páginas
        if current_page == "dashboard":
            show_dashboard()
        
        elif current_page == "clientes":
            st.title("👥 Gestão de Clientes")
            st.info("Módulo de clientes em desenvolvimento...")
            
        elif current_page == "produtos":
            st.title("📦 Gestão de Produtos")
            st.info("Módulo de produtos em desenvolvimento...")
            
        elif current_page == "fornecedores":
            st.title("🏢 Gestão de Fornecedores")
            st.info("Módulo de fornecedores em desenvolvimento...")
            
        elif current_page == "busca":
            st.title("🔍 Busca Avançada")
            st.info("Módulo de busca em desenvolvimento...")
            
        elif current_page == "duplicatas":
            st.title("⚠️ Detecção de Duplicatas")
            st.info("Módulo de duplicatas em desenvolvimento...")
            
        elif current_page == "auditoria":
            st.title("📈 Log de Auditoria")
            st.info("Módulo de auditoria em desenvolvimento...")
            
        elif current_page == "import_export":
            st.title("📤 Importação e Exportação")
            st.info("Módulo de import/export em desenvolvimento...")
        
    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()