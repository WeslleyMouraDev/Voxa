# Task 1: Configurações, Modelos de Dados e Armazenamento JSON Concorrente

## Objetivo
Implementar a camada de configuração, modelos Pydantic (enums e schemas) e persistência em arquivos JSON com atomic file write e thread locks seguros para concorrência em `backend/`.

## Arquivos a Criar
- `backend/__init__.py`
- `backend/models/__init__.py`
- `backend/models/enums.py`
- `backend/models/schemas.py`
- `backend/config.py`
- `backend/storage/__init__.py`
- `backend/storage/json_store.py`
- `backend/storage/settings_store.py`
- `backend/storage/voice_store.py`
- `backend/storage/history_store.py`
- `tests/__init__.py`
- `tests/test_storage.py`

## Especificações Técnicas e Interfaces

### 1. `backend/models/enums.py`
- `TranscriptionMode(str, Enum)`:
  - `NORMAL = "normal"`
  - `DYNAMIC = "dynamic"`
  - `ACCELERATED = "accelerated"`
- `TaskStatus(str, Enum)`:
  - `IDLE = "idle"`
  - `PROCESSING = "processing"`
  - `COMPLETED = "completed"`
  - `ERROR = "error"`

### 2. `backend/models/schemas.py`
- `ModeConfig(BaseModel)`:
  - `min_seconds: float`
  - `max_seconds: float`
- `SettingsSchema(BaseModel)`:
  - `cpu_percent: int = 75` (de 25 a 100)
  - `server_port: int = 7865`
  - `auto_open_browser: bool = True`
  - `whisper_model: str = "medium"`
  - `transcription_modes: dict[str, ModeConfig]` com defaults:
    - `"normal"`: min 4.0, max 6.0
    - `"dynamic"`: min 2.0, max 4.0
    - `"accelerated"`: min 1.0, max 2.0
- `VoiceSchema(BaseModel)`:
  - `id: str` (UUID)
  - `name: str`
  - `sample_path: str`
  - `is_default: bool = False`
  - `created_at: str` (ISO 8601)
- `HistoryItemSchema(BaseModel)`:
  - `id: str` (UUID)
  - `text: str`
  - `voice_id: str`
  - `voice_name: str`
  - `mode: Optional[TranscriptionMode] = None`
  - `audio_path: str`
  - `srt_path: Optional[str] = None`
  - `duration_seconds: float = 0.0`
  - `created_at: str` (ISO 8601)
- Schemas de requisição:
  - `NarrationRequestSchema(BaseModel)`: `text: str`, `voice_id: Optional[str] = None`
  - `TranscriptionRequestSchema(BaseModel)`: `audio_path: Optional[str] = None`, `mode: TranscriptionMode = TranscriptionMode.NORMAL`
  - `NarrationAndTranscriptionRequestSchema(BaseModel)`: `text: str`, `voice_id: Optional[str] = None`, `mode: TranscriptionMode = TranscriptionMode.NORMAL`

### 3. `backend/config.py`
- Obter o diretório raiz do projeto `BASE_DIR = Path(__file__).resolve().parent.parent`
- `DATA_DIR = BASE_DIR / "data"`
- `VOICES_DIR = BASE_DIR / "voices"`
- `OUTPUT_DIR = BASE_DIR / "output"`
- Garantir que as pastas `data`, `voices` e `output` sejam criadas se não existirem.
- Caminhos para `settings.json`, `voices.json`, `history.json`.

### 4. `backend/storage/json_store.py`
- `JSONStore`:
  - Leitura e escrita com `threading.Lock` ou `threading.RLock`.
  - Escrita atômica: escreve primeiro em arquivo temporário `.tmp` no mesmo diretório e depois usa `os.replace` para evitar corrupção em caso de queda de energia ou interrupção.
  - Encoding UTF-8 com indent=2.

### 5. `backend/storage/settings_store.py`
- Instância singleton ou classe `SettingsStore`:
  - `get_settings() -> SettingsSchema` (se arquivo não existir ou for inválido, carrega defaults e persiste).
  - `update_settings(updates: dict | SettingsSchema) -> SettingsSchema`.

### 6. `backend/storage/voice_store.py`
- `VoiceStore`:
  - `list_voices() -> list[VoiceSchema]`
  - `get_voice(voice_id: str) -> Optional[VoiceSchema]`
  - `get_default_voice() -> Optional[VoiceSchema]`
  - `add_voice(name: str, sample_path: str, is_default: bool = False) -> VoiceSchema`: se `is_default` for True ou se for a primeira voz, as demais deixam de ser default.
  - `set_default_voice(voice_id: str) -> bool`: define essa voz como `is_default = True` e todas as outras como `False`.
  - `delete_voice(voice_id: str, delete_file: bool = True) -> bool`: remove a voz da lista e opcionalmente remove o arquivo físico de amostra. Se a voz deletada era default, a primeira voz restante vira default (se houver).

### 7. `backend/storage/history_store.py`
- `HistoryStore`:
  - `list_history() -> list[HistoryItemSchema]` (ordenado por created_at decrescente)
  - `get_item(item_id: str) -> Optional[HistoryItemSchema]`
  - `add_item(item: HistoryItemSchema) -> HistoryItemSchema`
  - `delete_item(item_id: str, delete_files: bool = True) -> bool`: remove do histórico e apaga arquivos físicos de áudio (`.mp3`) e legenda (`.srt`) do disco se existirem.
  - `clear_all(delete_files: bool = True) -> int`: apaga todos os registros e arquivos físicos do disco.

## Requisitos de Testes (`tests/test_storage.py`)
- Testar defaults do `SettingsStore` e atualização de configurações.
- Testar `VoiceStore`: adição, garantia de voz padrão única, troca de padrão, exclusão física e lógica.
- Testar `HistoryStore`: adição de itens, busca, exclusão individual com remoção de arquivo e limpeza total (`clear_all`).
- Todos os testes devem rodar em diretórios temporários (`tmp_path`) sem poluir o diretório real do projeto.

## Comandos
- Testes: `python -m pytest tests/test_storage.py -v`
- Commits: `git add backend/ tests/ && git commit -m "feat: add models, configuration, and atomic json storage"`
