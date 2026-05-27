<template>
  <div>
    <!-- Mostra login se NON loggato -->
    <Login v-if="!isLoggedIn" @login-success="handleLoginSuccess" />

    <!-- Mostra dashboard SE loggato -->
    <div v-else>
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

export default {
  name: 'App',
  components: { AccountsList, TransactionsList, StatsOverview, Login },
  data() {
    return {
      isLoggedIn: false,
      currentFilters: { start_date: null, end_date: null }
    }
  },
  mounted() {
    const token = localStorage.getItem('token')
    this.isLoggedIn = !!token
  },
  methods: {
    handleLoginSuccess() {
      this.isLoggedIn = true
    },
    handleLogout() {
      localStorage.removeItem('token')
      this.isLoggedIn = false
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