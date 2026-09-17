/**
 * Voxa Modal Component
 * Modais dinâmicos para confirmação e ações customizadas.
 */

export function showConfirmModal({
  title = 'Confirmação',
  message = 'Deseja prosseguir?',
  onConfirm = () => {},
  confirmText = 'Confirmar',
  danger = false,
}) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';

  backdrop.innerHTML = `
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title">${escapeHtml(title)}</div>
        <button class="toast-close" id="modal-close-btn">&times;</button>
      </div>
      <div class="modal-body">
        ${escapeHtml(message)}
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="modal-cancel-btn">Cancelar</button>
        <button class="btn ${danger ? 'btn-danger' : 'btn-primary'}" id="modal-confirm-btn">${escapeHtml(confirmText)}</button>
      </div>
    </div>
  `;

  const close = () => {
    backdrop.style.opacity = '0';
    setTimeout(() => {
      if (backdrop.parentElement) {
        backdrop.parentElement.removeChild(backdrop);
      }
    }, 200);
  };

  backdrop.querySelector('#modal-close-btn').addEventListener('click', close);
  backdrop.querySelector('#modal-cancel-btn').addEventListener('click', close);

  backdrop.querySelector('#modal-confirm-btn').addEventListener('click', async () => {
    try {
      await onConfirm();
      close();
    } catch (err) {
      console.error('Erro na ação do modal:', err);
    }
  });

  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) {
      close();
    }
  });

  document.body.appendChild(backdrop);
}

export function showCustomModal({
  title = 'Modal',
  content = '',
  onConfirm = null,
  confirmText = 'Salvar',
  danger = false,
}) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';

  backdrop.innerHTML = `
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title">${escapeHtml(title)}</div>
        <button class="toast-close" id="modal-close-btn">&times;</button>
      </div>
      <div class="modal-body" id="modal-content-area">
        ${content}
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="modal-cancel-btn">Cancelar</button>
        ${onConfirm ? `<button class="btn ${danger ? 'btn-danger' : 'btn-primary'}" id="modal-confirm-btn">${escapeHtml(confirmText)}</button>` : ''}
      </div>
    </div>
  `;

  const close = () => {
    backdrop.style.opacity = '0';
    setTimeout(() => {
      if (backdrop.parentElement) {
        backdrop.parentElement.removeChild(backdrop);
      }
    }, 200);
  };

  backdrop.querySelector('#modal-close-btn').addEventListener('click', close);
  backdrop.querySelector('#modal-cancel-btn').addEventListener('click', close);

  if (onConfirm) {
    backdrop.querySelector('#modal-confirm-btn').addEventListener('click', async () => {
      try {
        const modalBody = backdrop.querySelector('#modal-content-area');
        const shouldClose = await onConfirm(modalBody);
        if (shouldClose !== false) {
          close();
        }
      } catch (err) {
        console.error('Erro no modal customizado:', err);
      }
    });
  }

  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) {
      close();
    }
  });

  document.body.appendChild(backdrop);
  return {
    dialog: backdrop.querySelector('.modal-dialog'),
    close,
  };
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
