"""
Modelos de dados para o sistema MDM
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import sqlite3
import json

@dataclass
class Cliente:
    """Modelo de dados para clientes"""
    nome: str
    cpf_cnpj: str
    email: str
    telefone: str
    endereco: str
    cidade: str
    estado: str
    cep: str
    tipo: str  # 'pessoa_fisica' ou 'pessoa_juridica'
    ativo: bool = True
    id: Optional[int] = None
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    criado_por: Optional[str] = None
    atualizado_por: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf_cnpj': self.cpf_cnpj,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'tipo': self.tipo,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'criado_por': self.criado_por,
            'atualizado_por': self.atualizado_por
        }

@dataclass
class Produto:
    """Modelo de dados para produtos"""
    nome: str
    codigo: str
    descricao: str
    categoria: str
    subcategoria: str
    preco: float
    unidade_medida: str
    ativo: bool = True
    id: Optional[int] = None
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    criado_por: Optional[str] = None
    atualizado_por: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'preco': self.preco,
            'unidade_medida': self.unidade_medida,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'criado_por': self.criado_por,
            'atualizado_por': self.atualizado_por
        }

@dataclass
class Fornecedor:
    """Modelo de dados para fornecedores"""
    nome: str
    cnpj: str
    email: str
    telefone: str
    endereco: str
    cidade: str
    estado: str
    cep: str
    contato_principal: str
    ativo: bool = True
    id: Optional[int] = None
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    criado_por: Optional[str] = None
    atualizado_por: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'contato_principal': self.contato_principal,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'criado_por': self.criado_por,
            'atualizado_por': self.atualizado_por
        }

@dataclass
class AuditLog:
    """Modelo para log de auditoria"""
    tabela: str
    registro_id: int
    operacao: str  # 'INSERT', 'UPDATE', 'DELETE'
    dados_anteriores: Optional[str] = None
    dados_novos: Optional[str] = None
    usuario: Optional[str] = None
    data_operacao: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'tabela': self.tabela,
            'registro_id': self.registro_id,
            'operacao': self.operacao,
            'dados_anteriores': self.dados_anteriores,
            'dados_novos': self.dados_novos,
            'usuario': self.usuario,
            'data_operacao': self.data_operacao.isoformat() if self.data_operacao else None
        }

@dataclass
class Usuario:
    """Modelo de dados para usuários"""
    username: str
    password_hash: str
    nome: str
    email: str
    perfil: str  # 'admin', 'editor', 'visualizador'
    ativo: bool = True
    id: Optional[int] = None
    data_criacao: Optional[datetime] = None
    ultimo_login: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'nome': self.nome,
            'email': self.email,
            'perfil': self.perfil,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None
        }