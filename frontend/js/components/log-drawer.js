/**
 * Voxa DevTools Log Drawer Component
 * Gerenciamento de painel deslizante de logs em tempo real via WebSocket (/api/ws/logs),
 * métricas de CPU/RAM de hardware, auto-scroll, filtros e redimensionamento manual.
 */

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatTimestamp(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return isoStr;
    const pad = (n) => String(n).padStart(2, '0');
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  } catch {
    return isoStr;
  }
}

export function initLogDrawer() {
  const drawer = document.getElementById('log-drawer');
  const toggleBtn = document.getElementById('btn-toggle-logs');
  const errorBadge = document.getElementById('log-error-badge');
  const resizeHandle = document.getElementById('log-drawer-resize-handle');
  const entriesContainer = document.getElementById('log-entries-container');
  const cpuMetric = document.getElementById('metric-cpu');
  const ramMetric = document.getElementById('metric-ram');
  const levelFilter = document.getElementById('log-level-filter');
  const searchInput = document.getElementById('log-search-input');
  const autoscrollBtn = document.getElementById('btn-autoscroll');
  const clearBtn = document.getElementById('btn-clear-logs');
  const closeBtn = document.getElementById('btn-close-drawer');

  if (!drawer || !toggleBtn || !entriesContainer) {
    return;
  }

  // Estado local do componente
  let logs = [];
  let autoScroll = true;
  let unreadErrors = 0;
  let currentLevelFilter = '';
  let currentSearch = '';
  let ws = null;
  let reconnectTimer = null;
  const MAX_LOGS = 1000;

  // 1. Restauração de altura e estado do localStorage
  const savedHeight = localStorage.getItem('voxa_log_drawer_height');
  if (savedHeight) {
    drawer.style.height = savedHeight;
  }

  const isInitiallyOpen = localStorage.getItem('voxa_log_drawer_open') === 'true';
  if (isInitiallyOpen) {
    openDrawer();
  } else {
    closeDrawer();
  }

  function openDrawer() {
    drawer.classList.remove('collapsed');
    unreadErrors = 0;
    if (errorBadge) {
      errorBadge.textContent = '0';
      errorBadge.classList.add('hidden');
    }
    localStorage.setItem('voxa_log_drawer_open', 'true');
    if (autoScroll) {
      scrollToBottom();
    }
  }

  function closeDrawer() {
    drawer.classList.add('collapsed');
    localStorage.setItem('voxa_log_drawer_open', 'false');
  }

  function toggleDrawer() {
    if (drawer.classList.contains('collapsed')) {
      openDrawer();
    } else {
      closeDrawer();
    }
  }

  toggleBtn.addEventListener('click', toggleDrawer);
  if (closeBtn) {
    closeBtn.addEventListener('click', closeDrawer);
  }

  // 2. Redimensionamento via drag no handle
  if (resizeHandle) {
    let isResizing = false;
    let startY = 0;
    let startHeight = 0;

    const onMouseDown = (e) => {
      isResizing = true;
      startY = e.clientY;
      startHeight = drawer.offsetHeight;
      resizeHandle.classList.add('active');
      document.body.style.userSelect = 'none';
      document.body.style.cursor = 'ns-resize';
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (e) => {
      if (!isResizing) return;
      const deltaY = startY - e.clientY;
      const newHeight = Math.max(160, Math.min(window.innerHeight - 60, startHeight + deltaY));
      drawer.style.height = `${newHeight}px`;
    };

    const onMouseUp = () => {
      if (!isResizing) return;
      isResizing = false;
      resizeHandle.classList.remove('active');
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      localStorage.setItem('voxa_log_drawer_height', drawer.style.height);
    };

    resizeHandle.addEventListener('mousedown', onMouseDown);
  }

  // 3. Renderização e filtros
  function matchFilter(entry) {
    if (currentLevelFilter && entry.level !== currentLevelFilter) {
      return false;
    }
    if (currentSearch) {
      const term = currentSearch.toLowerCase();
      const msgMatch = entry.message && entry.message.toLowerCase().includes(term);
      const srcMatch = entry.source && entry.source.toLowerCase().includes(term);
      if (!msgMatch && !srcMatch) return false;
    }
    return true;
  }

  function createLogNode(entry) {
    const row = document.createElement('div');
    const levelClass = entry.level ? `level-${entry.level.toLowerCase()}` : '';
    row.className = `log-entry ${levelClass}`;

    const timeStr = formatTimestamp(entry.timestamp);
    const lvl = entry.level || 'INFO';
    const src = entry.source || 'app';

    row.innerHTML = `
      <span class="log-time">${timeStr ? `[${escapeHtml(timeStr)}]` : ''}</span>
      <span class="log-level-badge log-level-${escapeHtml(lvl)}">${escapeHtml(lvl)}</span>
      <span class="log-source">[${escapeHtml(src)}]</span>
      <span class="log-msg">${escapeHtml(entry.message)}</span>
    `;
    return row;
  }

  function renderAllLogs() {
    entriesContainer.innerHTML = '';
    const filtered = logs.filter(matchFilter);
    if (filtered.length === 0) {
      entriesContainer.innerHTML = '<div class="log-empty-msg">Nenhum registro de log para os filtros selecionados.</div>';
      return;
    }

    const fragment = document.createDocumentFragment();
    for (const entry of filtered) {
      fragment.appendChild(createLogNode(entry));
    }
    entriesContainer.appendChild(fragment);

    if (autoScroll) {
      scrollToBottom();
    }
  }

  function appendLogEntry(entry) {
    logs.push(entry);
    if (logs.length > MAX_LOGS) {
      logs.shift();
    }

    // Alerta de erro com drawer fechado
    if (drawer.classList.contains('collapsed') && entry.level === 'ERROR') {
      unreadErrors++;
      if (errorBadge) {
        errorBadge.textContent = String(unreadErrors);
        errorBadge.classList.remove('hidden');
      }
    }

    if (matchFilter(entry)) {
      // Se estava exibindo mensagem vazia, limpa
      const emptyMsg = entriesContainer.querySelector('.log-empty-msg');
      if (emptyMsg) {
        entriesContainer.innerHTML = '';
      }

      entriesContainer.appendChild(createLogNode(entry));

      // Limita elementos no DOM para manter excelente performance
      while (entriesContainer.children.length > MAX_LOGS) {
        entriesContainer.removeChild(entriesContainer.firstElementChild);
      }

      if (autoScroll) {
        scrollToBottom();
      }
    }
  }

  function scrollToBottom() {
    entriesContainer.scrollTop = entriesContainer.scrollHeight;
  }

  // 4. Controles de Auto-Scroll
  function updateAutoScrollState(active) {
    autoScroll = active;
    if (autoscrollBtn) {
      if (active) {
        autoscrollBtn.classList.add('active');
      } else {
        autoscrollBtn.classList.remove('active');
      }
    }
  }

  if (autoscrollBtn) {
    autoscrollBtn.addEventListener('click', () => {
      const nextState = !autoScroll;
      updateAutoScrollState(nextState);
      if (nextState) {
        scrollToBottom();
      }
    });
  }

  entriesContainer.addEventListener('scroll', () => {
    const threshold = 35;
    const atBottom =
      entriesContainer.scrollHeight - entriesContainer.scrollTop - entriesContainer.clientHeight <= threshold;
    if (!atBottom && autoScroll) {
      updateAutoScrollState(false);
    } else if (atBottom && !autoScroll) {
      updateAutoScrollState(true);
    }
  });

  // 5. Filtros de Nível e Busca Textual
  if (levelFilter) {
    levelFilter.addEventListener('change', (e) => {
      currentLevelFilter = e.target.value.trim().toUpperCase();
      renderAllLogs();
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value.trim();
      renderAllLogs();
    });
  }

  // 6. Limpar Logs
  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'clear_logs' }));
      }
      try {
        await fetch('/api/logs', { method: 'DELETE' });
      } catch {
        // Silencioso se falhar
      }
      logs = [];
      renderAllLogs();
    });
  }

  // 7. Conexão WebSocket com reconexão resiliente
  function connectWebSocket() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || 'localhost:8000';
    const wsUrl = `${protocol}//${host}/api/ws/logs`;

    try {
      ws = new WebSocket(wsUrl);
    } catch {
      scheduleReconnect();
      return;
    }

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const type = payload.type;

        if (type === 'metrics' && payload.data) {
          const m = payload.data;
          if (cpuMetric && typeof m.cpu_percent === 'number') {
            cpuMetric.textContent = `CPU: ${m.cpu_percent.toFixed(1)}%`;
            if (m.cpu_percent > 85) {
              cpuMetric.classList.add('highlight');
            } else {
              cpuMetric.classList.remove('highlight');
            }
          }
          if (ramMetric && typeof m.ram_used_gb === 'number') {
            const pct = typeof m.ram_percent === 'number' ? ` (${m.ram_percent.toFixed(0)}%)` : '';
            ramMetric.textContent = `RAM: ${m.ram_used_gb.toFixed(1)} GB${pct}`;
          }
        } else if (type === 'log_batch' && Array.isArray(payload.data)) {
          logs = payload.data.slice(-MAX_LOGS);
          renderAllLogs();
        } else if (type === 'log') {
          const entry = payload.data || payload;
          if (entry && entry.message) {
            appendLogEntry(entry);
          }
        } else if (type === 'logs_cleared') {
          logs = [];
          renderAllLogs();
        }
      } catch (err) {
        console.warn('Erro ao processar mensagem do WebSocket de logs:', err);
      }
    };

    ws.onclose = () => {
      scheduleReconnect();
    };

    ws.onerror = () => {
      if (ws) ws.close();
    };
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connectWebSocket();
    }, 3000);
  }

  connectWebSocket();
}
