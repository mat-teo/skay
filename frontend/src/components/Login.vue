<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-header bg-dark text-white text-center">
            <h4>Skay Finance - Login</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label>Email</label>
                <input type="email" class="form-control" v-model="email" required>
              </div>
              <div class="mb-3">
                <label>Password</label>
                <input type="password" class="form-control" v-model="password" required>
              </div>
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <button type="submit" class="btn btn-dark w-100">Login</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        const formData = new URLSearchParams()
        formData.append('username', this.email)
        formData.append('password', this.password)
        
        const response = await axios.post('http://127.0.0.1:8000/api/auth/login', formData)
        localStorage.setItem('token', response.data.access_token)
        this.$emit('login-success')
      } catch (err) {
        this.error = 'Login failed. Check your credentials.'
      }
    }
  }
}
</script>