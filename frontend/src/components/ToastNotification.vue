<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
    <div v-for="toast in toasts" :key="toast.id" 
         class="toast show" 
         role="alert">
      <div class="toast-header" :class="headerClass(toast.type)">
        <strong class="me-auto">{{ toast.title }}</strong>
        <button type="button" class="btn-close" :class="closeButtonClass(toast.type)" @click="removeToast(toast.id)"></button>
      </div>
      <div class="toast-body" :class="bodyClass(toast.type)">
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
      }, 3000)
    },
    
    removeToast(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },
    
    headerClass(type) {
      const classes = {
        success: 'bg-success text-white',
        danger: 'bg-danger text-white',
        error: 'bg-danger text-white',
        warning: 'bg-warning text-dark',
        info: 'bg-info text-dark'
      }
      return classes[type] || classes.info
    },
    
    bodyClass(type) {
      const classes = {
        success: 'bg-success text-white',
        danger: 'bg-danger text-white',
        error: 'bg-danger text-white',
        warning: 'bg-warning text-dark',
        info: 'bg-info text-dark'
      }
      return classes[type] || classes.info
    },
    
    closeButtonClass(type) {
      // White close button for dark backgrounds, dark for light backgrounds
      const darkBg = ['success', 'danger', 'error']
      return darkBg.includes(type) ? 'btn-close-white' : ''
    }
  }
}
</script>