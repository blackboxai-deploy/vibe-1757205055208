"""
Sistema de importação e exportação de dados
"""
import pandas as pd
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import io
import json
import tempfile
import os

from database.database_manager import DatabaseManager
from database.models import Cliente, Produto, Fornecedor

class ImportExportManager:
    """Gerenciador de importação e exportação"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def export_to_csv(self, tabela: str, filtros: Dict[str, Any] = None) -> bytes:
        """Exportar dados para CSV"""
        with self.db_manager.get_connection() as conn:
            query = f"SELECT * FROM {tabela} WHERE ativo = 1"
            params = []
            
            # Aplicar filtros se fornecidos
            if filtros:
                conditions = []
                for campo, valor in filtros.items():
                    if valor:
                        conditions.append(f"{campo} LIKE ?")
                        params.append(f"%{valor}%")
                
                if conditions:
                    query += " AND " + " AND ".join(conditions)
            
            df = pd.read_sql_query(query, conn, params=params)
            
            # Remover colunas sensíveis
            columns_to_remove = ['password_hash'] if tabela == 'usuarios' else []
            if columns_to_remove:
                df = df.drop(columns=columns_to_remove, errors='ignore')
            
            # Converter para CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            
            return csv_buffer.getvalue().encode('utf-8')
    
    def export_to_excel(self, tabelas: List[str] = None, filtros: Dict[str, Dict] = None) -> bytes:
        """Exportar dados para Excel (múltiplas abas)"""
        if not tabelas:
            tabelas = ['clientes', 'produtos', 'fornecedores']
        
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            with self.db_manager.get_connection() as conn:
                for tabela in tabelas:
                    query = f"SELECT * FROM {tabela} WHERE ativo = 1"
                    params = []
                    
                    # Aplicar filtros específicos da tabela
                    if filtros and tabela in filtros:
                        conditions = []
                        for campo, valor in filtros[tabela].items():
                            if valor:
                                conditions.append(f"{campo} LIKE ?")
                                params.append(f"%{valor}%")
                        
                        if conditions:
                            query += " AND " + " AND ".join(conditions)
                    
                    df = pd.read_sql_query(query, conn, params=params)
                    
                    # Remover colunas sensíveis
                    if tabela == 'usuarios':
                        df = df.drop(columns=['password_hash'], errors='ignore')
                    
                    # Formatar datas
                    date_columns = ['data_criacao', 'data_atualizacao', 'ultimo_login']
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                    
                    df.to_excel(writer, sheet_name=tabela.title(), index=False)
        
        excel_buffer.seek(0)
        return excel_buffer.getvalue()
    
    def import_from_csv(self, arquivo_csv: bytes, tabela: str, usuario: str = None) -> Dict[str, Any]:
        """Importar dados de CSV"""
        try:
            # Ler CSV
            csv_content = arquivo_csv.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validar estrutura
            validation_result = self._validate_import_structure(df, tabela)
            if not validation_result['valido']:
                return validation_result
            
            # Processar importação
            return self._process_import(df, tabela, usuario)
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f"Erro ao processar arquivo: {str(e)}",
                'registros_importados': 0,
                'registros_erro': 0,
                'erros': []
            }
    
    def import_from_excel(self, arquivo_excel: bytes, aba_nome: str, tabela: str, usuario: str = None) -> Dict[str, Any]:
        """Importar dados de Excel"""
        try:
            # Ler Excel
            df = pd.read_excel(io.BytesIO(arquivo_excel), sheet_name=aba_nome)
            
            # Validar estrutura
            validation_result = self._validate_import_structure(df, tabela)
            if not validation_result['valido']:
                return validation_result
            
            # Processar importação
            return self._process_import(df, tabela, usuario)
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f"Erro ao processar arquivo: {str(e)}",
                'registros_importados': 0,
                'registros_erro': 0,
                'erros': []
            }
    
    def _validate_import_structure(self, df: pd.DataFrame, tabela: str) -> Dict[str, Any]:
        """Validar estrutura do arquivo de importação"""
        required_fields = self._get_required_fields(tabela)
        optional_fields = self._get_optional_fields(tabela)
        all_fields = required_fields + optional_fields
        
        # Verificar se DataFrame não está vazio
        if df.empty:
            return {
                'valido': False,
                'erro': 'Arquivo vazio ou sem dados válidos',
                'campos_obrigatorios': required_fields
            }
        
        # Verificar campos obrigatórios
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            return {
                'valido': False,
                'erro': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}',
                'campos_obrigatorios': required_fields,
                'campos_encontrados': list(df.columns)
            }
        
        # Verificar campos desconhecidos
        unknown_fields = [col for col in df.columns if col not in all_fields and col != 'id']
        
        return {
            'valido': True,
            'campos_obrigatorios': required_fields,
            'campos_opcionais': optional_fields,
            'campos_desconhecidos': unknown_fields,
            'total_registros': len(df)
        }
    
    def _get_required_fields(self, tabela: str) -> List[str]:
        """Obter campos obrigatórios para importação"""
        fields_map = {
            'clientes': ['nome', 'cpf_cnpj', 'email', 'tipo'],
            'produtos': ['nome', 'codigo', 'categoria', 'unidade_medida'],
            'fornecedores': ['nome', 'cnpj', 'email']
        }
        return fields_map.get(tabela, [])
    
    def _get_optional_fields(self, tabela: str) -> List[str]:
        """Obter campos opcionais para importação"""
        fields_map = {
            'clientes': ['telefone', 'endereco', 'cidade', 'estado', 'cep', 'ativo'],
            'produtos': ['descricao', 'subcategoria', 'preco', 'ativo'],
            'fornecedores': ['telefone', 'endereco', 'cidade', 'estado', 'cep', 'contato_principal', 'ativo']
        }
        return fields_map.get(tabela, [])
    
    def _process_import(self, df: pd.DataFrame, tabela: str, usuario: str = None) -> Dict[str, Any]:
        """Processar importação dos dados"""
        registros_importados = 0
        registros_erro = 0
        erros = []
        
        # Limpar dados
        df = df.fillna('')
        
        for index, row in df.iterrows():
            try:
                # Validar registro individual
                validation_errors = self._validate_record(row, tabela)
                if validation_errors:
                    registros_erro += 1
                    erros.append(f"Linha {index + 2}: {'; '.join(validation_errors)}")
                    continue
                
                # Criar objeto do modelo
                if tabela == 'clientes':
                    obj = self._create_cliente_from_row(row)
                    self.db_manager.create_cliente(obj, usuario)
                elif tabela == 'produtos':
                    obj = self._create_produto_from_row(row)
                    self.db_manager.create_produto(obj, usuario)
                elif tabela == 'fornecedores':
                    obj = self._create_fornecedor_from_row(row)
                    self.db_manager.create_fornecedor(obj, usuario)
                
                registros_importados += 1
                
            except Exception as e:
                registros_erro += 1
                erros.append(f"Linha {index + 2}: Erro ao importar - {str(e)}")
        
        return {
            'sucesso': registros_erro == 0,
            'registros_importados': registros_importados,
            'registros_erro': registros_erro,
            'total_processados': registros_importados + registros_erro,
            'erros': erros[:10],  # Limitar a 10 erros para não sobrecarregar a interface
            'mais_erros': len(erros) > 10
        }
    
    def _validate_record(self, row: pd.Series, tabela: str) -> List[str]:
        """Validar um registro individual"""
        errors = []
        
        if tabela == 'clientes':
            if not row.get('nome', '').strip():
                errors.append("Nome é obrigatório")
            if not row.get('cpf_cnpj', '').strip():
                errors.append("CPF/CNPJ é obrigatório")
            if not row.get('email', '').strip():
                errors.append("Email é obrigatório")
            if row.get('tipo', '').strip() not in ['pessoa_fisica', 'pessoa_juridica']:
                errors.append("Tipo deve ser 'pessoa_fisica' ou 'pessoa_juridica'")
        
        elif tabela == 'produtos':
            if not row.get('nome', '').strip():
                errors.append("Nome é obrigatório")
            if not row.get('codigo', '').strip():
                errors.append("Código é obrigatório")
            if not row.get('categoria', '').strip():
                errors.append("Categoria é obrigatória")
            if not row.get('unidade_medida', '').strip():
                errors.append("Unidade de medida é obrigatória")
            
            # Validar preço se fornecido
            try:
                if row.get('preco', '') != '':
                    float(row.get('preco', 0))
            except ValueError:
                errors.append("Preço deve ser um número válido")
        
        elif tabela == 'fornecedores':
            if not row.get('nome', '').strip():
                errors.append("Nome é obrigatório")
            if not row.get('cnpj', '').strip():
                errors.append("CNPJ é obrigatório")
            if not row.get('email', '').strip():
                errors.append("Email é obrigatório")
        
        return errors
    
    def _create_cliente_from_row(self, row: pd.Series) -> Cliente:
        """Criar objeto Cliente a partir de linha do DataFrame"""
        return Cliente(
            nome=str(row.get('nome', '')).strip(),
            cpf_cnpj=str(row.get('cpf_cnpj', '')).strip(),
            email=str(row.get('email', '')).strip(),
            telefone=str(row.get('telefone', '')).strip(),
            endereco=str(row.get('endereco', '')).strip(),
            cidade=str(row.get('cidade', '')).strip(),
            estado=str(row.get('estado', '')).strip(),
            cep=str(row.get('cep', '')).strip(),
            tipo=str(row.get('tipo', '')).strip(),
            ativo=bool(row.get('ativo', True))
        )
    
    def _create_produto_from_row(self, row: pd.Series) -> Produto:
        """Criar objeto Produto a partir de linha do DataFrame"""
        preco = 0.0
        try:
            if row.get('preco', '') != '':
                preco = float(row.get('preco', 0))
        except ValueError:
            preco = 0.0
        
        return Produto(
            nome=str(row.get('nome', '')).strip(),
            codigo=str(row.get('codigo', '')).strip(),
            descricao=str(row.get('descricao', '')).strip(),
            categoria=str(row.get('categoria', '')).strip(),
            subcategoria=str(row.get('subcategoria', '')).strip(),
            preco=preco,
            unidade_medida=str(row.get('unidade_medida', '')).strip(),
            ativo=bool(row.get('ativo', True))
        )
    
    def _create_fornecedor_from_row(self, row: pd.Series) -> Fornecedor:
        """Criar objeto Fornecedor a partir de linha do DataFrame"""
        return Fornecedor(
            nome=str(row.get('nome', '')).strip(),
            cnpj=str(row.get('cnpj', '')).strip(),
            email=str(row.get('email', '')).strip(),
            telefone=str(row.get('telefone', '')).strip(),
            endereco=str(row.get('endereco', '')).strip(),
            cidade=str(row.get('cidade', '')).strip(),
            estado=str(row.get('estado', '')).strip(),
            cep=str(row.get('cep', '')).strip(),
            contato_principal=str(row.get('contato_principal', '')).strip(),
            ativo=bool(row.get('ativo', True))
        )
    
    def get_template_csv(self, tabela: str) -> bytes:
        """Gerar template CSV para importação"""
        required_fields = self._get_required_fields(tabela)
        optional_fields = self._get_optional_fields(tabela)
        all_fields = required_fields + optional_fields
        
        # Criar DataFrame com uma linha de exemplo
        example_data = {}
        
        if tabela == 'clientes':
            example_data = {
                'nome': 'João da Silva',
                'cpf_cnpj': '123.456.789-00',
                'email': 'joao@email.com',
                'telefone': '(11) 99999-9999',
                'endereco': 'Rua das Flores, 123',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '01234-567',
                'tipo': 'pessoa_fisica',
                'ativo': True
            }
        elif tabela == 'produtos':
            example_data = {
                'nome': 'Produto Exemplo',
                'codigo': 'PROD001',
                'descricao': 'Descrição do produto',
                'categoria': 'Eletrônicos',
                'subcategoria': 'Smartphones',
                'preco': 299.99,
                'unidade_medida': 'UN',
                'ativo': True
            }
        elif tabela == 'fornecedores':
            example_data = {
                'nome': 'Empresa Fornecedora Ltda',
                'cnpj': '12.345.678/0001-90',
                'email': 'contato@fornecedor.com',
                'telefone': '(11) 3333-3333',
                'endereco': 'Av. Industrial, 456',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '04567-890',
                'contato_principal': 'Maria Santos',
                'ativo': True
            }
        
        df = pd.DataFrame([example_data])
        
        # Converter para CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        
        return csv_buffer.getvalue().encode('utf-8')

# Instância global do gerenciador
import_export_manager = ImportExportManager()