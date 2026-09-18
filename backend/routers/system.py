from fastapi import APIRouter

from backend.models.schemas import SystemMetricsSchema
from backend.services.metrics_service import MetricsService

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/metrics", response_model=SystemMetricsSchema)
def get_system_metrics() -> SystemMetricsSchema:
    """
    Retorna as métricas atuais de recursos do sistema:
    - Percentual de uso de CPU
    - Memória RAM utilizada (GB)
    - Memória RAM total (GB)
    - Percentual de uso de RAM
    """
    return MetricsService.get_current_metrics()
