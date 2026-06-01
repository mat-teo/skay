<template>
  <div>
    <StatsOverview ref="statsOverview" @filter-changed="handleFilterChange" />

    <NetWorthChart ref="netWorthChart" class="mb-4" />

    <div class="row">
      <div class="col-12 col-lg-5 mb-4">
        <AccountsList ref="accountsList" />
      </div>
      
      <div class="col-12 col-lg-7 mb-4">
        <TransactionsList 
          ref="transactionsList" 
          :dateFilters="currentFilters" 
          @transaction-saved="refreshDashboardData" 
        />
      </div>
    </div>
  </div>
</template>

<script>
import AccountsList from './AccountsList.vue';
import TransactionsList from './TransactionsList.vue';
import StatsOverview from './StatsOverview.vue';
import NetWorthChart from './NetWorthChart.vue';

export default {
  name: 'Dashboard',
  components: { AccountsList, TransactionsList, StatsOverview, NetWorthChart },
  data() {
    return {
      currentFilters: { start_date: null, end_date: null }
    }
  },
  methods: {
    handleFilterChange(filters) {
      this.currentFilters = filters;
      this.$nextTick(() => {
        if (this.$refs.transactionsList) {
          this.$refs.transactionsList.fetchTransactions(filters.start_date);
        }
      });
    },
    refreshDashboardData() {
      if (this.$refs.accountsList) this.$refs.accountsList.fetchAccounts();
      if (this.$refs.statsOverview) this.$refs.statsOverview.fetchStats();
      if (this.$refs.netWorthChart) this.$refs.netWorthChart.refresh();
    }
  }
}
</script>