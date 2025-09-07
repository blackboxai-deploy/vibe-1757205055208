"""
Aplicação web básica do Sistema MDM usando Flask
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse as urlparse
from datetime import datetime
import os
import sqlite3

# Importações dos módulos locais
from database.database_manager import db_manager
from utils.auth import auth_manager
from utils.duplicate_detector import duplicate_detector
from utils.validators import validators
from database.models import Cliente, Produto, Fornecedor

class MDMWebHandler(BaseHTTPRequestHandler):
    """Handler para requisições web"""
    
    def do_GET(self):
        """Lidar com requisições GET"""
        path = urlparse.urlparse(self.path).path
        
        if path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path == '/login':
            self.serve_login()
        elif path == '/api/metrics':
            self.serve_api_metrics()
        elif path == '/api/duplicates':
            self.serve_api_duplicates()
        elif path.startswith('/static/'):
            self.serve_static_file(path)
        else:
            self.serve_404()
    
    def do_POST(self):
        """Lidar com requisições POST"""
        path = urlparse.urlparse(self.path).path
        
        if path == '/api/login':
            self.handle_login()
        elif path == '/api/clientes':
            self.handle_create_cliente()
        elif path == '/api/produtos':
            self.handle_create_produto()
        elif path == '/api/fornecedores':
            self.handle_create_fornecedor()
        else:
            self.serve_404()
    
    def serve_dashboard(self):
        """Servir página do dashboard"""
        try:
            metrics = db_manager.get_dashboard_metrics()
            duplicate_counts = duplicate_detector.get_duplicate_count()
            
            html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sistema MDM - Dashboard</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f5f5f5;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        text-align: center;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .metrics {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin: 20px 0;
                    }}
                    .metric-card {{
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        text-align: center;
                    }}
                    .metric-value {{
                        font-size: 3rem;
                        font-weight: bold;
                        color: #667eea;
                    }}
                    .metric-label {{
                        font-size: 1.2rem;
                        color: #666;
                        margin-top: 10px;
                    }}
                    .section {{
                        background: white;
                        margin: 20px 0;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .alert {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 5px;
                        padding: 15px;
                        margin: 15px 0;
                        color: #856404;
                    }}
                    .btn {{
                        background: #667eea;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        text-decoration: none;
                        display: inline-block;
                        margin: 5px;
                    }}
                    .btn:hover {{
                        background: #5a6fd8;
                    }}
                    .nav {{
                        background: white;
                        padding: 10px 0;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        margin-bottom: 20px;
                    }}
                    .nav-container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 0 20px;
                    }}
                    .nav-links {{
                        display: flex;
                        gap: 20px;
                    }}
                    .nav-links a {{
                        color: #333;
                        text-decoration: none;
                        font-weight: 500;
                    }}
                    .nav-links a:hover {{
                        color: #667eea;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Sistema MDM - Gerenciamento de Dados Mestres</h1>
                    <p>Centralize, gerencie e mantenha a qualidade dos seus dados</p>
                </div>
                
                <div class="nav">
                    <div class="nav-container">
                        <div class="nav-links">
                            <a href="/dashboard">Dashboard</a>
                            <a href="/clientes">Clientes</a>
                            <a href="/produtos">Produtos</a>
                            <a href="/fornecedores">Fornecedores</a>
                            <a href="/duplicatas">Duplicatas</a>
                            <a href="/buscar">Buscar</a>
                        </div>
                        <div>
                            <span>👤 Admin</span>
                            <a href="/logout" class="btn">Sair</a>
                        </div>
                    </div>
                </div>
                
                <div class="container">
                    <div class="metrics">
                        <div class="metric-card">
                            <div class="metric-value">{metrics['total_clientes']}</div>
                            <div class="metric-label">👥 Clientes</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics['total_produtos']}</div>
                            <div class="metric-label">📦 Produtos</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics['total_fornecedores']}</div>
                            <div class="metric-label">🏢 Fornecedores</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{duplicate_counts['total']}</div>
                            <div class="metric-label">⚠️ Duplicatas</div>
                        </div>
                    </div>
                    
                    {self.get_duplicates_alert(duplicate_counts)}
                    
                    <div class="section">
                        <h2>🚀 Funcionalidades Principais</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                            <div>
                                <h3>👥 Gestão de Clientes</h3>
                                <p>Cadastro completo com validação de CPF/CNPJ, controle de duplicatas e histórico de alterações.</p>
                                <a href="/clientes" class="btn">Gerenciar Clientes</a>
                            </div>
                            <div>
                                <h3>📦 Gestão de Produtos</h3>
                                <p>Catálogo de produtos com categorização, controle de preços e códigos únicos.</p>
                                <a href="/produtos" class="btn">Gerenciar Produtos</a>
                            </div>
                            <div>
                                <h3>🏢 Gestão de Fornecedores</h3>
                                <p>Base completa de fornecedores com informações de contato e histórico comercial.</p>
                                <a href="/fornecedores" class="btn">Gerenciar Fornecedores</a>
                            </div>
                            <div>
                                <h3>🔍 Busca Avançada</h3>
                                <p>Sistema de busca inteligente com filtros múltiplos e resultados relevantes.</p>
                                <a href="/buscar" class="btn">Buscar Registros</a>
                            </div>
                            <div>
                                <h3>⚠️ Detecção de Duplicatas</h3>
                                <p>Identificação automática e resolução de registros duplicados no sistema.</p>
                                <a href="/duplicatas" class="btn">Ver Duplicatas</a>
                            </div>
                            <div>
                                <h3>📊 Auditoria</h3>
                                <p>Log completo de todas as operações realizadas no sistema para compliance.</p>
                                <a href="/auditoria" class="btn">Ver Auditoria</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>💼 Características do Sistema</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                <strong>🔐 Segurança</strong><br>
                                Sistema de autenticação, controle de permissões e auditoria completa.
                            </div>
                            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                <strong>📊 Qualidade de Dados</strong><br>
                                Validação automática, detecção de duplicatas e padronização.
                            </div>
                            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                <strong>🔄 Import/Export</strong><br>
                                Importação e exportação de dados em formato CSV para integração.
                            </div>
                            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                <strong>📱 Responsivo</strong><br>
                                Interface moderna que funciona em desktop, tablet e mobile.
                            </div>
                        </div>
                    </div>
                </div>
                
                <script>
                    // Carregar métricas em tempo real
                    setInterval(async () => {{
                        try {{
                            const response = await fetch('/api/metrics');
                            const data = await response.json();
                            // Atualizar métricas na tela
                        }} catch (error) {{
                            console.log('Erro ao carregar métricas:', error);
                        }}
                    }}, 30000); // A cada 30 segundos
                </script>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.serve_error(f"Erro ao carregar dashboard: {str(e)}")
    
    def get_duplicates_alert(self, duplicate_counts):
        """Gerar alerta de duplicatas"""
        if duplicate_counts['total'] > 0:
            return f"""
            <div class="alert">
                <h3>⚠️ Atenção: {duplicate_counts['total']} grupos de duplicatas detectados!</h3>
                <ul>
                    <li>Clientes: {duplicate_counts['clientes']} grupos</li>
                    <li>Produtos: {duplicate_counts['produtos']} grupos</li>
                    <li>Fornecedores: {duplicate_counts['fornecedores']} grupos</li>
                </ul>
                <a href="/duplicatas" class="btn">Resolver Duplicatas</a>
            </div>
            """
        return ""
    
    def serve_login(self):
        """Servir página de login"""
        html = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema MDM - Login</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .login-container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    width: 100%;
                    max-width: 400px;
                    text-align: center;
                }
                .login-container h1 {
                    color: #333;
                    margin-bottom: 30px;
                }
                .form-group {
                    margin-bottom: 20px;
                    text-align: left;
                }
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: 500;
                }
                .form-group input {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 16px;
                    box-sizing: border-box;
                }
                .form-group input:focus {
                    border-color: #667eea;
                    outline: none;
                }
                .btn-login {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: 500;
                }
                .btn-login:hover {
                    background: #5a6fd8;
                }
                .info {
                    margin-top: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    font-size: 14px;
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🔐 Sistema MDM</h1>
                <p>Acesso ao Sistema de Gerenciamento de Dados Mestres</p>
                
                <form id="loginForm">
                    <div class="form-group">
                        <label for="username">Usuário:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Senha:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn-login">Entrar</button>
                </form>
                
                <div class="info">
                    <strong>Acesso padrão:</strong><br>
                    • Usuário: <code>admin</code><br>
                    • Senha: <code>admin123</code><br><br>
                    
                    <strong>Perfis de usuário:</strong><br>
                    • <strong>Admin:</strong> Acesso total<br>
                    • <strong>Editor:</strong> Criar e editar<br>
                    • <strong>Visualizador:</strong> Apenas leitura
                </div>
            </div>
            
            <script>
                document.getElementById('loginForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    
                    try {
                        const response = await fetch('/api/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ username, password })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            window.location.href = '/dashboard';
                        } else {
                            alert('Usuário ou senha incorretos!');
                        }
                    } catch (error) {
                        alert('Erro ao fazer login: ' + error.message);
                    }
                });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_api_metrics(self):
        """Servir API de métricas"""
        try:
            metrics = db_manager.get_dashboard_metrics()
            duplicate_counts = duplicate_detector.get_duplicate_count()
            
            data = {
                'metrics': metrics,
                'duplicates': duplicate_counts,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.serve_json_error(f"Erro ao carregar métricas: {str(e)}")
    
    def serve_api_duplicates(self):
        """Servir API de duplicatas"""
        try:
            duplicates = duplicate_detector.find_all_duplicates()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(duplicates, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.serve_json_error(f"Erro ao carregar duplicatas: {str(e)}")
    
    def handle_login(self):
        """Lidar com login"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            username = data.get('username')
            password = data.get('password')
            
            # Autenticar usando o sistema existente
            user = auth_manager.authenticate(username, password)
            
            if user:
                response = {'success': True, 'user': user.nome, 'perfil': user.perfil}
            else:
                response = {'success': False, 'error': 'Credenciais inválidas'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.serve_json_error(f"Erro no login: {str(e)}")
    
    def serve_404(self):
        """Servir página 404"""
        html = """
        <html>
        <head><title>404 - Página não encontrada</title></head>
        <body>
            <h1>404 - Página não encontrada</h1>
            <p><a href="/dashboard">Voltar ao Dashboard</a></p>
        </body>
        </html>
        """
        
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_error(self, error_message):
        """Servir página de erro"""
        html = f"""
        <html>
        <head><title>Erro - Sistema MDM</title></head>
        <body>
            <h1>Erro no Sistema</h1>
            <p>{error_message}</p>
            <p><a href="/dashboard">Voltar ao Dashboard</a></p>
        </body>
        </html>
        """
        
        self.send_response(500)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_json_error(self, error_message):
        """Servir erro JSON"""
        error_data = {'error': error_message, 'success': False}
        
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(error_data, ensure_ascii=False).encode('utf-8'))

def run_server(port=8501):
    """Executar servidor web"""
    try:
        server_address = ('', port)
        httpd = HTTPServer(server_address, MDMWebHandler)
        print(f"""
        🚀 Sistema MDM iniciado com sucesso!
        
        📱 Acesse: http://localhost:{port}
        👤 Usuário: admin
        🔑 Senha: admin123
        
        🔗 Endpoints disponíveis:
        • http://localhost:{port}/dashboard - Dashboard principal
        • http://localhost:{port}/login - Página de login
        • http://localhost:{port}/api/metrics - API de métricas
        • http://localhost:{port}/api/duplicates - API de duplicatas
        
        ⚡ Servidor rodando... Pressione Ctrl+C para parar.
        """)
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    run_server()