<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-header bg-dark text-white text-center">
            <h4 class="mb-0">Create Account</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="email" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="password" 
                  required
                  minlength="6"
                >
                <small class="text-muted">Minimum 6 characters</small>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Confirm Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="confirmPassword" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">Base Currency</label>
                <select class="form-select" v-model="baseCurrency">
                  <option value="EUR">EUR (€)</option>
                  <option value="USD">USD ($)</option>
                  <option value="GBP">GBP (£)</option>
                </select>
              </div>
              
              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>
              
              <button 
                type="submit" 
                class="btn btn-dark w-100" 
                :disabled="loading"
              >
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
      error: null
    }
  },
  methods: {
    async handleRegister() {
      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match'
        return
      }
      
      this.loading = true
      this.error = null
      try {
        await auth.register(this.email, this.password, this.baseCurrency)
        // Auto-login after registration
        await auth.login(this.email, this.password)
        
        this.$emit('login-success')
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>