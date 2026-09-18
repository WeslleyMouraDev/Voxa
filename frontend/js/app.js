/**
 * Voxa SPA Main Application
 * Roteamento baseado em hash, ciclo de vida e estado global.
 */

import { api } from './api.js';
import { stateManager } from './state.js';
import { renderNarratePage } from './pages/narrate.js';
import { renderVoicesPage } from './pages/voices.js';
import { renderHistoryPage } from './pages/history.js';
import { renderSettingsPage } from './pages/settings.js';
import { initLogDrawer } from './components/log-drawer.js';

const routes = {
  narrate: renderNarratePage,
  voices: renderVoicesPage,
  history: renderHistoryPage,
  settings: renderSettingsPage,
};

async function init() {
  const contentArea = document.getElementById('main-content');
  const statusDot = document.getElementById('system-status-dot');
  const statusVal = document.getElementById('system-status-val');

  // Inicializa o painel deslizante de logs em tempo real (DevTools drawer)
  initLogDrawer();


  // Inscreve observador para o status de processamento no rodapé da sidebar
  stateManager.subscribe((state) => {
    if (statusDot && statusVal) {
      if (state.isProcessing) {
        statusDot.className = 'status-dot processing';
        statusVal.textContent = 'Processando...';
        statusVal.style.color = '#c4b5fd';
      } else {
        statusDot.className = 'status-dot';
        statusVal.textContent = 'Pronto';
        statusVal.style.color = '#10b981';
      }
    }
  });

  // Carrega dados iniciais essenciais em background
  try {
    const [voices, settings] = await Promise.all([
      api.getVoices().catch(() => []),
      api.getSettings().catch(() => null),
    ]);
    if (voices) stateManager.setVoices(voices);
    if (settings) stateManager.setSettings(settings);
  } catch (err) {
    console.warn('Aviso ao carregar dados iniciais:', err);
  }

  // Roteador de hash
  function navigate() {
    const hash = window.location.hash.replace(/^#\/?/, '').toLowerCase() || 'narrate';
    const pageRender = routes[hash] || routes.narrate;

    // Atualiza links da sidebar
    document.querySelectorAll('.sidebar-nav .nav-item').forEach((link) => {
      const href = link.getAttribute('href').replace(/^#\/?/, '').toLowerCase();
      if (href === hash || (hash === '' && href === 'narrate')) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Renderiza a página
    contentArea.innerHTML = '';
    pageRender(contentArea);
  }

  window.addEventListener('hashchange', navigate);
  navigate();
}

document.addEventListener('DOMContentLoaded', init);
