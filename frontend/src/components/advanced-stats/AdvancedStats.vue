<template>
  <div class="advanced-stats">
    <h2 class="mb-4 text-black"> Advanced Statistics</h2>
    
    <!-- Date Range Picker -->
    <DateRangePicker
      v-model:startDate="filters.startDate"
      v-model:endDate="filters.endDate"
      @change="onDateRangeChange"
    />
    
    <!-- Stats Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card border-success">
          <div class="card-body">
            <h6 class="text-muted">Total Income</h6>
            <h3 class="text-success">{{ totalIncome.toFixed(2) }} €</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-danger">
          <div class="card-body">
            <h6 class="text-muted">Total Expenses</h6>
            <h3 class="text-danger">{{ totalExpense.toFixed(2) }} €</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card" :class="savingsClass">
          <div class="card-body">
            <h6 class="text-muted">Net Savings</h6>
            <h3 :class="savingsTextClass">{{ netSavings.toFixed(2) }} €</h3>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Charts Grid -->
    <div class="row g-4">
      
      <!-- Category Breakdowns -->
      <div class="col-md-6">
        <CategoryPieChart 
          title="Expenses by Category"
          type="expense"
          :startDate="filters.startDate"
          :endDate="filters.endDate"
        />
      </div>
      <div class="col-md-6">
        <CategoryPieChart 
          title="Income by Category"
          type="income"
          :startDate="filters.startDate"
          :endDate="filters.endDate"
        />
      </div>
      
      <!-- Monthly Comparison -->
      <div class="col-12">
        <MonthlyBarChart 
          :startDate="filters.startDate"
          :endDate="filters.endDate"
        />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import DateRangePicker from './DateRangePicker.vue';
import CategoryPieChart from './CategoryPieChart.vue';
import MonthlyBarChart from './MonthlyBarChart.vue';

export default {
  name: 'AdvancedStats',
  components: { DateRangePicker, CategoryPieChart, MonthlyBarChart },
  data() {
    return {
      filters: {
        startDate: '',
        endDate: ''
      },
      totalIncome: 0,
      totalExpense: 0
    }
  },
  computed: {
    netSavings() {
      return this.totalIncome - this.totalExpense
    },
    savingsClass() {
      if (this.netSavings > 0) return 'border-success'
      if (this.netSavings < 0) return 'border-danger'
      return 'border-secondary'
    },
    savingsTextClass() {
      if (this.netSavings > 0) return 'text-success'
      if (this.netSavings < 0) return 'text-danger'
      return 'text-secondary'
    }
  },
  mounted() {
    // Set default range: current month
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    this.filters.startDate = start.toISOString().split('T')[0]
    this.filters.endDate = now.toISOString().split('T')[0]
    
    this.fetchTotals()
  },
  methods: {
    async fetchTotals() {
      try {
        let url = 'http://127.0.0.1:8000/api/transactions/stats'
        const params = new URLSearchParams()
        if (this.filters.startDate) params.append('start_date', this.filters.startDate)
        if (this.filters.endDate) params.append('end_date', this.filters.endDate)
        if (params.toString()) url += `?${params.toString()}`
        console.log('Fetching stats from:', url) 
        const response = await axios.get(url)
        console.log('Stats response:', response.data)
        this.totalIncome = response.data.total_income
        this.totalExpense = response.data.total_expense
      } catch (err) {
        console.error('Failed to fetch totals:', err)
      }
    },
    
    onDateRangeChange() {
      this.fetchTotals()
    }
  }
}
</script>

<style scoped>
.advanced-stats {
  padding: 20px;
}
</style>