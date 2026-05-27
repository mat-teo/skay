<template>
  <div>
    <nav class="navbar navbar-dark bg-dark mb-4">
      <div class="container">
        <a class="navbar-brand fw-bold" href="#">Skay Finance</a>
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

export default {
  name: 'App',
  components: { AccountsList, TransactionsList, StatsOverview },
  data() {
    return {
      currentFilters: { start_date: null, end_date: null }
    };
  },
  methods: {
    handleFilterChange(filters) {
      this.currentFilters = filters;
      // Trigger a refresh on the transactions list with the new date scope
      if (this.$refs.transactionsList) {
        this.$refs.transactionsList.fetchTransactions(filters.start_date);
      }
    },
    refreshDashboardData() {
      if (this.$refs.accountsList) this.$refs.accountsList.fetchAccounts();
      if (this.$refs.statsOverview) this.$refs.statsOverview.fetchStats();
    }
  }
};
</script>