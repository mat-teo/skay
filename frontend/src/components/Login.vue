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

    <!-- 2FA Modal -->
    <div class="modal fade" id="twoFactorModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Two-Factor Authentication</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Enter the 6-digit code from your authenticator app:</p>
            <input type="text" class="form-control text-center fs-3" v-model="otpCode" maxlength="6" placeholder="000000" @keyup.enter="submit2FALogin">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary w-100" @click="submit2FALogin" :disabled="verifying">
              {{ verifying ? 'Verifying...' : 'Verify' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { auth } from '../auth'
import { Modal } from 'bootstrap'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      tempToken: null,
      otpCode: '',
      verifying: false
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      try {
        const response = await auth.login(this.email, this.password)
        
        if (response.requires_2fa) {
          this.tempToken = response.temp_token
          const modal = new Modal(document.getElementById('twoFactorModal'))
          modal.show()
        } else {
          this.$root.showToast('Login successful!', 'success')
          this.$router.push('/dashboard')
        }
      } catch (err) {
        this.$root.showToast(err.message || 'Login failed. Please check your credentials.', 'danger')
      } finally {
        this.loading = false
      }
    },
    
    async submit2FALogin() {
      if (!this.otpCode || this.otpCode.length !== 6) {
        this.$root.showToast('Please enter a 6-digit code', 'warning')
        return
      }
      
      this.verifying = true
      try {
        await auth.verify2FA(this.tempToken, this.otpCode)
        this.$root.showToast('Login successful!', 'success')
        const modal = Modal.getInstance(document.getElementById('twoFactorModal'))
        if (modal) modal.hide()
        this.$router.push('/dashboard')
      } catch (err) {
        this.$root.showToast(err.message, 'danger')
      } finally {
        this.verifying = false
      }
    }
  }
}
</script>