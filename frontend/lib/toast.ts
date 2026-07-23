/**
 * Lightweight toast notification system.
 * Appends a temporary notification to the DOM.
 */
export function showToast(message: string, type: 'success' | 'info' | 'warning' | 'error' = 'info', durationMs = 3500) {
  if (typeof window === 'undefined') return;

  const container = document.getElementById('toast-container') || createToastContainer();
  
  const toast = document.createElement('div');
  toast.className = `toast-notification toast-${type}`;
  toast.textContent = message;
  
  container.appendChild(toast);
  
  // Trigger enter animation
  requestAnimationFrame(() => toast.classList.add('toast-visible'));
  
  // Auto-dismiss
  setTimeout(() => {
    toast.classList.remove('toast-visible');
    toast.addEventListener('transitionend', () => toast.remove());
  }, durationMs);
}

function createToastContainer(): HTMLElement {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.style.cssText = 'position:fixed;top:16px;right:16px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
  document.body.appendChild(container);
  return container;
}
