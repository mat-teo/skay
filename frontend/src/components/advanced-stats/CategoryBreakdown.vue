<template>
  <div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>Category Breakdown</span>
      <select class="form-select form-select-sm w-auto" v-model="localType">
        <option value="expense">Expenses by Category</option>
        <option value="income">Income by Category</option>
      </select>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary"></div>
      </div>
      <div v-else-if="error" class="alert alert-warning">
        {{ error }}
      </div>
      <div v-else-if="!hasData" class="text-center text-muted py-4">
        No data for selected period
      </div>
      <!-- Canvas sempre presente, nascosto con v-show invece di v-else -->
      <canvas v-show="hasData && !loading" ref="chartCanvas" style="min-height: 300px; width: 100%;"></canvas>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'CategoryBreakdown',
  props: {
    type: { type: String, default: 'expense' },
    startDate: { type: String, default: '' },
    endDate: { type: String, default: '' }
  },
  emits: ['update:type'],
  data() {
    return {
      chart: null,
      loading: false,
      error: null,
      hasData: false,
      localType: this.type
    }
  },
  watch: {
    type(val) { 
      this.localType = val 
    },
    localType(val) {
      this.$emit('update:type', val)
      this.fetchData()
    },
    startDate() { 
      this.fetchData() 
    },
    endDate() { 
      this.fetchData() 
    }
  },
  mounted() {
    this.fetchData()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy()
      this.chart = null
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null
      this.hasData = false
      
      // Destroy existing chart
      if (this.chart) {
        this.chart.destroy()
        this.chart = null
      }
      
      try {
        // Build URL for transactions
        let url = 'http://127.0.0.1:8000/api/transactions'
        const params = new URLSearchParams()
        
        if (this.startDate && this.startDate !== '') {
          params.append('start_date', this.startDate)
        }
        if (this.endDate && this.endDate !== '') {
          params.append('end_date', this.endDate)
        }
        
        if (params.toString()) {
          url += `?${params.toString()}`
        }
        
        const [transactionsRes, categoriesRes] = await Promise.all([
          axios.get(url),
          axios.get('http://127.0.0.1:8000/api/categories')
        ])
        
        const transactions = transactionsRes.data
        const categories = categoriesRes.data
        
        // Filter by type (expense or income)
        const filtered = transactions.filter(t => t.type === this.localType)
        
        // Aggregate by category
        const categoryMap = new Map()
        
        filtered.forEach(tx => {
          const cat = categories.find(c => c.id === tx.category_id)
          const catName = cat?.name || 'Uncategorized'
          const currentAmount = categoryMap.get(catName) || 0
          categoryMap.set(catName, currentAmount + tx.amount)
        })
        
        this.hasData = categoryMap.size > 0
        
        if (this.hasData) {
          // Wait for DOM update (canvas becomes visible)
          await this.$nextTick()
          // Small extra delay to ensure canvas is rendered
          setTimeout(() => {
            this.renderChart(categoryMap)
          }, 50)
        }
      } catch (err) {
        console.error('Failed to load category data:', err)
        this.error = err.message
        this.hasData = false
      } finally {
        this.loading = false
      }
    },
    
    renderChart(categoryMap) {
      const canvas = this.$refs.chartCanvas
      if (!canvas) {
        console.log('Canvas not found, retrying...')
        setTimeout(() => this.renderChart(categoryMap), 100)
        return
      }
      
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
      // Sort by value descending
      const sorted = Array.from(categoryMap.entries()).sort((a, b) => b[1] - a[1])
      const labels = sorted.map(item => item[0])
      const data = sorted.map(item => item[1])
      
      this.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: this.localType === 'expense' ? 'Expenses (€)' : 'Income (€)',
            data: data,
            backgroundColor: this.localType === 'expense' ? '#ef4444' : '#22c55e',
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              position: 'top'
            },
            tooltip: {
              callbacks: {
                label: (ctx) => `€ ${ctx.raw.toFixed(2)}`
              }
            }
          },
          scales: {
            y: {
              ticks: {
                callback: (v) => '€ ' + v.toFixed(2)
              }
            }
          }
        }
      })
    },
    
    refresh() {
      this.fetchData()
    }
  }
}
</script>