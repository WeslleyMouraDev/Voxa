/**
 * Voxa Voices Page
 * Gerenciamento e clonagem de vozes de referência.
 */

import { api } from '../api.js';
import { stateManager } from '../state.js';
import { showToast } from '../components/toast.js';
import { showConfirmModal, showCustomModal } from '../components/modal.js';

export async function renderVoicesPage(container) {
  container.innerHTML = `
    <div class="page-container">
      <div class="page-header">
        <div>
          <h1 class="page-title"><span>🗣</span> Vozes Clonadas</h1>
          <p class="page-subtitle">Gerencie suas vozes de referência para síntese neural em português.</p>
        </div>
        <button id="btn-add-voice" class="btn btn-primary">
          <span>+</span> Adicionar Nova Voz
        </button>
      </div>

      <div id="voices-list-container">
        <div style="text-align: center; color: var(--text-muted); padding: 40px;">Carregando vozes...</div>
      </div>
    </div>
  `;

  setupVoicesEvents(container);
  await loadAndRenderVoices(container);
}

function setupVoicesEvents(container) {
  const btnAddVoice = container.querySelector('#btn-add-voice');

  btnAddVoice.addEventListener('click', () => {
    openAddVoiceModal(container);
  });
}

async function loadAndRenderVoices(container) {
  try {
    const voices = await api.getVoices();
    stateManager.setVoices(voices);
    renderVoicesList(container, voices);
  } catch (err) {
    showToast(`Erro ao carregar vozes: ${err.message}`, 'error');
  }
}

function renderVoicesList(container, voices) {
  const listContainer = container.querySelector('#voices-list-container');
  if (!listContainer) return;

  if (voices.length === 0) {
    listContainer.innerHTML = `
      <div class="card" style="text-align: center; padding: 48px 24px;">
        <div style="font-size: 40px; margin-bottom: 12px;">🎙</div>
        <h3 style="font-size: 18px; margin-bottom: 8px;">Nenhuma voz cadastrada ainda</h3>
        <p style="color: var(--text-secondary); max-width: 480px; margin: 0 auto 20px auto;">
          Envie uma amostra de áudio (de 5 a 30 segundos) de uma voz limpa para clonagem instantânea.
        </p>
        <button id="btn-empty-add-voice" class="btn btn-primary">
          Cadastrar Primeira Voz
        </button>
      </div>
    `;

    const emptyAddBtn = listContainer.querySelector('#btn-empty-add-voice');
    if (emptyAddBtn) {
      emptyAddBtn.addEventListener('click', () => openAddVoiceModal(container));
    }
    return;
  }

  listContainer.innerHTML = `
    <div class="voices-grid">
      ${voices.map(voice => createVoiceCardHtml(voice)).join('')}
    </div>
  `;

  // Eventos nos cards
  voices.forEach(voice => {
    const starBtn = listContainer.querySelector(`#star-voice-${voice.id}`);
    const deleteBtn = listContainer.querySelector(`#delete-voice-${voice.id}`);

    if (starBtn) {
      starBtn.addEventListener('click', async () => {
        try {
          await api.setDefaultVoice(voice.id);
          showToast(`"${voice.name}" agora é a voz padrão!`, 'success');
          await loadAndRenderVoices(container);
        } catch (err) {
          showToast(`Erro ao definir voz padrão: ${err.message}`, 'error');
        }
      });
    }

    if (deleteBtn) {
      deleteBtn.addEventListener('click', () => {
        showConfirmModal({
          title: 'Excluir Voz',
          message: `Tem certeza que deseja excluir a voz "${voice.name}"? O arquivo de áudio de referência também será apagado.`,
          confirmText: 'Excluir Voz',
          danger: true,
          onConfirm: async () => {
            try {
              await api.deleteVoice(voice.id);
              showToast(`Voz "${voice.name}" excluída.`, 'success');
              await loadAndRenderVoices(container);
            } catch (err) {
              showToast(`Erro ao excluir voz: ${err.message}`, 'error');
            }
          },
        });
      });
    }
  });
}

