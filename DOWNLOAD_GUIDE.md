# 📥 GUIA DE DOWNLOAD - Sistema MDM

## 🎯 Arquivos Disponíveis para Download

### 📦 Arquivo Completo (ZIP)
Execute o comando para gerar o arquivo ZIP completo:
```bash
python3 generate_download.py
```

### 📋 Arquivos Individuais
Você pode baixar os seguintes arquivos individualmente:

#### 🚀 Aplicações Principais
- `simple_server.py` - Servidor HTTP principal (RECOMENDADO)
- `app.py` - Aplicação Streamlit (alternativa)
- `web_app.py` - Aplicação Flask (alternativa)
- `init_system.py` - Script de inicialização

#### ⚙️ Configuração
- `config.py` - Configurações do sistema
- `requirements.txt` - Dependências Python

#### 🗄️ Banco de Dados
- `database/models.py` - Modelos de dados
- `database/database_manager.py` - Gerenciador CRUD
- `database/__init__.py` - Inicializador do módulo

#### 🛠️ Utilitários
- `utils/auth.py` - Sistema de autenticação
- `utils/duplicate_detector.py` - Detector de duplicatas
- `utils/search_engine.py` - Motor de busca
- `utils/audit_manager.py` - Sistema de auditoria
- `utils/import_export.py` - Import/Export CSV
- `utils/validators.py` - Validadores de dados
- `utils/__init__.py` - Inicializador do módulo

#### 🎨 Interface
- `static/style.css` - Estilos CSS
- `pages/__init__.py` - Módulo de páginas

#### 📚 Documentação
- `TODO.md` - Status do projeto
- `README.md` - Manual completo

## 🏗️ Instruções de Instalação

### 1. Download dos Arquivos
```bash
# Opção A: Download do ZIP completo
python3 generate_download.py

# Opção B: Clone/download arquivos individuais
mkdir sistema_mdm
cd sistema_mdm
# Baixe todos os arquivos listados acima
```

### 2. Estrutura de Diretórios
Organize os arquivos na seguinte estrutura:
```
sistema_mdm/
├── app.py
├── simple_server.py
├── web_app.py
├── init_system.py
├── config.py
├── requirements.txt
├── README.md
├── TODO.md
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── database_manager.py
├── utils/
│   ├── __init__.py
│   ├── auth.py
│   ├── duplicate_detector.py
│   ├── search_engine.py
│   ├── audit_manager.py
│   ├── import_export.py
│   └── validators.py
├── pages/
│   └── __init__.py
└── static/
    └── style.css
```

### 3. Inicialização
```bash
# Inicializar o sistema
python3 init_system.py

# Executar o servidor
python3 simple_server.py
```

### 4. Acesso
- URL: http://localhost:8501/dashboard
- Login: admin
- Senha: admin123

## 📋 Lista de Verificação

### ✅ Arquivos Obrigatórios
- [ ] simple_server.py (servidor principal)
- [ ] init_system.py (inicializador)
- [ ] config.py (configurações)
- [ ] database/models.py (modelos)
- [ ] database/database_manager.py (CRUD)
- [ ] utils/auth.py (autenticação)
- [ ] utils/duplicate_detector.py (duplicatas)

### ✅ Arquivos Opcionais
- [ ] app.py (Streamlit - requer instalação)
- [ ] web_app.py (Flask - alternativa)
- [ ] utils/search_engine.py (busca avançada)
- [ ] utils/audit_manager.py (auditoria)
- [ ] utils/import_export.py (import/export)
- [ ] static/style.css (estilos)

## 🚨 Solução de Problemas

### Erro: "Módulo não encontrado"
- Verifique se todos os arquivos estão na estrutura correta
- Execute `python3 init_system.py` antes do servidor

### Erro: "Porta já em uso"
- Altere a porta no arquivo simple_server.py
- Ou mate o processo: `pkill -f python3`

### Erro: "Banco não inicializado"
- Execute `python3 init_system.py`
- Verifique se a pasta `data/` foi criada

## 📞 Suporte

Em caso de problemas:
1. Verifique a estrutura de diretórios
2. Execute o inicializador: `python3 init_system.py`
3. Verifique os logs no terminal
4. Teste as APIs: `curl http://localhost:8501/health`

---
**Sistema MDM - Desenvolvido em Python 🐍**
