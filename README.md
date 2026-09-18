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
  <img src="https://img.shields.io/badge/Testes-139%2F139_Passed-success?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest 100%" />
</p>

<p align="center">
  <strong>Uma solução desktop completa, ultra leve e multiplataforma para criadores de conteúdo, editores de vídeo e automações audiovisuais.</strong><br>
  Sem mensalidades. Sem envio de dados para nuvem. Sem travar seu computador.
</p>

[Visão Geral](#-visão-geral) •
[Funcionalidades](#-principais-funcionalidades) •
[Controles de Voz](#-controles-avançados-de-voz) •
[Modos de Legenda](#-modos-de-transcrição-inteligente) •
[Logs & Métricas](#-painel-de-logs--telemetria-em-tempo-real) •
[Controle de CPU](#-controle-anti-travamento-de-cpu) •
[Como Instalar & Rodar](#-como-instalar-e-executar) •
[Interface Web](#-interface-web-dark-premium) •
[API REST & Docs](#-api-rest--documentação-interativa) •
[Arquitetura](#-estrutura-do-projeto) •
[Licença](#-licença)

---

</div>

## 📖 Visão Geral

O **Voxa** é uma ferramenta projetada para resolver de forma definitiva o fluxo de produção de narração e legendagem para vídeos na língua portuguesa brasileira (**PT-BR**).

Diferente de soluções pesadas ou serviços em nuvem com limites de caracteres e assinaturas caras, o Voxa executa **100% localmente no seu computador** através de uma interface web gráfica moderna (*Dark Theme Premium*). Ele combina:

1. **Clonagem Zero-Shot e Narração Natural:** Utiliza o modelo **Chatterbox TTS Single Language Pack Brazilian Portuguese (PT-BR)**, permitindo clonar qualquer voz a partir de uma amostra curta (10 a 30 segundos) de áudio e sintetizar textos longos sem truncamento.
2. **Controles Finos de Entonação e Dinâmica:** Ajuste fino de velocidade de fala, duração máxima de pausas entre frases, afinação (tom) em semitons e expressividade da voz com presets prontos (Natural, Dinâmico, Solene, Energético).
3. **Transcrição de Alta Precisão com Sincronia para Vídeos:** Utiliza o motor **Faster Whisper** com alinhamento a nível de palavra (*word-level timestamps*) e formatação automática de legendas `.srt` preparadas sob medida para edição de vídeo (troca de 1 imagem/cena por timestamp).
4. **Painel de Logs & Telemetria em Tempo Real:** Drawer deslizante estilo DevTools com streaming WebSocket, medidores de CPU e RAM, busca em tempo real, filtros por nível e sanitização de dados.
5. **API REST Completa & Documentação Interativa:** Além da SPA, o Voxa oferece endpoints REST documentados com Swagger UI (`/docs`), ReDoc (`/redoc`) e uma página interna `#api-docs` com gerador de comandos cURL com 1 clique para integrações externas.
6. **Controle Anti-Travamento de Recursos:** Limita threads de inferência e reduz a prioridade do processo no sistema operacional, garantindo que o seu computador continue fluido mesmo durante gerações contínuas de áudio.

---

## ✨ Principais Funcionalidades

- 🗣 **Clonagem Vocal Zero-Shot PT-BR:** Clone qualquer locutor com apenas um arquivo de áudio de referência (WAV ou MP3).
- 🎙 **Voz Padrão com 1 Clique:** Defina uma voz favorita como padrão (★) para ser usada automaticamente em todas as próximas narrações.
- 🎛 **Controles Avançados de Voz:** Modifique ritmo (0.5x–2.0x), pausas entre frases (0.0s–2.0s), tom (-12 a +12 semitons) e presença emocional (0.0–1.0) com presets rápidos.
- ⚡ **Fluxo Direto (Narrar + Transcrever):** Cole o texto e receba simultaneamente o áudio `.mp3` masterizado e o arquivo `.srt` sincronizado.
- ✂️ **Divisão Inteligente de Textos Longos:** Algoritmo nativo de chunking semântico que quebra frases longas por pontuação, concatena áudios perfeitamente e impede corte de palavras.
- ⏱ **3 Modos de Transcrição por Cena:** Alterne instantaneamente entre os modos *Normal*, *Dinâmico* e *Acelerado* de acordo com a velocidade do seu vídeo.
- 📊 **Feedback em Tempo Real (SSE & WebSocket):** Acompanhe o percentual da tarefa via SSE e a telemetria do sistema (CPU/RAM) e logs de execução via WebSocket.
- 🛠 **DevTools / Drawer de Logs:** Inspecione logs detalhados, filtre por gravidade (DEBUG a CRITICAL), realize buscas instantâneas e copie traces com 1 clique.
- 🎵 **Player Inline & Downloads Imediatos:** Ouça a narração gerada na própria tela e baixe os arquivos individuais com facilidade.
- 🗄 **Gerenciamento de Histórico com Limpeza Física:** Consulte narrações anteriores com os parâmetros de voz utilizados, exclua itens específicos ou limpe todo o armazenamento.
- 📖 **API Docs Integrado na SPA:** Explore endpoints, contratos JSON e exemplos de cURL sem sair da ferramenta.
- 🛡️ **Total Privacidade:** Nenhum dado, texto ou áudio sai da sua máquina.

---

## 🎛️ Controles Avançados de Voz

Na tela de Narração, o painel colapsável **"Controles de Voz"** permite esculpir a entonação e a velocidade da fala para se adequar exatamente ao ritmo do seu conteúdo audiovisual:

| Controle | Parâmetro | Faixa de Valores | Padrão | Descrição & Aplicação |
| :--- | :---: | :---: | :---: | :--- |
| **Ritmo de Fala** | `speed` | `0.5x` a `2.0x` | `1.0x` | Acelera ou desacelera a narração mantendo a afinação natural original (processamento de tempo via FFmpeg `atempo`). |
| **Pausa Máxima** | `max_pause` | `0.0s` a `2.0s` | `0.5s` | Controla o intervalo de silêncio inserido entre frases e orações para respiração natural ou dinamismo total. |
| **Tom / Pitch** | `pitch` | `-12` a `+12` semitons | `0` | Eleva ou rebaixa a tonalidade da voz em semitons musicais sem alterar a duração total (ajuste harmônico via FFmpeg). |
| **Presença Vocal** | `presence` | `0.0` a `1.0` | `0.5` | Regula a expressividade e ênfase emocional da voz clonada (conectado ao hiperparâmetro de exagero do Chatterbox). |

### Presets Rápidos com 1 Clique
- 🍃 **Natural:** Configuração de referência para audiolivros e narrações tradicionais (`speed: 1.0x`, `pause: 0.5s`, `pitch: 0`, `presence: 0.5`).
- ⚡ **Dinâmico:** Ritmo ágil com pausas encurtadas, ideal para Reels, Shorts e TikToks (`speed: 1.15x`, `pause: 0.3s`, `pitch: +1`, `presence: 0.7`).
- 🏛️ **Solene:** Cadência lenta com tons mais graves e pausas dramáticas (`speed: 0.9x`, `pause: 0.8s`, `pitch: -2`, `presence: 0.3`).
- 🔥 **Energético:** Máxima velocidade, pausas mínimas e agudos destacados para VSLs de alta conversão (`speed: 1.25x`, `pause: 0.2s`, `pitch: +2`, `presence: 0.9`).

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

## 🖥️ Painel de Logs & Telemetria em Tempo Real

Para desenvolvedores, operadores e criadores que desejam monitorar a saúde da máquina durante sínteses intensivas, o Voxa conta com um drawer lateral deslizante no rodapé:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  VOXA DEVTOOLS  [ CPU: 18.4% | RAM: 42.1% (6.8GB / 16.0GB) ]    [ Copiar ] [ Limpar ] [ ✕ ] │
├─────────────────────────────────────────────────────────────────────────────┤
│  Filtros: [ Nível: TODOS ▼ ]  [ Buscar: "tts"                        ]  [x] Auto-scroll │
├─────────────────────────────────────────────────────────────────────────────┤
│  [13:10:02] [INFO] [backend.main] Servidor Voxa operacional na porta 7865   │
│  [13:10:15] [INFO] [backend.services.tts] Sintetizando chunk 1/3 (142 chars)│
│  [13:10:18] [INFO] [backend.services.tts] Aplicando filtros de voz: speed=1.15x│
│  [13:10:20] [SUCCESS] [backend.routers.narration] Tarefa concluída com sucesso│
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Streaming WebSocket (`/ws/logs`):** Transmissão instantânea de cada registro do logger do Python e métricas do sistema a cada 1 segundo.
- **Buffer Circular Concorrente:** Retenção das últimas 1.000 entradas em memória (`RingBuffer` thread-safe).
- **Sanitização de Segurança:** Filtro automático que detecta e oculta dados confidenciais (chaves, senhas, tokens de autorização).
- **Interface Flutuante:** Abra e feche o console de qualquer tela da aplicação sem interromper as operações em andamento.

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
│  📖 API Docs    │  └─────────────────────────────────────────────────────┘  │
│                 │                                                           │
│  ● Sistema      │  Voz: [ João Locutor (★ Padrão) ▼ ]    Modo: [ Dinâmico ▼ ]│
│    Pronto       │  ▼ Controles de Voz [Presets: Natural | Dinâmico | Solene]│
│                 │    Velocidade: [1.15x]  Pausa: [0.3s]  Pitch: [+1]  ...    │
│  [📋 DevTools]  │                                                           │
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

## 📡 API REST & Documentação Interativa

O Voxa inclui suporte integral a integrações headless, permitindo automatizar seus canais e pipelines via scripts Python, n8n ou webhooks:

- **Swagger UI:** Acesse `http://localhost:7865/docs` para testar as rotas interativamente no navegador.
- **ReDoc:** Acesse `http://localhost:7865/redoc` para visualização técnica das especificações OpenAPI.
- **Página Interna `#api-docs`:** Guia visual completo embutido na SPA com exemplos práticos de cURL e payloads JSON.

### Tabela de Endpoints

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/narrate` | Inicia geração de narração com voz clonada e controles finos (retorna `task_id`) |
| `POST` | `/api/narrate-and-transcribe` | Inicia fluxo direto gerando `.mp3` e `.srt` sincronizados com controles de voz |
| `POST` | `/api/transcribe` | Transcreve um áudio existente no modo de legenda selecionado |
| `GET` | `/api/progress/{task_id}` | Stream SSE com progresso e porcentagem da tarefa em tempo real |
| `GET` | `/api/voices` | Lista todas as vozes cadastradas |
| `POST` | `/api/voices` | Cadastra nova voz por upload de amostra (WAV/MP3) |
| `PUT` | `/api/voices/{id}/default` | Define uma voz como padrão do sistema |
| `DELETE` | `/api/voices/{id}` | Exclui a voz e apaga o arquivo físico de amostra |
| `GET` | `/api/history` | Retorna o histórico de narrações ordenado com parâmetros de voz |
| `DELETE` | `/api/history/{id}` | Exclui um item do histórico e seus arquivos de áudio/SRT do disco |
| `DELETE` | `/api/history` | Limpa todo o histórico e remove todos os arquivos físicos |
| `GET` | `/api/settings` | Obtém parâmetros atuais (CPU, limites de legenda, porta) |
| `PUT` | `/api/settings` | Atualiza parâmetros e aplica limite de CPU imediatamente |
| `GET` | `/api/logs` | Retorna logs recentes com filtros por nível (`DEBUG` a `CRITICAL`) e busca |
| `DELETE` | `/api/logs` | Limpa o buffer de logs em memória |
| `GET` | `/api/metrics` | Retorna telemetria pontual do sistema (núcleos de CPU, % de uso e RAM) |
| `WS` | `/ws/logs` | Conexão WebSocket para streaming bidirecional de logs e métricas em tempo real |

---

## 🧱 Estrutura do Projeto

```
Voxa/
├── backend/
│   ├── main.py                  # Servidor FastAPI, montagem de rotas e WebSocket
│   ├── config.py                # Diretórios de dados, cache e saídas
│   ├── models/
│   │   ├── enums.py             # Modos de transcrição e status de tarefas
│   │   └── schemas.py           # Modelos Pydantic (VoiceControls, Logs, Metrics)
│   ├── services/
│   │   ├── cpu_limiter.py       # Gerenciamento de threads e prioridade de processo
│   │   ├── log_service.py       # Buffer circular de logs, interceptor e sanitização
│   │   ├── metrics_service.py   # Telemetria de CPU e memória RAM com psutil
│   │   ├── srt_builder.py       # Algoritmo de empacotamento de legendas por cena
│   │   ├── stt_service.py       # Wrapper do Faster Whisper com word-level timestamps
│   │   ├── task_manager.py      # Fila assíncrona e emissor de eventos SSE
│   │   └── tts_service.py       # Chatterbox TTS com chunking e filtros de voz FFmpeg
│   ├── storage/
│   │   ├── json_store.py        # Gravação atômica em disco com lock de concorrência
│   │   ├── voice_store.py       # Gerenciador de vozes cadastradas e voz padrão
│   │   ├── history_store.py     # Histórico de narrações e exclusão física
│   │   └── settings_store.py    # Persistência de parâmetros do usuário
│   └── routers/
│       ├── narration.py         # Endpoints de narração e fluxo direto com controles
│       ├── transcription.py     # Endpoints de transcrição avulsa
│       ├── voices.py            # CRUD de vozes clonadas e upload
│       ├── history.py           # Consulta e exclusão de histórico
│       ├── settings.py          # Configurações do Voxa
│       ├── progress.py          # Streaming SSE em tempo real de tarefas
│       ├── logs.py              # REST e WebSocket de logs e métricas
│       └── system.py            # Endpoints de verificação e sistema
├── frontend/
│   ├── index.html               # Shell da aplicação SPA e Drawer de DevTools
│   ├── css/style.css            # Estilização Dark Premium moderna com variáveis CSS
│   ├── js/
│   │   ├── api.js               # Cliente HTTP e WebSocket centralizado
│   │   ├── app.js               # Roteamento por hash e ciclo de vida da SPA
│   │   ├── state.js             # Estado reativo compartilhado entre abas
│   │   ├── components/
│   │   │   ├── log-drawer.js    # Componente interativo do DevTools de Logs
│   │   │   ├── modal.js         # Diálogos de confirmação customizados
│   │   │   └── toast.js         # Notificações toast fluidas
│   │   └── pages/
│   │       ├── api-docs.js      # Documentação interativa da API com cURL
│   │       ├── history.js       # Visualização e gestão do histórico
│   │       ├── narrate.js       # Tela principal com controles de voz colapsáveis
│   │       ├── settings.js      # Configurações do sistema e CPU
│   │       └── voices.js        # Gestão de vozes e upload
│   └── assets/                  # Logo SVG e ícones visuais
├── docs/assets/                 # Banners e imagens de documentação
├── tests/                       # Suíte automatizada com 139 testes pytest
├── setup.bat                    # Instalador Windows (UTF-8 / sem erros de parser)
├── start.bat                    # Inicializador Windows com auto-open de navegador
├── setup.sh                     # Instalador Linux/macOS
├── start.sh                     # Inicializador Linux/macOS
├── requirements.txt             # Dependências do ecossistema Python
└── README.md                    # Documentação oficial
```

---

## 🧪 Testes Automatizados

O Voxa foi desenvolvido sob a disciplina rigorosa de **Test-Driven Development (TDD)** e **Subagent-Driven Development**. Toda a suíte de testes pode ser executada com:

```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

```text
======================= 139 passed, 1 warning in 28.49s =======================
```

Todos os 139 testes cobrem testes unitários, validação de schemas, processamento de filtros de áudio, geração de legendas SRT, concorrência atômica de arquivos, interceptação de logs, endpoints REST e ciclo de vida do WebSocket.

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
