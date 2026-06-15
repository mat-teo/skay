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
              <button type="submit" class="btn btn-dark w-100" :disabled="loading">
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
            </form>
            <hr>
            <div class="text-center">
              <p class="mb-0">Don't have an account?</p>
              <router-link to="/register" class="btn btn-link">
                Register here
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { auth } from '../auth'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      try {
        const result = await auth.login(this.email, this.password)
        this.$root.showToast('Login successful!', 'success')
        this.$router.push('/dashboard')
      } catch (err) {
        this.$root.showToast(err.message || 'Login failed', 'danger')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>