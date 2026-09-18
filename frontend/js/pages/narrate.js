/**
 * Voxa Narrate Page
 * Geração de narração por IA, transcrição e sincronização com legendas dinâmicas.
 */

import { api } from '../api.js';
import { stateManager } from '../state.js';
import { showToast } from '../components/toast.js';

let selectedMode = 'normal';
let activeStopListening = null;

export function renderNarratePage(container) {
  const state = stateManager.get();
  const voices = state.voices || [];

  container.innerHTML = `
    <div class="page-container">
      <div class="page-header">
        <div>
          <h1 class="page-title"><span>🎙</span> Estúdio de Narração & Transcrição</h1>
          <p class="page-subtitle">Sintetize vozes clonadas em português e gere legendas SRT perfeitamente sincronizadas.</p>
        </div>
      </div>

      <!-- Card Principal de Criação -->
      <div class="card" id="narrate-form-card">
        <div class="form-group">
          <label class="form-label" for="narrate-text">
            <span>Roteiro / Texto</span>
            <span class="char-counter" id="char-counter">0 caracteres • 0 palavras</span>
          </label>
          <textarea
            id="narrate-text"
            class="textarea-custom"
            placeholder="Insira aqui o roteiro ou texto que deseja narrar em PT-BR... Exemplo: 'No coração da floresta amazônica, pesquisadores descobriram uma nova espécie de orquídea luminosa...'"
          ></textarea>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
          <!-- Seletor de Voz -->
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" for="voice-select">
              <span>Voz Clonada</span>
              <a href="#voices" style="color: var(--primary); font-size: 12px; text-decoration: none;">+ Gerenciar Vozes</a>
            </label>
            <select id="voice-select" class="select-input">
              ${
                voices.length === 0
                  ? '<option value="">Nenhuma voz cadastrada (Vá em "Vozes" para adicionar)</option>'
                  : voices
                      .map(
                        v =>
                          `<option value="${v.id}" ${v.is_default ? 'selected' : ''}>${v.is_default ? '★ ' : ''}${v.name}</option>`
                      )
                      .join('')
              }
            </select>
            ${
              voices.length === 0
                ? '<div class="form-hint" style="color: var(--warning); margin-top: 4px;">⚠️ Nenhuma voz disponível. Cadastre uma amostra na aba Vozes.</div>'
                : ''
            }
          </div>

          <!-- Upload Opcional de Áudio (para Apenas Transcrever) -->
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" for="audio-upload-input">
              <span>Upload de Áudio (Apenas Transcrever)</span>
              <span class="form-hint">Opcional</span>
            </label>
            <input type="file" id="audio-upload-input" accept="audio/*,.mp3,.wav,.ogg,.m4a" class="input-text" style="padding: 8px 12px;" />
          </div>
        </div>

        <!-- Modos de Transcrição -->
        <div class="form-group">
          <label class="form-label">Modo de Legenda (Segmentação)</label>
          <div class="mode-selector-grid">
            <div class="mode-card ${selectedMode === 'normal' ? 'selected' : ''}" data-mode="normal">
              <div class="mode-header">
                <span class="mode-name">Normal</span>
                <span class="mode-badge">4-6s</span>
              </div>
              <p class="mode-desc">Equilibrado. Ideal para narrações tradicionais e 1 imagem por cena.</p>
            </div>

            <div class="mode-card ${selectedMode === 'dynamic' ? 'selected' : ''}" data-mode="dynamic">
              <div class="mode-header">
                <span class="mode-name">Dinâmico</span>
                <span class="mode-badge">2-4s</span>
              </div>
              <p class="mode-desc">Ritmo ágil. Recomendado para Reels, Shorts e TikTok.</p>
            </div>

            <div class="mode-card ${selectedMode === 'accelerated' ? 'selected' : ''}" data-mode="accelerated">
              <div class="mode-header">
                <span class="mode-name">Acelerado</span>
                <span class="mode-badge">1-2s</span>
              </div>
              <p class="mode-desc">Frenético. 1 a 3 palavras para retenção máxima de atenção.</p>
            </div>
          </div>
        </div>

        <!-- Linha de Botões de Ação -->
        <div class="action-buttons-row">
          <button id="btn-narrate-only" class="btn btn-secondary" title="Sintetiza apenas o arquivo de áudio MP3">
            <span>🎙</span> Apenas Narrar
          </button>
          <button id="btn-transcribe-only" class="btn btn-secondary" title="Gera arquivo SRT a partir do áudio enviado">
            <span>📝</span> Apenas Transcrever
          </button>
          <button id="btn-narrate-transcribe" class="btn btn-primary btn-highlight" title="Sintetiza a voz e transcreve automaticamente com sincronismo milimétrico">
            <span>🎙📝</span> Narrar + Transcrever
          </button>
        </div>
      </div>

      <!-- Painel de Progresso Ativo (Oculto inicialmente) -->
      <div id="progress-panel" class="progress-panel" style="display: none;">
        <div class="progress-header">
          <div class="progress-title">
            <span class="status-dot processing"></span>
            <span id="progress-task-name">Processando Tarefa...</span>
          </div>
          <span class="progress-pct" id="progress-pct">0%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" id="progress-bar-fill"></div>
        </div>
        <div class="progress-msg" id="progress-msg">Iniciando pipeline de processamento...</div>
      </div>

      <!-- Painel de Resultado (Oculto inicialmente) -->
      <div id="result-panel" class="result-panel" style="display: none;">
        <div class="card-title">
          <span>✨ Resultado Concluído</span>
          <span id="result-meta" class="form-hint" style="font-family: var(--font-mono);"></span>
        </div>
        <div class="audio-player-wrapper">
          <audio id="result-audio-player" controls preload="auto"></audio>
        </div>
        <div class="download-actions">
          <a id="btn-download-mp3" class="btn btn-secondary" download style="display: none;">
            <span>⬇</span> Baixar MP3
          </a>
          <a id="btn-download-srt" class="btn btn-secondary" download style="display: none;">
            <span>⬇</span> Baixar Legendas (.SRT)
          </a>
        </div>
      </div>
    </div>
  `;

  setupNarrateEvents(container);
}

