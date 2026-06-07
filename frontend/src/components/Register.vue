<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-header bg-dark text-white text-center">
            <h4>Create Account</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label>Email</label>
                <input type="email" class="form-control" v-model="email" required>
              </div>
              <div class="mb-3">
                <label>Password</label>
                <input type="password" class="form-control" v-model="password" required minlength="6">
              </div>
              <div class="mb-3">
                <label>Confirm Password</label>
                <input type="password" class="form-control" v-model="confirmPassword" required>
              </div>
              <div class="mb-3">
                <label>Base Currency</label>
                <select class="form-select" v-model="baseCurrency">
                  <option value="EUR">EUR (€)</option>
                  <option value="USD">USD ($)</option>
                  <option value="GBP">GBP (£)</option>
                </select>
              </div>
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <button type="submit" class="btn btn-dark w-100" :disabled="loading">
                {{ loading ? 'Creating account...' : 'Register' }}
              </button>
            </form>
            <hr>
            <div class="text-center">
              <p class="mb-0">Already have an account?</p>
              <router-link to="/login" class="btn btn-link">
                Login here
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
  name: 'Register',
  data() {
    return {
      email: '',
      password: '',
      confirmPassword: '',
      baseCurrency: 'EUR',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleRegister() {
      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match'
        return
      }
      
      this.loading = true
      this.error = ''
      try {
        await auth.register(this.email, this.password, this.baseCurrency)
        await auth.login(this.email, this.password)
        this.$router.push('/dashboard')
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>