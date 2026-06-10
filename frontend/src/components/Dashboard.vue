<template>
  <div>
    <!-- Header -->
    <header class="page-header mb-4 pb-2">
      <div>
        <span class="text-uppercase text-primary fw-bold small-caps">Welcome back</span>
        <h1 class="page-title mt-1 mb-0">Dashboard</h1>
      </div>
    </header>

    <!-- Stats Overview - Full width -->
    <StatsOverview ref="statsOverview" @filter-changed="handleFilterChange" />

    <!-- Main Dashboard Grid -->
    <div class="row g-4 mt-1">
      
      <!-- Left column: Accounts + Net Worth Chart -->
      <div class="col-12 col-lg-5">
        <div class="d-flex flex-column gap-4">
          <AccountsList ref="accountsList" />
          <NetWorthChart ref="netWorthChart" :startDate="startDate" :endDate="endDate" />
        </div>
      </div>
      
      <!-- Right column: Expense Pie Chart + Recent Transactions -->
      <div class="col-12 col-lg-7">
        <div class="d-flex flex-column gap-4">
          <ExpensePieChart :startDate="startDate" :endDate="endDate" ref="pieChart" />
          <RecentTransactions :startDate="startDate" :endDate="endDate" :limit="6" />
        </div>
      </div>
      
    </div>
  </div>
</template>

<script>
import AccountsList from './AccountsList.vue';
import StatsOverview from './StatsOverview.vue';
import NetWorthChart from './NetWorthChart.vue';
import ExpensePieChart from './dashboard/ExpensePieChart.vue';
import RecentTransactions from './dashboard/RecentTransactions.vue';

export default {
  name: 'Dashboard',
  components: {
    AccountsList,
    StatsOverview,
    NetWorthChart,
    ExpensePieChart,
    RecentTransactions
  },
  data() {
    return {
      currentFilters: { start_date: null, end_date: null },
      startDate: '',
      endDate: ''
    };
  },
  methods: {
    handleFilterChange(filters) {
      this.currentFilters = filters;
      this.startDate = filters.start_date;
      this.endDate = filters.end_date;
      
      // Refresh child components that need to react to date change
      this.$nextTick(() => {
        if (this.$refs.pieChart) this.$refs.pieChart.refresh();
        if (this.$refs.netWorthChart) this.$refs.netWorthChart.refresh();
      });
    },
    
    refreshDashboardData() {
      if (this.$refs.accountsList) this.$refs.accountsList.fetchAccounts();
      if (this.$refs.statsOverview) this.$refs.statsOverview.fetchStats();
      if (this.$refs.netWorthChart) this.$refs.netWorthChart.refresh();
      if (this.$refs.pieChart) this.$refs.pieChart.refresh();
    }
  }
};
</script>

<style scoped>
.small-caps {
  font-size: 0.75rem;
  letter-spacing: 0.08em;
}

.page-title {
  font-size: 1.85rem;
  font-weight: 700;
  letter-spacing: -0.8px;
  color: #1d1d1f;
}
</style>