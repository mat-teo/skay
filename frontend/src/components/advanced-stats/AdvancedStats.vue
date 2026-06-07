<template>
  <div class="stats-page-wrapper">
    <header class="page-header d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4 pb-2">
      <div>
        <span class="text-uppercase text-primary fw-bold tracking-wider small-caps">Analytics Workspace</span>
        <h1 class="page-title mt-1 mb-0">Advanced Statistics</h1>
      </div>
      
      <div class="d-flex flex-wrap align-items-center gap-2 core-controls">
        <div class="global-date-capsule d-flex align-items-center">
          <div class="date-input-group">
            <span class="input-inline-label">From</span>
            <input type="date" class="form-control blank-input" v-model="globalFilters.start" />
          </div>
          <div class="date-divider"></div>
          <div class="date-input-group">
            <span class="input-inline-label">To</span>
            <input type="date" class="form-control blank-input" v-model="globalFilters.end" />
          </div>
        </div>

        <button class="btn-refresh-master" @click="refreshAllCharts" title="Sync all widgets">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </header>

    <div class="row g-4">
      
      <div class="col-12">
        <div class="dashboard-card-wrapper">
          <NetWorthChart ref="netWorthChart" :start-date="globalFilters.start" :end-date="globalFilters.end" />
        </div>
      </div>

      <div class="col-lg-5">
        <div class="dashboard-card-wrapper h-100">
          <CategoryBreakdown ref="categoryChart" :start-date="globalFilters.start" :end-date="globalFilters.end" />
        </div>
      </div>

      <div class="col-lg-7">
        <div class="dashboard-card-wrapper h-100">
          <PeriodComparison ref="comparisonChart" />
        </div>
      </div>

    </div>
  </div>
</template>

<script>
// Importing fortified child components
import NetWorthChart from '../NetWorthChart.vue';
import CategoryBreakdown from "./CategoryBreakdown.vue";
import PeriodComparison from './PeriodComparison.vue';

export default {
  name: 'AdvancedStats',
  components: {
    NetWorthChart,
    CategoryBreakdown,
    PeriodComparison
  },
  data() {
    return {
      // Global reactive date filtering objects synchronized down to chart nodes
      globalFilters: {
        start: '',
        end: ''
      }
    };
  },
  mounted() {
    this.initializeDefaultDates();
  },
  methods: {
    // Populate smart lookback defaults on initial canvas setup (e.g., current year-to-date baseline)
    initializeDefaultDates() {
      const now = new Date();
      const currentYear = now.getFullYear();
      
      // Default: From Jan 1st of the current year until today
      this.globalFilters.start = `${currentYear}-01-01`;
      this.globalFilters.end = now.toISOString().split('T')[0];
    },

    // Master sync routine to safely trigger child component refreshers manually
    refreshAllCharts() {
      this.$refs.netWorthChart?.refresh();
      this.$refs.categoryChart?.refresh();
      this.$refs.comparisonChart?.fetchComparison();
    }
  }
};
</script>

<style scoped>
/* Core layout baseline padding adjustment */
.stats-page-wrapper {
  padding-bottom: 60px;
  animation: fadeInPage 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Typography & Layout Header Tokens */
.page-title {
  font-size: 1.85rem;
  font-weight: 700;
  letter-spacing: -0.8px;
  color: #1d1d1f; /* Native Apple Black */
}

.small-caps {
  font-size: 0.78rem;
  letter-spacing: 0.08em;
}

.tracking-wider {
  letter-spacing: 0.05em;
}

/* APPLE-STYLE GLOBAL DATE PICKER CAPSULE */
.global-date-capsule {
  background-color: rgba(0, 0, 0, 0.04);
  padding: 4px 12px;
  border-radius: 30px;
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.date-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.input-inline-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #86868b;
  text-uppercase: true;
}

/* Clean transparent input styling inside the design capsule */
.blank-input {
  background: transparent !important;
  border: none !important;
  padding: 4px 6px !important;
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  color: #1d1d1f !important;
  width: 130px;
}

.date-divider {
  width: 1px;
  height: 16px;
  background-color: rgba(0, 0, 0, 0.1);
  margin: 0 12px;
}

/* Elegant Apple-Style Sync Button */
.btn-refresh-master {
  background-color: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #515154;
  font-size: 1rem;
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.btn-refresh-master:hover {
  background-color: #f5f5f7;
  color: #1d1d1f;
  transform: rotate(30deg);
}

/* Dashboard Component Container Uniformity Wrapper */
.dashboard-card-wrapper {
  background: #ffffff;
  border-radius: 16px; /* Smooth iOS rounding mechanics */
}

/* Global deep override to force consistent premium styling inside child components */
:deep(.card) {
  border: none !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
  background: #ffffff !important;
  overflow: hidden;
}

:deep(.card-header) {
  background: #ffffff !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04) !important;
  padding: 18px 24px !important;
  font-weight: 600 !important;
  color: #1d1d1f !important;
}

:deep(.card-body) {
  padding: 24px !important;
}


/* Smooth structural entry fade animation for the whole view workspace */
@keyframes fadeInPage {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>