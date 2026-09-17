from pathlib import Path
from typing import Optional, Union

from backend.config import SETTINGS_FILE
from backend.models.schemas import SettingsSchema
from backend.storage.json_store import JSONStore


class SettingsStore:
    def __init__(self, file_path: Optional[Union[Path, str]] = None) -> None:
        self.file_path = Path(file_path) if file_path else SETTINGS_FILE
        self.store = JSONStore(self.file_path)

    def get_settings(self) -> SettingsSchema:
        with self.store.lock:
            data = self.store.read(default=None)
            if not isinstance(data, dict):
                default_settings = SettingsSchema()
                self.store.write(default_settings.model_dump())
                return default_settings
            try:
                return SettingsSchema.model_validate(data)
            except Exception:
                default_settings = SettingsSchema()
                self.store.write(default_settings.model_dump())
                return default_settings

    def update_settings(
        self, updates: Union[dict, SettingsSchema]
    ) -> SettingsSchema:
        with self.store.lock:
            current = self.get_settings()
            if isinstance(updates, SettingsSchema):
                merged_data = updates.model_dump()
            elif isinstance(updates, dict):
                merged_data = current.model_dump()
                merged_data.update(updates)
            else:
                raise ValueError("updates must be a dict or SettingsSchema")

            validated = SettingsSchema.model_validate(merged_data)
            self.store.write(validated.model_dump())
            return validated


# Instância padrão singleton
settings_store = SettingsStore()
