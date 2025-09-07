"""
Sistema de detecção de duplicidades
"""
from typing import List, Dict, Tuple, Any
import sqlite3
from fuzzywuzzy import fuzz
import re
import unicodedata

from database.database_manager import DatabaseManager
from config import DUPLICATE_CHECK_FIELDS, SIMILARITY_THRESHOLD

class DuplicateDetector:
    """Detector de duplicidades para registros MDM"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.threshold = SIMILARITY_THRESHOLD
    
    def normalize_text(self, text: str) -> str:
        """Normalizar texto para comparação"""
        if not text:
            return ""
        
        # Converter para lowercase
        text = text.lower()
        
        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Remover caracteres especiais
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remover espaços extras
        text = ' '.join(text.split())
        
        return text
    
    def normalize_document(self, doc: str) -> str:
        """Normalizar documentos (CPF/CNPJ)"""
        if not doc:
            return ""
        
        # Remover caracteres não numéricos
        return re.sub(r'\D', '', doc)
    
    def calculate_similarity(self, text1: str, text2: str, field_type: str = 'text') -> float:
        """Calcular similaridade entre dois textos"""
        if field_type == 'document':
            text1 = self.normalize_document(text1)
            text2 = self.normalize_document(text2)
            # Para documentos, usar comparação exata
            return 1.0 if text1 == text2 else 0.0
        else:
            text1 = self.normalize_text(text1)
            text2 = self.normalize_text(text2)
            
            if not text1 or not text2:
                return 0.0
            
            # Usar ratio da fuzzywuzzy
            return fuzz.ratio(text1, text2) / 100.0
    
    def find_duplicates_clientes(self) -> List[Dict[str, Any]]:
        """Encontrar duplicatas na tabela de clientes"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, nome, cpf_cnpj, email 
                FROM clientes 
                WHERE ativo = 1 
                ORDER BY id
            """)
            records = cursor.fetchall()
        
        duplicates = []
        processed_ids = set()
        
        for i, record1 in enumerate(records):
            if record1['id'] in processed_ids:
                continue
            
            duplicates_group = []
            
            for j, record2 in enumerate(records[i+1:], i+1):
                if record2['id'] in processed_ids:
                    continue
                
                # Verificar similaridade nos campos definidos
                similarities = {}
                
                # Nome
                similarities['nome'] = self.calculate_similarity(record1['nome'], record2['nome'])
                
                # CPF/CNPJ
                similarities['cpf_cnpj'] = self.calculate_similarity(record1['cpf_cnpj'], record2['cpf_cnpj'], 'document')
                
                # Email
                similarities['email'] = self.calculate_similarity(record1['email'], record2['email'])
                
                # Critério de duplicata: qualquer campo com 100% de similaridade ou nome com alta similaridade
                is_duplicate = (
                    similarities['cpf_cnpj'] >= 1.0 or
                    similarities['email'] >= 1.0 or
                    similarities['nome'] >= self.threshold
                )
                
                if is_duplicate:
                    if not duplicates_group:
                        duplicates_group.append({
                            'id': record1['id'],
                            'nome': record1['nome'],
                            'cpf_cnpj': record1['cpf_cnpj'],
                            'email': record1['email']
                        })
                    
                    duplicates_group.append({
                        'id': record2['id'],
                        'nome': record2['nome'],
                        'cpf_cnpj': record2['cpf_cnpj'],
                        'email': record2['email']
                    })
                    
                    similarities_display = {k: f"{v*100:.1f}%" for k, v in similarities.items()}
                    
                    processed_ids.add(record2['id'])
            
            if duplicates_group:
                processed_ids.add(record1['id'])
                duplicates.append({
                    'grupo': duplicates_group,
                    'total_registros': len(duplicates_group),
                    'tipo': 'clientes'
                })
        
        return duplicates
    
    def find_duplicates_produtos(self) -> List[Dict[str, Any]]:
        """Encontrar duplicatas na tabela de produtos"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, nome, codigo, categoria 
                FROM produtos 
                WHERE ativo = 1 
                ORDER BY id
            """)
            records = cursor.fetchall()
        
        duplicates = []
        processed_ids = set()
        
        for i, record1 in enumerate(records):
            if record1['id'] in processed_ids:
                continue
            
            duplicates_group = []
            
            for j, record2 in enumerate(records[i+1:], i+1):
                if record2['id'] in processed_ids:
                    continue
                
                similarities = {}
                
                # Nome
                similarities['nome'] = self.calculate_similarity(record1['nome'], record2['nome'])
                
                # Código
                similarities['codigo'] = self.calculate_similarity(record1['codigo'], record2['codigo'])
                
                # Categoria
                similarities['categoria'] = self.calculate_similarity(record1['categoria'], record2['categoria'])
                
                # Critério de duplicata
                is_duplicate = (
                    similarities['codigo'] >= 1.0 or
                    (similarities['nome'] >= self.threshold and similarities['categoria'] >= 0.8)
                )
                
                if is_duplicate:
                    if not duplicates_group:
                        duplicates_group.append({
                            'id': record1['id'],
                            'nome': record1['nome'],
                            'codigo': record1['codigo'],
                            'categoria': record1['categoria']
                        })
                    
                    duplicates_group.append({
                        'id': record2['id'],
                        'nome': record2['nome'],
                        'codigo': record2['codigo'],
                        'categoria': record2['categoria']
                    })
                    
                    processed_ids.add(record2['id'])
            
            if duplicates_group:
                processed_ids.add(record1['id'])
                duplicates.append({
                    'grupo': duplicates_group,
                    'total_registros': len(duplicates_group),
                    'tipo': 'produtos'
                })
        
        return duplicates
    
    def find_duplicates_fornecedores(self) -> List[Dict[str, Any]]:
        """Encontrar duplicatas na tabela de fornecedores"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, nome, cnpj, email 
                FROM fornecedores 
                WHERE ativo = 1 
                ORDER BY id
            """)
            records = cursor.fetchall()
        
        duplicates = []
        processed_ids = set()
        
        for i, record1 in enumerate(records):
            if record1['id'] in processed_ids:
                continue
            
            duplicates_group = []
            
            for j, record2 in enumerate(records[i+1:], i+1):
                if record2['id'] in processed_ids:
                    continue
                
                similarities = {}
                
                # Nome
                similarities['nome'] = self.calculate_similarity(record1['nome'], record2['nome'])
                
                # CNPJ
                similarities['cnpj'] = self.calculate_similarity(record1['cnpj'], record2['cnpj'], 'document')
                
                # Email
                similarities['email'] = self.calculate_similarity(record1['email'], record2['email'])
                
                # Critério de duplicata
                is_duplicate = (
                    similarities['cnpj'] >= 1.0 or
                    similarities['email'] >= 1.0 or
                    similarities['nome'] >= self.threshold
                )
                
                if is_duplicate:
                    if not duplicates_group:
                        duplicates_group.append({
                            'id': record1['id'],
                            'nome': record1['nome'],
                            'cnpj': record1['cnpj'],
                            'email': record1['email']
                        })
                    
                    duplicates_group.append({
                        'id': record2['id'],
                        'nome': record2['nome'],
                        'cnpj': record2['cnpj'],
                        'email': record2['email']
                    })
                    
                    processed_ids.add(record2['id'])
            
            if duplicates_group:
                processed_ids.add(record1['id'])
                duplicates.append({
                    'grupo': duplicates_group,
                    'total_registros': len(duplicates_group),
                    'tipo': 'fornecedores'
                })
        
        return duplicates
    
    def find_all_duplicates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Encontrar todas as duplicatas no sistema"""
        return {
            'clientes': self.find_duplicates_clientes(),
            'produtos': self.find_duplicates_produtos(),
            'fornecedores': self.find_duplicates_fornecedores()
        }
    
    def merge_records(self, tabela: str, master_id: int, duplicate_ids: List[int], usuario: str = None) -> bool:
        """Mesclar registros duplicados (manter o master e desativar os duplicados)"""
        try:
            with self.db_manager.get_connection() as conn:
                # Desativar registros duplicados
                placeholders = ','.join(['?' for _ in duplicate_ids])
                conn.execute(f"""
                    UPDATE {tabela} 
                    SET ativo = 0, data_atualizacao = CURRENT_TIMESTAMP, atualizado_por = ?
                    WHERE id IN ({placeholders})
                """, [usuario] + duplicate_ids)
                
                # Log de auditoria para cada registro mesclado
                for dup_id in duplicate_ids:
                    self.db_manager.log_audit(tabela, dup_id, "MERGE", 
                                            {'merged_into': master_id}, 
                                            {'ativo': False}, usuario)
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao mesclar registros: {e}")
            return False
    
    def get_duplicate_count(self) -> Dict[str, int]:
        """Obter contagem de duplicatas por tipo"""
        duplicates = self.find_all_duplicates()
        return {
            'clientes': len(duplicates['clientes']),
            'produtos': len(duplicates['produtos']),
            'fornecedores': len(duplicates['fornecedores']),
            'total': len(duplicates['clientes']) + len(duplicates['produtos']) + len(duplicates['fornecedores'])
        }

# Instância global do detector
duplicate_detector = DuplicateDetector()