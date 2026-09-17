<div align="center">

# 🎙️ VOXA
### Clonagem de Voz, Narração & Transcrição Inteligente PT-BR (100% Local & Ilimitado)

[![Banner Voxa](docs/assets/banner.png)](https://github.com/WeslleyMouraDev/Voxa.git)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Chatterbox_TTS-PT--BR-7C3AED?style=for-the-badge&logo=soundcharts&logoColor=white" alt="Chatterbox TTS" />
  <img src="https://img.shields.io/badge/Faster_Whisper-Medium-10B981?style=for-the-badge&logo=openai&logoColor=white" alt="Faster Whisper" />
  <img src="https://img.shields.io/badge/Interface-Dark_Premium-12121A?style=for-the-badge" alt="Dark Premium" />
  <img src="https://img.shields.io/badge/Processamento-100%25_Local-FF6F00?style=for-the-badge" alt="100% Local" />
  <img src="https://img.shields.io/badge/Testes-82%2F82_Passed-success?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest 100%" />
</p>

<p align="center">
  <strong>Uma solução desktop completa, ultra leve e multiplataforma para criadores de conteúdo, editores de vídeo e automações audiovisuais.</strong><br>
  Sem mensalidades. Sem envio de dados para nuvem. Sem travar seu computador.
</p>

[Visão Geral](#-visão-geral) •
[Funcionalidades](#-principais-funcionalidades) •
[Modos de Legenda](#-modos-de-transcrição-inteligente) •
[Controle de CPU](#-controle-anti-travamento-de-cpu) •
[Como Instalar & Rodar](#-como-instalar-e-executar) •
[Interface Web](#-interface-web-dark-premium) •
[Arquitetura](#-estrutura-do-projeto) •
[Licença](#-licença)

---

</div>

## 📖 Visão Geral

O **Voxa** é uma ferramenta projetada para resolver de forma definitiva o fluxo de produção de narração e legendagem para vídeos na língua portuguesa brasileira (**PT-BR**).

Diferente de soluções pesadas ou serviços em nuvem com limites de caracteres e assinaturas caras, o Voxa executa **100% localmente no seu computador** através de uma interface web gráfica moderna (*Dark Theme Premium*). Ele combina:

1. **Clonagem Zero-Shot e Narração Natural:** Utiliza o modelo **Chatterbox TTS Single Language Pack Brazilian Portuguese (PT-BR)**, permitindo clonar qualquer voz a partir de uma amostra curta (10 a 30 segundos) de áudio e sintetizar textos longos sem truncamento.
2. **Transcrição de Alta Precisão com Sincronia para Vídeos:** Utiliza o motor **Faster Whisper** com alinhamento a nível de palavra (*word-level timestamps*) e formatação automática de legendas `.srt` preparadas sob medida para edição de vídeo (troca de 1 imagem/cena por timestamp).
3. **Controle Anti-Travamento de Recursos:** Limita threads de inferência e reduz a prioridade do processo no sistema operacional, garantindo que o seu computador continue fluido mesmo durante gerações contínuas de áudio.
4. **100% Controlável pelo Navegador:** Todo o ciclo — upload de vozes, seleção de voz padrão, ajuste de tempos, narração, download e limpeza de histórico — é realizado visualmente sem tocar no terminal após iniciar.

---

## ✨ Principais Funcionalidades

- 🗣 **Clonagem Vocal Zero-Shot PT-BR:** Clone qualquer locutor com apenas um arquivo de áudio de referência (WAV ou MP3).
- 🎙 **Voz Padrão com 1 Clique:** Defina uma voz favorita como padrão (★) para ser usada automaticamente em todas as próximas narrações.
- ⚡ **Fluxo Direto (Narrar + Transcrever):** Cole o texto e receba simultaneamente o áudio `.mp3` masterizado e o arquivo `.srt` sincronizado.
- ✂️ **Divisão Inteligente de Textos Longos:** Algoritmo nativo de chunking semântico que quebra frases longas por pontuação, concatena áudios perfeitamente e impede corte de palavras.
- ⏱ **3 Modos de Transcrição por Cena:** Alterne instantaneamente entre os modos *Normal*, *Dinâmico* e *Acelerado* de acordo com a velocidade do seu vídeo.
- 📊 **Feedback em Tempo Real (SSE):** Acompanhe o percentual e a etapa exata do processamento via Server-Sent Events sem recarregar a tela.
- 🎵 **Player Inline & Downloads Imediatos:** Ouça a narração gerada na própria tela e baixe os arquivos individuais com facilidade.
- 🗄 **Gerenciamento de Histórico com Limpeza Física:** Consulte narrações anteriores, exclua itens específicos ou limpe todo o armazenamento com remoção automática dos arquivos do disco.
- 🛡️ **Total Privacidade:** Nenhum dado, texto ou áudio sai da sua máquina.

---

## 🎯 Modos de Transcrição Inteligente

O Voxa foi pensado especificamente para **edição de vídeo sincronizada** (onde cada bloco de legenda equivale à troca de uma imagem, take ou ilustração):

| Modo | Duração por Bloco | Estilo Recomendado | Cenário de Uso |
| :--- | :---: | :--- | :--- |
| **Normal** | **4.0s a 6.0s** | Documentários, Aulas, VSLs Institucionais | 1 imagem a cada 4–6s. Ritmo pausado e narrativo com quebras em pontuações fortes (`.`, `!`, `?`). |
| **Dinâmico** | **2.0s a 4.0s** | Reels, TikToks, Shorts, YouTube Padrão | Cortes médios e ágeis. Mantém alta retenção do público com estímulos visuais frequentes. |
| **Acelerado** | **1.0s a 2.0s** | VSL Acelerada, Vídeos Estilo MrBeast | Cortes ultra rápidos (1 a 2s por imagem). Dinamismo máximo para reter audiência móvel. |

> ⚙️ *Todos os tempos mínimo e máximo de cada modo são ajustáveis na aba de **Configurações** da interface web.*

---

## 🛡️ Controle Anti-Travamento de CPU

Gerações de áudio por inteligência artificial podem sobrecarregar núcleos de processamento se não forem contidas. O Voxa inclui o módulo **`CPULimiter`**:

- **Limitação de Threads:** Configuração dinâmica de uso da CPU (25% a 100% dos núcleos lógicos, com padrão em **75%**), controlando as threads do PyTorch (`torch.set_num_threads`).
- **Prioridade Reduzida no SO:**
  - **Windows:** Define o processo como `psutil.BELOW_NORMAL_PRIORITY_CLASS`.
  - **Linux / macOS:** Aplica `nice(10)`.
- **Resultado:** Seu navegador, editor de vídeo, Discord ou sistema continuam 100% utilizáveis e sem engasgos durante a síntese.

---

## 🚀 Como Instalar e Executar

### 💻 No Windows

O Voxa possui inicializadores premium no formato Batch (`.bat`), totalmente compatíveis com UTF-8 e imunes a erros de parser do CMD:

1. **Clone o repositório:**
   ```cmd
   git clone https://github.com/WeslleyMouraDev/Voxa.git
   cd Voxa
   ```

2. **Instalação Inicial (cria o ambiente virtual e instala dependências):**
   Dê dois cliques no arquivo ou rode no terminal:
   ```cmd
   setup.bat
   ```

3. **Iniciar a Aplicação:**
   Dê dois cliques no arquivo ou rode no terminal:
   ```cmd
   start.bat
   ```
   *O terminal ativará o ambiente virtual, iniciará o servidor FastAPI e abrirá o navegador automaticamente em `http://localhost:7865`.*

---

### 🍏🐧 No Linux ou macOS

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/WeslleyMouraDev/Voxa.git
   cd Voxa
   ```

2. **Dê permissão de execução e instale:**
   ```bash
   chmod +x setup.sh start.sh
   ./setup.sh
   ```

3. **Inicie o servidor:**
   ```bash
   ./start.sh
   ```

---

## 🖥️ Interface Web Dark Premium

A interface gráfica do Voxa foi desenvolvida em formato **Single Page Application (SPA)** leve e responsiva (sem necessidade de Node.js, Webpack ou builds demorados):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  VOXA [PT-BR]   │  🎙️ NARRAR                                                │
│                 │                                                           │
│  🎙️ Narrar      │  ┌─────────────────────────────────────────────────────┐  │
│  🗣️ Vozes       │  │ Digite ou cole o texto que deseja narrar...         │  │
│  📋 Histórico   │  │                                                     │  │
│  ⚙️ Config      │  │                                      342 caracteres │  │
│                 │  └─────────────────────────────────────────────────────┘  │
│                 │                                                           │
│  ● Sistema      │  Voz: [ João Locutor (★ Padrão) ▼ ]    Modo: [ Dinâmico ▼ ]│
│    Pronto       │                                                           │
│                 │  [ 🎙️ Apenas Narrar ]   [ 📝 Apenas Transcrever ]          │
│                 │  [ ⚡ Narrar + Transcrever (MP3 + SRT) ]                  │
│                 │                                                           │
│                 │  Status: Sintetizando áudio com voz clonada... [75%]      │
│                 │  [██████████████████████████░░░░░░░░]                     │
│                 │                                                           │
│                 │  ▶ [======●=================] 00:24 / 00:32               │
│                 │  [ ⬇ Baixar Áudio (.mp3) ]    [ ⬇ Baixar Legenda (.srt) ] │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Paleta de Cores:** Deep Black (`#0a0a0f`), Dark Surface (`#12121a`), Primary Purple (`#7c3aed`), Emerald Success (`#10b981`).
- **Tipografia:** `Inter` para clareza visual e `JetBrains Mono` para dados técnicos e timestamps.

---

## 🧱 Estrutura do Projeto

```
Voxa/
├── backend/
│   ├── main.py                  # Servidor FastAPI e rotas de arquivos estáticos
│   ├── config.py                # Diretórios de dados, cache e saídas
│   ├── models/
│   │   ├── enums.py             # Modos de transcrição e status de tarefas
│   │   └── schemas.py           # Modelos de validação Pydantic
│   ├── services/
│   │   ├── cpu_limiter.py       # Gerenciamento de threads e prioridade de processo
│   │   ├── task_manager.py      # Fila assíncrona e emissor de eventos SSE
│   │   ├── srt_builder.py       # Algoritmo de empacotamento de legendas
│   │   ├── tts_service.py       # Wrapper do Chatterbox TTS com chunking PT-BR
│   │   └── stt_service.py       # Wrapper do Faster Whisper com word-level timestamps
│   ├── storage/
│   │   ├── json_store.py        # Gravação atômica em disco com lock de concorrência
│   │   ├── voice_store.py       # Gerenciador de vozes cadastradas e voz padrão
│   │   ├── history_store.py     # Gerenciador de histórico e limpeza física
│   │   └── settings_store.py    # Persistência de parâmetros do usuário
│   └── routers/
│       ├── narration.py         # Endpoints de narração simples e fluxo direto
│       ├── transcription.py     # Endpoints de transcrição avulsa
│       ├── voices.py            # CRUD de vozes clonadas e upload
│       ├── history.py           # Consulta e exclusão de histórico
│       ├── settings.py          # Configurações do Voxa
│       └── progress.py          # Streaming SSE em tempo real
├── frontend/
│   ├── index.html               # Shell da aplicação SPA
│   ├── css/style.css            # Estilização Dark Premium moderna
│   ├── js/                      # Lógica Vanilla modularizada (API, State, Pages)
│   └── assets/                  # Logo SVG e ícones
├── docs/assets/                 # Banners e imagens de documentação
├── tests/                       # Suíte automatizada com 82 testes pytest
├── setup.bat                    # Instalador Windows (UTF-8 / sem erros de parser)
├── start.bat                    # Inicializador Windows com auto-open de navegador
├── setup.sh                     # Instalador Linux/macOS
├── start.sh                     # Inicializador Linux/macOS
├── requirements.txt             # Dependências do ecossistema Python
└── README.md                    # Documentação oficial
```

---

## 📡 Endpoints da API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/narrate` | Inicia geração de narração com voz clonada (retorna `task_id`) |
| `POST` | `/api/narrate-and-transcribe` | Inicia fluxo direto gerando `.mp3` e `.srt` sincronizados |
| `POST` | `/api/transcribe` | Transcreve um áudio existente no modo selecionado |
| `GET` | `/api/progress/{task_id}` | Stream SSE com progresso e porcentagem em tempo real |
| `GET` | `/api/voices` | Lista todas as vozes cadastradas |
| `POST` | `/api/voices` | Cadastra nova voz por upload de amostra (WAV/MP3) |
| `PUT` | `/api/voices/{id}/default` | Define uma voz como padrão do sistema |
| `DELETE` | `/api/voices/{id}` | Exclui a voz e apaga o arquivo físico de amostra |
| `GET` | `/api/history` | Retorna o histórico de narrações ordenado |
| `DELETE` | `/api/history/{id}` | Exclui um item e seus arquivos de áudio/SRT |
| `DELETE` | `/api/history` | Limpa todo o histórico e remove todos os arquivos físicos |
| `GET` | `/api/settings` | Obtém parâmetros atuais (CPU, limites de legenda, porta) |
| `PUT` | `/api/settings` | Atualiza parâmetros e aplica limite de CPU imediatamente |

---

## 🧪 Testes Automatizados

O Voxa foi desenvolvido sob a disciplina rigorosa de **Test-Driven Development (TDD)** e **Subagent-Driven Development**. Toda a suíte de testes pode ser executada com:

```bash
pytest -v
```

```text
======================== 82 passed, 1 warning in 2.15s ========================
```

---

## 🤝 Contribuição

Contribuições são muito bem-vindas! Se você deseja adicionar melhorias:

1. Faça um Fork do projeto no GitHub.
2. Crie uma branch para sua funcionalidade: `git checkout -b feature/minha-feature`.
3. Adicione testes para o seu código e certifique-se de que `pytest -v` passe 100%.
4. Faça o commit das suas alterações: `git commit -m 'feat: minha nova feature'`.
5. Envie para o branch remoto: `git push origin feature/minha-feature`.
6. Abra um **Pull Request**.

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais informações.

<div align="center">
  <sub>Desenvolvido com dedicação para a comunidade de criadores de conteúdo e inteligência artificial aberta.</sub>
</div>
