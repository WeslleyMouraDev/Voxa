import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from backend.config import OUTPUT_DIR
from backend.models.enums import TranscriptionMode
from backend.models.schemas import HistoryItemSchema
from backend.services.srt_builder import SRTBuilder
from backend.services.stt_service import STTService
from backend.services.task_manager import task_manager
from backend.storage.history_store import history_store
from backend.storage.settings_store import settings_store

router = APIRouter(prefix="/api", tags=["transcription"])


def _run_transcription_task(
    task_id: str,
    audio_path: str,
    mode: TranscriptionMode,
) -> None:
    try:
        output_srt = Path(OUTPUT_DIR) / f"{task_id}.srt"

        def on_progress(pct: float, msg: str) -> None:
            task_manager.update_progress(task_id, pct, msg)

        stt = STTService()
        settings = settings_store.get_settings()
        mode_cfg = settings.transcription_modes.get(mode.value)
        mode_dict = mode_cfg.model_dump() if mode_cfg else None

        srt_content, words, duration = stt.transcribe_audio(
            audio_path=audio_path,
            mode=mode,
            mode_config=mode_dict,
            progress_callback=on_progress,
        )

        SRTBuilder.save_srt_file(srt_content, output_srt)

        text_preview = " ".join(w.word for w in words) if words else "Áudio transcrito"

        history_item = HistoryItemSchema(
            text=text_preview,
            voice_id="",
            voice_name="Upload/Transcrição",
            mode=mode,
            audio_path=str(audio_path),
            srt_path=str(output_srt),
            duration_seconds=duration,
        )
        history_store.add_item(history_item)

        task_manager.complete_task(
            task_id,
            {
                "history_id": history_item.id,
                "audio_path": str(audio_path),
                "srt_url": f"/output/{output_srt.name}",
                "srt_content": srt_content,
            },
        )
    except Exception as e:
        task_manager.fail_task(task_id, str(e))


@router.post("/transcribe", status_code=status.HTTP_202_ACCEPTED)
async def transcribe(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    audio_path: Optional[str] = Form(None),
    mode: TranscriptionMode = Form(TranscriptionMode.NORMAL),
) -> dict:
    """
    Inicia tarefa de transcrição a partir de upload de arquivo ou caminho de áudio existente.
    """
    if not file and not audio_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário fornecer um arquivo de áudio ou um caminho audio_path.",
        )

    task_id = task_manager.create_task(name="Transcrição")

    if file:
        clean_name = Path(file.filename or "audio.mp3").name
        dest_path = Path(OUTPUT_DIR) / f"upload_{task_id}_{clean_name}"
        content = await file.read()
        with open(dest_path, "wb") as f_out:
            f_out.write(content)
        resolved_audio_path = str(dest_path)
    else:
        assert audio_path is not None
        p = Path(audio_path)
        if not p.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo de áudio não encontrado no caminho informado: {audio_path}",
            )
        resolved_audio_path = str(p.resolve())

    background_tasks.add_task(
        _run_transcription_task,
        task_id=task_id,
        audio_path=resolved_audio_path,
        mode=mode,
    )
    return {"task_id": task_id}
