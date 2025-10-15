(function (window) {
  if (window.notificationModal) {
    return;
  }

  const state = {
    title: '',
    message: '',
    primaryLabel: 'Ok',
    secondaryLabel: '',
    onPrimary: null,
    onSecondary: null,
  };

  function emit(type, detail = {}) {
    window.dispatchEvent(new CustomEvent(`notification-modal:${type}`, { detail }));
  }

  const api = {
    show({ title, message, primaryLabel = 'Ok', secondaryLabel = '', onPrimary = null, onSecondary = null }) {
      Object.assign(state, {
        title: title || '',
        message: message || '',
        primaryLabel,
        secondaryLabel,
        onPrimary: typeof onPrimary === 'function' ? onPrimary : null,
        onSecondary: typeof onSecondary === 'function' ? onSecondary : null,
      });
      emit('show', { ...state });
    },

    close(callback) {
      emit('close');
      if (typeof callback === 'function') {
        callback();
      }
    },

    primary() {
      const callback = state.onPrimary;
      this.close(callback);
    },

    secondary() {
      const callback = state.onSecondary;
      this.close(callback);
    },

    getState() {
      return { ...state };
    },
  };

  window.notificationModal = api;
}(window));

function notificationModalComponent() {
  return {
    open: false,
    title: '',
    message: '',
    primaryLabel: 'Ok',
    secondaryLabel: '',

    init() {
      window.addEventListener('notification-modal:show', (event) => {
        const detail = event.detail || {};
        this.title = detail.title || '';
        this.message = detail.message || '';
        this.primaryLabel = detail.primaryLabel || 'Ok';
        this.secondaryLabel = detail.secondaryLabel || '';
        this.open = true;
      });

      window.addEventListener('notification-modal:close', () => {
        this.open = false;
      });
    },

    handlePrimary() {
      window.notificationModal.primary();
    },

    handleSecondary() {
      window.notificationModal.secondary();
    },
    close(){
      this.open = false;
    }
  };
}
