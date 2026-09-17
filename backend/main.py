from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import backend.config as config
from backend.routers import history, narration, progress, settings, transcription, voices


def create_app() -> FastAPI:
    """Cria e configura a instância da aplicação FastAPI do Voxa."""
    app = FastAPI(
        title="Voxa",
        version="1.0.0",
        description="Ferramenta Local de Clonagem de Voz, Narração e Transcrição com Legendas Dinâmicas",
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
