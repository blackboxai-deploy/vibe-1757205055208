"""
Gerenciador de auditoria e controle de versões
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from database.database_manager import DatabaseManager
from database.models import AuditLog

class AuditManager:
    """Gerenciador de auditoria e versionamento"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_audit_history(self, tabela: str = None, registro_id: int = None, 
                         usuario: str = None, dias: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """Obter histórico de auditoria com filtros"""
        with self.db_manager.get_connection() as conn:
            query = """
                SELECT al.*, u.nome as nome_usuario
                FROM audit_log al
                LEFT JOIN usuarios u ON al.usuario = u.username
                WHERE 1=1
            """
            params = []
            
            # Filtros
            if tabela:
                query += " AND al.tabela = ?"
                params.append(tabela)
            
            if registro_id:
                query += " AND al.registro_id = ?"
                params.append(registro_id)
            
            if usuario:
                query += " AND al.usuario = ?"
                params.append(usuario)
            
            if dias > 0:
                data_limite = datetime.now() - timedelta(days=dias)
                query += " AND al.data_operacao >= ?"
                params.append(data_limite.isoformat())
            
            query += " ORDER BY al.data_operacao DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            results = []
            
            for row in cursor.fetchall():
                audit_data = {
                    'id': row['id'],
                    'tabela': row['tabela'],
                    'registro_id': row['registro_id'],
                    'operacao': row['operacao'],
                    'usuario': row['usuario'],
                    'nome_usuario': row['nome_usuario'] if row['nome_usuario'] else row['usuario'],
                    'data_operacao': row['data_operacao'],
                    'dados_anteriores': json.loads(row['dados_anteriores']) if row['dados_anteriores'] else None,
                    'dados_novos': json.loads(row['dados_novos']) if row['dados_novos'] else None
                }
                
                # Processar mudanças específicas
                audit_data['mudancas'] = self._extract_changes(audit_data['dados_anteriores'], audit_data['dados_novos'])
                
                results.append(audit_data)
            
            return results
    
    def _extract_changes(self, dados_anteriores: Dict, dados_novos: Dict) -> List[Dict[str, Any]]:
        """Extrair mudanças específicas entre versões"""
        if not dados_anteriores or not dados_novos:
            return []
        
        changes = []
        all_keys = set(dados_anteriores.keys()) | set(dados_novos.keys())
        
        for key in all_keys:
            old_value = dados_anteriores.get(key)
            new_value = dados_novos.get(key)
            
            if old_value != new_value:
                changes.append({
                    'campo': key,
                    'valor_anterior': old_value,
                    'valor_novo': new_value,
                    'tipo_mudanca': 'modificado' if key in dados_anteriores and key in dados_novos else 
                                  'adicionado' if key not in dados_anteriores else 'removido'
                })
        
        return changes
    
    def get_record_versions(self, tabela: str, registro_id: int) -> List[Dict[str, Any]]:
        """Obter todas as versões de um registro específico"""
        history = self.get_audit_history(tabela=tabela, registro_id=registro_id, limit=1000)
        
        versions = []
        current_data = {}
        
        # Processar do mais antigo para o mais novo
        for entry in reversed(history):
            if entry['operacao'] == 'INSERT':
                current_data = entry['dados_novos'].copy() if entry['dados_novos'] else {}
            elif entry['operacao'] == 'UPDATE':
                if entry['dados_novos']:
                    current_data.update(entry['dados_novos'])
            elif entry['operacao'] == 'DELETE':
                current_data['ativo'] = False
            
            versions.append({
                'versao': len(versions) + 1,
                'data_operacao': entry['data_operacao'],
                'operacao': entry['operacao'],
                'usuario': entry['nome_usuario'],
                'dados': current_data.copy(),
                'mudancas': entry['mudancas']
            })
        
        return list(reversed(versions))  # Retornar do mais novo para o mais antigo
    
    def get_activity_summary(self, dias: int = 7) -> Dict[str, Any]:
        """Obter resumo de atividades dos últimos dias"""
        data_limite = datetime.now() - timedelta(days=dias)
        
        with self.db_manager.get_connection() as conn:
            # Atividades por dia
            atividades_dia = conn.execute("""
                SELECT DATE(data_operacao) as dia, COUNT(*) as total
                FROM audit_log
                WHERE data_operacao >= ?
                GROUP BY DATE(data_operacao)
                ORDER BY dia DESC
            """, (data_limite.isoformat(),)).fetchall()
            
            # Atividades por usuário
            atividades_usuario = conn.execute("""
                SELECT al.usuario, u.nome as nome_usuario, COUNT(*) as total
                FROM audit_log al
                LEFT JOIN usuarios u ON al.usuario = u.username
                WHERE al.data_operacao >= ?
                GROUP BY al.usuario, u.nome
                ORDER BY total DESC
            """, (data_limite.isoformat(),)).fetchall()
            
            # Atividades por tabela
            atividades_tabela = conn.execute("""
                SELECT tabela, COUNT(*) as total
                FROM audit_log
                WHERE data_operacao >= ?
                GROUP BY tabela
                ORDER BY total DESC
            """, (data_limite.isoformat(),)).fetchall()
            
            # Atividades por operação
            atividades_operacao = conn.execute("""
                SELECT operacao, COUNT(*) as total
                FROM audit_log
                WHERE data_operacao >= ?
                GROUP BY operacao
                ORDER BY total DESC
            """, (data_limite.isoformat(),)).fetchall()
            
            return {
                'periodo': f"Últimos {dias} dias",
                'por_dia': [dict(row) for row in atividades_dia],
                'por_usuario': [dict(row) for row in atividades_usuario],
                'por_tabela': [dict(row) for row in atividades_tabela],
                'por_operacao': [dict(row) for row in atividades_operacao]
            }
    
    def get_user_activity(self, usuario: str, dias: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Obter atividades de um usuário específico"""
        return self.get_audit_history(usuario=usuario, dias=dias, limit=limit)
    
    def get_table_activity(self, tabela: str, dias: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Obter atividades de uma tabela específica"""
        return self.get_audit_history(tabela=tabela, dias=dias, limit=limit)
    
    def clean_old_logs(self, dias_manter: int = 365) -> int:
        """Limpar logs antigos (manter apenas dos últimos X dias)"""
        data_limite = datetime.now() - timedelta(days=dias_manter)
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM audit_log 
                WHERE data_operacao < ?
            """, (data_limite.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
    
    def export_audit_log(self, filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Exportar log de auditoria para relatórios"""
        if not filtros:
            filtros = {}
        
        history = self.get_audit_history(
            tabela=filtros.get('tabela'),
            registro_id=filtros.get('registro_id'),
            usuario=filtros.get('usuario'),
            dias=filtros.get('dias', 30),
            limit=filtros.get('limit', 1000)
        )
        
        # Formatar dados para exportação
        export_data = []
        for entry in history:
            export_record = {
                'Data/Hora': entry['data_operacao'],
                'Tabela': entry['tabela'],
                'Registro ID': entry['registro_id'],
                'Operação': entry['operacao'],
                'Usuário': entry['nome_usuario'],
                'Mudanças': len(entry['mudancas']) if entry['mudancas'] else 0
            }
            
            # Adicionar detalhes das mudanças
            if entry['mudancas']:
                mudancas_str = []
                for mudanca in entry['mudancas']:
                    mudancas_str.append(f"{mudanca['campo']}: {mudanca['valor_anterior']} → {mudanca['valor_novo']}")
                export_record['Detalhes'] = '; '.join(mudancas_str)
            else:
                export_record['Detalhes'] = ''
            
            export_data.append(export_record)
        
        return export_data
    
    def get_compliance_report(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """Gerar relatório de compliance"""
        data_inicio = datetime.now() - timedelta(days=periodo_dias)
        
        with self.db_manager.get_connection() as conn:
            # Total de operações
            total_operacoes = conn.execute("""
                SELECT COUNT(*) FROM audit_log WHERE data_operacao >= ?
            """, (data_inicio.isoformat(),)).fetchone()[0]
            
            # Operações por tipo
            operacoes_tipo = conn.execute("""
                SELECT operacao, COUNT(*) as total
                FROM audit_log
                WHERE data_operacao >= ?
                GROUP BY operacao
            """, (data_inicio.isoformat(),)).fetchall()
            
            # Usuários mais ativos
            usuarios_ativos = conn.execute("""
                SELECT al.usuario, u.nome, COUNT(*) as total
                FROM audit_log al
                LEFT JOIN usuarios u ON al.usuario = u.username
                WHERE al.data_operacao >= ?
                GROUP BY al.usuario, u.nome
                ORDER BY total DESC
                LIMIT 10
            """, (data_inicio.isoformat(),)).fetchall()
            
            # Tabelas mais modificadas
            tabelas_ativas = conn.execute("""
                SELECT tabela, COUNT(*) as total
                FROM audit_log
                WHERE data_operacao >= ?
                GROUP BY tabela
                ORDER BY total DESC
            """, (data_inicio.isoformat(),)).fetchall()
            
            return {
                'periodo': f"{periodo_dias} dias",
                'data_inicio': data_inicio.isoformat(),
                'data_fim': datetime.now().isoformat(),
                'total_operacoes': total_operacoes,
                'operacoes_por_tipo': [dict(row) for row in operacoes_tipo],
                'usuarios_mais_ativos': [dict(row) for row in usuarios_ativos],
                'tabelas_mais_modificadas': [dict(row) for row in tabelas_ativas]
            }

# Instância global do gerenciador de auditoria
audit_manager = AuditManager()