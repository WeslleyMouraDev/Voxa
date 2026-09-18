from typing import Any, Dict
import psutil


class MetricsService:
    """
    Serviço de coleta de métricas de sistema em tempo real (CPU e RAM).
    """

    @classmethod
    def get_current_metrics(cls) -> Dict[str, Any]:
        """
        Coleta e retorna as métricas atuais de CPU e memória RAM.
        """
        cpu_percent = float(psutil.cpu_percent(interval=None))
        mem = psutil.virtual_memory()

        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_total_gb = round(mem.total / (1024 ** 3), 2)
        ram_percent = float(mem.percent)

        return {
            "cpu_percent": cpu_percent,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "ram_percent": ram_percent,
        }
