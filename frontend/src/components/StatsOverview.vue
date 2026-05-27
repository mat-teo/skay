<template>
  <div>
    <div class="d-flex flex-wrap gap-2 mb-4 bg-light p-2 rounded shadow-sm align-items-center">
      <span class="text-muted small fw-bold text-uppercase ms-2 me-2">Timeframe:</span>
      <button v-for="filter in timeFilters" 
              :key="filter.id" 
              class="btn btn-sm"
              :class="activeFilter === filter.id ? 'btn-dark' : 'btn-outline-dark'"
              @click="setFilter(filter.id)">
        {{ filter.label }}
      </button>
      
      <span class="ms-auto me-2 badge bg-secondary px-3 py-2 text-capitalize">
        Active Period: {{ activePeriodLabel }}
      </span>
    </div>

    <div class="row mb-4">
      <div class="col-12 col-md-4 mb-3">
        <div class="card border-start border-success border-4 shadow-sm">
          <div class="card-body">
            <h6 class="card-title text-muted text-uppercase small font-weight-bold">Income</h6>
            <h3 class="text-success mb-0">{{ stats.total_income.toFixed(2) }} €</h3>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4 mb-3">
        <div class="card border-start border-danger border-4 shadow-sm">
          <div class="card-body">
            <h6 class="card-title text-muted text-uppercase small font-weight-bold">Expenses</h6>
            <h3 class="text-danger mb-0">{{ stats.total_expense.toFixed(2) }} €</h3>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4 mb-3">
        <div class="card border-start border-primary border-4 shadow-sm" :class="savingsBorderClass(stats.net_savings)">
          <div class="card-body">
            <h6 class="card-title text-muted text-uppercase small font-weight-bold">Net Savings</h6>
            <h3 class="mb-0" :class="savingsTextClass(stats.net_savings)">
              {{ stats.net_savings.toFixed(2) }} €
            </h3>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'StatsOverview',
  data() {
    return {
      stats: { total_income: 0.0, total_expense: 0.0, net_savings: 0.0 },
      activeFilter: 'month', // Default to current month as requested
      timeFilters: [
        { id: 'day', label: 'Today' },
        { id: 'week', label: 'This Week' },
        { id: 'month', label: 'This Month' },
        { id: 'year', label: 'This Year' },
        { id: 'all', label: 'All Time' }
      ]
    };
  },
  computed: {
    activePeriodLabel() {
      const now = new Date();
      if (this.activeFilter === 'month') return now.toLocaleString('default', { month: 'long', year: 'numeric' });
      if (this.activeFilter === 'year') return now.getFullYear().toString();
      return this.activeFilter;
    }
  },
  mounted() {
    this.fetchStats();
  },
  methods: {
    getDateRange() {
      const now = new Date();
      let start = null;
      let end = null;

      switch (this.activeFilter) {
        case 'day':
          start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
          break;
        case 'week':
          const day = now.getDay();
          const diff = now.getDate() - day + (day === 0 ? -6 : 1); // Adjust to Monday
          start = new Date(now.setDate(diff));
          start.setHours(0,0,0,0);
          break;
        case 'month':
          start = new Date(now.getFullYear(), now.getMonth(), 1);
          break;
        case 'year':
          start = new Date(now.getFullYear(), 0, 1);
          break;
        case 'all':
        default:
          return { start_date: null, end_date: null };
      }

      // Format to ISO string for API compatibility
      return {
        start_date: start ? start.toISOString() : null,
        end_date: end ? end.toISOString() : null
      };
    },
    async fetchStats() {
      try {
        const { start_date, end_date } = this.getDateRange();
        let url = 'http://127.0.0.1:8000/api/transactions/stats';
        
        if (start_date) url += `&start_date=${start_date}`;
        
        const response = await axios.get(url);
        this.stats = response.data;
        
        // Pass the updated dates up to App.vue so the transaction log can sync its filters too
        this.$emit('filter-changed', { start_date, end_date });
      } catch (err) {
        console.error('Failed to fetch financial stats:', err);
      }
    },
    setFilter(filterId) {
      this.activeFilter = filterId;
      this.fetchStats();
    },
    savingsTextClass(savings) {
      return { 'text-success': savings > 0, 'text-danger': savings < 0, 'text-primary': savings === 0 };
    },
    savingsBorderClass(savings) {
      return { 'border-success': savings > 0, 'border-danger': savings < 0, 'border-primary': savings === 0 };
    }
  }
};
</script>