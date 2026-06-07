<template>
  <div>
    <StatsOverview ref="statsOverview" @filter-changed="handleFilterChange" />

    <NetWorthChart ref="netWorthChart" class="mb-4" />

    <div class="row">
      <div class="col-12 col-lg-5 mb-4">
        <AccountsList ref="accountsList" />
      </div>
      
    </div>
  </div>
</template>

<script>
import AccountsList from './AccountsList.vue';
import StatsOverview from './StatsOverview.vue';
import NetWorthChart from './NetWorthChart.vue';

export default {
  name: 'Dashboard',
  components: { AccountsList, StatsOverview, NetWorthChart },
  data() {
    return {
      currentFilters: { start_date: null, end_date: null }
    }
  },
  methods: {
    handleFilterChange(filters) {
      this.currentFilters = filters;
    },
    refreshDashboardData() {
      if (this.$refs.accountsList) this.$refs.accountsList.fetchAccounts();
      if (this.$refs.statsOverview) this.$refs.statsOverview.fetchStats();
      if (this.$refs.netWorthChart) this.$refs.netWorthChart.refresh();
    }
  }
}
</script>