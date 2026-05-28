<template>
  <div>
    
    <Login v-if="showLogin" 
    @login-success="handleLoginSuccess"
    @show-register="showLogin = false; showRegister= true" />

    <Register
      v-if="showRegister"
      @login-success="handleLoginSuccess"
      />

    <div v-if="isLoggedIn">
      <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container">
          <a class="navbar-brand fw-bold" href="#">Skay Finance</a>
          <button class="btn btn-outline-light btn-sm" @click="handleLogout">
            Logout
          </button>
        </div>
      </nav>

      <main class="container">
        <StatsOverview ref="statsOverview" @filter-changed="handleFilterChange" />

        <div class="row">
          <div class="col-12 col-lg-5 mb-4">
            <AccountsList ref="accountsList" />
          </div>
          
          <div class="col-12 col-lg-7 mb-4">
            <TransactionsList ref="transactionsList" :dateFilters="currentFilters" @transaction-saved="refreshDashboardData" />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import AccountsList from './components/AccountsList.vue';
import TransactionsList from './components/TransactionsList.vue';
import StatsOverview from './components/StatsOverview.vue';
import Login from './components/Login.vue';
import Register from './components/Register.vue';

export default {
  name: 'App',
  components: { AccountsList, TransactionsList, StatsOverview, Login, Register },
  data() {
    return {
      isLoggedIn: false,
      showLogin: true,
      showRegister: false,
      currentFilters: { start_date: null, end_date: null }
    }
  },
  mounted() {
    const token = localStorage.getItem('token')
    this.isLoggedIn = !!token
    if(this.isLoggedIn){
      this.showLogin = false
      this.showRegister = false
    }
  },
  methods: {
    handleLoginSuccess() {
      this.isLoggedIn = true
      this.showLogin = false
      this.showRegister = false
    },
    handleLogout() {
      localStorage.removeItem('token')
      this.isLoggedIn = false
      this.showLogin = true
      this.showRegister = false
    },
    handleFilterChange(filters) {
      this.currentFilters = filters;
      if (this.$refs.transactionsList) {
        this.$refs.transactionsList.fetchTransactions(filters.start_date);
      }
    },
    refreshDashboardData() {
      if (this.$refs.accountsList) this.$refs.accountsList.fetchAccounts();
      if (this.$refs.statsOverview) this.$refs.statsOverview.fetchStats();
    }
  }
}
</script>