import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import backend.config as config
from backend.routers import (
    history,
    logs,
    narration,
    progress,
    settings,
    system,
    transcription,
    voices,
)
from backend.services.log_service import LogBufferHandler, log_service

OPENAPI_TAGS = [
    {
        "name": "settings",
        "description": "Configurações globais do sistema, limite de utilização de CPU, portas de rede e modos de transcrição.",
    },
    {
        "name": "voices",
        "description": "Gerenciamento e upload de amostras de áudio para clonagem vocal.",
    },
    {
        "name": "narration",
        "description": "Síntese de voz e narração neural com controle fino de velocidade, pausas, tom e expressividade.",
    },
    {
        "name": "transcription",
        "description": "Geração e alinhamento de legendas SRT dinâmicas via Whisper (Normal, Dinâmico, Acelerado).",
    },
    {
        "name": "history",
        "description": "Histórico persistente de narrações e transcrições geradas com links diretos para áudio e legendas.",
    },
    {
        "name": "progress",
        "description": "Streaming em tempo real do progresso de tarefas assíncronas via Server-Sent Events (SSE).",
    },
    {
        "name": "logs",
        "description": "Histórico e streaming em tempo real de logs estruturados do servidor via REST e WebSocket.",
    },
    {
        "name": "system",
        "description": "Métricas em tempo real de hardware e recursos (CPU e memória RAM).",
    },
]


def setup_logging() -> None:
    """Anexa o LogBufferHandler aos loggers raiz do Python e do uvicorn para streaming."""
    handler = LogBufferHandler(service=log_service)
    handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    if not any(isinstance(h, LogBufferHandler) for h in root_logger.handlers):
        root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        u_logger = logging.getLogger(logger_name)
        if not any(isinstance(h, LogBufferHandler) for h in u_logger.handlers):
            u_logger.addHandler(handler)


def create_app() -> FastAPI:
    """Cria e configura a instância da aplicação FastAPI do Voxa."""
    setup_logging()

    app = FastAPI(
        title="Voxa",
        version="1.0.0",
        description=(
            "Ferramenta Local de Clonagem de Voz, Narração Neural e Transcrição com Legendas Dinâmicas em PT-BR.\n\n"
            "### Funcionalidades Principais:\n"
            "- **Clonagem e Narração**: Síntese de voz realista via Chatterbox V3 PT-BR com controles de velocidade, pausa, pitch e expressividade.\n"
            "- **Transcrição Inteligente**: Geração de legendas SRT com segmentação dinâmica via Whisper.\n"
            "- **Telemetria e Logs**: Streaming contínuo de logs e métricas de hardware via WebSocket e SSE."
        ),
        openapi_tags=OPENAPI_TAGS,
    )

    # Configuração de CORS irrestrito para consumo local e flexível
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registro dos roteadores de API
    app.include_router(settings.router)
    app.include_router(voices.router)
    app.include_router(history.router)
    app.include_router(narration.router)
    app.include_router(transcription.router)
    app.include_router(progress.router)
    app.include_router(logs.router)
    app.include_router(system.router)

    # Montagem das pastas estáticas para acesso a arquivos de áudio e legendas
    Path(config.VOICES_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    app.mount("/voices", StaticFiles(directory=str(config.VOICES_DIR)), name="voices")
    app.mount("/output", StaticFiles(directory=str(config.OUTPUT_DIR)), name="output")

    # Montagem do frontend caso a pasta exista
    frontend_dir = Path(config.BASE_DIR) / "frontend"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app


app = create_app()
