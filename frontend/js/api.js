/**
 * Voxa API Client
 * Comunicação com o backend FastAPI e escuta SSE para progresso em tempo real.
 */

const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      let errorDetail = `Erro HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            errorDetail = errorData.detail.map(d => d.msg || JSON.stringify(d)).join(', ');
          } else {
            errorDetail = errorData.detail;
          }
        }
      } catch (_) {
        // Se não for JSON, mantém o status
      }
      throw new Error(errorDetail);
    }

    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (err) {
    console.error(`Falha na requisição para ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Configurações
  async getSettings() {
    return await request('/settings');
  },

  async updateSettings(settings) {
    return await request('/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
  },

  // Vozes
  async getVoices() {
    return await request('/voices');
  },

  async createVoice(formData) {
    return await request('/voices', {
      method: 'POST',
      body: formData, // multipart/form-data automático pelo browser
    });
  },

  async setDefaultVoice(voiceId) {
    return await request(`/voices/${encodeURIComponent(voiceId)}/default`, {
      method: 'PUT',
    });
  },

  async deleteVoice(voiceId) {
    return await request(`/voices/${encodeURIComponent(voiceId)}`, {
      method: 'DELETE',
    });
  },

  // Histórico
  async getHistory() {
    return await request('/history');
  },

  async deleteHistoryItem(itemId) {
    return await request(`/history/${encodeURIComponent(itemId)}`, {
      method: 'DELETE',
    });
  },

  async clearAllHistory() {
    return await request('/history', {
      method: 'DELETE',
    });
  },

  // Narração e Transcrição
  async startNarration(text, voiceId = null) {
    const payload = { text };
    if (voiceId) payload.voice_id = voiceId;
    return await request('/narrate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  async startNarrationAndTranscription(text, voiceId = null, mode = 'normal') {
    const payload = { text, mode };
    if (voiceId) payload.voice_id = voiceId;
    return await request('/narrate-and-transcribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  async startTranscription(formData) {
    return await request('/transcribe', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Conecta ao endpoint Server-Sent Events (SSE) e monitora o progresso de uma tarefa
   */
  listenProgress(taskId, onMessage, onComplete, onError) {
    const sseUrl = `${API_BASE}/progress/${encodeURIComponent(taskId)}`;
    const eventSource = new EventSource(sseUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onMessage) {
          onMessage(data);
        }

        if (data.status === 'completed') {
          eventSource.close();
          if (onComplete) {
            onComplete(data.result);
          }
        } else if (data.status === 'failed') {
          eventSource.close();
          if (onError) {
            onError(new Error(data.error || data.message || 'Falha no processamento da tarefa'));
          }
        }
      } catch (err) {
        console.error('Erro ao interpretar evento SSE:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.warn('Conexão SSE encerrada ou com erro:', err);
      eventSource.close();
      if (onError) {
        onError(err);
      }
    };

    return () => {
      eventSource.close();
    };
  },
};
