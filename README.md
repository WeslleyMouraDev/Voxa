# 🎙️ Voxa

> **Sistema Completo de Clonagem de Voz Zero-Shot, Narração e Transcrição Inteligente com Legendas Dinâmicas em Português do Brasil.**

[![GitHub Repository](https://img.shields.io/badge/GitHub-WeslleyMouraDev%2FVoxa-blue?style=flat&logo=github)](https://github.com/WeslleyMouraDev/Voxa.git)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Visão Geral

O **Voxa** é uma plataforma moderna desenvolvida para criadores de conteúdo, narradores e pesquisadores. Ele combina síntese de fala realista de ponta com transcrição ultra-rápida e sincronização precisa de legendas no formato `.srt`.

Repositório Oficial: **[https://github.com/WeslleyMouraDev/Voxa.git](https://github.com/WeslleyMouraDev/Voxa.git)**

---

## ✨ Recursos Principais

- **🎭 Clonagem Zero-Shot com Chatterbox TTS:**
  - Gera áudios ultrarrealistas mantendo o timbre, sotaque e nuances da voz de referência com apenas alguns segundos de áudio prévio.
  - Otimizado para o idioma Português do Brasil (Single Language Pack PT-BR).
  - Divisão inteligente de textos longos em sentenças naturais com normalização e junção precisa.

- **⚡ Transcrição Inteligente com Faster Whisper:**
  - Extração de timestamps em nível de palavra (*word-level timestamps*).
  - 3 Modos de segmentação de legendas para vídeos e redes sociais:
    - **Normal:** Frases completas para documentários e vídeos longos de YouTube.
    - **Dinâmico (Reels / TikTok):** Segmentos de 2 a 4 segundos com quebras rítmicas e pontuações fortes.
    - **Acelerado (Shorts):** Palavra a palavra ou blocos ultra-curtos de até 1.5s para engajamento frenético.

- **🛡️ Proteção Anti-Travamento e Controle de CPU:**
  - Limitação inteligente de threads do PyTorch (`torch.set_num_threads`) e afinidade de processos (`psutil`).
  - Prioridade de processo (`BELOW_NORMAL_PRIORITY_CLASS` no Windows / `os.nice` no Linux) para garantir que seu sistema permaneça responsivo mesmo durante renderizações pesadas.

- **🎨 Interface Web Dark Premium (SPA):**
  - Painel moderno, limpo e responsivo com navegação em abas (Narração, Vozes, Histórico, Configurações).
  - Acompanhamento de progresso em tempo real com barra de progresso via **Server-Sent Events (SSE)**.
  - Reprodutor de áudio nativo integrado com download direto de áudio e legendas `.srt`.

---

## 🚀 Instalação e Execução

### 🪟 Windows

1. **Instalação:**
   Dê um duplo clique em `setup.bat` ou execute no PowerShell/CMD:
   ```cmd
   setup.bat
   ```
   *O instalador verificará o Python 3.10+, criará o ambiente virtual `.venv`, atualizará o pip e instalará todos os pacotes do `requirements.txt`.*

2. **Inicialização:**
   Dê um duplo clique em `start.bat` ou execute:
   ```cmd
   start.bat
   ```
   *O inicializador ativará o ambiente virtual e abrirá automaticamente seu navegador padrão em `http://localhost:7865`.*

---

### 🐧 Linux / 🍎 macOS

1. **Permissões de Execução (se necessário):**
   ```bash
   chmod +x setup.sh start.sh
   ```

2. **Instalação:**
   ```bash
   ./setup.sh
   ```

3. **Inicialização:**
   ```bash
   ./start.sh
   ```
   *Acesse no navegador: `http://localhost:7865`*

---

## 📁 Estrutura do Projeto

```text
Voxa/
├── backend/
│   ├── models/            # Schemas Pydantic e Enums (Voice, Task, SRTMode, Settings)
│   ├── routers/           # Endpoints FastAPI (narration, transcription, voices, history, settings, progress)
│   ├── services/          # Chatterbox TTS, Faster Whisper STT, SRT Builder, CPU Limiter, Task Manager
│   ├── storage/           # Persistência atômica JSON thread-safe para configurações, vozes e histórico
│   ├── config.py          # Configurações globais e caminhos
│   └── main.py            # Ponto de entrada FastAPI e montagem da SPA estática
├── frontend/
│   ├── assets/            # Ícones e logotipos SVG
│   ├── css/               # Folha de estilos Dark Premium (glassmorphism, responsividade)
│   ├── js/                # Controladores modulares (api.js, state.js, pages/, components/)
│   └── index.html         # Página única SPA
├── data/                  # Armazenamento JSON local (persistência de configurações e histórico)
├── voices/                # Amostras de voz de referência (.wav / .mp3)
├── output/                # Áudios gerados e legendas .srt exportadas
├── tests/                 # Suíte completa de testes unitários e de integração (Pytest)
├── setup.bat              # Instalador automatizado para Windows
├── start.bat              # Inicializador com abertura de navegador para Windows
├── setup.sh               # Instalador automatizado para Linux/macOS
├── start.sh               # Inicializador para Linux/macOS
├── requirements.txt       # Dependências oficiais do projeto
└── README.md              # Documentação completa
```

---

## 📡 Endpoints da API REST

A API do Voxa é totalmente documentada via OpenAPI (Swagger). Você pode acessar a documentação interativa em:
`http://localhost:7865/docs`

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/narrate` | Inicia tarefa em background de narração por síntese/clonagem |
| `POST` | `/api/transcribe` | Inicia transcrição de áudio e geração de SRT com timestamps |
| `POST` | `/api/narrate-and-transcribe` | Pipeline completo: sintetiza o áudio e gera as legendas |
| `GET` | `/api/progress/{task_id}` | Consulta status de uma tarefa |
| `GET` | `/api/progress/{task_id}/stream` | Stream em tempo real de eventos de progresso via **SSE** |
| `GET` | `/api/voices` | Lista todas as vozes de referência cadastradas |
| `POST` | `/api/voices` | Cadastra uma nova voz de referência (upload de arquivo de áudio) |
| `POST` | `/api/voices/{id}/default` | Define a voz padrão do sistema |
| `DELETE` | `/api/voices/{id}` | Remove uma voz cadastrada |
| `GET` | `/api/history` | Retorna o histórico de gerações recentes |
| `DELETE` | `/api/history/{id}` | Remove um item específico do histórico |
| `DELETE` | `/api/history` | Limpa todo o histórico |
| `GET` | `/api/settings` | Obtém as preferências do sistema e limites de CPU |
| `PUT` | `/api/settings` | Atualiza parâmetros de síntese, transcrição e hardware |

---

## 🛠️ Tecnologias Utilizadas

- **FastAPI & Uvicorn**: Backend assíncrono de alta performance.
- **Chatterbox TTS**: Síntese de voz neural com clonagem zero-shot em PT-BR.
- **Faster Whisper (CTranslate2)**: Transcrição rápida com uso otimizado de memória.
- **PyTorch & TorchAudio**: Computação de tensores e processamento de áudio.
- **Vanilla JavaScript & CSS Moderno**: Frontend ultraleve, sem dependências pesadas, com tema Dark Glassmorphism.

---

## 📄 Licença

Este projeto é disponibilizado sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
