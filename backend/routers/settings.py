from fastapi import APIRouter

from backend.models.schemas import SettingsSchema
from backend.services.cpu_limiter import CPULimiter
from backend.storage.settings_store import settings_store

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsSchema)
def get_settings() -> SettingsSchema:
    """Retorna as configurações atuais da aplicação."""
    return settings_store.get_settings()


@router.put("", response_model=SettingsSchema)
def update_settings(new_settings: SettingsSchema) -> SettingsSchema:
    """
    Atualiza as configurações da aplicação e aplica o novo limite de CPU.
    """
    updated = settings_store.update_settings(new_settings)
    cpu_limiter = CPULimiter()
    cpu_limiter.apply_limits(updated.cpu_percent)
    return updated
