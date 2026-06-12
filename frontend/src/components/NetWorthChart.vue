<template>
  <div class="card shadow-sm mb-4" style="position: relative;">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Net Worth Over Time</h5>
      <select class="form-select form-select-sm w-auto" v-model="interval">
        <option value="day">Daily</option>
        <option value="week">Weekly</option>
        <option value="month">Monthly</option>
      </select>
    </div>
    
    <div class="card-body" style="position: relative; min-height: 320px;">
      
      <div v-if="loading" class="position-absolute top-50 start-50 translate-middle text-center" style="z-index: 10; background: rgba(255,255,255,0.7); width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-if="error" class="alert alert-danger m-3">
        {{ error }}
      </div>
      
      <div v-else-if="(!chartData || chartData.length === 0) && !loading" class="text-center py-5 text-muted">
        No data yet. Add accounts and transactions to see your net worth chart!
      </div>
      
      <div :style="{ opacity: loading ? 0.2 : 1, visibility: (chartData && chartData.length > 0) ? 'visible' : 'hidden' }" style="position: relative; height: 300px; width: 100%;">
        <canvas :key="canvasKey" ref="chartCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '../config';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'NetWorthChart',
  props: {
    startDate: { type: String, default: '' },
    endDate: { type: String, default: '' }
  },
  computed: {
    filterTrigger() {
      return `${this.startDate}_${this.endDate}_${this.interval}`;
    }
  },
  watch: {
    filterTrigger() {
      this.fetchData();
    }
  },
  data() {
    return {
      chartInstance: null,
      loading: false,
      error: null,
      interval: 'month',
      chartData: null,
      isUnmounted: false,
      fetchCounter: 0,
      canvasKey: 0 
    }
  },
  mounted() {
    this.fetchData();
    window.addEventListener('theme-change',this.onThemeChange);
  },
  beforeUnmount() {
    this.isUnmounted = true;
    this.safelyDestroyChart();
    window.removeEventListener('theme-change',this.onThemeChange);
  },
  methods: {
    safelyDestroyChart() {
      if (this.chartInstance) {
        try {
          this.chartInstance.destroy();
        } catch (e) {
          // Suppress thread bubbles
        }
        this.chartInstance = null;
      }
    },

    async fetchData() {
      this.safelyDestroyChart();
      this.fetchCounter++;
      const currentFetchId = this.fetchCounter;

      this.loading = true;
      this.error = null;
      
      try {
        let url = API_URL + "/transactions/net-worth?interval=" + this.interval
        if (this.startDate) url += `&start_date=${this.startDate}`
        if (this.endDate) url += `&end_date=${this.endDate}`
        
        const response = await axios.get(url);
        
        if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;

        this.chartData = response.data.data;
        
        if (this.chartData && this.chartData.length > 0) {
          this.canvasKey++;
          await this.$nextTick();
          
          if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;
          this.renderChart();
        }
      } catch (err) {
        if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;
        console.error('Error:', err);
        this.error = err.response?.data?.detail || err.message;
      } finally {
        if (currentFetchId === this.fetchCounter && !this.isUnmounted) {
          this.loading = false;
        }
      }
    },

    onThemeChange() {
      // Destroy existing chart before re-rendering
      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
      // Re-render with current data
      if (this.chartData && this.chartData.length > 0) {
        this.$nextTick(() => {
          this.renderChart();
        });
      }
    },
    
    renderChart() {
      const isDark = document.documentElement.classList.contains('dark-theme');

      const textColor = isDark ? '#ffffff' : '#1d1d1f';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
      const tooltipBg = isDark ? 'rgba(44, 44, 46, 0.95)' : 'rgba(29, 29, 31, 0.9)';
      

      const canvas = this.$refs.chartCanvas;
      if (!canvas || this.isUnmounted) return;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      const labels = this.chartData.map(d => {
        const date = new Date(d.date);
        if (this.interval === 'month') {
          return date.toLocaleDateString('default', { month: 'short', year: 'numeric' });
        } else if (this.interval === 'week') {
          return d.date;
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
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.04)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.3,
            pointRadius: 3,
            pointHoverRadius: 6,
            pointBackgroundColor: '#4f46e5',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointHoverBackgroundColor: '#4338ca',
            pointHoverBorderColor: '#ffffff',
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          animation: false, // ANTIDOTE: Kills async background paint frames to avoid node null pointer exceptions
          plugins: {
            tooltip: {
              enabled: true,
              mode: 'index',
              intersect: false,
              backgroundColor: tooltipBg,
              titleColor: '#ffffff',
              bodyColor: '#e5e5e7',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderWidth: 1,
              padding: 10,
              cornerRadius: 8,
              displayColors: false,
              callbacks: {
                label: function(context) {
                  return `€ ${context.parsed.y.toFixed(2)}`;
                }
              }
            },
            legend: {
              position: 'top',
              align: 'center',
              labels: {
                font: { size: 11, family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto' },
                boxWidth: 10,
                boxHeight: 10,
                usePointStyle: true,
                color: textColor
              }
            }
          },
          scales: {
            x: {
              grid: { color: gridColor},
              ticks: { 
                font: { size: 11, family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto' },
                color: textColor,
                maxRotation: 45,
                minRotation: 45
              }
            },
            y: {
              min: 0,
              grid: { 
                color: gridColor,
                drawBorder: false,
                lineWidth: 0.5
              },
              ticks: { 
                font: { size: 11, family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto' },
                color: textColor,
                callback: function(value) {
                  return '€ ' + value.toFixed(0);
                }
              }
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          },
          elements: {
            line: {
              borderJoin: 'round'
            }
          }
        }
      });
    },
    refresh() { this.fetchData(); }
  }
};
</script>