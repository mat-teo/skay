<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-pie-chart"></i>
        <span>Expenses by Category</span>
      </div>
      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-secondary">{{ periodLabel }}</span>
        <router-link to="/stats" class="btn btn-sm btn-link text-decoration-none">
          Details <i class="bi bi-arrow-right"></i>
        </router-link>
      </div>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="!hasData" class="text-center py-5 text-muted">
        <i class="bi bi-inbox fs-1"></i>
        <p class="mt-2 mb-0">No expenses in this period</p>
      </div>
      <canvas v-else ref="chartCanvas" style="max-height: 250px; width: 100%;"></canvas>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
import { API_URL } from '../../config';
Chart.register(...registerables);

export default {
  name: 'ExpensePieChart',
  props: {
    startDate: { type: String, default: '' },
    endDate: { type: String, default: '' }
  },
  data() {
    return {
      chart: null,
      loading: false,
      hasData: false,
      periodLabel: '',
      lastCategoryMap: null
    };
  },
  mounted() {
    this.fetchData();
    window.addEventListener('theme-change', this.onThemeChange);
  },
  watch: {
    startDate() { this.fetchData(); },
    endDate() { this.fetchData(); }
  },
  beforeUnmount() {
    if (this.chart) this.chart.destroy();
    window.removeEventListener('theme-change', this.onThemeChange);
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.hasData = false;
      
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
      
      try {
        // Build URL with date filters
        let url = API_URL +  '/transactions';
        const params = new URLSearchParams();
        
        if (this.startDate) params.append('start_date', this.startDate);
        if (this.endDate) params.append('end_date', this.endDate);
        if (params.toString()) url += `?${params.toString()}`;
        
        const [transactionsRes, categoriesRes] = await Promise.all([
          axios.get(url),
          axios.get(API_URL + '/categories')
        ]);
        
        const transactions = transactionsRes.data;
        const categories = categoriesRes.data;
        
        // Filter only expenses
        const expenses = transactions.filter(t => t.type === 'expense');
        
        if (expenses.length === 0) {
          this.hasData = false;
          this.setPeriodLabel();
          return;
        }
        
        // Aggregate by category
        const categoryMap = new Map();
        expenses.forEach(tx => {
          const cat = categories.find(c => c.id === tx.category_id);
          const catName = cat?.name || 'Uncategorized';
          categoryMap.set(catName, (categoryMap.get(catName) || 0) + tx.amount);
        });
        
        this.hasData = categoryMap.size > 0;
        
        if (this.hasData) {
          this.lastCategoryMap = categoryMap; // Store for theme change
          await this.$nextTick();
          this.renderChart(categoryMap);
        }
        
        this.setPeriodLabel();
      } catch (err) {
        console.error('Failed to load expense data:', err);
      } finally {
        this.loading = false;
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
    
    renderChart(categoryMap) {
      const isDark = document.documentElement.classList.contains('dark-theme');
      const textColor = isDark ? '#ffffff' : '#1d1d1f';
      const tooltipBg = isDark ? 'rgba(44, 44, 46, 0.95)' : 'rgba(29, 29, 31, 0.9)';
      
      const canvas = this.$refs.chartCanvas;
      if (!canvas) return;
      
      const ctx = canvas.getContext('2d');
      
      // Sort by amount descending
      const sorted = Array.from(categoryMap.entries()).sort((a, b) => b[1] - a[1]);
      const labels = sorted.map(item => item[0]);
      const data = sorted.map(item => item[1]);
      
      // Apple-style colors
      const colors = [
        '#4f46e5', '#22c55e', '#ef4444', '#f59e0b', '#06b6d4',
        '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1'
      ];
      
      this.chart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors.slice(0, labels.length),
            borderWidth: 0,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            tooltip: {
              backgroundColor: tooltipBg,
              titleColor: '#ffffff',
              bodyColor: '#e5e5e7',
              cornerRadius: 8,
              callbacks: {
                label: (ctx) => {
                  const total = data.reduce((a, b) => a + b, 0);
                  const percentage = ((ctx.parsed / total) * 100).toFixed(1);
                  return `${ctx.label}: € ${ctx.parsed.toFixed(2)} (${percentage}%)`;
                }
              }
            },
            legend: {
              position: 'right',
              labels: {
                font: { size: 10 },
                boxWidth: 10,
                boxHeight: 10,
                color: textColor
              }
            }
          }
        }
      });
    },
    
    setPeriodLabel() {
      if (this.startDate && this.endDate) {
        const start = new Date(this.startDate).toLocaleDateString();
        const end = new Date(this.endDate).toLocaleDateString();
        this.periodLabel = `${start} - ${end}`;
      } else if (this.startDate) {
        this.periodLabel = `From ${new Date(this.startDate).toLocaleDateString()}`;
      } else {
        this.periodLabel = 'Current period';
      }
    },
    
    refresh() {
      this.fetchData();
    }
  }
};
</script>

<style scoped>
.btn-link {
  padding: 0;
  font-size: 0.75rem;
}

.btn-link:hover {
  text-decoration: underline !important;
}

.d-flex.align-items-center.gap-2 {
  gap: 0.5rem;
}

.bi-pie-chart {
  font-size: 1rem;
}
</style>