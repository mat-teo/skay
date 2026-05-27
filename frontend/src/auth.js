// src/auth.js
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

export const auth = {
  getToken() {
    return localStorage.getItem('token')
  },
  
  isAuthenticated() {
    return !!this.getToken()
  },
  
  logout() {
    localStorage.removeItem('token')
    window.location.reload()
  }
}

// Interceptor - aggiunge token a TUTTE le richieste
axios.interceptors.request.use(config => {
  const token = auth.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor - gestisce errori 401
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      auth.logout()
    }
    return Promise.reject(error)
  }
)