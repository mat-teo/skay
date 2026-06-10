<template>
  <div class="dashboard-root">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <span class="header-eyebrow">Welcome back</span>
        <h1 class="page-title">Dashboard</h1>
      </div>
    </header>

    <!-- Stats Overview - Full width -->
    <div class="stats-row">
      <StatsOverview ref="statsOverview" @filter-changed="handleFilterChange" />
    </div>

    <!-- Main Dashboard Grid -->
    <div class="dashboard-grid">

      <!-- Left column: Accounts + Net Worth Chart -->
      <div class="col-left">
        <div class="widget-stack">
          <AccountsList ref="accountsList" />
          <NetWorthChart ref="netWorthChart" :startDate="startDate" :endDate="endDate" />
        </div>
      </div>

      <!-- Right column: Expense Pie Chart + Recent Transactions -->
      <div class="col-right">
        <div class="widget-stack">
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
/* ── Root ── */
.dashboard-root {
  padding: 2rem 2.5rem 3rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* ── Header ── */
.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #e8e8ed;
}

.header-eyebrow {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6e6e80;
  margin-bottom: 0.35rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.6px;
  color: #111118;
  margin: 0;
  line-height: 1.1;
}

/* ── Stats row ── */
.stats-row {
  margin-bottom: 2rem;
}

/* ── Main 2-column grid ── */
.dashboard-grid {
  display: grid;
  grid-template-columns: 5fr 7fr;
  gap: 1.5rem;
  align-items: start;
}

/* ── Widget stacks inside each column ── */
.widget-stack {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Cards inside widgets: uniform look ── */
.col-left :deep(.card),
.col-right :deep(.card) {
  border: 1px solid #e8e8ed;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  background: #fff;
  transition: box-shadow 0.2s ease;
}

.col-left :deep(.card:hover),
.col-right :deep(.card:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.col-left :deep(.card-header),
.col-right :deep(.card-header) {
  background: transparent;
  border-bottom: 1px solid #f0f0f5;
  padding: 1.1rem 1.4rem 1rem;
  font-weight: 600;
  font-size: 0.92rem;
  color: #111118;
}

.col-left :deep(.card-body),
.col-right :deep(.card-body) {
  padding: 1.25rem 1.4rem;
}

/* ── Canvas: prevent charts from overflowing ── */
.col-left :deep(canvas),
.col-right :deep(canvas) {
  max-height: 260px;
  width: 100% !important;
}

/* ── Table inside Recent Transactions ── */
.col-right :deep(.table) {
  font-size: 0.875rem;
}

.col-right :deep(.table thead th) {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #8e8ea0;
  border-bottom: 1px solid #e8e8ed;
  padding-bottom: 0.6rem;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .dashboard-root {
    padding: 1.25rem 1rem 2rem;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>