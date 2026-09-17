# Voxa Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Desenvolver o Voxa, uma aplicação local e multiplataforma de clonagem de voz (Chatterbox TTS Single Language Pack PT-BR), narração e transcrição precisa com geração de SRT nos modos Normal, Dinâmico e Acelerado, com controle de CPU anti-travamento e interface web dark premium 100% controlável.

**Architecture:** Servidor monolítico assíncrono em Python (FastAPI + Uvicorn) servindo API REST, SSE para streaming de progresso e frontend estático (HTML/CSS/JS vanilla). Persistência local em arquivos JSON com atomic lock. Motores de IA modulares isolados (Chatterbox TTS e Faster Whisper) com limitação de threads via `torch.set_num_threads` e prioridade baixa de SO via `psutil`.

**Tech Stack:** Python 3.10+, FastAPI, Uvicorn, SSE-Starlette, Chatterbox-TTS (PT-BR), Faster-Whisper, PyTorch, PyDub, SoundFile, psutil, HTML5/CSS3/Vanilla JS, pytest.

## Global Constraints

- 100% controlável pela interface web local após inicialização (sem necessidade de comandos manuais ou terminal pelo usuário final).
- Repositório Git: `https://github.com/WeslleyMouraDev/Voxa.git`.
- TTS: Chatterbox TTS com Single Language Pack Brazilian Portuguese (PT-BR).
- STT: Faster Whisper com modelo `medium` e word-level timestamps.
- Três modos de transcrição: Normal (4-6s), Dinâmico (2-4s), Acelerado (1-2s), todos com min/max configuráveis.
- Controle de CPU: Limitação configurável de threads (padrão 75% dos núcleos lógicos) e prioridade baixa do processo (Windows `BELOW_NORMAL_PRIORITY_CLASS`, Unix `nice(10)`).
- Scripts `.bat` no Windows devem seguir estritamente o padrão da skill `windows-batch-launchers`: codificação `chcp 65001 >nul`, caminhos entre aspas `cd /d "%~dp0..."`, sem parênteses não escapados dentro de blocos `if`/`for` (usar `goto`), título estilizado e passos numerados (`[1/3]`, etc.).
- Persistência 100% local em arquivos JSON organizados em `data/` e arquivos de áudio/legenda em `output/` organizados por data.

---

### Task 1: Configurações, Modelos de Dados e Armazenamento JSON Concorrente

**Files:**
- Create: `backend/models/enums.py`
- Create: `backend/models/schemas.py`
- Create: `backend/config.py`
- Create: `backend/storage/json_store.py`
- Create: `backend/storage/settings_store.py`
- Create: `backend/storage/voice_store.py`
- Create: `backend/storage/history_store.py`
- Test: `tests/test_storage.py`

**Interfaces:**
- Produces:
  - `TranscriptionMode(str, Enum)`: `NORMAL = "normal"`, `DYNAMIC = "dynamic"`, `ACCELERATED = "accelerated"`
  - `TaskStatus(str, Enum)`: `IDLE = "idle"`, `PROCESSING = "processing"`, `COMPLETED = "completed"`, `ERROR = "error"`
  - `SettingsSchema`, `VoiceSchema`, `HistoryItemSchema`, `NarrationRequestSchema`, `TranscriptionRequestSchema`
  - `JSONStore`: `read_json(file_path: Path) -> dict`, `write_json(file_path: Path, data: dict) -> None` (com atomic file write e thread lock)
  - `SettingsStore`: `get_settings() -> SettingsSchema`, `update_settings(new_settings) -> SettingsSchema`
  - `VoiceStore`: `list_voices() -> list[VoiceSchema]`, `add_voice(name, sample_path, is_default) -> VoiceSchema`, `set_default_voice(voice_id) -> None`, `delete_voice(voice_id) -> bool`
  - `HistoryStore`: `list_history() -> list[HistoryItemSchema]`, `add_history_item(item) -> HistoryItemSchema`, `delete_item(history_id) -> bool`, `clear_all() -> int`

