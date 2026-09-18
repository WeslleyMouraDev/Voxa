# Painel de Logs em Tempo Real + API REST Completa + Métricas de Sistema

## Visão Geral

Adicionar ao Voxa:
1. **Painel de logs em tempo real** — drawer inferior (estilo DevTools) acessível em qualquer página da SPA
2. **API REST completa documentada** — todas as funcionalidades da UI com endpoints REST equivalentes e Swagger UI interativo
3. **Métricas do sistema** — CPU e RAM em tempo real no painel de logs

## Arquitetura

### Captura de Logs — Abordagem Híbrida

Dois mecanismos complementares que alimentam o mesmo ring buffer:

1. **Python logging handler** (`LogBufferHandler(logging.Handler)`) — intercepta logs estruturados do Python/uvicorn com nível (INFO, WARNING, ERROR, DEBUG), source, timestamp
2. **stdout/stderr redirect** (`StreamInterceptor`) — tee objects que duplicam output para console original + buffer; captura prints de libs C (Chatterbox, Faster Whisper) como nível INFO genérico

### Armazenamento

- `collections.deque(maxlen=1000)` — ring buffer em memória
- Cada entry: `{ id, timestamp, level, message, source }`
- Sem persistência em disco — logs perdidos ao reiniciar

### Transporte

- **WebSocket** `/api/ws/logs` — streaming bidirecional em tempo real
  - Ao conectar: envia histórico completo do buffer como batch
  - Em seguida: cada nova linha de log é enviada imediatamente
  - Métricas CPU/RAM enviadas a cada 2 segundos como mensagens separadas
  - Suporta múltiplos clientes simultâneos
- **REST** `GET /api/logs` — busca histórico do buffer com filtros opcionais (`level`, `search`, `limit`)
- **REST** `GET /api/system/metrics` — snapshot único de CPU/RAM
- **REST** `DELETE /api/logs` — limpa o buffer

### Coleta de Métricas

- `psutil` para CPU percent e RAM usage
- Task asyncio em background que coleta a cada 2 segundos
- Broadcast para todos os WebSocket clients conectados

## Frontend — Drawer de Logs

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [Sidebar]  │              Main Content                     │
│             │                                               │
│             │                                               │
│             │                                               │
│             ├───────────────────────────────────────────────┤
│             │ ▲ LOGS  [CPU: 23%] [RAM: 4.2GB]  [🔍] [🗑️] │
│             │ 12:34:05 INFO  Modelo carregado com sucesso   │
│             │ 12:34:06 INFO  POST /api/narrate 202          │
│             │ 12:34:07 WARN  CPU usage alto: 89%            │
│             │ 12:34:08 ERROR Falha na conexão WebSocket     │
│             └───────────────────────────────────────────────┘
```

### Comportamento

- **Toggle:** botão fixo no canto inferior direito com ícone de terminal (🖥️) + badge com contagem de erros
- **Drawer:** 300px de altura padrão, redimensionável verticalmente via drag handle
- **Auto-scroll:** scroll automático para novas linhas, pausado quando o usuário scrollar manualmente para cima
- **Filtros:** dropdown de nível (ALL/DEBUG/INFO/WARNING/ERROR) + campo de busca por texto
- **Limpar:** botão para esvaziar o buffer visual (não afeta o backend)
- **Métricas:** badges de CPU e RAM no header do drawer, atualizados em tempo real via WebSocket
- **Cores por nível:** DEBUG=cinza, INFO=verde, WARNING=amarelo, ERROR=vermelho
- **Fonte:** JetBrains Mono (já carregada no projeto)

### Persistência Visual

- Estado do drawer (aberto/fechado, altura) salvo em `localStorage`
- Drawer NÃO é uma rota — é um componente global que vive fora do `#main-content`

## API REST Completa

