<template>
  <div class="card mb-4" style="position: relative;">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>Category Breakdown</span>
      <select class="form-select form-select-sm w-auto" v-model="localType">
        <option value="expense">Expenses by Category</option>
        <option value="income">Income by Category</option>
      </select>
    </div>
    
    <div class="card-body" style="position: relative; min-height: 320px;">
      
      <div v-if="loading" class="position-absolute top-50 start-50 translate-middle text-center" style="z-index: 10; background: rgba(255,255,255,0.7); width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
        <div class="spinner-border text-primary"></div>
      </div>
      
      <div v-if="error" class="alert alert-warning m-3">
        {{ error }}
      </div>
      
      <div v-else-if="!hasData && !loading" class="text-center text-muted py-5">
        No data for selected period
      </div>
      
      <div :style="{ opacity: loading ? 0.2 : 1, visibility: hasData ? 'visible' : 'hidden' }" style="position: relative; height: 300px; width: 100%;">
        <canvas :key="canvasKey" ref="chartCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import { API_URL } from '../../config';
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
  computed: {
    filterTrigger() {
      return `${this.startDate}_${this.endDate}_${this.localType}`;
    }
  },
  data() {
    return {
      chart: null,
      loading: false,
      error: null,
      hasData: false,
      localType: this.type,
      isUnmounted: false,
      fetchCounter: 0,
      canvasKey: 0,
      lastCategoryMap: null
    }
  },
  watch: {
    type(val) { this.localType = val },
    localType(val) { this.$emit('update:type', val) },
    filterTrigger() { this.fetchData() }
  },
  mounted() {
    this.fetchData()
    window.addEventListener('theme-change',this.onThemeChange);
  },
  beforeUnmount() {
    this.isUnmounted = true;
    this.safelyDestroyChart();
    window.removeEventListener('theme-change', this.onThemeChange)
  },
  methods: {
    safelyDestroyChart() {
      if (this.chart) {
        try {
          this.chart.destroy();
        } catch (e) {
          // Suppress thread bubbles
        }
        this.chart = null;
      }
    },

    onThemeChange() {
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
      if (this.lastCategoryMap) {
        this.$nextTick(() => {
          this.renderChart(this.lastCategoryMap);
        });
      }
    },

    async fetchData() {
      this.safelyDestroyChart();
      this.fetchCounter++;
      const currentFetchId = this.fetchCounter;

      this.loading = true
      this.error = null
      
      try {
        let url = API_URL + '/transactions'
        const params = new URLSearchParams()
        
        if (this.startDate && this.startDate !== '') params.append('start_date', this.startDate)
        if (this.endDate && this.endDate !== '') params.append('end_date', this.endDate)
        if (params.toString()) url += `?${params.toString()}`
        
        const [transactionsRes, categoriesRes] = await Promise.all([
          axios.get(url),
          axios.get(API_URL + '/categories')
        ])
        
        if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;

        const transactions = transactionsRes.data
        const categories = categoriesRes.data
        
        const filtered = transactions.filter(t => t.type === this.localType)
        const categoryMap = new Map()
        
        filtered.forEach(tx => {
          const cat = categories.find(c => c.id === tx.category_id)
          const catName = cat?.name || 'Uncategorized'
          const currentAmount = categoryMap.get(catName) || 0
          categoryMap.set(catName, currentAmount + tx.amount)
        })
        
        this.hasData = categoryMap.size > 0
        
        this.lastCategoryMap = categoryMap; // Store
          if (this.hasData) {
            await this.$nextTick();
            this.renderChart(categoryMap);
        }

        if (this.hasData) {
          this.canvasKey++; 
          await this.$nextTick() 
          
          if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;
          this.renderChart(categoryMap)
        }
      } catch (err) {
        if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;
        console.error('Failed to load category data:', err)
        this.error = err.message
      } finally {
        if (currentFetchId === this.fetchCounter && !this.isUnmounted) {
          this.loading = false
        }
      }
    },
    
    renderChart(categoryMap) {
      const isDark = document.documentElement.classList.contains('dark-theme');
      const textColor = isDark ? '#ffffff' : '#1d1d1f';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
      
      const canvas = this.$refs.chartCanvas
      if (!canvas || this.isUnmounted) return;
      
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
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
            borderRadius: 8,
            barPercentage: 0.7,
            categoryPercentage: 0.8,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          animation: false, // ANTIDOTE: Blocks background ticker frame executions entirely
          plugins: {
            tooltip: {
              backgroundColor: 'rgba(29, 29, 31, 0.9)',
              titleColor: '#ffffff',
              bodyColor: '#e5e5e7',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderWidth: 1,
              padding: 10,
              cornerRadius: 8,
              displayColors: false,
              callbacks: {
                label: (ctx) => `€ ${ctx.raw.toFixed(2)}`
              }
            },
            legend: {
              position: 'top',
              labels: {
                font: { size: 11, family: '-apple-system, BlinkMacSystemFont' },
                boxWidth: 10,
                boxHeight: 10,
                usePointStyle: true,
                color: textColor
              }
            }
          },
          scales: {
            x: {
              grid: { color: gridColor },
              ticks: { 
                font: { size: 11, color: textColor },
                maxRotation: 35,
                minRotation: 35,
                color: textColor
              }
            },
            y: {
              grid: { 
                color: gridColor,
                drawBorder: false
              },
              ticks: { 
                font: { size: 11, color: textColor },
                callback: (v) => '€ ' + v.toFixed(0),
                color: textColor
              }
            }
          }
        }
      });
    },
    refresh() { this.fetchData() }
  }
}
</script>