- [ ] **Step 1: Write the failing test for storage and models**
Crie `tests/test_storage.py` testando `SettingsStore`, `VoiceStore` (com garantia de única voz default) e `HistoryStore` (com exclusão física e lógica).
- [ ] **Step 2: Run test to verify it fails**
Execute `pytest tests/test_storage.py -v`. Deve falhar com `ModuleNotFoundError`.
- [ ] **Step 3: Implement models, config and storage**
Crie `backend/models/enums.py`, `backend/models/schemas.py`, `backend/config.py` e os arquivos em `backend/storage/`.
- [ ] **Step 4: Run test to verify it passes**
Execute `pytest tests/test_storage.py -v`. Deve passar 100%.
- [ ] **Step 5: Commit**
`git add backend/ tests/test_storage.py && git commit -m "feat: add models, configuration, and atomic json storage"`

---

### Task 2: Limitador de Recursos de CPU e Gerenciador de Tarefas em Background (SSE)

**Files:**
- Create: `backend/services/cpu_limiter.py`
- Create: `backend/services/task_manager.py`
- Test: `tests/test_cpu_limiter.py`
- Test: `tests/test_task_manager.py`

**Interfaces:**
- Consumes: `SettingsStore`, `TaskStatus`
- Produces:
  - `CPULimiter`: `calculate_threads(cpu_percent: int) -> int`, `apply_limits(cpu_percent: int) -> None`
  - `TaskManager`: `create_task(name: str) -> str`, `update_progress(task_id: str, progress: float, message: str) -> None`, `complete_task(task_id: str, result: dict) -> None`, `fail_task(task_id: str, error: str) -> None`, `subscribe(task_id: str) -> AsyncGenerator[dict, None]`

- [ ] **Step 1: Write failing tests for CPULimiter and TaskManager**
Crie `tests/test_cpu_limiter.py` e `tests/test_task_manager.py`.
- [ ] **Step 2: Run tests to verify they fail**
Execute `pytest tests/test_cpu_limiter.py tests/test_task_manager.py -v`.
- [ ] **Step 3: Implement CPULimiter and TaskManager**
Implemente `CPULimiter` usando `psutil` e `torch` (se disponível, com fallback gracioso para mock/cpu), e `TaskManager` com filas assíncronas `asyncio.Queue` para SSE.
- [ ] **Step 4: Run tests to verify they pass**
Execute `pytest tests/test_cpu_limiter.py tests/test_task_manager.py -v`.
- [ ] **Step 5: Commit**
`git add backend/services/ tests/test_cpu_limiter.py tests/test_task_manager.py && git commit -m "feat: add cpu limiter and async background task manager with sse"`

---

### Task 3: Algoritmo de Geração de Legenda SRT Inteligente (3 Modos)

**Files:**
- Create: `backend/services/srt_builder.py`
- Test: `tests/test_srt_builder.py`

**Interfaces:**
- Consumes: `TranscriptionMode`, `SettingsSchema`
- Produces:
  - `WordTimestamp`: `dataclass(word: str, start: float, end: float, probability: float = 1.0)`
  - `SRTSegment`: `dataclass(index: int, start: float, end: float, text: str)`
  - `SRTBuilder`:
    - `format_timestamp(seconds: float) -> str` (formato `HH:MM:SS,mmm`)
    - `build_srt(words: list[WordTimestamp], mode: TranscriptionMode, mode_config: dict) -> str`
    - `save_srt_file(srt_content: str, destination_path: Path) -> Path`

- [ ] **Step 1: Write failing tests for SRTBuilder**
Crie `tests/test_srt_builder.py` testando formatação de timestamp, divisão nos modos Normal (4-6s), Dinâmico (2-4s) e Acelerado (1-2s), pontuações e limites de duração.
- [ ] **Step 2: Run tests to verify they fail**
Execute `pytest tests/test_srt_builder.py -v`.
- [ ] **Step 3: Implement SRTBuilder algorithm**
Implemente a lógica precisa em `backend/services/srt_builder.py`.
- [ ] **Step 4: Run tests to verify they pass**
Execute `pytest tests/test_srt_builder.py -v`.
- [ ] **Step 5: Commit**
`git add backend/services/srt_builder.py tests/test_srt_builder.py && git commit -m "feat: implement intelligent srt generator for normal, dynamic, and accelerated modes"`

