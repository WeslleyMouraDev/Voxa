# Painel de Logs em Tempo Real, Controles de Voz e API Completa — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar um painel de logs em tempo real estilo DevTools com streaming WebSocket e métricas de CPU/RAM, controles avançados de geração de voz (Ritmo, Pausa, Tom, Presença) na UI e no backend TTS, e expor/documentar toda a API REST via Swagger e página `#api-docs`.

**Architecture:** Abordagem híbrida de captura de logs (logging.Handler + interceptação de stdout/stderr) canalizada para um ring buffer em memória de 1000 itens transmitido via WebSocket `/api/ws/logs`. Controles de síntese vocal aplicados via Chatterbox (`exaggeration`) e processamento de áudio FFmpeg (`atempo`, `silenceremove`/intervalo de pausa, afinação). Frontend com Drawer de logs persistente e componente Accordion para ajustes de voz na página de narração.

**Tech Stack:** FastAPI, WebSocket, psutil, FFmpeg, Chatterbox Multilingual PT-BR, Vanilla JavaScript ES Modules, CSS3 Dark Premium, Pytest.

## Global Constraints

- Sistema travado exclusivamente em Português Brasileiro (PT-BR).
- Respostas e documentações em PT-BR.
- Windows Batch scripts e comandos Powershell devem seguir estritamente as regras de escape e sem `&&`.
- Testes 100% passando (cobertura total das novas funcionalidades sem quebrar nenhum dos 82 testes existentes).
- Atualizar o grafo graphify (`graphify update .`) ao concluir alterações de código.

---

### Task 1: Schemas de Dados para Controles de Áudio, Logs e Métricas

**Files:**
- Modify: `backend/models/schemas.py`
- Test: `tests/test_schemas_controls.py`

**Interfaces:**
- Produces: `NarrationRequestSchema(text, voice_id, speed, max_pause, pitch, presence)`
- Produces: `NarrationAndTranscriptionRequestSchema(text, voice_id, mode, speed, max_pause, pitch, presence)`
- Produces: `HistoryItemSchema` com campos de áudio opcionais `speed`, `max_pause`, `pitch`, `presence`
- Produces: `LogEntrySchema(id, timestamp, level, message, source)`, `SystemMetricsSchema(cpu_percent, ram_used_gb, ram_total_gb, ram_percent)`

- [ ] **Step 1: Escrever teste que falha em `tests/test_schemas_controls.py`**

```python
import pytest
from backend.models.schemas import (
    NarrationRequestSchema,
    NarrationAndTranscriptionRequestSchema,
    HistoryItemSchema,
    LogEntrySchema,
    SystemMetricsSchema,
)
from backend.models.enums import TranscriptionMode

def test_narration_request_schema_defaults():
    req = NarrationRequestSchema(text="Teste de narração")
    assert req.speed == 1.0
    assert req.max_pause == 0.3
    assert req.pitch == 0.0
    assert req.presence == 0.5

def test_narration_request_schema_custom():
    req = NarrationRequestSchema(
        text="Teste custom",
        speed=1.25,
        max_pause=0.5,
        pitch=2.0,
        presence=0.8,
    )
    assert req.speed == 1.25
    assert req.max_pause == 0.5
    assert req.pitch == 2.0
    assert req.presence == 0.8

def test_narrate_and_transcribe_schema_controls():
    req = NarrationAndTranscriptionRequestSchema(
        text="Texto",
        mode=TranscriptionMode.DYNAMIC,
        speed=1.1,
        max_pause=0.2,
        pitch=-1.0,
        presence=0.7,
    )
    assert req.mode == TranscriptionMode.DYNAMIC
    assert req.speed == 1.1
    assert req.max_pause == 0.2

def test_log_and_metrics_schemas():
    log = LogEntrySchema(
        id=1,
        timestamp="2026-09-18T12:00:00Z",
        level="INFO",
        message="Servidor iniciado",
        source="uvicorn",
    )
    assert log.level == "INFO"

    metric = SystemMetricsSchema(
        cpu_percent=15.5,
        ram_used_gb=4.2,
        ram_total_gb=16.0,
        ram_percent=26.25,
    )
    assert metric.cpu_percent == 15.5
```

