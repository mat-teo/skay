import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import './auth.js'
import router from './router/index.js'
import './assets/theme.css'
import i18n from './i18n.js';

const app = createApp(App)
app.use(router)
app.use(i18n);

let confirmModalInstance = null

window.confirm = function(message, title = 'Confirm', confirmText = 'OK', type = 'primary') {
  return new Promise((resolve) => {
    if (!confirmModalInstance) {
      console.error('ConfirmModal not initialized')
      resolve(false)
      return
    }
    
    confirmModalInstance.show({
      title: title || 'Confirm',
      message: message || 'Are you sure?',
      confirmText: confirmText || 'OK',
      type: type || 'primary'
    }).then(result => {
      resolve(result)
    })
  })
}

app.mount('#app')

export function setConfirmModal(instance) {
  confirmModalInstance = instance
}