import os
import psutil
from typing import Any, Dict


class CPULimiter:
    """
    Gerencia o uso de recursos de CPU limitando a contagem de threads do PyTorch
    e ajustando a prioridade do processo operacional para evitar travamentos da máquina.
    """

    @staticmethod
    def calculate_threads(cpu_percent: int) -> int:
        """
        Calcula a quantidade de threads baseando-se na porcentagem de CPU informada.
        Garante no mínimo 1 thread.
        """
        total_cores = os.cpu_count() or 1
        pct = max(0, min(100, cpu_percent))
        return max(1, int(total_cores * (pct / 100.0)))

    def apply_limits(self, cpu_percent: int = 75) -> Dict[str, Any]:
        """
        Aplica os limites calculados de CPU:
        - Define número de threads no PyTorch se disponível
        - Reduz a prioridade de execução do processo atual para não congelar o SO
        """
        total_cores = os.cpu_count() or 1
        n_threads = self.calculate_threads(cpu_percent)

        # 1. Configurar threads do PyTorch
        try:
            import torch
            torch.set_num_threads(n_threads)
        except Exception:
            pass

        # 2. Ajustar prioridade de processo (nice)
        nice_applied = False
        try:
            p = psutil.Process()
            if os.name == "nt":
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            else:
                p.nice(10)
            nice_applied = True
        except Exception:
            nice_applied = False

        return {
            "cpu_percent": cpu_percent,
            "threads": n_threads,
            "total_cores": total_cores,
            "nice_applied": nice_applied,
        }
