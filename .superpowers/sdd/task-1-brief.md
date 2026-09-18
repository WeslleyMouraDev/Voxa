# Task 1 Brief: Schemas de Dados para Controles de Áudio, Logs e Métricas

## Objetivo
Adicionar os campos de modulação vocal (`speed`, `max_pause`, `pitch`, `presence`) nos schemas Pydantic de requisição e histórico, e criar os novos schemas de logs e métricas.

## Arquivos a Modificar / Criar
- Modificar: `backend/models/schemas.py`
- Criar: `tests/test_schemas_controls.py`
- Relatório a gerar: `d:\Projetos\Voxa\.superpowers\sdd\task-1-report.md`

## Requisitos Técnicos

1. Em `backend/models/schemas.py`:
   - Em `NarrationRequestSchema`:
     - `speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Velocidade da narração (0.5x a 2.0x)")`
     - `max_pause: float = Field(default=0.3, ge=0.0, le=2.0, description="Pausa máxima entre frases em segundos")`
     - `pitch: float = Field(default=0.0, ge=-12.0, le=12.0, description="Ajuste de tom em semitons (-12 a +12)")`
     - `presence: float = Field(default=0.5, ge=0.0, le=1.0, description="Presença vocal / expressividade (0.0 a 1.0)")`
   - Em `NarrationAndTranscriptionRequestSchema`:
     - Mesmos campos adicionais: `speed`, `max_pause`, `pitch`, `presence` com mesmos defaults e validações.
   - Em `HistoryItemSchema`:
     - `speed: Optional[float] = Field(default=1.0)`
     - `max_pause: Optional[float] = Field(default=0.3)`
     - `pitch: Optional[float] = Field(default=0.0)`
     - `presence: Optional[float] = Field(default=0.5)`
   - Novo `LogEntrySchema(BaseModel)`:
     - `id: int`
     - `timestamp: str`
     - `level: str` (INFO, WARNING, ERROR, DEBUG)
     - `message: str`
     - `source: str = "app"`
   - Novo `SystemMetricsSchema(BaseModel)`:
     - `cpu_percent: float`
     - `ram_used_gb: float`
     - `ram_total_gb: float`
     - `ram_percent: float`

2. Ciclo TDD:
   - Escrever teste em `tests/test_schemas_controls.py`
   - Rodar `.venv\Scripts\python.exe -m pytest tests/test_schemas_controls.py -v` para confirmar falha
   - Modificar `backend/models/schemas.py`
   - Rodar novamente `.venv\Scripts\python.exe -m pytest tests/test_schemas_controls.py tests/ -v` até passar 100%
   - Escrever relatório em `d:\Projetos\Voxa\.superpowers\sdd\task-1-report.md`
   - Fazer commit git: `feat(models): add voice control parameters and logging schemas`
