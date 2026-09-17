import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.config import VOICES_DIR
from backend.models.schemas import VoiceSchema
from backend.storage.voice_store import voice_store

router = APIRouter(prefix="/api/voices", tags=["voices"])


@router.get("", response_model=List[VoiceSchema])
def list_voices() -> List[VoiceSchema]:
    """Lista todas as vozes cadastradas."""
    return voice_store.list_voices()


@router.post("", response_model=VoiceSchema, status_code=status.HTTP_201_CREATED)
async def create_voice(
    name: str = Form(...),
    file: UploadFile = File(...),
    is_default: bool = Form(False),
) -> VoiceSchema:
    """
    Cadastra uma nova voz a partir do upload de um arquivo de áudio de amostra.
    """
    clean_filename = Path(file.filename or "sample.wav").name
    dest_path = VOICES_DIR / f"{uuid.uuid4()}_{clean_filename}"

    content = await file.read()
    with open(dest_path, "wb") as f_out:
        f_out.write(content)

    new_voice = voice_store.add_voice(
        name=name,
        sample_path=str(dest_path),
        is_default=is_default,
    )
    return new_voice


@router.put("/{voice_id}/default", response_model=VoiceSchema)
def set_default_voice(voice_id: str) -> VoiceSchema:
    """Define a voz especificada como a padrão do sistema."""
    success = voice_store.set_default_voice(voice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voz não encontrada")
    voice = voice_store.get_voice(voice_id)
    if voice is None:
        raise HTTPException(status_code=404, detail="Voz não encontrada")
    return voice


@router.delete("/{voice_id}")
def delete_voice(voice_id: str) -> dict:
    """Exclui a voz e apaga o arquivo físico de amostra de voz."""
    success = voice_store.delete_voice(voice_id, delete_file=True)
    if not success:
        raise HTTPException(status_code=404, detail="Voz não encontrada")
    return {"message": "Voz excluída com sucesso"}
