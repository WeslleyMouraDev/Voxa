# Task 2 Report: Limitador de Recursos de CPU e Gerenciador de Tarefas em Background (SSE)

## Status: Concluído com Sucesso

### 1. Implementações Realizadas
- `backend/services/__init__.py`: Exportação dos serviços `CPULimiter`, `TaskManager` e instância singleton `task_manager`.
- `backend/services/cpu_limiter.py`:
  - Cálculo proporcional de threads de CPU baseado em percentual (`calculate_threads`), garantindo mínimo de 1 thread e respeitando `os.cpu_count()`.
  - Configuração de threads no PyTorch (`torch.set_num_threads`) com tratamento de exceção gracioso caso indisponível.
  - Ajuste de prioridade do processo operacional para abaixo do normal (`psutil.BELOW_NORMAL_PRIORITY_CLASS` no Windows e `nice(10)` em POSIX) prevenindo travamento do SO.
- `backend/services/task_manager.py`:
  - Gerenciador singleton `TaskManager` com ciclo de vida completo (`create_task`, `update_progress`, `complete_task`, `fail_task`, `get_task`).
  - Suporte a múltiplos ouvintes assíncronos via `subscribe` com `asyncio.Queue`, compatível com streaming SSE e encerramento limpo.

### 2. Testes e Validação TDD
- `tests/test_cpu_limiter.py`:
  - 5 testes cobrindo cálculo de threads (25%, 50%, 75%, 100%, 1 core, `cpu_count=None`), integração com Windows e POSIX, mock de PyTorch e tratamento de erros de permissão.
- `tests/test_task_manager.py`:
  - 7 testes assíncronos cobrindo criação, atualização de progresso, conclusão com payload, falha, ciclo completo de SSE, múltiplos ouvintes paralelos.
- **Resultado dos Testes**: 19/19 testes passaram com 100% de sucesso em toda a suíte do projeto (`pytest tests/ -v`).
