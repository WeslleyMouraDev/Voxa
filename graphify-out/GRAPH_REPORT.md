# Graph Report - Voxa  (2026-09-18)

## Corpus Check
- 80 files · ~109,698 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 822 nodes · 1043 edges · 71 communities (44 shown, 27 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 159 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `98f846f5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]

## God Nodes (most connected - your core abstractions)
1. `LogService` - 21 edges
2. `TranscriptionMode` - 20 edges
3. `TaskManager` - 20 edges
4. `🎙️ VOXA` - 20 edges
5. `WordTimestamp` - 18 edges
6. `STTService` - 17 edges
7. `TTSService` - 17 edges
8. `StateManager` - 16 edges
9. `VoiceStore` - 15 edges
10. `CPULimiter` - 14 edges

## Surprising Connections (you probably didn't know these)
- `test_transcribe_with_file_upload_success()` --calls--> `WordTimestamp`  [INFERRED]
  tests/test_api.py → backend/services/srt_builder.py
- `client()` --calls--> `create_app()`  [INFERRED]
  tests/test_frontend.py → backend/main.py
- `test_schemas_defaults_and_validation()` --calls--> `SettingsSchema`  [INFERRED]
  tests/test_storage.py → backend/models/schemas.py
- `test_history_item_schema_controls_defaults()` --calls--> `HistoryItemSchema`  [INFERRED]
  tests/test_schemas_controls.py → backend/models/schemas.py
- `test_history_item_schema_controls_custom()` --calls--> `HistoryItemSchema`  [INFERRED]
  tests/test_schemas_controls.py → backend/models/schemas.py

## Communities (71 total, 27 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (18): SettingsSchema, VoiceSchema, HistoryStore, JSONStore, Thread-safe and atomic JSON storage handler., Reads JSON data safely under lock. Returns `default` on missing or corrupt file., Atomically writes data into the JSON file using a temp file and os.replace., SettingsStore (+10 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (16): 1. `backend/models/enums.py`, 2. `backend/models/schemas.py`, 3. `backend/config.py`, 4. `backend/storage/json_store.py`, 5. `backend/storage/settings_store.py`, 6. `backend/storage/voice_store.py`, 7. `backend/storage/history_store.py`, Arquivos a Criar (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.29
Nodes (6): clear_logs(), get_logs(), Retorna o histórico estruturado de logs em memória do ring buffer,     com supor, Limpa todos os logs em memória do ring buffer e emite broadcast     aos clientes, Endpoint WebSocket para streaming bidirecional de logs e telemetria:     - Envia, websocket_logs()

### Community 3 - "Community 3"
Cohesion: 0.2
Nodes (9): Global Constraints, Task 1: Configurações, Modelos de Dados e Armazenamento JSON Concorrente, Task 2: Limitador de Recursos de CPU e Gerenciador de Tarefas em Background (SSE), Task 3: Algoritmo de Geração de Legenda SRT Inteligente (3 Modos), Task 4: Motores de IA TTS (Chatterbox PT-BR) e STT (Faster Whisper) com Chunking, Task 5: Endpoints FastAPI e Servidor da Aplicação, Task 6: Interface Web Dark Premium (HTML5, CSS3, Vanilla JS Reativo), Task 7: Scripts de Inicialização Multiplataforma, Dependências e Validação E2E (+1 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (38): initLogDrawer(), escapeHtml(), showConfirmModal(), showCustomModal(), escapeHtml(), showToast(), api, init() (+30 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (16): Marca a tarefa com erro, notificando os ouvintes., Gerenciador assíncrono de tarefas em segundo plano com suporte a streaming     d, Gerador assíncrono que consome eventos de atualização da tarefa         até a ta, Cria e inicializa uma nova tarefa com status PROCESSING e progresso 0.0., Retorna os dados da tarefa ou None se não encontrada., Envia uma cópia do estado atual da tarefa para todos os ouvintes inscritos., Atualiza o progresso (0-100) e mensagem da tarefa, notificando subscribers., Marca a tarefa como concluída com sucesso, define progresso como 100% e emite re (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (20): Inicia tarefa de transcrição a partir de upload de arquivo ou caminho de áudio e, _run_transcription_task(), transcribe(), create_voice(), delete_voice(), list_voices(), Lista todas as vozes cadastradas., Cadastra uma nova voz a partir do upload de um arquivo de áudio de amostra. (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.29
Nodes (6): Controle de Recursos da Máquina (Anti-Travamento), Interface Web 100% Controlável (Dark Premium), Modos de Transcrição e Geração de SRT, Stack Tecnológica, Visão Geral, Voxa — Ferramenta Local de Clonagem de Voz, Narração e Transcrição

### Community 10 - "Community 10"
Cohesion: 0.5
Nodes (3): Novo Plano: Painel de Logs em Tempo Real, Controles de Voz e API Completa, Plano Anterior: Voxa Inicial (Concluído), Subagent-Driven Development Progress Ledger

### Community 16 - "Community 16"
Cohesion: 0.15
Nodes (13): get_settings(), Retorna as configurações atuais da aplicação., Atualiza as configurações da aplicação e aplica o novo limite de CPU., update_settings(), calculate_threads(), CPULimiter, Aplica os limites calculados de CPU:         - Define número de threads no PyTor, Gerencia o uso de recursos de CPU limitando a contagem de threads do PyTorch (+5 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (13): 1. `backend/services/cpu_limiter.py`, 1. `backend/services/log_service.py`, 2. `backend/services/metrics_service.py`, 2. `backend/services/task_manager.py`, 3. Ciclo TDD, Arquivos a Criar, Comandos, Especificações Técnicas e Interfaces (+5 more)

### Community 18 - "Community 18"
Cohesion: 0.18
Nodes (10): 1. `backend/models/schemas.py`, 2. `tests/test_schemas_controls.py` (Novo), Alterações Realizadas, Ciclo TDD e Verificação, Relatório da Task 1: Schemas de Dados para Controles de Áudio, Logs e Métricas, Resultado dos Testes, Resumo dos Arquivos Criados, Status (+2 more)

### Community 21 - "Community 21"
Cohesion: 0.06
Nodes (32): create_app(), Cria e configura a instância da aplicação FastAPI do Voxa., Anexa o LogBufferHandler aos loggers raiz do Python e do uvicorn para streaming., Cria e configura a instância da aplicação FastAPI do Voxa., setup_logging(), client(), Testa se app.js importa renderApiDocsPage e registra a rota api-docs., Testa se api.js aceita e repassa o objeto controls em startNarration e startNarr (+24 more)

### Community 22 - "Community 22"
Cohesion: 0.14
Nodes (15): 1. `backend/services/srt_builder.py`, 1. `backend/services/tts_service.py`, 2. Testes em `tests/test_voice_controls.py`, 3. Ciclo TDD, Arquivos a Criar, Arquivos a Modificar / Criar, code:python (def generate_speech(), code:python (@staticmethod) (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (13): 1. `backend/services/log_service.py` (Novo), 1. Implementações Realizadas, 2. `backend/services/metrics_service.py` (Novo), 2. Testes e Validação TDD, 3. `tests/test_log_service.py` (Novo), 4. `tests/test_metrics_service.py` (Novo), Alterações Realizadas, Ciclo TDD e Verificação (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.05
Nodes (47): Enum, TaskStatus, TranscriptionMode, build_segments(), build_srt(), format_timestamp(), SRTBuilder, SRTSegment (+39 more)

### Community 29 - "Community 29"
Cohesion: 0.1
Nodes (20): 1. `frontend/js/pages/narrate.js`, 1. Paleta de Cores e Estilo Visual (`frontend/css/style.css`), 2. `frontend/js/api.js`, 2. Layout SPA (`frontend/index.html`), 3. `frontend/js/pages/api-docs.js`, 3. Módulos JavaScript, 4. `frontend/js/app.js`, 5. `frontend/css/style.css` (+12 more)

### Community 30 - "Community 30"
Cohesion: 0.12
Nodes (16): 1. `backend/routers/logs.py`, 1. `backend/services/tts_service.py`, 2. `backend/routers/system.py`, 2. `backend/services/stt_service.py`, 3. `backend/routers/narration.py`, 4. `backend/main.py`, 5. Ciclo TDD, Arquivos a Criar (+8 more)

### Community 31 - "Community 31"
Cohesion: 0.17
Nodes (11): 1. `backend/services/tts_service.py`, 1. Implementações Realizadas, 2. Testes e Validação TDD, 2. `tests/test_voice_controls.py` (Novo), Alterações Realizadas, Ciclo TDD e Verificação, Preocupações / Observações, Relatório da Task 3: Controles de Geração no Motor TTS (Ritmo, Pausa, Tom, Presença) (+3 more)

### Community 35 - "Community 35"
Cohesion: 0.13
Nodes (14): max_seconds, min_seconds, auto_open_browser, cpu_percent, max_seconds, min_seconds, max_seconds, min_seconds (+6 more)

### Community 36 - "Community 36"
Cohesion: 0.09
Nodes (23): 1. `backend/routers/settings.py`, 1. `frontend/index.html`, 2. `backend/routers/voices.py`, 2. `frontend/css/style.css`, 3. `backend/routers/history.py`, 3. `frontend/js/components/log-drawer.js`, 4. `backend/routers/narration.py`, 4. `frontend/js/app.js` (+15 more)

### Community 38 - "Community 38"
Cohesion: 0.29
Nodes (6): clear_all_history(), delete_history_item(), list_history(), Retorna o histórico ordenado de gerações realizadas., Exclui um item do histórico e remove os arquivos de áudio e legenda do disco., Limpa todo o histórico e apaga todos os arquivos gerados associados.

### Community 39 - "Community 39"
Cohesion: 0.13
Nodes (14): 1. `backend/routers/logs.py` (Novo), 1. Implementações Realizadas, 2. `backend/routers/system.py` (Novo), 2. Testes e Validação TDD, 3. `backend/routers/narration.py`, 4. `backend/main.py`, 5. `tests/test_logs_api.py` (Novo), Alterações Realizadas (+6 more)

### Community 43 - "Community 43"
Cohesion: 0.13
Nodes (14): 1. `frontend/js/components/log-drawer.js` (Novo), 1. Implementações Realizadas, 2. `frontend/index.html`, 2. Testes e Validação TDD, 3. `frontend/css/style.css`, 4. `frontend/js/app.js`, 5. `tests/test_frontend.py`, Alterações Realizadas (+6 more)

### Community 44 - "Community 44"
Cohesion: 0.12
Nodes (15): 1. `frontend/js/pages/narrate.js`, 1. Visão Geral, 2. Arquivos Implementados, 2. `frontend/js/api.js`, 3. `frontend/js/pages/api-docs.js` (Novo), 3. Resultados dos Testes, 4. `frontend/js/app.js` e `frontend/index.html`, 5. `frontend/css/style.css` (+7 more)

### Community 45 - "Community 45"
Cohesion: 0.1
Nodes (19): Tests for launcher scripts, requirements.txt, .gitignore, and project structure, Verify setup.sh and start.sh have shebang, set -e, and proper commands., Verify requirements.txt contains all core packages specified in task brief., Verify all required launcher, requirement, and doc files exist., Verify .gitignore covers virtualenv, python cache, test cache, and output folder, Verify README.md contains Portuguese documentation, repository link, and guides., Verify setup.bat and start.bat use strict CRLF (\\r\\n) line endings required by, Ensure setup.bat and start.bat adhere to the windows-batch-launchers rule:     N (+11 more)

### Community 46 - "Community 46"
Cohesion: 0.07
Nodes (37): 📡 API REST & Documentação Interativa, Clonagem de Voz, Narração & Transcrição Inteligente PT-BR (100% Local & Ilimitado), code:block1 (┌───────────────────────────────────────────────────────────), code:bash (.venv\Scripts\python.exe -m pytest tests/ -v), code:text (======================= 139 passed, 1 warning in 28.49s ====), code:cmd (git clone https://github.com/WeslleyMouraDev/Voxa.git), code:cmd (setup.bat), code:cmd (start.bat) (+29 more)

### Community 47 - "Community 47"
Cohesion: 0.12
Nodes (16): 1. `setup.bat` (Windows Installer), 2. `start.bat` (Windows Launcher), 3. `setup.sh` e `start.sh` (Linux / macOS), 4. `requirements.txt`, 5. `.gitignore`, 6. `README.md`, Arquivos a Criar, Arquivos a Modificar (+8 more)

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (5): Arquivos Criados / Modificados, Ciclo TDD e Resultados de Validação, Objetivo, Relatório de Conclusão — Tarefa 7, Status

### Community 52 - "Community 52"
Cohesion: 0.07
Nodes (24): LogBufferHandler, LogService, Limpa todos os logs do buffer e notifica os assinantes., Serviço thread-safe de ring buffer em memória para captura e streaming     de lo, Alias de compatibilidade para clear., Gerador assíncrono que entrega o histórico inicial em lote         e novos logs/, Handler do logging nativo do Python que envia logs para o LogService., Interceptador de fluxos de texto (stdout/stderr) que duplica saídas para     o c (+16 more)

### Community 62 - "Community 62"
Cohesion: 0.07
Nodes (29): API REST Completa, Armazenamento, Arquivos a Criar, Arquivos a Modificar, Backend, Captura de Logs — Abordagem Híbrida, code:block1 (┌───────────────────────────────────────────────────────────), code:json (// Log entry) (+21 more)

### Community 63 - "Community 63"
Cohesion: 0.09
Nodes (21): code:python (import pytest), code:bash (git add frontend/index.html frontend/css/style.css frontend/), code:bash (git add frontend/js/pages/narrate.js frontend/js/pages/api-d), code:bash (git add README.md graphify-out/), code:bash (git add backend/models/schemas.py tests/test_schemas_control), code:python (import logging), code:python (from backend.services.metrics_service import MetricsService), code:bash (git add backend/services/log_service.py backend/services/met) (+13 more)

### Community 66 - "Community 66"
Cohesion: 0.07
Nodes (34): _invoke_tts_generate(), narrate(), narrate_and_transcribe(), Inicia tarefa de narração em background a partir de um texto e voz selecionada., Inicia tarefa em background que sintetiza voz e transcreve com legendas SRT dinâ, Inicia tarefa de narração em background a partir de um texto e voz selecionada,, Inicia tarefa em background que sintetiza voz com controles dinâmicos e transcre, Invoca tts.generate_speech filtrando kwargs caso o alvo seja um mock antigo sem (+26 more)

### Community 71 - "Community 71"
Cohesion: 0.13
Nodes (21): BaseModel, get_default_transcription_modes(), HistoryItemSchema, LogEntrySchema, ModeConfig, NarrationAndTranscriptionRequestSchema, NarrationRequestSchema, SystemMetricsSchema (+13 more)

## Knowledge Gaps
- **337 isolated node(s):** `Anexa o LogBufferHandler aos loggers raiz do Python e do uvicorn para streaming.`, `Cria e configura a instância da aplicação FastAPI do Voxa.`, `Voxa backend package.`, `Retorna o histórico ordenado de gerações realizadas.`, `Exclui um item do histórico e remove os arquivos de áudio e legenda do disco.` (+332 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TranscriptionMode` connect `Community 28` to `Community 0`, `Community 6`, `Community 71`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `create_app()` connect `Community 21` to `Community 6`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `str` (e.g. with `create_app()` and `_run_narration_task()`) actually correct?**
  _`str` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `LogService` (e.g. with `test_log_service_ring_buffer()` and `test_log_service_entry_structure()`) actually correct?**
  _`LogService` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TranscriptionMode` (e.g. with `ModeConfig` and `SettingsSchema`) actually correct?**
  _`TranscriptionMode` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TaskManager` (e.g. with `TaskStatus` and `test_env()`) actually correct?**
  _`TaskManager` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Anexa o LogBufferHandler aos loggers raiz do Python e do uvicorn para streaming.`, `Cria e configura a instância da aplicação FastAPI do Voxa.`, `Voxa backend package.` to the rest of the system?**
  _337 weakly-connected nodes found - possible documentation gaps or missing edges._