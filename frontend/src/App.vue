<template>
  <div>
    <ToastNotification ref="toast" />
    
    <!-- Auth Views (Login/Register) -->
    <Login 
      v-if="showLogin" 
      @login-success="handleLoginSuccess"
      @show-register="showLogin = false; showRegister = true" 
    />

    <Register
      v-if="showRegister"
      @login-success="handleLoginSuccess"
    />

    <!-- Main App (when logged in) -->
    <div v-if="isLoggedIn">
      <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container">
          <a class="navbar-brand fw-bold" href="#">Skay Finance</a>
          <div class="d-flex">
            <button 
              class="btn btn-outline-light me-2" 
              :class="{ 'active': currentView === 'dashboard' }"
              @click="currentView = 'dashboard'"
            >
              Dashboard
            </button>
            <button 
              class="btn btn-outline-light me-3" 
              :class="{ 'active': currentView === 'stats' }"
              @click="currentView = 'stats'"
            >
              Advanced Stats
            </button>
            <button class="btn btn-outline-light" @click="handleLogout">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main class="container">
        <Dashboard v-if="currentView === 'dashboard'" ref="dashboard" />
        <AdvancedStats v-else-if="currentView === 'stats'" />
      </main>
    </div>
  </div>
</template>

<script>
import Login from './components/Login.vue';
import Register from './components/Register.vue';
import Dashboard from './components/Dashboard.vue';
import AdvancedStats from './components/advanced-stats/AdvancedStats.vue';
import ToastNotification from './components/ToastNotification.vue';

export default {
  name: 'App',
  components: { Login, Register, Dashboard, AdvancedStats, ToastNotification },
  data() {
    return {
      isLoggedIn: false,
      showLogin: true,
      showRegister: false,
      currentView: 'dashboard'
    }
  },
  mounted() {
    const token = localStorage.getItem('token');
    this.isLoggedIn = !!token;
    if (this.isLoggedIn) {
      this.showLogin = false;
      this.showRegister = false;
    }
  },
  methods: {
    showToast(message, type) {
      this.$refs.toast.show(message, type);
    },
    handleLoginSuccess() {
      this.isLoggedIn = true;
      this.showLogin = false;
      this.showRegister = false;
      this.showToast('Login successful!', 'success');
    },
    handleLogout() {
      localStorage.removeItem('token');
      this.isLoggedIn = false;
      this.showLogin = true;
      this.showRegister = false;
      this.showToast('Logged out successfully', 'info');
    }
  }
}
</script>

<style scoped>
.btn-outline-light.active {
  background-color: white;
  color: #212529;
}
</style>