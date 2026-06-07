<template>
  <div class="advanced-stats">
    <h2 class="mb-4 text-black"> Advanced Statistics</h2>
    
    <!-- Date Range Picker -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-5">
            <label class="form-label">Start Date</label>
            <input type="date" class="form-control" v-model="tempStartDate">
          </div>
          <div class="col-md-5">
            <label class="form-label">End Date</label>
            <input type="date" class="form-control" v-model="tempEndDate">
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary w-100" @click="applyFilters">Apply</button>
          </div>
        </div>
        
        <div class="row mt-3">
          <div class="col-12">
            <div class="btn-group btn-group-sm" role="group">
              <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('month')">Last Month</button>
              <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('quarter')">Last Quarter</button>
              <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('year')">Last Year</button>
              <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('all')">All Time</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Net Worth Chart -->
    <NetWorthChart
      :key="`networth-${activeStartDate}-${activeEndDate}`"
      :startDate="activeStartDate"
      :endDate="activeEndDate"
      ref="netWorthChart"
    />
    
    <!-- Category Breakdown -->
    <CategoryBreakdown
      :key="`category-${categoryType}-${activeStartDate}-${activeEndDate}`"
      v-model:type="categoryType"
      :startDate="activeStartDate"
      :endDate="activeEndDate"
      ref="categoryChart"
    />

    
    <!-- Period Comparison -->
    <PeriodComparison />
  </div>
</template>

<script>
import NetWorthChart from '../NetWorthChart.vue'
import CategoryBreakdown from './CategoryBreakdown.vue'
import PeriodComparison from './PeriodComparison.vue';


export default {
  name: 'AdvancedStats',
  components: { NetWorthChart, CategoryBreakdown, PeriodComparison },
  data() {
    return {
      // Temporary values (what user sees in inputs)
      tempStartDate: '',
      tempEndDate: '',
      // Active values (what charts actually use)
      activeStartDate: '',
      activeEndDate: '',
      categoryType: 'expense'
    }
  },
  mounted() {
    // Set default dates: last 6 months
    const end = new Date()
    const start = new Date()
    start.setMonth(end.getMonth() - 6)
    
    const startStr = start.toISOString().split('T')[0]
    const endStr = end.toISOString().split('T')[0]
    
    this.tempStartDate = startStr
    this.tempEndDate = endStr
    this.activeStartDate = startStr
    this.activeEndDate = endStr
  },
  methods: {
    applyFilters() {
      // Only update active dates when Apply is clicked
      this.activeStartDate = this.tempStartDate
      this.activeEndDate = this.tempEndDate
    },
    
    setQuickRange(range) {
      const end = new Date()
      const start = new Date()
      
      switch(range) {
        case 'month':
          start.setMonth(end.getMonth() - 1)
          break
        case 'quarter':
          start.setMonth(end.getMonth() - 3)
          break
        case 'year':
          start.setFullYear(end.getFullYear() - 1)
          break
        case 'all':
          this.tempStartDate = ''
          this.tempEndDate = ''
          this.applyFilters()
          return
      }
      
      this.tempStartDate = start.toISOString().split('T')[0]
      this.tempEndDate = end.toISOString().split('T')[0]
      this.applyFilters()
    }
  }
}
</script>

<style scoped>
.advanced-stats {
  padding-bottom: 40px;
}
</style>