---

### Task 4: Motores de IA TTS (Chatterbox PT-BR) e STT (Faster Whisper) com Chunking

**Files:**
- Create: `backend/services/tts_service.py`
- Create: `backend/services/stt_service.py`
- Test: `tests/test_services.py`

**Interfaces:**
- Consumes: `CPULimiter`, `SRTBuilder`, `SettingsStore`
- Produces:
  - `TTSService`:
    - `split_text_into_chunks(text: str, max_chars: int = 250) -> list[str]`
    - `generate_speech(text: str, voice_sample_path: Path, output_mp3_path: Path, progress_callback = None) -> Path`
  - `STTService`:
    - `transcribe_audio(audio_path: Path, mode: TranscriptionMode, progress_callback = None) -> tuple[str, list[WordTimestamp]]`

- [ ] **Step 1: Write failing tests for TTSService and STTService**
Crie `tests/test_services.py` com mocks para o modelo Chatterbox e Faster Whisper para testar sanitização, chunking, conversão WAV->MP3, fallback gracioso e callbacks de progresso.
- [ ] **Step 2: Run tests to verify they fail**
Execute `pytest tests/test_services.py -v`.
- [ ] **Step 3: Implement TTSService and STTService**
Implemente `backend/services/tts_service.py` e `backend/services/stt_service.py` com importações condicionais e fallbacks defensivos para execução segura em qualquer ambiente.
- [ ] **Step 4: Run tests to verify they pass**
Execute `pytest tests/test_services.py -v`.
- [ ] **Step 5: Commit**
`git add backend/services/ tests/test_services.py && git commit -m "feat: implement chatterbox tts and faster whisper stt services with chunking"`

---

### Task 5: Endpoints FastAPI e Servidor da Aplicação

**Files:**
- Create: `backend/routers/settings.py`
- Create: `backend/routers/voices.py`
- Create: `backend/routers/history.py`
- Create: `backend/routers/narration.py`
- Create: `backend/routers/transcription.py`
- Create: `backend/routers/progress.py`
- Create: `backend/main.py`
- Test: `tests/test_api.py`

**Interfaces:**
- Produces:
  - `app = FastAPI(title="Voxa", version="1.0.0")`
  - Rotas `/api/settings` (GET, PUT)
  - Rotas `/api/voices` (GET, POST multipart, PUT `/{id}/default`, DELETE `/{id}`)
  - Rotas `/api/history` (GET, DELETE `/{id}`, DELETE `/all`)
  - Rotas `/api/narrate` (POST)
  - Rotas `/api/transcribe` (POST multipart / path)
  - Rotas `/api/narrate-and-transcribe` (POST)
  - Rotas `/api/progress/{task_id}` (GET SSE)
  - Montagem de arquivos estáticos em `/` e `/output` para servir áudios e SRTs diretamente.

- [ ] **Step 1: Write failing integration tests for API endpoints**
Crie `tests/test_api.py` com `httpx.AsyncClient` ou `fastapi.testclient.TestClient`.
- [ ] **Step 2: Run tests to verify they fail**
Execute `pytest tests/test_api.py -v`.
- [ ] **Step 3: Implement all routers and main.py**
Implemente todas as rotas e configure CORS, montagem estática de `frontend/` e `output/`.
- [ ] **Step 4: Run tests to verify they pass**
Execute `pytest tests/test_api.py -v`.
- [ ] **Step 5: Commit**
`git add backend/ tests/test_api.py && git commit -m "feat: add fastapi routers for voices, history, settings, narration, and transcription with sse"`

---

### Task 6: Interface Web Dark Premium (HTML5, CSS3, Vanilla JS Reativo)

