<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Net Worth Over Time</h5>
      <select class="form-select form-select-sm w-auto" v-model="interval" @change="onIntervalChange">
        <option value="day">Daily</option>
        <option value="week">Weekly</option>
        <option value="month">Monthly</option>
      </select>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
      </div>
      <div v-else-if="!chartData || chartData.length === 0" class="text-center py-4 text-muted">
        No data yet. Add accounts and transactions to see your net worth chart!
      </div>
      <canvas v-else ref="chartCanvas" style="min-height: 300px; width: 100%;"></canvas>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'NetWorthChart',
  data() {
    return {
      isMounted : false,
      chartInstance: null,
      loading: false,
      error: null,
      interval: 'month',
      chartData: null
    }
  },
  async mounted() {
    this.isMounted = true
    this.fetchData();
    //Force render after DOM is fully ready
    this.$nextTick(() =>{
      setTimeout(() => {
        if(this.chartData && this.chartData.length > 0){
          this.renderChart();
        }
      }, 200);
    })
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/transactions/net-worth?interval=${this.interval}`);
        this.chartData = response.data.data;
        

        await this.$nextTick();
        
        if (this.chartData && this.chartData.length > 0) {
          this.renderChart();
        }
      } catch (err) {
        console.error('Error:', err);
        this.error = err.response?.data?.detail || err.message;
      } finally {
        this.loading = false;
      }
    },
    
    renderChart() {
      const canvas = this.$refs.chartCanvas;
      if (!canvas) return;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      if (!this.chartData || this.chartData.length === 0) return;
      
      // Destroy existing chart instance
      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
      
      const labels = this.chartData.map(d => {
        const date = new Date(d.date);
        if (this.interval === 'month') {
          return date.toLocaleDateString('default', { month: 'short', year: 'numeric' });
        } else if (this.interval === 'week') {
          return `Week ${this.getWeekNumber(date)}`;
        }
        return date.toLocaleDateString();
      });
      
      const values = this.chartData.map(d => d.net_worth);
      
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Net Worth (€)',
            data: values,
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointBackgroundColor: '#16a34a'
          }]
        },
        options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        tooltip: {
          enabled: true,
          mode: 'index',  
          intersect: false,
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              let value = context.parsed.y;
              return `${label}: € ${value.toFixed(2)}`;
            },
            title: function(tooltipItems) {
              return tooltipItems[0].label;
            }
          }
        }
      },
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 6
          }
        }
      },
      scales: {
        y: {
          ticks: {
            callback: function(value) {
              return '€ ' + value.toFixed(2);
            }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
      });
    },
    
    getWeekNumber(date) {
      const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
      const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
      return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
    },
    
    onIntervalChange() {
      this.fetchData();
    },
    
    refresh() {
      this.fetchData();
    }
  },
  watch: {
    interval() {
      this.fetchData();
    }
  }
};
</script>