function setupNarrateEvents(container) {
  const textInput = container.querySelector('#narrate-text');
  const counter = container.querySelector('#char-counter');
  const modeCards = container.querySelectorAll('.mode-card');
  const voiceSelect = container.querySelector('#voice-select');
  const audioUploadInput = container.querySelector('#audio-upload-input');

  const btnNarrateOnly = container.querySelector('#btn-narrate-only');
  const btnTranscribeOnly = container.querySelector('#btn-transcribe-only');
  const btnNarrateTranscribe = container.querySelector('#btn-narrate-transcribe');

  // Contador de caracteres e palavras
  textInput.addEventListener('input', () => {
    const text = textInput.value;
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    counter.textContent = `${chars} caracteres • ${words} palavras`;
  });

  // Troca de Modo de Transcrição
  modeCards.forEach(card => {
    card.addEventListener('click', () => {
      modeCards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      selectedMode = card.getAttribute('data-mode') || 'normal';
    });
  });

  // Apenas Narrar
  btnNarrateOnly.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) {
      showToast('Por favor, insira o texto a ser narrado.', 'error');
      textInput.focus();
      return;
    }
    const voiceId = voiceSelect.value || null;
    try {
      setProcessingUI(true, 'Narração em Andamento');
      const response = await api.startNarration(text, voiceId);
      trackTaskProgress(response.task_id, 'Narração');
    } catch (err) {
      setProcessingUI(false);
      showToast(err.message || 'Erro ao iniciar narração', 'error');
    }
  });

  // Apenas Transcrever
  btnTranscribeOnly.addEventListener('click', async () => {
    const file = audioUploadInput.files[0];
    if (!file) {
      showToast('Selecione um arquivo de áudio para transcrever no campo acima.', 'error');
      audioUploadInput.focus();
      return;
    }

    try {
      setProcessingUI(true, 'Transcrição de Áudio');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mode', selectedMode);

      const response = await api.startTranscription(formData);
      trackTaskProgress(response.task_id, 'Transcrição');
    } catch (err) {
      setProcessingUI(false);
      showToast(err.message || 'Erro ao iniciar transcrição', 'error');
    }
  });

  // Narrar + Transcrever (Destaque Principal)
  btnNarrateTranscribe.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) {
      showToast('Por favor, insira o roteiro a ser narrado.', 'error');
      textInput.focus();
      return;
    }
    const voiceId = voiceSelect.value || null;
    try {
      setProcessingUI(true, 'Narração e Transcrição Sincronizada');
      const response = await api.startNarrationAndTranscription(text, voiceId, selectedMode);
      trackTaskProgress(response.task_id, 'Narração + Transcrição');
    } catch (err) {
      setProcessingUI(false);
      showToast(err.message || 'Erro ao iniciar geração', 'error');
    }
  });
}

