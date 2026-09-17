# Task 5 Report: Endpoints FastAPI e Servidor da Aplicação

## Status: Concluído com Sucesso

### 1. Implementações Realizadas
- `backend/routers/__init__.py`: Módulo inicializador de roteadores.
- `backend/routers/settings.py`:
  - `GET /api/settings`: Retorna as configurações atuais (`SettingsSchema`).
  - `PUT /api/settings`: Atualiza configurações no `SettingsStore` e aplica dinamicamente o novo limite de CPU no `CPULimiter`.
- `backend/routers/voices.py`:
  - `GET /api/voices`: Lista todas as vozes cadastradas.
  - `POST /api/voices`: Upload multipart de amostra de áudio (`name`, `file`, `is_default`), persistindo o arquivo em `voices/` e registrando no `VoiceStore` (HTTP 201).
  - `PUT /api/voices/{id}/default`: Define a voz selecionada como padrão (HTTP 404 caso inexistente).
  - `DELETE /api/voices/{id}`: Exclui a voz e apaga o arquivo físico de amostra de áudio (HTTP 404 caso inexistente).
- `backend/routers/history.py`:
  - `GET /api/history`: Retorna lista ordenada decrescente por data dos itens de histórico (`HistoryItemSchema`).
  - `DELETE /api/history/{id}`: Exclui item e apaga fisicamente arquivos `.mp3` e `.srt` vinculados.
  - `DELETE /api/history`: Limpa todo o histórico e remove todos os arquivos físicos gerados.
- `backend/routers/narration.py`:
  - `POST /api/narrate`: Validação de texto não vazio e disponibilidade de voz (HTTP 400); despacho assíncrono em segundo plano via `BackgroundTasks`; síntese com `TTSService` reportando progresso contínuo; salvamento no `HistoryStore`; conclusão da tarefa no `TaskManager` com `audio_url` (HTTP 202 com `task_id`).
  - `POST /api/narrate-and-transcribe`: Síntese de áudio (0%-60%), transcrição com Faster Whisper (60%-90%), salvamento de legenda `.srt` e registro no histórico com `audio_url` e `srt_url` (HTTP 202).
- `backend/routers/transcription.py`:
  - `POST /api/transcribe`: Suporta upload de arquivo de áudio ou caminho `audio_path` existente com modo de legenda (`normal`, `dynamic`, `accelerated`); executa transcrição em background; salva `.srt`; salva no histórico; conclui tarefa (HTTP 202).
- `backend/routers/progress.py`:
  - `GET /api/progress/{task_id}`: Streaming SSE (`text/event-stream`) em tempo real consumindo eventos do `TaskManager.subscribe(task_id)` em formato `data: {...}\n\n` (HTTP 404 se tarefa inexistente).
- `backend/main.py`:
  - Inicialização FastAPI ("Voxa" v1.0.0) com CORS middleware irrestrito (`*`), inclusão de todos os roteadores sob `/api`, montagem de rotas estáticas `/voices` e `/output`, e montagem dinâmica do frontend `/` quando a pasta existir.
  - Disponibilização da factory `create_app()` e da instância padrão `app`.

### 2. Testes e Validação TDD
- `tests/test_api.py`:
  - 18 testes automatizados cobrindo exaustivamente:
    - Settings: consulta (`GET`) e atualização com reconfiguração do CPULimiter (`PUT`).
    - Voices: listagem, upload multipart com persistência, definição de padrão e exclusão com remoção de arquivo.
    - History: listagem, remoção unitária e limpeza total com verificação de exclusão dos arquivos físicos.
    - Narration & Narrate-and-Transcribe: retorno de HTTP 400 para ausência de voz/texto, despacho assíncrono em background, geração de áudio e legendas, atualização de progresso e conclusão no TaskManager.
    - Transcription: validação de parâmetros de entrada, transcrição via `audio_path`, transcrição via upload e emissão de URLs.
    - Progress SSE: validação de HTTP 404 e streaming `text/event-stream` com eventos JSON válidos.
    - Arquivos Estáticos: resolução correta de rotas `/voices/...` e `/output/...`.
- **Resultado dos Testes**: 60/60 testes passaram com 100% de sucesso em toda a suíte do projeto (`pytest tests/ -v`).
