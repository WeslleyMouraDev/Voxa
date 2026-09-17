# Task 5: Endpoints FastAPI e Servidor da Aplicação

## Objetivo
Implementar a API REST e streaming SSE com FastAPI, integrando todos os serviços criados nas tarefas anteriores:
- Configurações (`/api/settings`)
- Vozes (`/api/voices`)
- Histórico (`/api/history`)
- Narração (`/api/narrate`)
- Transcrição (`/api/transcribe`)
- Fluxo Direto (`/api/narrate-and-transcribe`)
- Progresso em tempo real SSE (`/api/progress/{task_id}`)
- Servir arquivos de saída (`/output/...`) e arquivos de vozes (`/voices/...`)
- Arquivo principal `backend/main.py` com CORS e montagem estática de `frontend/`

## Arquivos a Criar
- `backend/routers/__init__.py`
- `backend/routers/settings.py`
- `backend/routers/voices.py`
- `backend/routers/history.py`
- `backend/routers/narration.py`
- `backend/routers/transcription.py`
- `backend/routers/progress.py`
- `backend/main.py`
- `tests/test_api.py`

## Especificações Técnicas e Endpoints

### 1. `backend/routers/settings.py`
- `GET /api/settings`: Retorna `SettingsSchema`.
- `PUT /api/settings`: Recebe `SettingsSchema` e salva via `SettingsStore.update_settings()`. Aplica o limite de CPU atualizado no `CPULimiter`.

### 2. `backend/routers/voices.py`
- `GET /api/voices`: Lista todas as vozes (`list[VoiceSchema]`).
- `POST /api/voices`: Recebe multipart form (`name: str`, `file: UploadFile`, `is_default: bool = False`).
  - Salva o arquivo de áudio enviado em `voices/<uuid>_<filename>`.
  - Cadastra no `VoiceStore`.
  - Retorna `VoiceSchema` com status 201.
- `PUT /api/voices/{id}/default`: Define a voz como padrão. Se não encontrada, 404.
- `DELETE /api/voices/{id}`: Exclui a voz e o arquivo físico de amostra. Se não encontrada, 404.

### 3. `backend/routers/history.py`
- `GET /api/history`: Retorna lista ordenada de `HistoryItemSchema`.
- `DELETE /api/history/{id}`: Exclui o item e remove arquivos físicos de `.mp3` e `.srt` do disco.
- `DELETE /api/history`: Limpa todo o histórico e apaga todos os arquivos físicos gerados.

### 4. `backend/routers/narration.py`
- `POST /api/narrate`:
  - Recebe `NarrationRequestSchema(text, voice_id)`.
  - Se `voice_id` não for fornecido, usa a voz padrão do `VoiceStore`. Se não houver voz cadastrada, retorna HTTP 400 informando que nenhuma voz está disponível.
  - Cria tarefa no `TaskManager` e despacha em background (via `asyncio.create_task` ou `BackgroundTasks`).
  - Fluxo em background:
    1. Gera áudio via `TTSService.generate_speech` com callback de progresso no `TaskManager` (0% a 90%).
    2. Registra no `HistoryStore`.
    3. Finaliza com `TaskManager.complete_task(task_id, {"history_id": ..., "audio_url": ...})`.
  - Retorna imediatamente `{"task_id": task_id}` com status 202.
- `POST /api/narrate-and-transcribe`:
  - Recebe `NarrationAndTranscriptionRequestSchema(text, voice_id, mode)`.
  - Se `voice_id` não for fornecido, usa a voz padrão. Se não houver voz, HTTP 400.
  - Cria tarefa no `TaskManager` e despacha em background:
    1. Gera áudio MP3 (0% a 60% de progresso).
    2. Transcreve o MP3 gerado via `STTService.transcribe_audio` no modo selecionado (60% a 90%).
    3. Salva arquivo `.srt` correspondente no mesmo diretório do MP3.
    4. Registra no `HistoryStore` com `audio_path` e `srt_path`.
    5. Finaliza com `TaskManager.complete_task(task_id, {"history_id": ..., "audio_url": ..., "srt_url": ...})`.
  - Retorna imediatamente `{"task_id": task_id}` com status 202.

### 5. `backend/routers/transcription.py`
- `POST /api/transcribe`:
  - Suporta upload de arquivo de áudio (`file: UploadFile`) ou caminho de áudio existente (`audio_path: str`), mais `mode: TranscriptionMode`.
  - Salva arquivo temporário se for upload.
  - Cria tarefa no `TaskManager` e despacha em background:
    1. Transcreve o áudio via `STTService.transcribe_audio`.
    2. Salva `.srt`.
    3. Registra no `HistoryStore`.
    4. Conclui tarefa.
  - Retorna imediatamente `{"task_id": task_id}` com status 202.

### 6. `backend/routers/progress.py`
- `GET /api/progress/{task_id}`:
  - Consome `TaskManager.subscribe(task_id)`.
  - Retorna `EventSourceResponse` (ou streaming de texto `text/event-stream`) com eventos formatados em JSON: `data: {"status": ..., "progress": ..., "message": ..., "result": ..., "error": ...}\n\n`.

### 7. `backend/main.py`
- Inicializa FastAPI com título "Voxa" e versão "1.0.0".
- CORS middleware permitindo `*`.
- Monta rotas estáticas:
  - `/voices` apontando para `VOICES_DIR`
  - `/output` apontando para `OUTPUT_DIR`
  - `/` servindo `frontend/` (quando a pasta existir)
- Inclui todos os routers com prefixo ou rotas definidas.

## Requisitos de Testes (`tests/test_api.py`)
- Usar `fastapi.testclient.TestClient` (ou `httpx.AsyncClient`).
- Testar endpoints de Settings (GET e PUT).
- Testar endpoints de Voices (POST upload, GET list, PUT default, DELETE).
- Testar endpoints de History (GET list, DELETE individual, DELETE all).
- Testar endpoints de Narration e Narrate-and-Transcribe retornando `task_id` e 400 quando não há voz.
- Testar endpoint de progresso SSE emitindo status correto.

## Comandos
- Testes: `python -m pytest tests/test_api.py -v`
- Commits: `git add backend/ tests/test_api.py && git commit -m "feat: add fastapi routers for voices, history, settings, narration, and transcription with sse"`
