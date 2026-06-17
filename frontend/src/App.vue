<template>
  <div>
    <ToastNotification ref="toast" />
    
    <router-view v-if="!isLoggedIn" @2fa-required="show2FAModal"/>
    
    <div v-if="isLoggedIn" class="app-layout">
      <nav class="navbar navbar-expand-md custom-navbar sticky-top">
        <div class="container">
          <!-- Brand -->
          <router-link class="navbar-brand-apple" to="/dashboard">
            <span class="brand-gradient">Skay</span>Finance
          </router-link>
          
          <!-- Controlli sempre visibili a destra (Dark mode + Hamburger) -->
          <div class="d-flex align-items-center gap-1 order-md-last">
            <!-- Dark Mode Toggle -->
            <button class="btn-darkmode-apple" @click="toggleDarkMode" :title="isDark ? 'Light mode' : 'Dark mode'">
              <i :class="isDark ? 'bi bi-sun-fill' : 'bi bi-moon-fill'"></i>
            </button>

            <!-- Bottone Hamburger (visibile solo su mobile) -->
            <button class="btn-hamburger-apple d-md-none" @click="mobileMenuOpen = !mobileMenuOpen" :aria-expanded="mobileMenuOpen">
              <i :class="mobileMenuOpen ? 'bi bi-x-lg' : 'bi bi-list'"></i>
            </button>
          </div>

          <!-- Menu Collassabile -->
          <div class="collapse navbar-collapse" :class="{ 'show': mobileMenuOpen }">
            <!-- Links di navigazione -->
            <div class="nav-capsule-wrapper d-flex flex-column flex-md-row mx-auto my-3 my-md-0 gap-1 gap-md-0">
              <router-link class="nav-link-apple" to="/dashboard">Dashboard</router-link>
              <router-link class="nav-link-apple" to="/transactions">Transactions</router-link>
              <router-link class="nav-link-apple" to="/stats">Stats</router-link>
              <router-link class="nav-link-apple" to="/categories">Categories</router-link>
              <router-link class="nav-link-apple" to="/budgets">Budgets</router-link>
              <router-link class="nav-link-apple" to="/profile">Profile</router-link>
              <router-link class="nav-link-apple" to="/stocks">Stocks</router-link>
            </div>

            <!-- Area Logout -->
            <div class="logout-wrapper d-flex align-items-center flex-column flex-md-row gap-2 ms-md-2">
              <div class="v-divider d-none d-md-block"></div>
              <button class="btn-logout-apple w-100 w-md-auto justify-content-center" @click="handleLogout">
                <i class="bi bi-box-arrow-right me-1"></i>Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main class="container main-content">
        <router-view />
      </main>

      <GlobalFooter />
    </div>
  </div>
</template>

<script>
import ToastNotification from './components/ToastNotification.vue'
import { auth } from './auth'
import { useDarkMode } from './composables/useDarkMode'
import GlobalFooter from './components/GlobalFooter.vue'
import Login from './components/Login.vue'

import './assets/theme-dark.css'

export default {
  name: 'App',
  components: { Login, ToastNotification, GlobalFooter },
  setup() {
    const { isDark, toggleDarkMode } = useDarkMode();
    return { isDark, toggleDarkMode };
  },
  data() {
    return {
      isLoggedIn: false,
      mobileMenuOpen: false // Gestisce l'apertura/chiusura del menu mobile
    }
  },
  mounted() {
    this.checkAuth()
  },
  watch: {
    '$route'() {
      this.checkAuth();
      this.mobileMenuOpen = false; // Chiude automaticamente il menu al cambio pagina
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
      this.mobileMenuOpen = false
      this.$router.push('/login')
      this.showToast('Logged out successfully', 'info')
    }
  }
}
</script>

<style scoped>
/* Cambiamenti e fix per Mobile Responsive */
@media (max-width: 767.98px) {
  .navbar-collapse {
    width: 100%;
    padding-top: 10px;
  }
  
  /* Rimuove lo sfondo a "capsula" unita su mobile e incolonna i link */
  .nav-capsule-wrapper {
    background-color: transparent !important;
    padding: 0;
    border-radius: 0;
    width: 100%;
  }

  .nav-link-apple {
    width: 100%;
    text-align: left;
    padding: 10px 16px;
    border-radius: 10px;
  }

  /* Rende l'area logout full width su mobile */
  .logout-wrapper {
    width: 100%;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    padding-top: 12px;
    margin-top: 8px;
  }

  .dark-theme .logout-wrapper {
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }

  .btn-logout-apple {
    padding: 10px 16px;
    border-radius: 10px;
  }
}

/* Stili del Bottone Hamburger */
.btn-hamburger-apple {
  background: none;
  border: none;
  color: #515154;
  font-size: 1.4rem;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-hamburger-apple:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.dark-theme .btn-hamburger-apple {
  color: #8e8e93;
}

.dark-theme .btn-hamburger-apple:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

/* Vecchi stili non modificati */
.btn-darkmode-apple {
  background: none;
  border: none;
  color: #515154;
  font-size: 1.1rem;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-darkmode-apple:hover {
  background-color: rgba(0, 0, 0, 0.04);
  transform: scale(1.05);
}

.dark-theme .btn-darkmode-apple {
  color: #8e8e93;
}

.dark-theme .btn-darkmode-apple:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.app-layout {
  min-height: 100vh;
  background-color: #f8f9fa;
  transition: background-color 0.3s ease;
}

.dark-theme .app-layout {
  background-color: #1c1c1e;
}

.custom-navbar {
  background: rgba(255, 255, 255, 0.75) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 12px 0;
  transition: background-color 0.3s ease;
}

.dark-theme .custom-navbar {
  background: rgba(28, 28, 30, 0.85) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.navbar-brand-apple {
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.6px;
  color: #1d1d1f;
  text-decoration: none;
}

.dark-theme .navbar-brand-apple {
  color: #ffffff;
}

.brand-gradient {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-right: 2px;
}

.nav-capsule-wrapper {
  background-color: rgba(0, 0, 0, 0.04);
  padding: 4px;
  border-radius: 30px;
}

.dark-theme .nav-capsule-wrapper {
  background-color: rgba(255, 255, 255, 0.08);
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

.nav-link-apple:hover {
  color: #1d1d1f;
  background-color: rgba(0, 0, 0, 0.02);
}

.dark-theme .nav-link-apple {
  color: #8e8e93;
}

.dark-theme .nav-link-apple:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-link-apple.router-link-active {
  background-color: #ffffff !important;
  color: #1d1d1f !important;
  font-weight: 600;
  box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.06);
}

.dark-theme .nav-link-apple.router-link-active {
  background-color: #3a3a3c !important;
  color: #ffffff !important;
}

.v-divider {
  width: 1px;
  height: 20px;
  background-color: rgba(0, 0, 0, 0.12);
}

.dark-theme .v-divider {
  background-color: rgba(255, 255, 255, 0.12);
}

.btn-logout-apple {
  background: none;
  border: none;
  color: #e11d48;
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

.dark-theme .btn-logout-apple:hover {
  background-color: rgba(225, 29, 72, 0.15);
}

.main-content {
  padding-top: 24px;
}
</style>