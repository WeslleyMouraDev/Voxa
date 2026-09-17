from typing import List

from fastapi import APIRouter, HTTPException

from backend.models.schemas import HistoryItemSchema
from backend.storage.history_store import history_store

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=List[HistoryItemSchema])
def list_history() -> List[HistoryItemSchema]:
    """Retorna o histórico ordenado de gerações realizadas."""
    return history_store.list_history()


@router.delete("/{item_id}")
def delete_history_item(item_id: str) -> dict:
    """Exclui um item do histórico e remove os arquivos de áudio e legenda do disco."""
    success = history_store.delete_item(item_id, delete_files=True)
    if not success:
        raise HTTPException(status_code=404, detail="Item de histórico não encontrado")
    return {"message": "Item excluído com sucesso"}


@router.delete("")
def clear_all_history() -> dict:
    """Limpa todo o histórico e apaga todos os arquivos gerados associados."""
    deleted_count = history_store.clear_all(delete_files=True)
    return {"message": "Histórico limpo com sucesso", "deleted_count": deleted_count}
