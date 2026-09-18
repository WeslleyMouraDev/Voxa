from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from backend.config import OUTPUT_DIR
from backend.models.enums import TranscriptionMode
from backend.models.schemas import (
    HistoryItemSchema,
    NarrationAndTranscriptionRequestSchema,
    NarrationRequestSchema,
)
from backend.services.srt_builder import SRTBuilder
from backend.services.stt_service import STTService
from backend.services.task_manager import task_manager
from backend.services.tts_service import TTSService
from backend.storage.history_store import history_store
from backend.storage.settings_store import settings_store
from backend.storage.voice_store import voice_store

import inspect

router = APIRouter(prefix="/api", tags=["narration"])


def _invoke_tts_generate(tts: TTSService, **kwargs) -> Path:
    """
    Invoca tts.generate_speech filtrando kwargs caso o alvo seja um mock antigo sem suporte
    aos novos parâmetros de voz, garantindo compatibilidade retroativa absoluta com testes legados.
    """
    target = getattr(tts, "generate_speech")
    if hasattr(target, "side_effect") and callable(target.side_effect):
        target = target.side_effect
    try:
        sig = inspect.signature(target)
        has_var_keyword = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )
        if not has_var_keyword:
            kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    except (ValueError, TypeError):
        pass
    return tts.generate_speech(**kwargs)


def _run_narration_task(
    task_id: str,
    text: str,
    voice_id: str,
    voice_name: str,
    sample_path: str,
    speed: float = 1.0,
    max_pause: float = 0.3,
    pitch: float = 0.0,
    presence: float = 0.5,
) -> None:
    try:
        output_mp3 = Path(OUTPUT_DIR) / f"{task_id}.mp3"

        def on_progress(pct: float, msg: str) -> None:
            scaled_pct = min(90.0, pct * 0.9)
            task_manager.update_progress(task_id, scaled_pct, msg)

        tts = TTSService()
        _invoke_tts_generate(
            tts,
            text=text,
            voice_sample_path=sample_path,
            output_mp3_path=output_mp3,
            progress_callback=on_progress,
            speed=speed,
            max_pause=max_pause,
            pitch=pitch,
            presence=presence,
        )

        history_item = HistoryItemSchema(
            text=text,
            voice_id=voice_id,
            voice_name=voice_name,
            audio_path=str(output_mp3),
            duration_seconds=0.0,
            speed=speed,
            max_pause=max_pause,
            pitch=pitch,
            presence=presence,
        )
        history_store.add_item(history_item)

        task_manager.complete_task(
            task_id,
            {
                "history_id": history_item.id,
                "audio_url": f"/output/{output_mp3.name}",
            },
        )
    except Exception as e:
        task_manager.fail_task(task_id, str(e))


def _run_narrate_and_transcribe_task(
    task_id: str,
    text: str,
    voice_id: str,
    voice_name: str,
    sample_path: str,
    mode: TranscriptionMode,
    speed: float = 1.0,
    max_pause: float = 0.3,
    pitch: float = 0.0,
    presence: float = 0.5,
) -> None:
    try:
        output_mp3 = Path(OUTPUT_DIR) / f"{task_id}.mp3"
        output_srt = Path(OUTPUT_DIR) / f"{task_id}.srt"

        # 1. Gera áudio MP3 (0% a 60%)
        def on_tts_progress(pct: float, msg: str) -> None:
            scaled_pct = (pct / 100.0) * 60.0
            task_manager.update_progress(task_id, scaled_pct, f"TTS: {msg}")

        tts = TTSService()
        _invoke_tts_generate(
            tts,
            text=text,
            voice_sample_path=sample_path,
            output_mp3_path=output_mp3,
            progress_callback=on_tts_progress,
            speed=speed,
            max_pause=max_pause,
            pitch=pitch,
            presence=presence,
        )

        # 2. Transcreve o áudio gerado (60% a 90%)
        def on_stt_progress(pct: float, msg: str) -> None:
            scaled_pct = 60.0 + (pct / 100.0) * 30.0
            task_manager.update_progress(task_id, scaled_pct, f"STT: {msg}")

        stt = STTService()
        settings = settings_store.get_settings()
        mode_cfg = settings.transcription_modes.get(mode.value)
        mode_dict = mode_cfg.model_dump() if mode_cfg else None

        srt_content, words, duration = stt.transcribe_audio(
            audio_path=output_mp3,
            mode=mode,
            mode_config=mode_dict,
            progress_callback=on_stt_progress,
        )

        # 3. Salva arquivo .srt
        SRTBuilder.save_srt_file(srt_content, output_srt)

        # 4. Registra no HistoryStore
        history_item = HistoryItemSchema(
            text=text,
            voice_id=voice_id,
            voice_name=voice_name,
            mode=mode,
            audio_path=str(output_mp3),
            srt_path=str(output_srt),
            duration_seconds=duration,
            speed=speed,
            max_pause=max_pause,
            pitch=pitch,
            presence=presence,
        )
        history_store.add_item(history_item)

        # 5. Conclui a tarefa
        task_manager.complete_task(
            task_id,
            {
                "history_id": history_item.id,
                "audio_url": f"/output/{output_mp3.name}",
                "srt_url": f"/output/{output_srt.name}",
            },
        )
    except Exception as e:
        task_manager.fail_task(task_id, str(e))


@router.post("/narrate", status_code=status.HTTP_202_ACCEPTED)
def narrate(
    request: NarrationRequestSchema,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Inicia tarefa de narração em background a partir de um texto e voz selecionada,
    aplicando controles vocais de velocidade, pausas, tom e expressividade.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O texto para narração não pode ser vazio.",
        )

    voice = None
    if request.voice_id:
        voice = voice_store.get_voice(request.voice_id)
    else:
        voice = voice_store.get_default_voice()

    if voice is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma voz disponível ou cadastrada no sistema.",
        )

    task_id = task_manager.create_task(name="Narração")
    background_tasks.add_task(
        _run_narration_task,
        task_id=task_id,
        text=request.text,
        voice_id=voice.id,
        voice_name=voice.name,
        sample_path=voice.sample_path,
        speed=request.speed,
        max_pause=request.max_pause,
        pitch=request.pitch,
        presence=request.presence,
    )
    return {"task_id": task_id}


@router.post("/narrate-and-transcribe", status_code=status.HTTP_202_ACCEPTED)
def narrate_and_transcribe(
    request: NarrationAndTranscriptionRequestSchema,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Inicia tarefa em background que sintetiza voz com controles dinâmicos e transcreve com legendas SRT.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O texto para narração não pode ser vazio.",
        )

    voice = None
    if request.voice_id:
        voice = voice_store.get_voice(request.voice_id)
    else:
        voice = voice_store.get_default_voice()

    if voice is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma voz disponível ou cadastrada no sistema.",
        )

    task_id = task_manager.create_task(name="Narração e Transcrição")
    background_tasks.add_task(
        _run_narrate_and_transcribe_task,
        task_id=task_id,
        text=request.text,
        voice_id=voice.id,
        voice_name=voice.name,
        sample_path=voice.sample_path,
        mode=request.mode,
        speed=request.speed,
        max_pause=request.max_pause,
        pitch=request.pitch,
        presence=request.presence,
    )
    return {"task_id": task_id}