- [ ] **Step 2: Executar teste para verificar que falha**

Run: `.venv\Scripts\python.exe -m pytest tests/test_schemas_controls.py -v`
Expected: FAIL com `ImportError` ou `AttributeError`

- [ ] **Step 3: Implementar schemas em `backend/models/schemas.py`**

Adicionar campos `speed`, `max_pause`, `pitch`, `presence` em `NarrationRequestSchema`, `NarrationAndTranscriptionRequestSchema` e `HistoryItemSchema`.
Definir `LogEntrySchema` e `SystemMetricsSchema`.

- [ ] **Step 4: Executar teste para verificar que passa**

Run: `.venv\Scripts\python.exe -m pytest tests/test_schemas_controls.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/models/schemas.py tests/test_schemas_controls.py
git commit -m "feat(models): add voice control parameters and logging schemas"
```

---

### Task 2: Serviços de Captura de Logs e Coleta de Métricas

**Files:**
- Create: `backend/services/log_service.py`
- Create: `backend/services/metrics_service.py`
- Test: `tests/test_log_service.py`
- Test: `tests/test_metrics_service.py`

**Interfaces:**
- Produces: `LogService.get_logs(level=None, search=None, limit=100) -> list[dict]`
- Produces: `LogService.clear_logs()`
- Produces: `LogService.broadcast_log(entry: dict)`
- Produces: `MetricsService.get_current_metrics() -> dict`
- Produces: `LogBufferHandler(logging.Handler)`, `StreamInterceptor(io.TextIOBase)`

- [ ] **Step 1: Escrever teste que falha em `tests/test_log_service.py`**

```python
import logging
from backend.services.log_service import LogService, LogBufferHandler

def test_log_service_ring_buffer():
    service = LogService(max_entries=5)
    for i in range(10):
        service.add_log(level="INFO", message=f"Mensagem {i}", source="test")
    
    logs = service.get_logs()
    assert len(logs) == 5
    assert logs[-1]["message"] == "Mensagem 9"

def test_log_service_filter_level():
    service = LogService(max_entries=10)
    service.add_log("INFO", "Info msg", "test")
    service.add_log("ERROR", "Error msg", "test")
    service.add_log("WARNING", "Warn msg", "test")

    errors = service.get_logs(level="ERROR")
    assert len(errors) == 1
    assert errors[0]["message"] == "Error msg"

def test_log_service_clear():
    service = LogService()
    service.add_log("INFO", "Test", "test")
    assert len(service.get_logs()) == 1
    service.clear()
    assert len(service.get_logs()) == 0

def test_log_buffer_handler():
    service = LogService()
    handler = LogBufferHandler(service)
    logger = logging.getLogger("test_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Log via standard logging")
    logs = service.get_logs()
    assert any("Log via standard logging" in l["message"] for l in logs)
```

- [ ] **Step 2: Escrever teste que falha em `tests/test_metrics_service.py`**

```python
from backend.services.metrics_service import MetricsService

def test_metrics_service_structure():
    metrics = MetricsService.get_current_metrics()
    assert "cpu_percent" in metrics
    assert "ram_used_gb" in metrics
    assert "ram_total_gb" in metrics
    assert "ram_percent" in metrics
    assert isinstance(metrics["cpu_percent"], (int, float))
    assert metrics["ram_total_gb"] > 0
```

- [ ] **Step 3: Implementar `backend/services/log_service.py` e `backend/services/metrics_service.py`**

- [ ] **Step 4: Executar testes de log e métricas**

Run: `.venv\Scripts\python.exe -m pytest tests/test_log_service.py tests/test_metrics_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/log_service.py backend/services/metrics_service.py tests/test_log_service.py tests/test_metrics_service.py
git commit -m "feat(services): implement log buffer handler and system metrics collector"
```

