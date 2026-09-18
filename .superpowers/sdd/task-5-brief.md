# Task 5 Brief: Interface Web — Drawer de Logs em Tempo Real e Métricas

## Objetivo
Implementar o painel deslizante inferior (drawer DevTools) de logs em tempo real na interface web do Voxa, com conexão WebSocket, métricas dinâmicas de CPU/RAM, filtros por nível e texto, auto-scroll inteligente e botão flutuante persistente em toda a SPA.

## Arquivos a Criar / Modificar
- Criar: `frontend/js/components/log-drawer.js`
- Modificar: `frontend/index.html`
- Modificar: `frontend/css/style.css`
- Modificar: `frontend/js/app.js`
- Modificar: `tests/test_frontend.py`
- Relatório: `d:\Projetos\Voxa\.superpowers\sdd\task-5-report.md`

## Requisitos Técnicos

### 1. `frontend/index.html`
- Inserir o botão toggle de logs no rodapé (visível em qualquer página):
  ```html
  <button id="btn-toggle-logs" class="btn-toggle-logs" title="Abrir painel de logs e terminal em tempo real">
    <span class="log-icon">🖥️</span>
    <span class="log-btn-text">Terminal</span>
    <span id="log-error-badge" class="log-error-badge hidden">0</span>
  </button>
  ```
- Inserir a estrutura do Drawer de logs (fora do `<main id="main-content">`):
  ```html
  <div id="log-drawer" class="log-drawer collapsed">
    <div class="log-drawer-resize-handle" id="log-drawer-resize-handle"></div>
    <div class="log-drawer-header">
      <div class="log-header-title">
        <span>⚡ Terminal em Tempo Real</span>
        <div class="metrics-badges">
          <span class="metric-badge" id="metric-cpu">CPU: --%</span>
          <span class="metric-badge" id="metric-ram">RAM: -- GB (--%)</span>
        </div>
      </div>
      <div class="log-header-controls">
        <select id="log-level-filter" class="log-select">
          <option value="">Todos os Níveis</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="DEBUG">DEBUG</option>
        </select>
        <input type="text" id="log-search-input" class="log-search" placeholder="Filtrar logs..." />
        <button id="btn-autoscroll" class="log-ctrl-btn active" title="Pausar / Retomar Auto-Scroll">⬇ Auto-Scroll</button>
        <button id="btn-clear-logs" class="log-ctrl-btn" title="Limpar logs">🗑️ Limpar</button>
        <button id="btn-close-drawer" class="log-ctrl-btn close-btn" title="Minimizar painel">✕</button>
      </div>
    </div>
    <div class="log-drawer-body" id="log-entries-container">
      <!-- Linhas de logs injetadas dinamicamente -->
    </div>
  </div>
  ```

### 2. `frontend/css/style.css`
- Estilos para:
  - `.btn-toggle-logs`: fixo no canto inferior direito (`position: fixed; bottom: 20px; right: 24px; z-index: 990;`), fundo escuro elegante com borda e hover iluminado, badge vermelha de erro pulsante.
  - `.log-drawer`: fixo no rodapé (`position: fixed; bottom: 0; left: 240px; right: 0; z-index: 1000; height: 320px; transition: transform 0.25s ease; background: rgba(13, 17, 23, 0.96); backdrop-filter: blur(12px); border-top: 1px solid var(--border);`), classe `.collapsed` com `transform: translateY(100%); pointer-events: none;`.
  - `.log-drawer-resize-handle`: barra superior com cursor `ns-resize`.
  - `.log-drawer-header`: layout flex, botões compactos, mostradores de métricas com background sutil.
  - `.log-drawer-body`: tipografia `JetBrains Mono, monospace`, scrollbar escura estilizada, seleção de texto limpa.
  - `.log-entry`: layout com timestamp cinza, badge de level colorido (verde para INFO, amarelo para WARNING, vermelho para ERROR, ciano/cinza para DEBUG), source em roxo e texto da mensagem com quebra de linha preservada.

### 3. `frontend/js/components/log-drawer.js`
- Conexão WebSocket em `${protocol}//${window.location.host}/api/ws/logs`.
- Reconexão com retry automático.
- Renderização de linhas com sanitização anti-XSS (`escapeHtml`).
- Lógica de auto-scroll (desativa se usuário sobe o scroll, reativa ao clicar no botão ou descer até o fim).
- Filtros por nível e texto em memória.
- Métricas atualizadas no DOM quando evento do tipo `"metrics"` for recebido.
- Persistência no `localStorage` (`voxa_log_drawer_open` e `voxa_log_drawer_height`).

### 4. `frontend/js/app.js`
- Importar e inicializar `initLogDrawer()`.

### 5. `tests/test_frontend.py`
- Adicionar asserções verificando que `index.html` contém `#log-drawer`, `#btn-toggle-logs`, e que `log-drawer.js` existe e é referenciado ou importado no frontend.
- Rodar `.venv\Scripts\python.exe -m pytest tests/test_frontend.py -v`.
- Rodar a suíte inteira de 130 testes para garantir que tudo continue passando.
- Fazer commit git: `feat(ui): implement real-time log drawer with system metrics and devtools style`.
