import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import './auth.js'
import router from './router/index.js'
import './assets/theme.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
