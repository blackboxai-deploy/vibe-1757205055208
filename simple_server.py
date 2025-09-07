#!/usr/bin/env python3
"""
Servidor web simples para demonstração do Sistema MDM
"""
import http.server
import socketserver
import json
import urllib.parse
import os
from datetime import datetime

# Importar os módulos do sistema
try:
    from database.database_manager import db_manager
    from utils.duplicate_detector import duplicate_detector
    print("✅ Módulos MDM carregados com sucesso")
except Exception as e:
    print(f"❌ Erro ao carregar módulos: {e}")
    db_manager = None
    duplicate_detector = None

class MDMRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler customizado para o servidor MDM"""
    
    def do_GET(self):
        """Lidar com requisições GET"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print(f"📥 GET {path}")
        
        if path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path == '/api/metrics':
            self.serve_metrics_api()
        elif path == '/api/status':
            self.serve_status_api()
        elif path == '/health':
            self.serve_health_check()
        else:
            self.serve_default_page()
    
    def serve_dashboard(self):
        """Servir dashboard principal"""
        try:
            # Obter métricas do sistema
            if db_manager:
                metrics = db_manager.get_dashboard_metrics()
                duplicate_counts = duplicate_detector.get_duplicate_count()
            else:
                metrics = {'total_clientes': 0, 'total_produtos': 0, 'total_fornecedores': 0}
                duplicate_counts = {'total': 0, 'clientes': 0, 'produtos': 0, 'fornecedores': 0}
            
            html_content = f'''
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sistema MDM - Dashboard</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        color: #333;
                    }}
                    .container {{ 
                        max-width: 1200px; 
                        margin: 0 auto; 
                        padding: 20px;
                    }}
                    .header {{ 
                        text-align: center; 
                        color: white; 
                        padding: 40px 0; 
                    }}
                    .header h1 {{ 
                        font-size: 3rem; 
                        margin-bottom: 10px; 
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    }}
                    .header p {{ 
                        font-size: 1.2rem; 
                        opacity: 0.9; 
                    }}
                    .metrics {{ 
                        display: grid; 
                        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                        gap: 20px; 
                        margin: 30px 0; 
                    }}
                    .metric-card {{ 
                        background: white; 
                        padding: 30px; 
                        border-radius: 15px; 
                        text-align: center; 
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        transition: transform 0.3s ease;
                    }}
                    .metric-card:hover {{ 
                        transform: translateY(-5px); 
                    }}
                    .metric-value {{ 
                        font-size: 3rem; 
                        font-weight: bold; 
                        color: #667eea; 
                        margin-bottom: 10px;
                    }}
                    .metric-label {{ 
                        font-size: 1.3rem; 
                        color: #666; 
                    }}
                    .alert {{ 
                        background: rgba(255, 255, 255, 0.95); 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin: 20px 0;
                        border-left: 5px solid #ffc107;
                    }}
                    .features {{ 
                        background: rgba(255, 255, 255, 0.95); 
                        padding: 30px; 
                        border-radius: 15px; 
                        margin: 30px 0;
                    }}
                    .features h2 {{ 
                        color: #333; 
                        margin-bottom: 20px; 
                        text-align: center;
                    }}
                    .feature-grid {{ 
                        display: grid; 
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                        gap: 20px; 
                        margin-top: 20px;
                    }}
                    .feature-item {{ 
                        padding: 20px; 
                        background: #f8f9fa; 
                        border-radius: 10px;
                    }}
                    .feature-item h3 {{ 
                        color: #667eea; 
                        margin-bottom: 10px; 
                    }}
                    .btn {{ 
                        background: #667eea; 
                        color: white; 
                        border: none; 
                        padding: 12px 24px; 
                        border-radius: 8px; 
                        cursor: pointer; 
                        text-decoration: none; 
                        display: inline-block;
                        margin-top: 10px;
                        transition: background 0.3s ease;
                    }}
                    .btn:hover {{ 
                        background: #5a6fd8; 
                    }}
                    .status {{ 
                        text-align: center; 
                        margin: 20px 0; 
                        color: white; 
                    }}
                    .api-links {{ 
                        background: rgba(255, 255, 255, 0.1); 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin: 20px 0;
                    }}
                    .api-links h3 {{ 
                        color: white; 
                        margin-bottom: 15px; 
                    }}
                    .api-links a {{ 
                        color: #fff; 
                        text-decoration: none; 
                        display: block; 
                        padding: 5px 0;
                    }}
                    .api-links a:hover {{ 
                        text-decoration: underline; 
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Sistema MDM</h1>
                        <p>Gerenciamento de Dados Mestres - Master Data Management</p>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_clientes', 0)}</div>
                            <div class="metric-label">👥 Clientes Cadastrados</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_produtos', 0)}</div>
                            <div class="metric-label">📦 Produtos no Catálogo</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_fornecedores', 0)}</div>
                            <div class="metric-label">🏢 Fornecedores Ativos</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{duplicate_counts.get('total', 0)}</div>
                            <div class="metric-label">⚠️ Duplicatas Detectadas</div>
                        </div>
                    </div>
                    
                    {self.get_duplicates_alert_html(duplicate_counts)}
                    
                    <div class="features">
                        <h2>🚀 Funcionalidades do Sistema</h2>
                        <div class="feature-grid">
                            <div class="feature-item">
                                <h3>👥 Gestão de Clientes</h3>
                                <p>Cadastro completo de clientes pessoa física e jurídica com validação de CPF/CNPJ, detecção de duplicatas e histórico de alterações.</p>
                                <a href="#" class="btn">Gerenciar Clientes</a>
                            </div>
                            <div class="feature-item">
                                <h3>📦 Catálogo de Produtos</h3>
                                <p>Gestão completa do catálogo com categorização, controle de preços, códigos únicos e informações detalhadas.</p>
                                <a href="#" class="btn">Gerenciar Produtos</a>
                            </div>
                            <div class="feature-item">
                                <h3>🏢 Base de Fornecedores</h3>
                                <p>Cadastro e gestão de fornecedores com informações comerciais, contatos e histórico de relacionamento.</p>
                                <a href="#" class="btn">Gerenciar Fornecedores</a>
                            </div>
                            <div class="feature-item">
                                <h3>🔍 Busca Inteligente</h3>
                                <p>Sistema de busca avançada com múltiplos critérios, filtros dinâmicos e resultados relevantes.</p>
                                <a href="#" class="btn">Buscar Registros</a>
                            </div>
                            <div class="feature-item">
                                <h3>⚠️ Detecção de Duplicatas</h3>
                                <p>Identificação automática de registros duplicados com algoritmos inteligentes de similaridade.</p>
                                <a href="#" class="btn">Ver Duplicatas</a>
                            </div>
                            <div class="feature-item">
                                <h3>📊 Auditoria Completa</h3>
                                <p>Log detalhado de todas as operações realizadas no sistema para compliance e rastreabilidade.</p>
                                <a href="#" class="btn">Ver Auditoria</a>
                            </div>
                            <div class="feature-item">
                                <h3>📤 Import/Export</h3>
                                <p>Importação e exportação de dados em formato CSV com validação automática e tratamento de erros.</p>
                                <a href="#" class="btn">Import/Export</a>
                            </div>
                            <div class="feature-item">
                                <h3>🔐 Controle de Acesso</h3>
                                <p>Sistema de autenticação com diferentes perfis de usuário (Admin, Editor, Visualizador).</p>
                                <a href="#" class="btn">Gerenciar Usuários</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="api-links">
                        <h3>🔗 APIs Disponíveis</h3>
                        <a href="/api/metrics" target="_blank">📊 GET /api/metrics - Métricas do sistema</a>
                        <a href="/api/status" target="_blank">✅ GET /api/status - Status do sistema</a>
                        <a href="/health" target="_blank">💓 GET /health - Health check</a>
                    </div>
                    
                    <div class="status">
                        <p>🕒 Sistema iniciado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
                        <p>🌐 Servidor rodando na porta 8501</p>
                        <p>✅ Banco de dados ativo | 🔄 APIs funcionando</p>
                    </div>
                </div>
                
                <script>
                    // Atualizar métricas a cada 30 segundos
                    setInterval(async () => {{
                        try {{
                            const response = await fetch('/api/metrics');
                            const data = await response.json();
                            console.log('Métricas atualizadas:', data);
                        }} catch (error) {{
                            console.log('Erro ao atualizar métricas:', error);
                        }}
                    }}, 30000);
                    
                    console.log('🚀 Sistema MDM carregado com sucesso!');
                </script>
            </body>
            </html>
            '''
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f"Erro ao carregar dashboard: {str(e)}")
    
    def get_duplicates_alert_html(self, duplicate_counts):
        """Gerar HTML do alerta de duplicatas"""
        if duplicate_counts.get('total', 0) > 0:
            return f'''
            <div class="alert">
                <h3>⚠️ Atenção: {duplicate_counts['total']} grupos de duplicatas detectados!</h3>
                <ul style="margin: 15px 0 15px 30px;">
                    <li><strong>Clientes:</strong> {duplicate_counts['clientes']} grupos duplicados</li>
                    <li><strong>Produtos:</strong> {duplicate_counts['produtos']} grupos duplicados</li>
                    <li><strong>Fornecedores:</strong> {duplicate_counts['fornecedores']} grupos duplicados</li>
                </ul>
                <p style="margin-top: 15px;">
                    <a href="#" class="btn">🔧 Resolver Duplicatas</a>
                </p>
            </div>
            '''
        return ""
    
    def serve_metrics_api(self):
        """Servir API de métricas"""
        try:
            if db_manager and duplicate_detector:
                metrics = db_manager.get_dashboard_metrics()
                duplicate_counts = duplicate_detector.get_duplicate_count()
                
                response_data = {{
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics,
                    'duplicates': duplicate_counts,
                    'system_info': {{
                        'database_connected': True,
                        'duplicate_detector_active': True,
                        'total_tables': 5
                    }}
                }}
            else:
                response_data = {{
                    'status': 'error',
                    'message': 'Sistema não inicializado corretamente',
                    'timestamp': datetime.now().isoformat()
                }}
            
            self.send_json_response(response_data)
            
        except Exception as e:
            self.send_json_response({{
                'status': 'error',
                'message': f'Erro ao obter métricas: {{str(e)}}',
                'timestamp': datetime.now().isoformat()
            }}, status=500)
    
    def serve_status_api(self):
        """Servir API de status do sistema"""
        try:
            status_data = {{
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'database_connected': db_manager is not None,
                'duplicate_detector_active': duplicate_detector is not None,
                'uptime': 'Sistema ativo',
                'port': 8501,
                'endpoints': [
                    '/dashboard',
                    '/api/metrics',
                    '/api/status',
                    '/health'
                ]
            }}
            
            self.send_json_response(status_data)
            
        except Exception as e:
            self.send_json_response({{
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }}, status=500)
    
    def serve_health_check(self):
        """Health check endpoint"""
        self.send_json_response({{
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'message': '💚 Sistema MDM funcionando corretamente'
        }})
    
    def serve_default_page(self):
        """Servir página padrão para rotas não encontradas"""
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sistema MDM - Página não encontrada</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .container { max-width: 600px; margin: 0 auto; }
                h1 { color: #667eea; }
                .btn { background: #667eea; color: white; padding: 10px 20px; 
                       text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404 - Página não encontrada</h1>
                <p>A página que você está procurando não existe.</p>
                <a href="/dashboard" class="btn">🏠 Voltar ao Dashboard</a>
            </div>
        </body>
        </html>
        '''
        
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data, status=200):
        """Enviar resposta JSON"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, error_message, status=500):
        """Enviar resposta de erro"""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Sistema MDM</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>Erro no Sistema</h1>
            <p>{error_message}</p>
            <a href="/dashboard">Voltar ao Dashboard</a>
        </body>
        </html>
        '''
        
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

def main():
    """Função principal"""
    PORT = 8501
    
    print("🚀 Iniciando Sistema MDM...")
    print("=" * 50)
    
    # Verificar se os módulos foram carregados
    if db_manager and duplicate_detector:
        print("✅ Todos os módulos carregados com sucesso")
        
        # Mostrar algumas métricas iniciais
        try:
            metrics = db_manager.get_dashboard_metrics()
            print(f"📊 Clientes: {metrics['total_clientes']}")
            print(f"📊 Produtos: {metrics['total_produtos']}")
            print(f"📊 Fornecedores: {metrics['total_fornecedores']}")
        except Exception as e:
            print(f"⚠️  Erro ao obter métricas: {e}")
    else:
        print("⚠️  Alguns módulos não foram carregados, funcionalidade limitada")
    
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), MDMRequestHandler) as httpd:
            print(f"🌐 Servidor iniciado na porta {PORT}")
            print(f"📱 Acesse: http://localhost:{PORT}/dashboard")
            print(f"🔗 APIs disponíveis:")
            print(f"   • http://localhost:{PORT}/api/metrics")
            print(f"   • http://localhost:{PORT}/api/status")
            print(f"   • http://localhost:{PORT}/health")
            print(f"")
            print(f"⚡ Servidor rodando... Pressione Ctrl+C para parar.")
            print("=" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\\n🛑 Servidor encerrado pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()