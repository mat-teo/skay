<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
    <div v-for="toast in toasts" :key="toast.id" 
         class="toast apple-toast show" 
         role="alert"
         :class="`toast-${toast.type}`">
      <div class="toast-header" :class="`toast-header-${toast.type}`">
        <i :class="toastIcon(toast.type)" class="me-2"></i>
        <strong class="me-auto">{{ toast.title }}</strong>
        <button type="button" class="btn-close" :class="toastCloseClass(toast.type)" @click="removeToast(toast.id)"></button>
      </div>
      <div class="toast-body">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ToastNotification',
  data() {
    return {
      toasts: []
    }
  },
  methods: {
    show(message, type = 'success', title = '') {
      const id = Date.now()
      const titles = {
        success: 'Success',
        danger: 'Error',
        error: 'Error',
        warning: 'Warning',
        info: 'Info'
      }
      
      this.toasts.push({
        id,
        message,
        type,
        title: title || titles[type] || 'Notification'
      })
      
      setTimeout(() => {
        this.removeToast(id)
      }, 4000)
    },
    
    removeToast(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },
    
    toastIcon(type) {
      const icons = {
        success: 'bi bi-check-circle-fill',
        danger: 'bi bi-exclamation-triangle-fill',
        error: 'bi bi-exclamation-triangle-fill',
        warning: 'bi bi-exclamation-circle-fill',
        info: 'bi bi-info-circle-fill'
      }
      return icons[type] || icons.info
    },
    
    toastCloseClass(type) {
      const darkBg = ['success', 'danger', 'error']
      return darkBg.includes(type) ? 'btn-close-white' : ''
    }
  }
}
</script>

<style scoped>
/* Apple-style toast container */
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1100;
}

/* Base toast style */
.apple-toast {
  min-width: 280px;
  max-width: 380px;
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 12px !important;
  border: none !important;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12), 0 0 0 0.5px rgba(0, 0, 0, 0.03) !important;
  margin-top: 12px;
  overflow: hidden;
}

/* Toast header base */
.apple-toast .toast-header {
  background: transparent !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
  padding: 14px 16px 10px 16px !important;
  font-weight: 600;
}

/* Toast body */
.apple-toast .toast-body {
  padding: 12px 16px 16px 16px !important;
  font-size: 0.875rem;
  color: #1d1d1f;
}

/* ============================================
   TIPI DI TOAST (COLORI SFUMATI)
   ============================================ */

/* Success - Verde delicato */
.toast-success .toast-header {
  color: #0a7e3b !important;
}
.toast-success .toast-header i {
  color: #22c55e;
}

/* Danger/Error - Rosso delicato */
.toast-danger .toast-header,
.toast-error .toast-header {
  color: #be123c !important;
}
.toast-danger .toast-header i,
.toast-error .toast-header i {
  color: #e11d48;
}

/* Warning - Arancione delicato */
.toast-warning .toast-header {
  color: #b45309 !important;
}
.toast-warning .toast-header i {
  color: #f59e0b;
}

/* Info - Blu delicato */
.toast-info .toast-header {
  color: #1e40af !important;
}
.toast-info .toast-header i {
  color: #3b82f6;
}

/* ============================================
   ANIMAZIONI
   ============================================ */

/* Animazione di entrata */
.apple-toast {
  animation: toastSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Animazione di uscita */
.apple-toast.removing {
  animation: toastSlideOut 0.2s ease forwards;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toastSlideOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(30px);
  }
}

/* Hover effect - leggermente più opaco */
.apple-toast:hover {
  background: rgba(255, 255, 255, 0.98) !important;
}

/* Responsive */
@media (max-width: 576px) {
  .toast-container {
    left: 16px;
    right: 16px;
    bottom: 16px;
  }
  
  .apple-toast {
    width: 100%;
    max-width: none;
    min-width: auto;
  }
}
</style>