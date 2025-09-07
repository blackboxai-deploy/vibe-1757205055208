"""
Motor de busca avançada para o sistema MDM
"""
from typing import List, Dict, Any, Optional, Tuple
import sqlite3
import re

from database.database_manager import DatabaseManager

class SearchEngine:
    """Motor de busca avançada"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def build_search_query(self, tabela: str, filtros: Dict[str, Any]) -> Tuple[str, List]:
        """Construir query de busca baseada nos filtros"""
        base_query = f"SELECT * FROM {tabela} WHERE ativo = 1"
        params = []
        conditions = []
        
        # Busca por texto livre
        if filtros.get('termo_busca'):
            termo = filtros['termo_busca']
            if tabela == 'clientes':
                text_conditions = [
                    "nome LIKE ?",
                    "cpf_cnpj LIKE ?",
                    "email LIKE ?",
                    "cidade LIKE ?",
                    "endereco LIKE ?"
                ]
                conditions.append(f"({' OR '.join(text_conditions)})")
                params.extend([f"%{termo}%" for _ in text_conditions])
            
            elif tabela == 'produtos':
                text_conditions = [
                    "nome LIKE ?",
                    "codigo LIKE ?",
                    "descricao LIKE ?",
                    "categoria LIKE ?",
                    "subcategoria LIKE ?"
                ]
                conditions.append(f"({' OR '.join(text_conditions)})")
                params.extend([f"%{termo}%" for _ in text_conditions])
            
            elif tabela == 'fornecedores':
                text_conditions = [
                    "nome LIKE ?",
                    "cnpj LIKE ?",
                    "email LIKE ?",
                    "cidade LIKE ?",
                    "contato_principal LIKE ?"
                ]
                conditions.append(f"({' OR '.join(text_conditions)})")
                params.extend([f"%{termo}%" for _ in text_conditions])
        
        # Filtros específicos
        for campo, valor in filtros.items():
            if campo == 'termo_busca' or not valor:
                continue
            
            if campo == 'tipo' and tabela == 'clientes':
                conditions.append("tipo = ?")
                params.append(valor)
            
            elif campo == 'categoria' and tabela == 'produtos':
                conditions.append("categoria LIKE ?")
                params.append(f"%{valor}%")
            
            elif campo == 'subcategoria' and tabela == 'produtos':
                conditions.append("subcategoria LIKE ?")
                params.append(f"%{valor}%")
            
            elif campo == 'estado':
                conditions.append("estado = ?")
                params.append(valor)
            
            elif campo == 'cidade':
                conditions.append("cidade LIKE ?")
                params.append(f"%{valor}%")
            
            elif campo == 'preco_min' and tabela == 'produtos':
                conditions.append("preco >= ?")
                params.append(valor)
            
            elif campo == 'preco_max' and tabela == 'produtos':
                conditions.append("preco <= ?")
                params.append(valor)
        
        # Adicionar condições à query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        return base_query, params
    
    def search_clientes(self, filtros: Dict[str, Any], limit: int = 50, offset: int = 0, 
                       order_by: str = 'nome', order_dir: str = 'ASC') -> List[Dict]:
        """Buscar clientes com filtros avançados"""
        query, params = self.build_search_query('clientes', filtros)
        
        # Adicionar ordenação
        valid_columns = ['nome', 'cpf_cnpj', 'email', 'cidade', 'data_criacao']
        if order_by in valid_columns:
            query += f" ORDER BY {order_by} {order_dir.upper()}"
        else:
            query += " ORDER BY nome ASC"
        
        # Adicionar paginação
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def search_produtos(self, filtros: Dict[str, Any], limit: int = 50, offset: int = 0,
                       order_by: str = 'nome', order_dir: str = 'ASC') -> List[Dict]:
        """Buscar produtos com filtros avançados"""
        query, params = self.build_search_query('produtos', filtros)
        
        # Adicionar ordenação
        valid_columns = ['nome', 'codigo', 'categoria', 'preco', 'data_criacao']
        if order_by in valid_columns:
            query += f" ORDER BY {order_by} {order_dir.upper()}"
        else:
            query += " ORDER BY nome ASC"
        
        # Adicionar paginação
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def search_fornecedores(self, filtros: Dict[str, Any], limit: int = 50, offset: int = 0,
                           order_by: str = 'nome', order_dir: str = 'ASC') -> List[Dict]:
        """Buscar fornecedores com filtros avançados"""
        query, params = self.build_search_query('fornecedores', filtros)
        
        # Adicionar ordenação
        valid_columns = ['nome', 'cnpj', 'email', 'cidade', 'data_criacao']
        if order_by in valid_columns:
            query += f" ORDER BY {order_by} {order_dir.upper()}"
        else:
            query += " ORDER BY nome ASC"
        
        # Adicionar paginação
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_search_count(self, tabela: str, filtros: Dict[str, Any]) -> int:
        """Obter contagem total de resultados da busca"""
        query, params = self.build_search_query(tabela, filtros)
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(count_query, params)
            return cursor.fetchone()[0]
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Obter opções para filtros (categorias, estados, etc.)"""
        with self.db_manager.get_connection() as conn:
            # Estados únicos
            estados = [row[0] for row in conn.execute("SELECT DISTINCT estado FROM clientes WHERE estado IS NOT NULL AND estado != '' AND ativo = 1").fetchall()]
            estados.extend([row[0] for row in conn.execute("SELECT DISTINCT estado FROM fornecedores WHERE estado IS NOT NULL AND estado != '' AND ativo = 1").fetchall()])
            estados = sorted(list(set(estados)))
            
            # Categorias de produtos
            categorias = [row[0] for row in conn.execute("SELECT DISTINCT categoria FROM produtos WHERE categoria IS NOT NULL AND categoria != '' AND ativo = 1").fetchall()]
            categorias = sorted(categorias)
            
            # Subcategorias de produtos
            subcategorias = [row[0] for row in conn.execute("SELECT DISTINCT subcategoria FROM produtos WHERE subcategoria IS NOT NULL AND subcategoria != '' AND ativo = 1").fetchall()]
            subcategorias = sorted(subcategorias)
            
            # Tipos de cliente
            tipos_cliente = ['pessoa_fisica', 'pessoa_juridica']
            
            return {
                'estados': estados,
                'categorias': categorias,
                'subcategorias': subcategorias,
                'tipos_cliente': tipos_cliente
            }
    
    def search_global(self, termo: str, limit: int = 20) -> Dict[str, List[Dict]]:
        """Busca global em todas as tabelas"""
        results = {
            'clientes': self.search_clientes({'termo_busca': termo}, limit=limit),
            'produtos': self.search_produtos({'termo_busca': termo}, limit=limit),
            'fornecedores': self.search_fornecedores({'termo_busca': termo}, limit=limit)
        }
        
        return results
    
    def get_recent_records(self, limit: int = 10) -> Dict[str, List[Dict]]:
        """Obter registros recentes"""
        with self.db_manager.get_connection() as conn:
            clientes = conn.execute("""
                SELECT id, nome, cpf_cnpj, email, data_criacao 
                FROM clientes 
                WHERE ativo = 1 
                ORDER BY data_criacao DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            
            produtos = conn.execute("""
                SELECT id, nome, codigo, categoria, data_criacao 
                FROM produtos 
                WHERE ativo = 1 
                ORDER BY data_criacao DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            
            fornecedores = conn.execute("""
                SELECT id, nome, cnpj, email, data_criacao 
                FROM fornecedores 
                WHERE ativo = 1 
                ORDER BY data_criacao DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            
            return {
                'clientes': [dict(row) for row in clientes],
                'produtos': [dict(row) for row in produtos],
                'fornecedores': [dict(row) for row in fornecedores]
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas de busca"""
        with self.db_manager.get_connection() as conn:
            # Estatísticas por estado
            stats_estados = conn.execute("""
                SELECT estado, COUNT(*) as total
                FROM (
                    SELECT estado FROM clientes WHERE ativo = 1 AND estado IS NOT NULL
                    UNION ALL
                    SELECT estado FROM fornecedores WHERE ativo = 1 AND estado IS NOT NULL
                )
                GROUP BY estado
                ORDER BY total DESC
                LIMIT 10
            """).fetchall()
            
            # Estatísticas por categoria de produto
            stats_categorias = conn.execute("""
                SELECT categoria, COUNT(*) as total
                FROM produtos 
                WHERE ativo = 1 AND categoria IS NOT NULL
                GROUP BY categoria
                ORDER BY total DESC
                LIMIT 10
            """).fetchall()
            
            # Tipo de cliente
            stats_tipos = conn.execute("""
                SELECT tipo, COUNT(*) as total
                FROM clientes 
                WHERE ativo = 1
                GROUP BY tipo
            """).fetchall()
            
            return {
                'por_estado': [dict(row) for row in stats_estados],
                'por_categoria': [dict(row) for row in stats_categorias],
                'por_tipo_cliente': [dict(row) for row in stats_tipos]
            }

# Instância global do motor de busca
search_engine = SearchEngine()