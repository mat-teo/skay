<template>
  <div>
    <nav class="navbar navbar-dark bg-dark mb-4">
      <div class="container">
        <a class="navbar-brand fw-bold" href="#">Skay Finance</a>
        <div class="d-flex align-items-center">
          <span class="text-white me-3">{{ userEmail }}</span>
          <button class="btn btn-outline-light btn-sm" @click="handleLogout">
            Logout
          </button>
        </div>
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
</template>

<script>
import AccountsList from './components/AccountsList.vue';
import TransactionsList from './components/TransactionsList.vue';
import StatsOverview from './components/StatsOverview.vue';
import { auth } from './auth';

export default {
  name: 'App',
  components: { AccountsList, TransactionsList, StatsOverview },
  data() {
    return {
      currentFilters: { start_date: null, end_date: null },
      userEmail: ''
    }
  },
  computed: {
    currentUserId() {
      // Decode JWT to get user ID? Or store in state
      const token = auth.getToken()
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]))
          return payload.sub
        } catch {
          return null
        }
      }
      return null
    }
  },
  mounted() {
    // Set user email (you might want to fetch from API)
    // For now, you could decode from token or fetch from /me endpoint
  },
  methods: {
    handleFilterChange(filters) {
      this.currentFilters = filters;
      if (this.$refs.transactionsList) {
        this.$refs.transactionsList.fetchTransactions(filters.start_date);
      }
    },
    refreshDashboardData() {
      if (this.$refs.accountsList) this.$refs.accountsList.fetchAccounts();
      if (this.$refs.statsOverview) this.$refs.statsOverview.fetchStats();
    },
    handleLogout() {
      auth.logout()
    }
  }
}
</script>