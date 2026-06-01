<template>
  <div class="card h-100">
    <div class="card-header">
      <h6 class="mb-0">{{ title }}</h6>
    </div>
    <div class="card-body">
      <canvas ref="chartCanvas"></canvas>
      <div v-if="!hasData" class="text-center text-muted py-5">
        No data for this period
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'CategoryPieChart',
  props: {
    title: { type: String, default: 'Category Breakdown' },
    type: { type: String, required: true, validator: v => ['income', 'expense'].includes(v) },
    startDate: { type: String, default: '' },
    endDate: { type: String, default: '' }
  },
  data() {
    return {
      chart: null,
      hasData: false
    }
  },
  mounted() {
    this.fetchData()
  },
  watch: {
    startDate() { this.fetchData() },
    endDate() { this.fetchData() }
  },
  beforeUnmount() {
    if (this.chart) this.chart.destroy()
  },
  methods: {
    async fetchData() {
      try {
        // Fetch transactions
        let url = 'http://127.0.0.1:8000/api/transactions'
        const params = new URLSearchParams()
        if (this.startDate) params.append('start_date', this.startDate)
        if (this.endDate) params.append('end_date', this.endDate)
        if (params.toString()) url += `?${params.toString()}`
        
        const transactionsRes = await axios.get(url)
        const categoriesRes = await axios.get('http://127.0.0.1:8000/api/categories')
        
        const transactions = transactionsRes.data
        const categories = categoriesRes.data
        
        // Filter by type and aggregate by category
        const filtered = transactions.filter(t => t.type === this.type)
        const categoryMap = new Map()
        
        filtered.forEach(tx => {
          const cat = categories.find(c => c.id === tx.category_id)
          const catName = cat?.name || 'Uncategorized'
          categoryMap.set(catName, (categoryMap.get(catName) || 0) + tx.amount)
        })
        
        this.hasData = categoryMap.size > 0
        
        // Colors for chart
        const colors = [
          '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
          '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#3b82f6',
          '#8b5cf6', '#d946ef', '#ec4899', '#f43f5e'
        ]
        
        this.renderChart(categoryMap, colors)
      } catch (err) {
        console.error('Failed to fetch category data:', err)
      }
    },
    
    renderChart(categoryMap, colors) {
      const canvas = this.$refs.chartCanvas
      if (!canvas) return
      
      if (this.chart) {
        this.chart.destroy()
      }
      
      const labels = Array.from(categoryMap.keys())
      const data = Array.from(categoryMap.values())
      
      const ctx = canvas.getContext('2d')
      this.chart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors.slice(0, labels.length),
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { position: 'right', labels: { font: { size: 11 } } },
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const total = data.reduce((a, b) => a + b, 0)
                  const percentage = ((ctx.parsed / total) * 100).toFixed(1)
                  return `${ctx.label}: € ${ctx.parsed.toFixed(2)} (${percentage}%)`
                }
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