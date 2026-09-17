/**
 * Voxa Toast Component
 * Exibe notificações flutuantes no canto superior direito com auto-dismiss.
 */

export function showToast(message, type = 'success', durationMs = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
  };
  const icon = iconMap[type] || 'ℹ';

  toast.innerHTML = `
    <span style="font-weight: 700; color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#7c3aed'};">${icon}</span>
    <div class="toast-message">${escapeHtml(message)}</div>
    <button class="toast-close" aria-label="Fechar">&times;</button>
  `;

  const closeBtn = toast.querySelector('.toast-close');
  const dismiss = () => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => {
      if (toast.parentElement) {
        toast.parentElement.removeChild(toast);
      }
    }, 300);
  };

  closeBtn.addEventListener('click', dismiss);

  container.appendChild(toast);

  if (durationMs > 0) {
    setTimeout(dismiss, durationMs);
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