---

### Task 3: Controles de Geração no Motor TTS (Ritmo, Pausa, Tom, Presença)

**Files:**
- Modify: `backend/services/tts_service.py`
- Test: `tests/test_voice_controls.py`

**Interfaces:**
- Modifies: `TTSService.generate_speech(text, voice_sample_path, output_mp3_path, progress_callback=None, speed=1.0, max_pause=0.3, pitch=0.0, presence=0.5)`
- Produces: áudio MP3 com velocidade ajustada (`atempo`), pausas moduladas e presença aplicada no Chatterbox (`exaggeration=presence`).

- [ ] **Step 1: Escrever teste de modulação de voz em `tests/test_voice_controls.py`**

```python
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from backend.services.tts_service import TTSService

def test_tts_service_passes_presence_as_exaggeration(tmp_path):
    mock_model = MagicMock()
    mock_model.sr = 24000
    mock_model.generate.return_value = np.zeros(2400, dtype=np.float32)

    tts = TTSService(model=mock_model)
    out_file = tmp_path / "out.mp3"
    dummy_sample = tmp_path / "sample.wav"
    dummy_sample.write_bytes(b"RIFFdummyWAVEfmt ")

    with patch.object(tts, "_export_to_mp3"):
        tts.generate_speech(
            text="Frase de teste",
            voice_sample_path=dummy_sample,
            output_mp3_path=out_file,
            speed=1.2,
            max_pause=0.2,
            pitch=2.0,
            presence=0.8,
        )

    # Verifica se exaggeration foi repassado com o valor de presence
    _, kwargs = mock_model.generate.call_args
    assert kwargs.get("exaggeration") == 0.8
```

- [ ] **Step 2: Executar teste para verificar falha**

Run: `.venv\Scripts\python.exe -m pytest tests/test_voice_controls.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar parâmetros em `backend/services/tts_service.py`**

Atualizar `generate_speech` para aceitar `speed`, `max_pause`, `pitch`, `presence`:
1. Inserir silêncio de duração `max_pause` entre chunks de áudio na concatenação.
2. Passar `exaggeration=presence` na chamada `model.generate()`.
3. Adicionar filtros de áudio em `_export_to_mp3` (`atempo`, etc.) quando `speed != 1.0` ou `pitch != 0.0`.

- [ ] **Step 4: Executar testes de controles de voz**

Run: `.venv\Scripts\python.exe -m pytest tests/test_voice_controls.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/tts_service.py tests/test_voice_controls.py
git commit -m "feat(tts): add voice generation controls for speed, pause, pitch and presence"
```

---

### Task 4: Endpoints REST e WebSocket de Logs, Métricas e Narração Atualizada

**Files:**
- Create: `backend/routers/logs.py`
- Create: `backend/routers/system.py`
- Modify: `backend/routers/narration.py`
- Modify: `backend/main.py`
- Test: `tests/test_logs_api.py`

**Interfaces:**
- Produces: `GET /api/logs`, `DELETE /api/logs`, `WS /api/ws/logs`
- Produces: `GET /api/system/metrics`
- Modifies: `POST /api/narrate` e `POST /api/narrate-and-transcribe` aceitando os novos campos nos payloads JSON.

- [ ] **Step 1: Escrever teste que falha em `tests/test_logs_api.py`**

```python
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.services.log_service import log_service

def test_get_and_clear_logs_endpoint():
    app = create_app()
    client = TestClient(app)
    
    log_service.clear()
    log_service.add_log("INFO", "Log de teste API", "test")

    res = client.get("/api/logs")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[-1]["message"] == "Log de teste API"

    del_res = client.delete("/api/logs")
    assert del_res.status_code == 200
    assert len(log_service.get_logs()) == 0

