from pathlib import Path
from typing import List, Optional, Union

from backend.config import HISTORY_FILE
from backend.models.schemas import HistoryItemSchema
from backend.storage.json_store import JSONStore


class HistoryStore:
    def __init__(self, file_path: Optional[Union[Path, str]] = None) -> None:
        self.file_path = Path(file_path) if file_path else HISTORY_FILE
        self.store = JSONStore(self.file_path)

    def _load_items(self) -> List[HistoryItemSchema]:
        data = self.store.read(default=[])
        if not isinstance(data, list):
            return []
        items = []
        for item in data:
            try:
                items.append(HistoryItemSchema.model_validate(item))
            except Exception:
                continue
        return items

    def _save_items(self, items: List[HistoryItemSchema]) -> None:
        self.store.write([it.model_dump() for it in items])

    def list_history(self) -> List[HistoryItemSchema]:
        with self.store.lock:
            items = self._load_items()
            # Ordenado por created_at decrescente
            return sorted(items, key=lambda x: x.created_at, reverse=True)

    def get_item(self, item_id: str) -> Optional[HistoryItemSchema]:
        with self.store.lock:
            for item in self._load_items():
                if item.id == item_id:
                    return item
            return None

    def add_item(self, item: HistoryItemSchema) -> HistoryItemSchema:
        with self.store.lock:
            items = self._load_items()
            items.append(item)
            self._save_items(items)
            return item

    def delete_item(self, item_id: str, delete_files: bool = True) -> bool:
        with self.store.lock:
            items = self._load_items()
            target_idx = None
            for idx, it in enumerate(items):
                if it.id == item_id:
                    target_idx = idx
                    break

            if target_idx is None:
                return False

            deleted = items.pop(target_idx)

            if delete_files:
                for file_path_str in (deleted.audio_path, deleted.srt_path):
                    if file_path_str:
                        p = Path(file_path_str)
                        if p.exists() and p.is_file():
                            try:
                                p.unlink()
                            except OSError:
                                pass

            self._save_items(items)
            return True

    def clear_all(self, delete_files: bool = True) -> int:
        with self.store.lock:
            items = self._load_items()
            count = len(items)

            if delete_files:
                for it in items:
                    for file_path_str in (it.audio_path, it.srt_path):
                        if file_path_str:
                            p = Path(file_path_str)
                            if p.exists() and p.is_file():
                                try:
                                    p.unlink()
                                except OSError:
                                    pass

            self._save_items([])
            return count


# Instância padrão singleton
history_store = HistoryStore()
