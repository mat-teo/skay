<template>
  <div>
    
    <div class="d-flex flex-wrap gap-2 mb-4 bg-light p-2 rounded shadow-sm align-items-center">
      <span class="text-muted small fw-bold text-uppercase ms-2 me-2">Period:</span>
      
      <select class="form-select form-select-sm w-auto" v-model="periodType">
        <option value="day">Day</option>
        <option value="week">Week</option>
        <option value="month">Month</option>
        <option value="year">Year</option>
      </select>
      
      <div class="btn-group" role="group">
        <button class="btn btn-sm btn-outline-secondary" @click="navigatePeriod(-1)">← Prev</button>
        <button class="btn btn-sm btn-outline-secondary" @click="navigatePeriod(1)">Next →</button>
      </div>
      
      <span class="ms-auto badge bg-secondary px-3 py-2">
        {{ periodLabel }}
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
      periodType: 'month', // Default to current month 
      currentOffset: 0,
    };
  },
  computed: {
    periodLabel() {
      const now = new Date();
      const targetDate = new Date(now);
      
      // Apply offset based on period type
      switch(this.periodType) {
        case 'day':
          targetDate.setDate(now.getDate() + this.currentOffset);
          return targetDate.toLocaleDateString('default', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          });
        case 'week':
          const weekNumber = this.getWeekNumber(targetDate);
          const year = targetDate.getFullYear();
          return `Week ${weekNumber + this.currentOffset}, ${year}`;
        case 'month':
          targetDate.setMonth(now.getMonth() + this.currentOffset);
          return targetDate.toLocaleDateString('default', { 
            month: 'long', 
            year: 'numeric' 
          });
        case 'year':
          return (targetDate.getFullYear() + this.currentOffset).toString();
        default:
          return 'Custom';
      }
    }
  },
  watch:{
    periodType(){
      this.currentOffset = 0;  // Reset the offset when period type changes
      this.fetchStats();       // Fetch new stats
    }
  },
  mounted() {
    this.fetchStats();
  },
  methods: {
    getWeekNumber(date){
      const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
      const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
      return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1)/ 7);
    },
    getDateRange() {
      const now = new Date();
      let start = null;
      let end = null;

      switch (this.periodType) {
        case 'day':
          const dayDate = new Date(now);
          dayDate.setDate(now.getDate() + this.currentOffset);
          start = new Date(dayDate.getFullYear(), dayDate.getMonth(), dayDate.getDate());
          end = new Date(start);
          end.setDate(start.getDate() + 1);
          break;
          
        case 'week':
          const weekDate = new Date(now);
          weekDate.setDate(now.getDate() + (this.currentOffset * 7));
          const dayOfWeek = weekDate.getDay();
          const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
          start = new Date(weekDate);
          start.setDate(weekDate.getDate() + diffToMonday);
          start.setHours(0, 0, 0, 0);
          end = new Date(start);
          end.setDate(start.getDate() + 7);
          break;
          
        case 'month':
          const monthDate = new Date(now);
          monthDate.setMonth(now.getMonth() + this.currentOffset);
          start = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
          end = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 1);
          break;
          
        case 'year':
          const year = now.getFullYear() + this.currentOffset;
          start = new Date(year, 0, 1);
          end = new Date(year + 1, 0, 1);
          break;
      }

      // Format to ISO string for API compatibility
      return {
        start_date: start ? start.toISOString() : null,
        end_date: end ? end.toISOString() : null
      };
    },
    navigatePeriod(direction) {
      this.currentOffset += direction;
      this.fetchStats();
    },
    async fetchStats() {
      try {
        const { start_date, end_date } = this.getDateRange();
        let url = 'http://127.0.0.1:8000/api/transactions/stats';
        
        if (start_date) url += `?start_date=${start_date}`;
        if(end_date) url += `${start_date ? '&' : '?'}end_date=${encodeURIComponent(end_date)}`;
        
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