**Files:**
- Create: `frontend/assets/logo.svg`
- Create: `frontend/css/style.css`
- Create: `frontend/js/api.js`
- Create: `frontend/js/state.js`
- Create: `frontend/js/components/toast.js`
- Create: `frontend/js/components/modal.js`
- Create: `frontend/js/pages/narrate.js`
- Create: `frontend/js/pages/voices.js`
- Create: `frontend/js/pages/history.js`
- Create: `frontend/js/pages/settings.js`
- Create: `frontend/js/app.js`
- Create: `frontend/index.html`
- Test: `tests/test_frontend_routes.py`

**Features:**
- Design Dark Premium com Inter & JetBrains Mono, acentos roxo vibrante e esmeralda.
- Sidebar lateral com navegação fluida SPA sem recarregar a página.
- Tela Narrar: Textarea com contador de caracteres, seleção de voz (destacando a padrão ★), seletor dos 3 modos de SRT, botões [Apenas Narrar], [Apenas Transcrever], [Narrar + Transcrever], barra de progresso SSE em tempo real, e player inline com botões de download MP3 e SRT.
- Tela Vozes: Lista de vozes com player de amostra, botão para marcar voz padrão com estrela instantânea, exclusão e modal de cadastro "+ Nova Voz" com upload de áudio.
- Tela Histórico: Lista completa de gerações passadas, player inline, botões de download, remoção individual e botão "Limpar Tudo" que limpa banco e remove arquivos do disco.
- Tela Configurações: Sliders de controle de CPU (25% a 100%), configuração de tempos min/max para Normal, Dinâmico e Acelerado, porta e auto-abrir navegador.

- [ ] **Step 1: Write test verifying frontend assets and routing**
Crie `tests/test_frontend_routes.py` validando que `index.html`, css, js e svg são servidos com os MIME types corretos pelo FastAPI.
- [ ] **Step 2: Run test to verify it fails**
Execute `pytest tests/test_frontend_routes.py -v`.
- [ ] **Step 3: Implement frontend files with Dark Premium theme**
Crie todos os arquivos da interface web moderna, responsiva e 100% funcional.
- [ ] **Step 4: Run test to verify it passes**
Execute `pytest tests/test_frontend_routes.py -v`.
- [ ] **Step 5: Commit**
`git add frontend/ tests/test_frontend_routes.py && git commit -m "feat: create dark premium web interface with full spa controls, sse progress, and audio player"`

---

### Task 7: Scripts de Inicialização Multiplataforma, Dependências e Validação E2E

**Files:**
- Create: `requirements.txt`
- Create: `setup.bat` (Seguindo estritamente `windows-batch-launchers`)
- Create: `start.bat` (Seguindo estritamente `windows-batch-launchers`)
- Create: `setup.sh`
- Create: `start.sh`
- Create: `.gitignore`
- Create: `README.md`
- Test: `tests/test_launchers.py`

**Constraints:**
- `setup.bat` e `start.bat`: `chcp 65001 >nul`, `cd /d "%~dp0"`, sem parênteses não escapados em blocos `if`/`for`, uso de rótulos `goto`, visual limpo no terminal com cabeçalho estilizado `Voxa`, passos `[1/3]`, `[2/3]`, `[3/3]` e abertura automática do navegador com `start "" "http://localhost:7865"`.
- `requirements.txt` com todas as dependências especificadas.

- [ ] **Step 1: Write test for launcher syntax and scripts integrity**
Crie `tests/test_launchers.py` verificando a integridade dos arquivos `.bat` e `.sh` (codificação UTF-8, ausência de parênteses fatais em blocos IF, presença de chcp 65001).
- [ ] **Step 2: Run test to verify it fails**
Execute `pytest tests/test_launchers.py -v`.
- [ ] **Step 3: Implement requirements.txt, bat/sh launchers, .gitignore and README.md**
Crie os inicializadores premium, `.gitignore` completo para arquivos de saída temporários e venv, e README documentado.
- [ ] **Step 4: Run full test suite to verify everything passes**
Execute `pytest -v`.
- [ ] **Step 5: Commit**
`git add requirements.txt setup.bat start.bat setup.sh start.sh .gitignore README.md tests/test_launchers.py && git commit -m "feat: add multiplatform launcher scripts, requirements and complete documentation"`
