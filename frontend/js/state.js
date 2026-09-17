/**
 * Voxa State Management
 * Gerenciador de estado reativo simples para a SPA.
 */

class StateManager {
  constructor() {
    this.state = {
      voices: [],
      defaultVoice: null,
      settings: null,
      history: [],
      activeTask: null,
      isProcessing: false,
    };
    this.listeners = new Set();
  }

  get() {
    return this.state;
  }

  set(updates) {
    this.state = { ...this.state, ...updates };
    this.notify();
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify() {
    for (const listener of this.listeners) {
      try {
        listener(this.state);
      } catch (err) {
        console.error('Erro no ouvinte de estado:', err);
      }
    }
  }

  setVoices(voices) {
    const defaultVoice = voices.find(v => v.is_default) || (voices.length > 0 ? voices[0] : null);
    this.set({ voices, defaultVoice });
  }

  setSettings(settings) {
    this.set({ settings });
  }

  setHistory(history) {
    this.set({ history });
  }

  setProcessing(isProcessing, activeTask = null) {
    this.set({ isProcessing, activeTask });
  }
}

export const stateManager = new StateManager();