function createVoiceCardHtml(voice) {
  const audioSrc = resolveVoiceSampleUrl(voice.sample_path);
  const isDefault = voice.is_default;

  return `
    <div class="voice-card ${isDefault ? 'is-default' : ''}">
      <div class="voice-card-header">
        <div class="voice-card-name">
          <span>${escapeHtml(voice.name)}</span>
          ${isDefault ? '<span class="badge-lang">PADRÃO</span>' : ''}
        </div>
        <button
          id="star-voice-${voice.id}"
          class="star-btn ${isDefault ? 'active' : ''}"
          title="${isDefault ? 'Voz padrão atual' : 'Definir como voz padrão'}"
          aria-label="Definir como padrão"
        >
          ★
        </button>
      </div>

      <div class="audio-player-wrapper">
        <audio controls preload="none" src="${audioSrc}"></audio>
      </div>

      <div class="voice-card-footer">
        <span class="form-hint" style="font-family: var(--font-mono);">ID: ${voice.id.slice(0, 8)}...</span>
        <button
          id="delete-voice-${voice.id}"
          class="btn btn-outline-danger btn-icon"
          title="Excluir Voz"
        >
          🗑
        </button>
      </div>
    </div>
  `;
}

function openAddVoiceModal(container) {
  const modalContent = `
    <form id="add-voice-form" style="display: flex; flex-direction: column; gap: 16px;">
      <div class="form-group" style="margin-bottom: 0;">
        <label class="form-label" for="new-voice-name">Nome / Apelido da Voz *</label>
        <input type="text" id="new-voice-name" class="input-text" placeholder="Ex: Narrador Épico, Maria Clara" required />
      </div>

      <div class="form-group" style="margin-bottom: 0;">
        <label class="form-label" for="new-voice-file">Áudio de Amostra (WAV, MP3) *</label>
        <div class="form-hint" style="margin-bottom: 6px;">Áudio limpo de 5 a 30 segundos, sem música de fundo.</div>
        <input type="file" id="new-voice-file" accept="audio/*,.wav,.mp3,.ogg,.m4a" class="input-text" required />
      </div>

      <div style="display: flex; align-items: center; gap: 10px; margin-top: 4px;">
        <input type="checkbox" id="new-voice-default" style="accent-color: var(--primary); width: 16px; height: 16px;" />
        <label for="new-voice-default" style="font-size: 13px; color: var(--text-primary); cursor: pointer;">
          Definir como voz padrão do sistema
        </label>
      </div>
    </form>
  `;

  showCustomModal({
    title: 'Adicionar Nova Voz de Referência',
    content: modalContent,
    confirmText: 'Salvar Voz',
    onConfirm: async (modalBody) => {
      const nameInput = modalBody.querySelector('#new-voice-name');
      const fileInput = modalBody.querySelector('#new-voice-file');
      const isDefaultCheckbox = modalBody.querySelector('#new-voice-default');

      const name = nameInput.value.trim();
      const file = fileInput.files[0];
      const isDefault = isDefaultCheckbox.checked;

      if (!name) {
        showToast('Informe o nome da voz.', 'error');
        nameInput.focus();
        return false;
      }

      if (!file) {
        showToast('Selecione um arquivo de áudio de amostra.', 'error');
        fileInput.focus();
        return false;
      }

      try {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('file', file);
        formData.append('is_default', String(isDefault));

        await api.createVoice(formData);
        showToast(`Voz "${name}" adicionada com sucesso!`, 'success');
        await loadAndRenderVoices(container);
        return true;
      } catch (err) {
        showToast(`Erro ao cadastrar voz: ${err.message}`, 'error');
        return false;
      }
    },
  });
}

function resolveVoiceSampleUrl(samplePath) {
  if (!samplePath) return '';
  if (samplePath.startsWith('http') || samplePath.startsWith('/')) {
    return samplePath;
  }
  const filename = samplePath.replace(/\\/g, '/').split('/').pop();
  return `/voices/${encodeURIComponent(filename)}`;
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
