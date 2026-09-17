/**
 * Voxa Settings Page
 * Configurações de hardware, modos de segmentação de legendas e servidor.
 */

import { api } from '../api.js';
import { stateManager } from '../state.js';
import { showToast } from '../components/toast.js';

export async function renderSettingsPage(container) {
  container.innerHTML = `
    <div class="page-container">
      <div class="page-header">
        <div>
          <h1 class="page-title"><span>⚙</span> Configurações do Sistema</h1>
          <p class="page-subtitle">Ajuste o uso de CPU, parâmetros de legendas dinâmicas e comportamento do servidor.</p>
        </div>
      </div>

      <div id="settings-content-wrapper">
        <div style="text-align: center; color: var(--text-muted); padding: 40px;">Carregando configurações...</div>
      </div>
    </div>
  `;

  await loadAndRenderSettings(container);
}

async function loadAndRenderSettings(container) {
  try {
    const settings = await api.getSettings();
    stateManager.setSettings(settings);
    renderSettingsForm(container, settings);
  } catch (err) {
    showToast(`Erro ao carregar configurações: ${err.message}`, 'error');
  }
}

function renderSettingsForm(container, settings) {
  const wrapper = container.querySelector('#settings-content-wrapper');
  if (!wrapper) return;

  const totalCores = navigator.hardwareConcurrency || 8;
  const initialPercent = settings.cpu_percent || 75;
  const initialEstimatedCores = Math.max(1, Math.round((initialPercent / 100) * totalCores));

  const modes = settings.transcription_modes || {
    normal: { min_seconds: 4.0, max_seconds: 6.0 },
    dynamic: { min_seconds: 2.0, max_seconds: 4.0 },
    accelerated: { min_seconds: 1.0, max_seconds: 2.0 },
  };

  wrapper.innerHTML = `
    <form id="settings-form" class="settings-grid">
      <!-- Card: Limite de CPU -->
      <div class="card">
        <div class="card-title">
          <span>⚡ Desempenho e Limitação de CPU</span>
          <span class="badge-lang">HARDWARE</span>
        </div>
        <p class="form-hint" style="margin-bottom: 16px;">
          Controle o limite de utilização de CPU pelo F5-TTS e Whisper para manter o computador responsivo durante a síntese.
        </p>

        <div class="form-group">
          <label class="form-label" for="cpu-slider">
            <span>Alocação Máxima de CPU: <strong id="cpu-percent-label">${initialPercent}%</strong></span>
            <span id="cpu-cores-label" style="font-family: var(--font-mono); color: #a78bfa;">~${initialEstimatedCores} de ${totalCores} núcleos</span>
          </label>
          <div class="slider-container">
            <span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted);">25%</span>
            <input type="range" id="cpu-slider" class="slider-input" min="25" max="100" step="5" value="${initialPercent}" />
            <span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted);">100%</span>
          </div>
        </div>
      </div>

      <!-- Card: Modos de Legenda Dinâmica -->
      <div class="card">
        <div class="card-title">
          <span>📝 Parâmetros de Segmentação de Legendas (SRT)</span>
          <span class="badge-lang">TEMPOS</span>
        </div>
        <p class="form-hint" style="margin-bottom: 20px;">
          Defina o intervalo de tempo mínimo e máximo em segundos para cada bloco de legenda gerado.
        </p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px;">
          <!-- Modo Normal -->
          <div style="background: var(--bg-input); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <div style="font-weight: 600; color: #ffffff; margin-bottom: 12px; display: flex; justify-content: space-between;">
              <span>Normal</span>
              <span class="form-hint">4 a 6s</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 11px;">Mínimo (s)</label>
                <input type="number" step="0.1" id="mode-normal-min" class="input-text" value="${modes.normal?.min_seconds ?? 4.0}" />
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 11px;">Máximo (s)</label>
                <input type="number" step="0.1" id="mode-normal-max" class="input-text" value="${modes.normal?.max_seconds ?? 6.0}" />
              </div>
            </div>
          </div>

          <!-- Modo Dinâmico -->
          <div style="background: var(--bg-input); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <div style="font-weight: 600; color: #ffffff; margin-bottom: 12px; display: flex; justify-content: space-between;">
              <span>Dinâmico</span>
              <span class="form-hint">2 a 4s</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 11px;">Mínimo (s)</label>
                <input type="number" step="0.1" id="mode-dynamic-min" class="input-text" value="${modes.dynamic?.min_seconds ?? 2.0}" />
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 11px;">Máximo (s)</label>
                <input type="number" step="0.1" id="mode-dynamic-max" class="input-text" value="${modes.dynamic?.max_seconds ?? 4.0}" />
              </div>
            </div>
          </div>

          <!-- Modo Acelerado -->
          <div style="background: var(--bg-input); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <div style="font-weight: 600; color: #ffffff; margin-bottom: 12px; display: flex; justify-content: space-between;">
              <span>Acelerado</span>
              <span class="form-hint">1 a 2s</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 11px;">Mínimo (s)</label>
                <input type="number" step="0.1" id="mode-accelerated-min" class="input-text" value="${modes.accelerated?.min_seconds ?? 1.0}" />
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 11px;">Máximo (s)</label>
                <input type="number" step="0.1" id="mode-accelerated-max" class="input-text" value="${modes.accelerated?.max_seconds ?? 2.0}" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Card: Servidor e Inicialização -->
      <div class="card">
        <div class="card-title">
          <span>🌐 Servidor Local</span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: center;">
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" for="server-port">Porta HTTP do Servidor</label>
            <input type="number" id="server-port" class="input-text" value="${settings.server_port || 7865}" />
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; background: var(--bg-input); padding: 14px 18px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <div>
              <div style="font-weight: 600; font-size: 14px; color: #ffffff;">Abrir Navegador Automaticamente</div>
              <div class="form-hint">Abre a interface web ao iniciar o servidor</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" id="auto-open-browser" ${settings.auto_open_browser ? 'checked' : ''} />
              <span class="slider-toggle"></span>
            </label>
          </div>
        </div>
      </div>

      <div style="display: flex; justify-content: flex-end;">
        <button type="submit" id="btn-save-settings" class="btn btn-primary" style="padding: 12px 28px; font-size: 15px;">
          <span>💾</span> Salvar Configurações
        </button>
      </div>
    </form>
  `;

  setupSettingsEvents(wrapper, settings, totalCores);
}

