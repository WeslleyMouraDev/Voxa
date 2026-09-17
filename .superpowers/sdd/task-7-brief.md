# Task 7: Scripts de Inicialização Multiplataforma, Dependências e Validação E2E

## Objetivo
Criar os instaladores e inicializadores multiplataforma para Windows, macOS e Linux, o arquivo de dependências `requirements.txt`, `.gitignore` e a documentação completa em `README.md`. Testar a conformidade de todos os scripts e validar a suíte completa de testes.

## Arquivos a Criar
- `requirements.txt`
- `setup.bat`
- `start.bat`
- `setup.sh`
- `start.sh`
- `.gitignore`
- `README.md`
- `tests/test_launchers.py`

## Especificações Técnicas e Diretrizes Rigorosas

### 1. `setup.bat` (Windows Installer)
- Deve seguir RIGOROSAMENTE a skill `windows-batch-launchers` e as regras globais:
  - `@echo off`
  - `setlocal EnableDelayedExpansion`
  - `chcp 65001 >nul`
  - `title Voxa — Instalador do Sistema`
  - `color 0B`
  - `cd /d "%~dp0"`
  - **NUNCA** colocar parênteses não escapados dentro de blocos `if (...)` ou `for (...)`. Use SEMPRE desvios com rótulos `goto :label`.
  - Passos numerados:
    - `[1/4]` Verificando Python 3.10+
    - `[2/4]` Configurando ambiente virtual Python (.venv)
    - `[3/4]` Instalando dependências (requirements.txt) via `call python -m pip install -r requirements.txt`
    - `[4/4]` Verificando diretórios de dados e saída (data/, voices/, output/)
  - Finalizar com mensagem de sucesso e instrução para executar `start.bat`.

### 2. `start.bat` (Windows Launcher)
- `@echo off`
- `setlocal EnableDelayedExpansion`
- `chcp 65001 >nul`
- `title Voxa — Clonagem, Narração e Transcrição PT-BR`
- `color 0A`
- `cd /d "%~dp0"`
- Sem parênteses em blocos IF (usar `goto :label`).
- Passos:
  - `[1/3]` Verificando ambiente virtual (.venv) -> se não existir, redireciona com aviso para rodar `setup.bat`.
  - `[2/3]` Ativando ambiente virtual...
  - `[3/3]` Abrindo interface web e iniciando servidor FastAPI na porta 7865...
- Executa `start "" "http://localhost:7865"` para abrir o navegador sem travar o terminal.
- Executa `call python -m uvicorn backend.main:app --host 127.0.0.1 --port 7865`.

### 3. `setup.sh` e `start.sh` (Linux / macOS)
- `#!/usr/bin/env bash`
- `set -e`
- Passos equivalentes aos `.bat` com cores ANSI elegantes no terminal.

### 4. `requirements.txt`
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
python-multipart>=0.0.9
psutil>=5.9.0
chatterbox-tts>=0.3.0
faster-whisper>=1.0.0
torch>=2.0.0
torchaudio>=2.0.0
pydub>=0.25.0
soundfile>=0.12.1
numpy>=1.24.0
pytest>=8.0.0
httpx>=0.27.0
```

### 5. `.gitignore`
- Ignorar `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `data/*.tmp`, `output/*`, `voices/*` (mantendo pastas com `.gitkeep`), `.superpowers/`.

### 6. `README.md`
- Documentação completa, limpa e profissional em Português do Brasil:
  - Título, badge e descrição do Voxa.
  - Link oficial do repositório: `https://github.com/WeslleyMouraDev/Voxa.git`
  - Recursos principais:
    - Clonagem zero-shot com Chatterbox TTS (Single Language Pack PT-BR).
    - Transcrição inteligente com Faster Whisper e 3 modos (Normal, Dinâmico, Acelerado).
    - Controle anti-travamento de CPU.
    - 100% controlável via interface web moderna Dark Premium.
  - Como instalar e rodar no Windows (`setup.bat` / `start.bat`) e Linux/Mac (`./setup.sh` / `./start.sh`).
  - Estrutura de pastas e endpoints da API.

## Requisitos de Testes (`tests/test_launchers.py`)
- Testar que `setup.bat` e `start.bat` contêm `chcp 65001`.
- Testar que os scripts batch não contêm parênteses não escapados dentro de blocos `if` ou `for` (analisador sintático de batch).
- Testar que `requirements.txt` contém os pacotes fundamentais (`fastapi`, `chatterbox-tts`, `faster-whisper`, `psutil`, `pydantic`).
- Testar que `.gitignore` ignora arquivos temporários e caches.

## Comandos
- Testes: `python -m pytest -v`
- Commits: `git add requirements.txt setup.bat start.bat setup.sh start.sh .gitignore README.md tests/test_launchers.py && git commit -m "feat: add multiplatform launcher scripts, requirements and complete documentation"`
