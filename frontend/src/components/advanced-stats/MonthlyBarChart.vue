<template>
  <div class="card">
    <div class="card-header">
      <h6 class="mb-0">Monthly Income vs Expenses</h6>
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
  name: 'MonthlyBarChart',
  props: {
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
        let url = 'http://127.0.0.1:8000/api/transactions'
        const params = new URLSearchParams()
        if (this.startDate) params.append('start_date', this.startDate)
        if (this.endDate) params.append('end_date', this.endDate)
        if (params.toString()) url += `?${params.toString()}`
        
        const response = await axios.get(url)
        const transactions = response.data
        
        // Group by month
        const monthlyData = new Map()
        
        transactions.forEach(tx => {
          const date = new Date(tx.date)
          const monthKey = `${date.getFullYear()}-${date.getMonth() + 1}`
          const monthLabel = date.toLocaleDateString('default', { month: 'short', year: 'numeric' })
          
          if (!monthlyData.has(monthKey)) {
            monthlyData.set(monthKey, { label: monthLabel, income: 0, expense: 0 })
          }
          
          const month = monthlyData.get(monthKey)
          if (tx.type === 'income') month.income += tx.amount
          if (tx.type === 'expense') month.expense += tx.amount
        })
        
        const sorted = Array.from(monthlyData.values()).reverse()
        this.hasData = sorted.length > 0
        
        this.renderChart(sorted)
      } catch (err) {
        console.error('Failed to fetch monthly data:', err)
      }
    },
    
    renderChart(data) {
      const canvas = this.$refs.chartCanvas
      if (!canvas) return
      
      if (this.chart) this.chart.destroy()
      
      const ctx = canvas.getContext('2d')
      this.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(d => d.label),
          datasets: [
            {
              label: 'Income',
              data: data.map(d => d.income),
              backgroundColor: '#22c55e',
              borderRadius: 4
            },
            {
              label: 'Expenses',
              data: data.map(d => d.expense),
              backgroundColor: '#ef4444',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => `€ ${ctx.parsed.y.toFixed(2)}`
              }
            }
          },
          scales: {
            y: {
              ticks: { callback: (v) => '€ ' + v.toFixed(2) }
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