function setupSettingsEvents(wrapper, initialSettings, totalCores) {
  const slider = wrapper.querySelector('#cpu-slider');
  const percentLabel = wrapper.querySelector('#cpu-percent-label');
  const coresLabel = wrapper.querySelector('#cpu-cores-label');
  const form = wrapper.querySelector('#settings-form');
  const btnSave = wrapper.querySelector('#btn-save-settings');

  slider.addEventListener('input', () => {
    const val = parseInt(slider.value, 10);
    percentLabel.textContent = `${val}%`;
    const estimatedCores = Math.max(1, Math.round((val / 100) * totalCores));
    coresLabel.textContent = `~${estimatedCores} de ${totalCores} núcleos`;
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    btnSave.disabled = true;
    btnSave.innerHTML = '<span>⏳</span> Salvando...';

    const newSettings = {
      ...initialSettings,
      cpu_percent: parseInt(slider.value, 10),
      server_port: parseInt(wrapper.querySelector('#server-port').value, 10),
      auto_open_browser: wrapper.querySelector('#auto-open-browser').checked,
      transcription_modes: {
        normal: {
          min_seconds: parseFloat(wrapper.querySelector('#mode-normal-min').value),
          max_seconds: parseFloat(wrapper.querySelector('#mode-normal-max').value),
        },
        dynamic: {
          min_seconds: parseFloat(wrapper.querySelector('#mode-dynamic-min').value),
          max_seconds: parseFloat(wrapper.querySelector('#mode-dynamic-max').value),
        },
        accelerated: {
          min_seconds: parseFloat(wrapper.querySelector('#mode-accelerated-min').value),
          max_seconds: parseFloat(wrapper.querySelector('#mode-accelerated-max').value),
        },
      },
    };

    try {
      const updated = await api.updateSettings(newSettings);
      stateManager.setSettings(updated);
      showToast('Configurações salvas e aplicadas com sucesso!', 'success');
    } catch (err) {
      showToast(`Erro ao salvar configurações: ${err.message}`, 'error');
    } finally {
      btnSave.disabled = false;
      btnSave.innerHTML = '<span>💾</span> Salvar Configurações';
    }
  });
}
