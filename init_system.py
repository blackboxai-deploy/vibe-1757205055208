"""
Script de inicialização do sistema MDM
"""
import os
import sqlite3
from datetime import datetime

def init_database():
    """Inicializar banco de dados"""
    print("🔧 Inicializando banco de dados...")
    
    # Criar diretório data se não existir
    if not os.path.exists('data'):
        os.makedirs('data')
        print("📁 Diretório 'data' criado")
    
    # Importar e inicializar o gerenciador de banco
    try:
        from database.database_manager import db_manager
        print("✅ Banco de dados inicializado com sucesso!")
        
        # Verificar se usuário admin existe
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                print("👤 Usuário admin não encontrado, será criado automaticamente")
            else:
                print("👤 Usuário admin já existe")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def add_sample_data():
    """Adicionar dados de exemplo"""
    print("\n📊 Adicionando dados de exemplo...")
    
    try:
        from database.database_manager import db_manager
        from database.models import Cliente, Produto, Fornecedor
        
        # Verificar se já existem dados
        metrics = db_manager.get_dashboard_metrics()
        if metrics['total_clientes'] > 0 or metrics['total_produtos'] > 0 or metrics['total_fornecedores'] > 0:
            print("ℹ️  Dados já existem no sistema")
            return True
        
        print("➕ Inserindo dados de exemplo...")
        
        # Clientes de exemplo
        clientes = [
            Cliente(
                nome="João Silva Santos",
                cpf_cnpj="12345678901",
                email="joao.silva@email.com",
                telefone="11999887766",
                endereco="Rua das Flores, 123",
                cidade="São Paulo",
                estado="SP",
                cep="01234567",
                tipo="pessoa_fisica"
            ),
            Cliente(
                nome="Maria Oliveira Ltda",
                cpf_cnpj="12345678000199",
                email="contato@mariaoliveira.com",
                telefone="1133334444",
                endereco="Av. Paulista, 1000",
                cidade="São Paulo",
                estado="SP",
                cep="01310100",
                tipo="pessoa_juridica"
            ),
            Cliente(
                nome="Pedro Costa",
                cpf_cnpj="98765432100",
                email="pedro.costa@gmail.com",
                telefone="11888777666",
                endereco="Rua Augusta, 456",
                cidade="São Paulo",
                estado="SP",
                cep="01305000",
                tipo="pessoa_fisica"
            )
        ]
        
        # Produtos de exemplo
        produtos = [
            Produto(
                nome="Notebook Dell Inspiron",
                codigo="DELL001",
                descricao="Notebook para uso profissional",
                categoria="Informática",
                subcategoria="Notebooks",
                preco=2500.00,
                unidade_medida="UN"
            ),
            Produto(
                nome="Mouse Sem Fio Logitech",
                codigo="LOG001",
                descricao="Mouse óptico sem fio",
                categoria="Informática",
                subcategoria="Periféricos",
                preco=89.90,
                unidade_medida="UN"
            ),
            Produto(
                nome="Cadeira Ergonômica",
                codigo="MOB001",
                descricao="Cadeira para escritório",
                categoria="Móveis",
                subcategoria="Cadeiras",
                preco=450.00,
                unidade_medida="UN"
            )
        ]
        
        # Fornecedores de exemplo
        fornecedores = [
            Fornecedor(
                nome="TechMart Distribuidora",
                cnpj="11222333000144",
                email="vendas@techmart.com",
                telefone="1144445555",
                endereco="Rua da Tecnologia, 789",
                cidade="São Paulo",
                estado="SP",
                cep="04567890",
                contato_principal="Ana Santos"
            ),
            Fornecedor(
                nome="Móveis & Cia",
                cnpj="55666777000188",
                email="pedidos@moveisecia.com",
                telefone="1155556666",
                endereco="Av. dos Móveis, 321",
                cidade="São Paulo",
                estado="SP",
                cep="05432109",
                contato_principal="Carlos Lima"
            )
        ]
        
        # Inserir dados
        for cliente in clientes:
            db_manager.create_cliente(cliente, "admin")
        
        for produto in produtos:
            db_manager.create_produto(produto, "admin")
        
        for fornecedor in fornecedores:
            db_manager.create_fornecedor(fornecedor, "admin")
        
        print(f"✅ Dados inseridos: {len(clientes)} clientes, {len(produtos)} produtos, {len(fornecedores)} fornecedores")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar dados de exemplo: {e}")
        return False

def check_system_status():
    """Verificar status do sistema"""
    print("\n🔍 Verificando status do sistema...")
    
    try:
        from database.database_manager import db_manager
        from utils.duplicate_detector import duplicate_detector
        
        # Métricas do sistema
        metrics = db_manager.get_dashboard_metrics()
        print(f"📊 Clientes: {metrics['total_clientes']}")
        print(f"📊 Produtos: {metrics['total_produtos']}")
        print(f"📊 Fornecedores: {metrics['total_fornecedores']}")
        
        # Verificar duplicatas
        duplicate_counts = duplicate_detector.get_duplicate_count()
        print(f"⚠️  Duplicatas detectadas: {duplicate_counts['total']}")
        
        # Verificar tabelas
        with db_manager.get_connection() as conn:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [table[0] for table in tables]
            print(f"🗃️  Tabelas criadas: {', '.join(table_names)}")
        
        print("✅ Sistema funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar sistema: {e}")
        return False

def main():
    """Função principal de inicialização"""
    print("🚀 Iniciando Sistema MDM...")
    print("=" * 50)
    
    # Passo 1: Inicializar banco
    if not init_database():
        print("❌ Falha na inicialização do banco de dados")
        return False
    
    # Passo 2: Adicionar dados de exemplo
    add_sample_data()
    
    # Passo 3: Verificar status
    if not check_system_status():
        print("❌ Sistema com problemas")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Sistema MDM inicializado com sucesso!")
    print("\n💡 Para iniciar a aplicação web, execute:")
    print("   python3 web_app.py")
    print("\n🌐 Acesso: http://localhost:8501")
    print("👤 Login: admin / admin123")
    
    return True

if __name__ == "__main__":
    main()