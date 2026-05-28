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
  },
  async register(email, password, baseCurrency = 'EUR') {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        email, 
        password, 
        base_currency: baseCurrency 
      })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }
    
    return await response.json()
  },
  async login(email, password){
    try {
        const formData = new URLSearchParams()
        formData.append('username', email)
        formData.append('password', password)
        
        const response = await axios.post('http://127.0.0.1:8000/api/auth/login', formData)
        localStorage.setItem('token', response.data.access_token)
        this.$emit('login-success')
      } catch (err) {
        this.error = 'Login failed. Check your credentials.'
      }
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