### Endpoints Existentes (enriquecer com descrições PT-BR no Swagger)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/settings` | Retorna configurações atuais |
| PUT | `/api/settings` | Atualiza configurações |
| GET | `/api/voices` | Lista todas as vozes |
| POST | `/api/voices` | Cadastra nova voz |
| PUT | `/api/voices/{id}/default` | Define voz padrão |
| DELETE | `/api/voices/{id}` | Exclui voz |
| GET | `/api/history` | Lista histórico de gerações |
| DELETE | `/api/history/{id}` | Exclui item do histórico |
| DELETE | `/api/history` | Limpa todo o histórico |
| POST | `/api/narrate` | Inicia narração (async, retorna task_id) |
| POST | `/api/narrate-and-transcribe` | Narração + transcrição (async) |
| POST | `/api/transcribe` | Transcrição de áudio (async) |
| GET | `/api/progress/{task_id}` | SSE de progresso da tarefa |

### Novos Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| WS | `/api/ws/logs` | WebSocket de logs + métricas em tempo real |
| GET | `/api/logs` | Histórico de logs do buffer (query: `level`, `search`, `limit`) |
| DELETE | `/api/logs` | Limpa buffer de logs |
| GET | `/api/system/metrics` | Snapshot de CPU e RAM |

### Página #api-docs na Interface Web

- Nova rota `#api-docs` na SPA (sem link na sidebar — acessível via URL direta ou link no footer)
- Exibe iframe ou link para o Swagger UI (`/docs`)
- Lista organizada dos endpoints com exemplos de uso via `curl`
- Agrupados por categoria: Narração, Transcrição, Vozes, Histórico, Configurações, Logs, Sistema

## Arquivos a Criar

### Backend

| Arquivo | Propósito |
|---------|-----------|
| `backend/services/log_service.py` | LogBufferHandler, StreamInterceptor, ring buffer, WebSocket broadcast |
| `backend/services/metrics_service.py` | Coleta de CPU/RAM via psutil, task asyncio |
| `backend/routers/logs.py` | Endpoints REST de logs + WebSocket |
| `backend/routers/system.py` | Endpoint de métricas |

### Frontend

| Arquivo | Propósito |
|---------|-----------|
| `frontend/js/components/log-drawer.js` | Drawer de logs com auto-scroll, filtros, métricas |
| `frontend/js/pages/api-docs.js` | Página #api-docs com documentação dos endpoints |

### Arquivos a Modificar

| Arquivo | Mudança |
|---------|---------|
| `backend/main.py` | Registrar routers de logs/system, inicializar log capture no startup |
| `frontend/index.html` | Adicionar container do drawer de logs fora do main-content |
| `frontend/js/app.js` | Importar log-drawer, adicionar rota #api-docs, inicializar drawer |
| `frontend/css/style.css` | Estilos do drawer, cores por nível, animações |
| `requirements.txt` | Adicionar `psutil` |

## Protocolo WebSocket `/api/ws/logs`

### Mensagens Server → Client

```json
// Log entry
{
  "type": "log",
  "data": {
    "id": 42,
    "timestamp": "2026-09-18T12:34:05.123Z",
    "level": "INFO",
    "message": "POST /api/narrate 202 Accepted",
    "source": "uvicorn.access"
  }
}

// Batch (ao conectar)
{
  "type": "log_batch",
  "data": [/* array de log entries */]
}

// Métricas
{
  "type": "metrics",
  "data": {
    "cpu_percent": 23.5,
    "ram_used_gb": 4.2,
    "ram_total_gb": 16.0,
    "ram_percent": 26.3
  }
}

// Buffer limpo
{
  "type": "logs_cleared"
}
```

### Mensagens Client → Server

```json
// Limpar buffer
{ "action": "clear_logs" }
```

## Testes

| Arquivo de Teste | Cobertura |
|------------------|-----------|
| `tests/test_log_service.py` | Ring buffer, handler, interceptor, broadcast |
| `tests/test_metrics_service.py` | Coleta CPU/RAM, formato de dados |
| `tests/test_logs_api.py` | REST GET/DELETE logs, filtros, WebSocket |

## Dependências Novas

- `psutil>=5.9.0` — métricas de CPU/RAM (já é dependência do Chatterbox, zero overhead)

> **Nota:** FastAPI já suporta WebSocket nativamente — `websockets` é dependência transitiva do `uvicorn[standard]`, não precisa ser adicionado explicitamente.
