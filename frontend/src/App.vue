<template>
  <div>
    <ToastNotification ref="toast" />
    
    <router-view v-if="!isLoggedIn" />
    
    <div v-if="isLoggedIn" class="app-layout">
      <nav class="navbar navbar-expand-md custom-navbar sticky-top">
        <div class="container">
          <router-link class="navbar-brand-apple" to="/dashboard">
            <span class="brand-gradient">Skay</span>Finance
          </router-link>
          
          <div class="d-flex align-items-center gap-2">
            <div class="nav-capsule-wrapper d-flex">
              <router-link class="nav-link-apple" to="/dashboard">
                Dashboard
              </router-link>
              <router-link class="nav-link-apple" to="/transactions">
                Transactions
              </router-link>
              <router-link class="nav-link-apple" to="/stats">
                Stats
              </router-link>
              <router-link class="nav-link-apple" to="/categories">
                Categories
              </router-link>
            </div>

            <div class="v-divider ms-2 me-1"></div>

            <button class="btn-logout-apple" @click="handleLogout">
              <i class="bi bi-box-arrow-right me-1"></i>Logout
            </button>
          </div>
        </div>
      </nav>

      <main class="container main-content">
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
/* Core layout background setup for a cleaner overall UI canvas */
.app-layout {
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* 1. APPLE GLASSMORPHISM NAVBAR */
.custom-navbar {
  background: rgba(255, 255, 255, 0.75) !important;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 12px 0;
  transition: background-color 0.3s ease;
}

/* 2. TYPOGRAPHY & BRANDING */
.navbar-brand-apple {
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.6px;
  color: #1d1d1f;
  text-decoration: none;
  transition: opacity 0.2s ease;
}
.navbar-brand-apple:hover {
  opacity: 0.8;
}
.brand-gradient {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-right: 2px;
}

/* 3. IOS-STYLE SEGMENTED NAVIGATION CAPSULE */
.nav-capsule-wrapper {
  background-color: rgba(0, 0, 0, 0.04);
  padding: 4px;
  border-radius: 30px;
}

.nav-link-apple {
  color: #515154;
  font-size: 0.88rem;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 20px;
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Hover State */
.nav-link-apple:hover {
  color: #1d1d1f;
  background-color: rgba(0, 0, 0, 0.02);
}

/* Native Vue Active Link State mimicking native Apple tab selection sliding cards */
.nav-link-apple.router-link-active {
  background-color: #ffffff !important;
  color: #1d1d1f !important;
  font-weight: 600;
  box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.06), 0px 0px 1px rgba(0, 0, 0, 0.04);
}

/* 4. SLEEK LOGOUT INTERACTION */
.v-divider {
  width: 1px;
  height: 20px;
  background-color: rgba(0, 0, 0, 0.12);
  align-self: center;
}

.btn-logout-apple {
  background: none;
  border: none;
  color: #e11d48; /* Sophisticated structural iOS Red */
  font-size: 0.88rem;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 20px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
}

.btn-logout-apple:hover {
  background-color: rgba(225, 29, 72, 0.08);
}

.main-content {
  padding-top: 24px;
}
</style>