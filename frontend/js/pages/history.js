/**
 * Voxa History Page
 * Visualização, reprodução, download e gerenciamento de arquivos gerados.
 */

import { api } from '../api.js';
import { stateManager } from '../state.js';
import { showToast } from '../components/toast.js';
import { showConfirmModal } from '../components/modal.js';

export async function renderHistoryPage(container) {
  container.innerHTML = `
    <div class="page-container">
      <div class="page-header">
        <div>
          <h1 class="page-title"><span>📋</span> Histórico de Gerações</h1>
          <p class="page-subtitle">Acesse, reproduza e faça o download de todas as narrações e legendas geradas.</p>
        </div>
        <button id="btn-clear-all-history" class="btn btn-danger" style="display: none;">
          <span>🗑</span> Limpar Histórico Completo
        </button>
      </div>

      <div id="history-items-container">
        <div style="text-align: center; color: var(--text-muted); padding: 40px;">Carregando histórico...</div>
      </div>
    </div>
  `;

  setupHistoryEvents(container);
  await loadAndRenderHistory(container);
}

function setupHistoryEvents(container) {
  const btnClearAll = container.querySelector('#btn-clear-all-history');

  btnClearAll.addEventListener('click', () => {
    showConfirmModal({
      title: 'Limpar Todo o Histórico',
      message: 'Tem certeza que deseja apagar todos os registros do histórico e excluir os arquivos de áudio e legendas gerados do disco? Essa ação não pode ser desfeita.',
      confirmText: 'Limpar Tudo',
      danger: true,
      onConfirm: async () => {
        try {
          const result = await api.clearAllHistory();
          showToast(result.message || 'Histórico completamente apagado.', 'success');
          await loadAndRenderHistory(container);
        } catch (err) {
          showToast(`Erro ao limpar histórico: ${err.message}`, 'error');
        }
      },
    });
  });
}

async function loadAndRenderHistory(container) {
  try {
    const history = await api.getHistory();
    stateManager.setHistory(history);
    renderHistoryList(container, history);
  } catch (err) {
    showToast(`Erro ao carregar histórico: ${err.message}`, 'error');
  }
}

function renderHistoryList(container, history) {
  const itemsContainer = container.querySelector('#history-items-container');
  const btnClearAll = container.querySelector('#btn-clear-all-history');
  if (!itemsContainer) return;

  if (history.length === 0) {
    if (btnClearAll) btnClearAll.style.display = 'none';
    itemsContainer.innerHTML = `
      <div class="card" style="text-align: center; padding: 48px 24px;">
        <div style="font-size: 40px; margin-bottom: 12px;">📁</div>
        <h3 style="font-size: 18px; margin-bottom: 8px;">Nenhuma geração no histórico</h3>
        <p style="color: var(--text-secondary); max-width: 460px; margin: 0 auto 20px auto;">
          Gere uma narração na aba Estúdio para vê-la listada aqui com opções de reprodução e download de MP3 e SRT.
        </p>
        <a href="#narrate" class="btn btn-primary">Ir para o Estúdio</a>
      </div>
    `;
    return;
  }

  if (btnClearAll) btnClearAll.style.display = 'inline-flex';

  itemsContainer.innerHTML = `
    <div class="history-list">
      ${history.map(item => createHistoryCardHtml(item)).join('')}
    </div>
  `;

  history.forEach(item => {
    const deleteBtn = itemsContainer.querySelector(`#delete-history-${item.id}`);
    if (deleteBtn) {
      deleteBtn.addEventListener('click', () => {
        showConfirmModal({
          title: 'Excluir Item do Histórico',
          message: 'Deseja excluir permanentemente este registro e os arquivos de áudio/legenda associados?',
          confirmText: 'Excluir',
          danger: true,
          onConfirm: async () => {
            try {
              await api.deleteHistoryItem(item.id);
              showToast('Item do histórico excluído.', 'success');
              await loadAndRenderHistory(container);
            } catch (err) {
              showToast(`Erro ao excluir item: ${err.message}`, 'error');
            }
          },
        });
      });
    }
  });
}

function createHistoryCardHtml(item) {
  const audioSrc = resolveOutputUrl(item.audio_path);
  const srtSrc = item.srt_path ? resolveOutputUrl(item.srt_path) : null;
  const formattedDate = formatDate(item.created_at);

  const modeBadge = item.mode
    ? `<span class="badge-lang">${escapeHtml(item.mode.toUpperCase())}</span>`
    : '';

  const durationText = item.duration_seconds > 0
    ? `<span style="font-family: var(--font-mono); color: var(--text-muted);">⏱ ${item.duration_seconds.toFixed(1)}s</span>`
    : '';

  return `
    <div class="history-card" id="history-card-${item.id}">
      <div class="history-meta">
        <div class="history-badges">
          <span style="font-weight: 600; color: #ffffff;">🎙 ${escapeHtml(item.voice_name || 'Voz')}</span>
          ${modeBadge}
          ${durationText}
        </div>
        <span class="history-timestamp">${formattedDate}</span>
      </div>

      <div class="history-text">
        "${escapeHtml(item.text)}"
      </div>

      <div class="audio-player-wrapper" style="margin: 4px 0;">
        <audio controls preload="none" src="${audioSrc}"></audio>
      </div>

      <div class="history-actions">
        <div style="display: flex; gap: 10px;">
          <a href="${audioSrc}" download class="btn btn-secondary" style="padding: 7px 14px; font-size: 13px;">
            <span>⬇</span> MP3
          </a>
          ${
            srtSrc
              ? `<a href="${srtSrc}" download class="btn btn-secondary" style="padding: 7px 14px; font-size: 13px;">
                   <span>⬇</span> SRT
                 </a>`
              : ''
          }
        </div>

        <button id="delete-history-${item.id}" class="btn btn-outline-danger btn-icon" title="Excluir Item">
          🗑
        </button>
      </div>
    </div>
  `;
}

function resolveOutputUrl(path) {
  if (!path) return '';
  if (path.startsWith('http') || path.startsWith('/')) {
    return path;
  }
  const filename = path.replace(/\\/g, '/').split('/').pop();
  return `/output/${encodeURIComponent(filename)}`;
}

function formatDate(isoString) {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (_) {
    return isoString;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
