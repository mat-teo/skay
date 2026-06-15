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
  
  logout(redirect = true) {
    localStorage.removeItem('token')
    if (redirect) {
      window.location.href = '/login'
    }
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
  
  async login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await axios.post(`${API_URL}/auth/login`, formData)
    
    if (response.data && response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
      return response.data
    } else {
      throw new Error('Invalid response from server')
    }
  }
}

// Interceptor - adds token to ALL requests
axios.interceptors.request.use(config => {
  const token = auth.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor - handles 401 errors
axios.interceptors.response.use(
  response => response,
  error => {
    const isLoginAttempt = error.config?.url?.includes('/auth/login')
    const hasToken = auth.getToken()
    
    if (error.response?.status === 401 && !isLoginAttempt && hasToken) {
      auth.logout()
    }
    return Promise.reject(error)
  }
)