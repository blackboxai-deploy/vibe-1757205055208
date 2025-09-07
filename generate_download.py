#!/usr/bin/env python3
"""
Script para gerar arquivo ZIP com todos os arquivos do projeto MDM
"""
import os
import zipfile
from datetime import datetime

def create_project_zip():
    """Criar arquivo ZIP com todo o projeto"""
    
    # Nome do arquivo ZIP
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"sistema_mdm_completo_{timestamp}.zip"
    
    # Lista de arquivos e diretórios para incluir
    files_to_include = [
        # Arquivos principais
        'app.py',
        'web_app.py',
        'simple_server.py',
        'init_system.py',
        'config.py',
        'requirements.txt',
        'TODO.md',
        'README.md',
        
        # Diretório database
        'database/__init__.py',
        'database/models.py',
        'database/database_manager.py',
        
        # Diretório utils
        'utils/__init__.py',
        'utils/auth.py',
        'utils/duplicate_detector.py',
        'utils/search_engine.py',
        'utils/audit_manager.py',
        'utils/import_export.py',
        'utils/validators.py',
        
        # Diretório pages
        'pages/__init__.py',
        
        # Diretório static
        'static/style.css'
    ]
    
    print(f"📦 Criando arquivo ZIP: {zip_filename}")
    print("=" * 50)
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        files_added = 0
        total_size = 0
        
        for file_path in files_to_include:
            if os.path.exists(file_path):
                zipf.write(file_path, file_path)
                file_size = os.path.getsize(file_path)
                total_size += file_size
                print(f"✅ {file_path:<40} ({file_size:>6} bytes)")
                files_added += 1
            else:
                print(f"⚠️  {file_path:<40} (não encontrado)")
        
        # Adicionar arquivo de banco de dados se existir
        if os.path.exists('data/mdm_database.db'):
            zipf.write('data/mdm_database.db', 'data/mdm_database.db')
            file_size = os.path.getsize('data/mdm_database.db')
            total_size += file_size
            print(f"✅ {'data/mdm_database.db':<40} ({file_size:>6} bytes)")
            files_added += 1
        
        print("=" * 50)
        print(f"📊 Total de arquivos incluídos: {files_added}")
        print(f"📏 Tamanho total dos arquivos: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
    # Mostrar informações do arquivo ZIP
    zip_size = os.path.getsize(zip_filename)
    print(f"📁 Arquivo ZIP criado: {zip_filename}")
    print(f"📦 Tamanho compactado: {zip_size:,} bytes ({zip_size/1024:.1f} KB)")
    print(f"🗜️  Taxa de compressão: {((total_size - zip_size) / total_size * 100):.1f}%")
    
    return zip_filename

def create_download_guide():
    """Criar guia de download"""
    guide_content = """# 📥 GUIA DE DOWNLOAD - Sistema MDM

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
"""
    
    with open('DOWNLOAD_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ DOWNLOAD_GUIDE.md criado")

def show_file_manifest():
    """Mostrar manifest dos arquivos"""
    print("\n📋 MANIFEST DE ARQUIVOS DO SISTEMA MDM")
    print("=" * 60)
    
    file_categories = {
        "🚀 Aplicações Principais": [
            "simple_server.py",
            "app.py", 
            "web_app.py",
            "init_system.py"
        ],
        "⚙️ Configuração": [
            "config.py",
            "requirements.txt"
        ],
        "🗄️ Banco de Dados": [
            "database/__init__.py",
            "database/models.py",
            "database/database_manager.py"
        ],
        "🛠️ Utilitários": [
            "utils/__init__.py",
            "utils/auth.py",
            "utils/duplicate_detector.py",
            "utils/search_engine.py",
            "utils/audit_manager.py",
            "utils/import_export.py",
            "utils/validators.py"
        ],
        "🎨 Interface": [
            "static/style.css",
            "pages/__init__.py"
        ],
        "📚 Documentação": [
            "TODO.md",
            "README.md"
        ]
    }
    
    total_files = 0
    total_size = 0
    
    for category, files in file_categories.items():
        print(f"\n{category}")
        print("-" * 30)
        
        for file_path in files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size
                status = "✅"
                size_info = f"({file_size:>5} bytes)"
            else:
                status = "❌"
                size_info = "(não encontrado)"
            
            print(f"{status} {file_path:<30} {size_info}")
            total_files += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMO:")
    print(f"   Total de arquivos: {total_files}")
    print(f"   Tamanho total: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"   Arquivos encontrados: {len([f for cat in file_categories.values() for f in cat if os.path.exists(f)])}")

def main():
    """Função principal"""
    print("📥 SISTEMA MDM - GERADOR DE DOWNLOAD")
    print("=" * 60)
    
    # Mostrar manifest
    show_file_manifest()
    
    # Criar guia de download
    print("\n📝 Criando guia de download...")
    create_download_guide()
    
    # Criar ZIP
    print("\n📦 Gerando arquivo ZIP...")
    zip_file = create_project_zip()
    
    print("\n🎉 ARQUIVOS PRONTOS PARA DOWNLOAD!")
    print("=" * 60)
    print(f"📦 Arquivo ZIP completo: {zip_file}")
    print(f"📋 Guia de download: DOWNLOAD_GUIDE.md")
    print()
    print("💡 COMO BAIXAR:")
    print("1. Execute este script para gerar o ZIP")
    print("2. Baixe o arquivo ZIP gerado")
    print("3. Ou baixe arquivos individuais conforme o guia")
    print()
    print("🚀 COMO USAR:")
    print("1. Extraia o ZIP em seu computador")
    print("2. python3 init_system.py")
    print("3. python3 simple_server.py")
    print("4. Acesse: http://localhost:8501/dashboard")
    print("5. Login: admin / admin123")
    print("=" * 60)

if __name__ == "__main__":
    main()