function setProcessingUI(isProcessing, taskName = '') {
  stateManager.setProcessing(isProcessing);
  const progressPanel = document.getElementById('progress-panel');
  const actionBtns = document.querySelectorAll('.action-buttons-row .btn');

  actionBtns.forEach(btn => {
    btn.disabled = isProcessing;
  });

  if (progressPanel) {
    if (isProcessing) {
      progressPanel.style.display = 'block';
      const nameEl = document.getElementById('progress-task-name');
      if (nameEl) nameEl.textContent = taskName;
      updateProgressBar(0, 'Preparando sintetizador...');
    } else {
      progressPanel.style.display = 'none';
    }
  }
}

function updateProgressBar(pct, msg) {
  const fill = document.getElementById('progress-bar-fill');
  const pctEl = document.getElementById('progress-pct');
  const msgEl = document.getElementById('progress-msg');

  const clamped = Math.min(100, Math.max(0, Math.round(pct)));
  if (fill) fill.style.width = `${clamped}%`;
  if (pctEl) pctEl.textContent = `${clamped}%`;
  if (msgEl && msg) msgEl.textContent = msg;
}

function trackTaskProgress(taskId, taskLabel) {
  if (activeStopListening) {
    activeStopListening();
  }

  activeStopListening = api.listenProgress(
    taskId,
    // onMessage
    (event) => {
      updateProgressBar(event.progress || 0, event.message || 'Processando...');
    },
    // onComplete
    (result) => {
      setProcessingUI(false);
      showToast(`${taskLabel} concluída com sucesso!`, 'success');
      showResultPanel(result);
      // Atualiza o histórico em background
      api.getHistory().then(history => stateManager.setHistory(history)).catch(() => {});
    },
    // onError
    (err) => {
      setProcessingUI(false);
      const msg = (err && err.message) ? err.message : (typeof err === 'string' ? err : 'Falha desconhecida no servidor');
      showToast(`Falha no processamento: ${msg}`, 'error');
    }
  );
}

function showResultPanel(result) {
  const panel = document.getElementById('result-panel');
  const audio = document.getElementById('result-audio-player');
  const btnMp3 = document.getElementById('btn-download-mp3');
  const btnSrt = document.getElementById('btn-download-srt');

  if (!panel || !audio) return;

  panel.style.display = 'block';

  if (result && result.audio_url) {
    audio.src = result.audio_url;
    audio.load();
    btnMp3.href = result.audio_url;
    btnMp3.style.display = 'inline-flex';
  } else {
    audio.src = '';
    btnMp3.style.display = 'none';
  }

  if (result && result.srt_url) {
    btnSrt.href = result.srt_url;
    btnSrt.style.display = 'inline-flex';
  } else {
    btnSrt.style.display = 'none';
  }

  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
