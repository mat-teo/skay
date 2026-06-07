<template>
  <div>
    <ToastNotification ref="toast" />
    
    <!-- Router View for auth pages (no navbar) -->
    <router-view v-if="!isLoggedIn" />
    
    <!-- Main App (when logged in) -->
    <div v-if="isLoggedIn">
      <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container">
          <router-link class="navbar-brand fw-bold" to="/dashboard" active-class="" exact-active-class="">
            Skay Finance
          </router-link>
          <div class="d-flex">
            <router-link 
              class="btn btn-outline-light me-2" 
              to="/dashboard"
              active-class="active">
              Dashboard
            </router-link>
            <router-link 
              class="btn btn-outline-light me-2" 
              to="/transactions"
              active-class="active">
              Transactions
            </router-link>
            <router-link 
              class="btn btn-outline-light me-2" 
              to="/stats"
              active-class="active">
              Advanced Stats
            </router-link>
            <router-link 
              class="btn btn-outline-light me-2" 
              to="/categories"
              active-class="active">
              Categories
            </router-link>
            <button class="btn btn-outline-light" @click="handleLogout">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main class="container">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import ToastNotification from './components/ToastNotification.vue'
import { auth } from './auth'

export default {
  name: 'App',
  components: { ToastNotification },
  data() {
    return {
      isLoggedIn: false
    }
  },
  mounted() {
    this.checkAuth()
  },
  watch: {
    // Watch for route changes to update auth state
    '$route'() {
      this.checkAuth()
    }
  },
  methods: {
    checkAuth() {
      this.isLoggedIn = auth.isAuthenticated()
    },
    showToast(message, type) {
      this.$refs.toast?.show(message, type)
    },
    async handleLogout() {
      auth.logout()
      this.isLoggedIn = false
      this.$router.push('/login')
      this.showToast('Logged out successfully', 'info')
    }
  }
}
</script>

<style scoped>
.router-link-active {
  background-color: white !important;
  color: #212529 !important;
}

.navbar-brand {
  text-decoration: none;
}
</style>