def test_system_metrics_endpoint():
    app = create_app()
    client = TestClient(app)

    res = client.get("/api/system/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "cpu_percent" in data
    assert "ram_percent" in data
```

- [ ] **Step 2: Executar teste para verificar que falha**

Run: `.venv\Scripts\python.exe -m pytest tests/test_logs_api.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar roteadores e registro em `backend/main.py`**

- [ ] **Step 4: Executar testes de API de logs e regressão da API geral**

Run: `.venv\Scripts\python.exe -m pytest tests/test_logs_api.py tests/test_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/routers/logs.py backend/routers/system.py backend/routers/narration.py backend/main.py tests/test_logs_api.py
git commit -m "feat(api): add logs websocket, system metrics and update narration with voice controls"
```

---

### Task 5: Interface Web — Drawer de Logs em Tempo Real e Métricas

**Files:**
- Create: `frontend/js/components/log-drawer.js`
- Modify: `frontend/index.html`
- Modify: `frontend/css/style.css`
- Modify: `frontend/js/app.js`

**Interfaces:**
- Produces: Componente `LogDrawer` com conexão WebSocket em `/api/ws/logs`, toggle inferior com badge de erros, filtros de nível, busca em tempo real, auto-scroll inteligente e mostradores de CPU/RAM.

- [ ] **Step 1: Criar estilos CSS do drawer em `frontend/css/style.css`**
- [ ] **Step 2: Criar markup do container e botão toggle em `frontend/index.html`**
- [ ] **Step 3: Implementar lógica do drawer em `frontend/js/components/log-drawer.js`**
- [ ] **Step 4: Inicializar o drawer em `frontend/js/app.js`**
- [ ] **Step 5: Testar via `tests/test_frontend.py`**
- [ ] **Step 6: Commit**

```bash
git add frontend/index.html frontend/css/style.css frontend/js/components/log-drawer.js frontend/js/app.js tests/test_frontend.py
git commit -m "feat(ui): implement real-time log drawer with system metrics and devtools style"
```

---

### Task 6: Interface Web — Controles de Geração (Accordion) e Página #api-docs

**Files:**
- Modify: `frontend/js/pages/narrate.js`
- Modify: `frontend/js/api.js`
- Create: `frontend/js/pages/api-docs.js`
- Modify: `frontend/js/app.js`

**Interfaces:**
- Produces: Accordion retrátil com sliders para Ritmo (`speed`), Pausa (`max_pause`), Tom (`pitch`), Presença (`presence`) e botão de reset.
- Produces: Rota `#api-docs` com visualização de todos os endpoints REST, exemplos `curl` e link direto para o Swagger UI interativo (`/docs`).

- [ ] **Step 1: Atualizar `frontend/js/pages/narrate.js` com o Accordion de ajustes de voz e eventos de slider**
- [ ] **Step 2: Atualizar `frontend/js/api.js` para repassar os novos controles**
- [ ] **Step 3: Criar `frontend/js/pages/api-docs.js` com documentação visual e exemplos curl de todas as rotas**
- [ ] **Step 4: Registrar rota `api-docs` em `frontend/js/app.js`**
- [ ] **Step 5: Testar frontend**

Run: `.venv\Scripts\python.exe -m pytest tests/test_frontend.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add frontend/js/pages/narrate.js frontend/js/pages/api-docs.js frontend/js/api.js frontend/js/app.js
git commit -m "feat(ui): add voice adjustments accordion and api documentation page"
```

---

### Task 7: Validação Completa de Regressão e Atualização do Conhecimento

**Files:**
- Modify: `README.md` (documentar os novos endpoints e controles)
- Run: `graphify update .`

- [ ] **Step 1: Executar suite completa de testes**

Run: `.venv\Scripts\python.exe -m pytest tests/ -v`
Expected: PASS (todos os testes passando sem erros)

- [ ] **Step 2: Atualizar README.md com a documentação dos novos recursos**
- [ ] **Step 3: Executar atualização do grafo graphify**

Run: `.venv\Scripts\python.exe -c "import os; print('Graphify check')"` e `graphify update .`

- [ ] **Step 4: Commit final**

```bash
git add README.md graphify-out/
git commit -m "docs: update readme and knowledge graph with log panel, voice controls and full api"
```
