from pathlib import Path
from typing import List, Optional, Union

from backend.config import VOICES_FILE
from backend.models.schemas import VoiceSchema
from backend.storage.json_store import JSONStore


class VoiceStore:
    def __init__(self, file_path: Optional[Union[Path, str]] = None) -> None:
        self.file_path = Path(file_path) if file_path else VOICES_FILE
        self.store = JSONStore(self.file_path)

    def _load_voices(self) -> List[VoiceSchema]:
        data = self.store.read(default=[])
        if not isinstance(data, list):
            return []
        voices = []
        for item in data:
            try:
                voices.append(VoiceSchema.model_validate(item))
            except Exception:
                continue
        return voices

    def _save_voices(self, voices: List[VoiceSchema]) -> None:
        self.store.write([v.model_dump() for v in voices])

    def list_voices(self) -> List[VoiceSchema]:
        with self.store.lock:
            return self._load_voices()

    def get_voice(self, voice_id: str) -> Optional[VoiceSchema]:
        with self.store.lock:
            for v in self._load_voices():
                if v.id == voice_id:
                    return v
            return None

    def get_default_voice(self) -> Optional[VoiceSchema]:
        with self.store.lock:
            for v in self._load_voices():
                if v.is_default:
                    return v
            return None

    def add_voice(
        self, name: str, sample_path: str, is_default: bool = False
    ) -> VoiceSchema:
        with self.store.lock:
            voices = self._load_voices()
            is_first = len(voices) == 0
            should_be_default = is_default or is_first

            if should_be_default:
                for v in voices:
                    v.is_default = False

            new_voice = VoiceSchema(
                name=name,
                sample_path=sample_path,
                is_default=should_be_default,
            )
            voices.append(new_voice)
            self._save_voices(voices)
            return new_voice

    def set_default_voice(self, voice_id: str) -> bool:
        with self.store.lock:
            voices = self._load_voices()
            found = False
            for v in voices:
                if v.id == voice_id:
                    v.is_default = True
                    found = True
                else:
                    v.is_default = False

            if found:
                self._save_voices(voices)
            return found

    def delete_voice(self, voice_id: str, delete_file: bool = True) -> bool:
        with self.store.lock:
            voices = self._load_voices()
            target_idx = None
            for idx, v in enumerate(voices):
                if v.id == voice_id:
                    target_idx = idx
                    break

            if target_idx is None:
                return False

            deleted = voices.pop(target_idx)

            if delete_file and deleted.sample_path:
                p = Path(deleted.sample_path)
                if p.exists() and p.is_file():
                    try:
                        p.unlink()
                    except OSError:
                        pass

            if deleted.is_default and len(voices) > 0:
                voices[0].is_default = True

            self._save_voices(voices)
            return True


# Instância padrão singleton
voice_store = VoiceStore()
