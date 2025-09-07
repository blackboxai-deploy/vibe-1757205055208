"""
Gerenciador de banco de dados SQLite para o sistema MDM
"""
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import json
import pandas as pd

from .models import Cliente, Produto, Fornecedor, AuditLog, Usuario
from config import DATABASE_PATH, DATABASE_DIR, create_directories

class DatabaseManager:
    """Gerenciador principal do banco de dados"""
    
    def __init__(self):
        create_directories()
        self.db_path = DATABASE_PATH
        self.init_database()
        self.create_default_user()

    def get_connection(self) -> sqlite3.Connection:
        """Obter conexão com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Inicializar o banco de dados com as tabelas necessárias"""
        with self.get_connection() as conn:
            # Tabela de usuários
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    perfil TEXT NOT NULL DEFAULT 'visualizador',
                    ativo BOOLEAN NOT NULL DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login DATETIME
                )
            """)

            # Tabela de clientes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf_cnpj TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    telefone TEXT,
                    endereco TEXT,
                    cidade TEXT,
                    estado TEXT,
                    cep TEXT,
                    tipo TEXT NOT NULL CHECK (tipo IN ('pessoa_fisica', 'pessoa_juridica')),
                    ativo BOOLEAN NOT NULL DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    criado_por TEXT,
                    atualizado_por TEXT
                )
            """)

            # Tabela de produtos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    codigo TEXT NOT NULL UNIQUE,
                    descricao TEXT,
                    categoria TEXT NOT NULL,
                    subcategoria TEXT,
                    preco REAL NOT NULL DEFAULT 0.0,
                    unidade_medida TEXT NOT NULL,
                    ativo BOOLEAN NOT NULL DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    criado_por TEXT,
                    atualizado_por TEXT
                )
            """)

            # Tabela de fornecedores
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fornecedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cnpj TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    telefone TEXT,
                    endereco TEXT,
                    cidade TEXT,
                    estado TEXT,
                    cep TEXT,
                    contato_principal TEXT,
                    ativo BOOLEAN NOT NULL DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    criado_por TEXT,
                    atualizado_por TEXT
                )
            """)

            # Tabela de auditoria
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tabela TEXT NOT NULL,
                    registro_id INTEGER NOT NULL,
                    operacao TEXT NOT NULL CHECK (operacao IN ('INSERT', 'UPDATE', 'DELETE')),
                    dados_anteriores TEXT,
                    dados_novos TEXT,
                    usuario TEXT,
                    data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clientes_cpf_cnpj ON clientes(cpf_cnpj)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos(codigo)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fornecedores_cnpj ON fornecedores(cnpj)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fornecedores_nome ON fornecedores(nome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_tabela ON audit_log(tabela)")

            conn.commit()

    def create_default_user(self):
        """Criar usuário padrão admin se não existir"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM usuarios WHERE username = ?", ("admin",))
            if cursor.fetchone()[0] == 0:
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                conn.execute("""
                    INSERT INTO usuarios (username, password_hash, nome, email, perfil)
                    VALUES (?, ?, ?, ?, ?)
                """, ("admin", password_hash, "Administrador", "admin@mdm.com", "admin"))
                conn.commit()

    def log_audit(self, tabela: str, registro_id: int, operacao: str, 
                  dados_anteriores: Dict = None, dados_novos: Dict = None, usuario: str = None):
        """Registrar operação no log de auditoria"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO audit_log (tabela, registro_id, operacao, dados_anteriores, dados_novos, usuario)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tabela, registro_id, operacao,
                json.dumps(dados_anteriores) if dados_anteriores else None,
                json.dumps(dados_novos) if dados_novos else None,
                usuario
            ))
            conn.commit()

    # CRUD para Clientes
    def create_cliente(self, cliente: Cliente, usuario: str = None) -> int:
        """Criar novo cliente"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO clientes (nome, cpf_cnpj, email, telefone, endereco, cidade, estado, cep, tipo, criado_por, atualizado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente.nome, cliente.cpf_cnpj, cliente.email, cliente.telefone,
                cliente.endereco, cliente.cidade, cliente.estado, cliente.cep,
                cliente.tipo, usuario, usuario
            ))
            cliente_id = cursor.lastrowid
            
            # Log de auditoria
            self.log_audit("clientes", cliente_id, "INSERT", None, cliente.to_dict(), usuario)
            conn.commit()
            return cliente_id

    def get_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Obter cliente por ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
            row = cursor.fetchone()
            if row:
                return Cliente(
                    id=row['id'], nome=row['nome'], cpf_cnpj=row['cpf_cnpj'],
                    email=row['email'], telefone=row['telefone'], endereco=row['endereco'],
                    cidade=row['cidade'], estado=row['estado'], cep=row['cep'],
                    tipo=row['tipo'], ativo=bool(row['ativo']),
                    data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
                    data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None,
                    criado_por=row['criado_por'], atualizado_por=row['atualizado_por']
                )
            return None

    def update_cliente(self, cliente_id: int, cliente: Cliente, usuario: str = None) -> bool:
        """Atualizar cliente"""
        # Obter dados anteriores para auditoria
        cliente_anterior = self.get_cliente(cliente_id)
        if not cliente_anterior:
            return False

        with self.get_connection() as conn:
            conn.execute("""
                UPDATE clientes SET nome=?, cpf_cnpj=?, email=?, telefone=?, endereco=?, cidade=?, estado=?, cep=?, tipo=?, ativo=?, data_atualizacao=CURRENT_TIMESTAMP, atualizado_por=?
                WHERE id=?
            """, (
                cliente.nome, cliente.cpf_cnpj, cliente.email, cliente.telefone,
                cliente.endereco, cliente.cidade, cliente.estado, cliente.cep,
                cliente.tipo, cliente.ativo, usuario, cliente_id
            ))
            
            # Log de auditoria
            self.log_audit("clientes", cliente_id, "UPDATE", cliente_anterior.to_dict(), cliente.to_dict(), usuario)
            conn.commit()
            return True

    def delete_cliente(self, cliente_id: int, usuario: str = None) -> bool:
        """Excluir cliente (soft delete)"""
        cliente_anterior = self.get_cliente(cliente_id)
        if not cliente_anterior:
            return False

        with self.get_connection() as conn:
            conn.execute("UPDATE clientes SET ativo=0, data_atualizacao=CURRENT_TIMESTAMP, atualizado_por=? WHERE id=?", (usuario, cliente_id))
            
            # Log de auditoria
            self.log_audit("clientes", cliente_id, "DELETE", cliente_anterior.to_dict(), None, usuario)
            conn.commit()
            return True

    def list_clientes(self, ativo_apenas: bool = True, limit: int = None, offset: int = 0) -> List[Cliente]:
        """Listar clientes"""
        with self.get_connection() as conn:
            query = "SELECT * FROM clientes"
            params = []
            
            if ativo_apenas:
                query += " WHERE ativo = 1"
            
            query += " ORDER BY nome"
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor = conn.execute(query, params)
            clientes = []
            for row in cursor.fetchall():
                clientes.append(Cliente(
                    id=row['id'], nome=row['nome'], cpf_cnpj=row['cpf_cnpj'],
                    email=row['email'], telefone=row['telefone'], endereco=row['endereco'],
                    cidade=row['cidade'], estado=row['estado'], cep=row['cep'],
                    tipo=row['tipo'], ativo=bool(row['ativo']),
                    data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
                    data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None,
                    criado_por=row['criado_por'], atualizado_por=row['atualizado_por']
                ))
            return clientes

    # CRUD para Produtos
    def create_produto(self, produto: Produto, usuario: str = None) -> int:
        """Criar novo produto"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO produtos (nome, codigo, descricao, categoria, subcategoria, preco, unidade_medida, criado_por, atualizado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                produto.nome, produto.codigo, produto.descricao, produto.categoria,
                produto.subcategoria, produto.preco, produto.unidade_medida, usuario, usuario
            ))
            produto_id = cursor.lastrowid
            
            # Log de auditoria
            self.log_audit("produtos", produto_id, "INSERT", None, produto.to_dict(), usuario)
            conn.commit()
            return produto_id

    def get_produto(self, produto_id: int) -> Optional[Produto]:
        """Obter produto por ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            row = cursor.fetchone()
            if row:
                return Produto(
                    id=row['id'], nome=row['nome'], codigo=row['codigo'],
                    descricao=row['descricao'], categoria=row['categoria'], subcategoria=row['subcategoria'],
                    preco=row['preco'], unidade_medida=row['unidade_medida'], ativo=bool(row['ativo']),
                    data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
                    data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None,
                    criado_por=row['criado_por'], atualizado_por=row['atualizado_por']
                )
            return None

    def update_produto(self, produto_id: int, produto: Produto, usuario: str = None) -> bool:
        """Atualizar produto"""
        produto_anterior = self.get_produto(produto_id)
        if not produto_anterior:
            return False

        with self.get_connection() as conn:
            conn.execute("""
                UPDATE produtos SET nome=?, codigo=?, descricao=?, categoria=?, subcategoria=?, preco=?, unidade_medida=?, ativo=?, data_atualizacao=CURRENT_TIMESTAMP, atualizado_por=?
                WHERE id=?
            """, (
                produto.nome, produto.codigo, produto.descricao, produto.categoria,
                produto.subcategoria, produto.preco, produto.unidade_medida, produto.ativo, usuario, produto_id
            ))
            
            # Log de auditoria
            self.log_audit("produtos", produto_id, "UPDATE", produto_anterior.to_dict(), produto.to_dict(), usuario)
            conn.commit()
            return True

    def delete_produto(self, produto_id: int, usuario: str = None) -> bool:
        """Excluir produto (soft delete)"""
        produto_anterior = self.get_produto(produto_id)
        if not produto_anterior:
            return False

        with self.get_connection() as conn:
            conn.execute("UPDATE produtos SET ativo=0, data_atualizacao=CURRENT_TIMESTAMP, atualizado_por=? WHERE id=?", (usuario, produto_id))
            
            # Log de auditoria
            self.log_audit("produtos", produto_id, "DELETE", produto_anterior.to_dict(), None, usuario)
            conn.commit()
            return True

    def list_produtos(self, ativo_apenas: bool = True, limit: int = None, offset: int = 0) -> List[Produto]:
        """Listar produtos"""
        with self.get_connection() as conn:
            query = "SELECT * FROM produtos"
            params = []
            
            if ativo_apenas:
                query += " WHERE ativo = 1"
            
            query += " ORDER BY nome"
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor = conn.execute(query, params)
            produtos = []
            for row in cursor.fetchall():
                produtos.append(Produto(
                    id=row['id'], nome=row['nome'], codigo=row['codigo'],
                    descricao=row['descricao'], categoria=row['categoria'], subcategoria=row['subcategoria'],
                    preco=row['preco'], unidade_medida=row['unidade_medida'], ativo=bool(row['ativo']),
                    data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
                    data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None,
                    criado_por=row['criado_por'], atualizado_por=row['atualizado_por']
                ))
            return produtos

    # CRUD para Fornecedores
    def create_fornecedor(self, fornecedor: Fornecedor, usuario: str = None) -> int:
        """Criar novo fornecedor"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO fornecedores (nome, cnpj, email, telefone, endereco, cidade, estado, cep, contato_principal, criado_por, atualizado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fornecedor.nome, fornecedor.cnpj, fornecedor.email, fornecedor.telefone,
                fornecedor.endereco, fornecedor.cidade, fornecedor.estado, fornecedor.cep,
                fornecedor.contato_principal, usuario, usuario
            ))
            fornecedor_id = cursor.lastrowid
            
            # Log de auditoria
            self.log_audit("fornecedores", fornecedor_id, "INSERT", None, fornecedor.to_dict(), usuario)
            conn.commit()
            return fornecedor_id

    def get_fornecedor(self, fornecedor_id: int) -> Optional[Fornecedor]:
        """Obter fornecedor por ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM fornecedores WHERE id = ?", (fornecedor_id,))
            row = cursor.fetchone()
            if row:
                return Fornecedor(
                    id=row['id'], nome=row['nome'], cnpj=row['cnpj'],
                    email=row['email'], telefone=row['telefone'], endereco=row['endereco'],
                    cidade=row['cidade'], estado=row['estado'], cep=row['cep'],
                    contato_principal=row['contato_principal'], ativo=bool(row['ativo']),
                    data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
                    data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None,
                    criado_por=row['criado_por'], atualizado_por=row['atualizado_por']
                )
            return None

    def update_fornecedor(self, fornecedor_id: int, fornecedor: Fornecedor, usuario: str = None) -> bool:
        """Atualizar fornecedor"""
        fornecedor_anterior = self.get_fornecedor(fornecedor_id)
        if not fornecedor_anterior:
            return False

        with self.get_connection() as conn:
            conn.execute("""
                UPDATE fornecedores SET nome=?, cnpj=?, email=?, telefone=?, endereco=?, cidade=?, estado=?, cep=?, contato_principal=?, ativo=?, data_atualizacao=CURRENT_TIMESTAMP, atualizado_por=?
                WHERE id=?
            """, (
                fornecedor.nome, fornecedor.cnpj, fornecedor.email, fornecedor.telefone,
                fornecedor.endereco, fornecedor.cidade, fornecedor.estado, fornecedor.cep,
                fornecedor.contato_principal, fornecedor.ativo, usuario, fornecedor_id
            ))
            
            # Log de auditoria
            self.log_audit("fornecedores", fornecedor_id, "UPDATE", fornecedor_anterior.to_dict(), fornecedor.to_dict(), usuario)
            conn.commit()
            return True

    def delete_fornecedor(self, fornecedor_id: int, usuario: str = None) -> bool:
        """Excluir fornecedor (soft delete)"""
        fornecedor_anterior = self.get_fornecedor(fornecedor_id)
        if not fornecedor_anterior:
            return False

        with self.get_connection() as conn:
            conn.execute("UPDATE fornecedores SET ativo=0, data_atualizacao=CURRENT_TIMESTAMP, atualizado_por=? WHERE id=?", (usuario, fornecedor_id))
            
            # Log de auditoria
            self.log_audit("fornecedores", fornecedor_id, "DELETE", fornecedor_anterior.to_dict(), None, usuario)
            conn.commit()
            return True

    def list_fornecedores(self, ativo_apenas: bool = True, limit: int = None, offset: int = 0) -> List[Fornecedor]:
        """Listar fornecedores"""
        with self.get_connection() as conn:
            query = "SELECT * FROM fornecedores"
            params = []
            
            if ativo_apenas:
                query += " WHERE ativo = 1"
            
            query += " ORDER BY nome"
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor = conn.execute(query, params)
            fornecedores = []
            for row in cursor.fetchall():
                fornecedores.append(Fornecedor(
                    id=row['id'], nome=row['nome'], cnpj=row['cnpj'],
                    email=row['email'], telefone=row['telefone'], endereco=row['endereco'],
                    cidade=row['cidade'], estado=row['estado'], cep=row['cep'],
                    contato_principal=row['contato_principal'], ativo=bool(row['ativo']),
                    data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
                    data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None,
                    criado_por=row['criado_por'], atualizado_por=row['atualizado_por']
                ))
            return fornecedores
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Obter métricas para o dashboard"""
        with self.get_connection() as conn:
            # Contar registros
            clientes_count = conn.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1").fetchone()[0]
            produtos_count = conn.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1").fetchone()[0]
            fornecedores_count = conn.execute("SELECT COUNT(*) FROM fornecedores WHERE ativo = 1").fetchone()[0]
            
            # Últimas alterações
            ultimas_alteracoes = conn.execute("""
                SELECT tabela, COUNT(*) as count FROM audit_log 
                WHERE date(data_operacao) = date('now') 
                GROUP BY tabela
            """).fetchall()
            
            return {
                'total_clientes': clientes_count,
                'total_produtos': produtos_count,
                'total_fornecedores': fornecedores_count,
                'alteracoes_hoje': {row['tabela']: row['count'] for row in ultimas_alteracoes}
            }

    def search_records(self, tabela: str, termo: str, campos: List[str] = None, limit: int = 50) -> List[Dict]:
        """Buscar registros em uma tabela"""
        if not campos:
            campos = ['nome']  # campo padrão
        
        with self.get_connection() as conn:
            # Construir query de busca
            conditions = []
            params = []
            
            for campo in campos:
                conditions.append(f"{campo} LIKE ?")
                params.append(f"%{termo}%")
            
            query = f"""
                SELECT * FROM {tabela} 
                WHERE ativo = 1 AND ({' OR '.join(conditions)})
                ORDER BY nome
                LIMIT ?
            """
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_audit_log(self, tabela: str = None, registro_id: int = None, limit: int = 100) -> List[AuditLog]:
        """Obter logs de auditoria"""
        with self.get_connection() as conn:
            query = "SELECT * FROM audit_log"
            params = []
            conditions = []
            
            if tabela:
                conditions.append("tabela = ?")
                params.append(tabela)
            
            if registro_id:
                conditions.append("registro_id = ?")
                params.append(registro_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY data_operacao DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            logs = []
            for row in cursor.fetchall():
                logs.append(AuditLog(
                    id=row['id'], tabela=row['tabela'], registro_id=row['registro_id'],
                    operacao=row['operacao'], dados_anteriores=row['dados_anteriores'],
                    dados_novos=row['dados_novos'], usuario=row['usuario'],
                    data_operacao=datetime.fromisoformat(row['data_operacao']) if row['data_operacao'] else None
                ))
            return logs

# Instância global do gerenciador
db_manager = DatabaseManager()