<template>
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-header bg-white border-bottom py-3">
      <h5 class="mb-0 fw-bold text-secondary">
        <i class="bi bi-arrow-left-right me-2 text-primary"></i>Period Comparison Analysis
      </h5>
    </div>

    <div class="card-body p-4">
      
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else>
        <!-- Date selectors -->
        <div class="row g-3 align-items-center mb-4 bg-light p-3 rounded border">
          <div class="col-md-5">
            <label class="form-label fw-semibold text-muted small text-uppercase">Period 1</label>
            <div class="d-flex gap-2">
              <input type="date" class="form-control" v-model="period1.start">
              <span class="align-self-center text-muted">to</span>
              <input type="date" class="form-control" v-model="period1.end">
            </div>
          </div>

          <div class="col-md-2 text-center">
            <span class="badge bg-primary px-3 py-2 rounded-pill">VS</span>
          </div>

          <div class="col-md-5">
            <label class="form-label fw-semibold text-muted small text-uppercase">Period 2</label>
            <div class="d-flex gap-2">
              <input type="date" class="form-control" v-model="period2.start">
              <span class="align-self-center text-muted">to</span>
              <input type="date" class="form-control" v-model="period2.end">
            </div>
          </div>
        </div>

        <!-- Quick buttons -->
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
          <div class="btn-group btn-group-sm">
            <button type="button" class="btn btn-outline-secondary" @click="setLastTwoMonths">Last 2 Months</button>
            <button type="button" class="btn btn-outline-secondary" @click="setMonthVsPrevious">Month vs Previous</button>
            <button type="button" class="btn btn-outline-secondary" @click="setYearVsPrevious">Year vs Previous</button>
          </div>
          
          <button class="btn btn-primary" @click="fetchComparison" :disabled="loading">
            Run Comparison
          </button>
        </div>

        <!-- Error -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <!-- Results -->
        <div v-if="comparisonData">
          <!-- Stats Cards -->
          <div class="row g-3 mb-4">
            <div class="col-lg-4">
              <div class="card h-100 border-start border-4 border-success bg-white p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <span class="text-uppercase text-muted fw-bold small">Total Income</span>
                  <span :class="comparisonData.comparison.income_change >= 0 ? 'bg-success' : 'bg-danger'" class="badge text-white px-2 py-1">
                    {{ comparisonData.comparison.income_change >= 0 ? '↑' : '↓' }} {{ Math.abs(comparisonData.comparison.income_change) }}%
                  </span>
                </div>
                <div class="text-muted small">P1: € {{ comparisonData.period1.income.toFixed(2) }}</div>
                <div class="fs-4 fw-bold text-success mt-1">P2: € {{ comparisonData.period2.income.toFixed(2) }}</div>
              </div>
            </div>

            <div class="col-lg-4">
              <div class="card h-100 border-start border-4 border-danger bg-white p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <span class="text-uppercase text-muted fw-bold small">Total Expenses</span>
                  <span :class="comparisonData.comparison.expense_change <= 0 ? 'bg-success' : 'bg-danger'" class="badge text-white px-2 py-1">
                    {{ comparisonData.comparison.expense_change >= 0 ? '↑' : '↓' }} {{ Math.abs(comparisonData.comparison.expense_change) }}%
                  </span>
                </div>
                <div class="text-muted small">P1: € {{ comparisonData.period1.expense.toFixed(2) }}</div>
                <div class="fs-4 fw-bold text-danger mt-1">P2: € {{ comparisonData.period2.expense.toFixed(2) }}</div>
              </div>
            </div>

            <div class="col-lg-4">
              <div class="card h-100 border-start border-4 border-primary bg-white p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <span class="text-uppercase text-muted fw-bold small">Net Cash Flow</span>
                  <span :class="comparisonData.comparison.cashflow_change >= 0 ? 'bg-success' : 'bg-danger'" class="badge text-white px-2 py-1">
                    {{ comparisonData.comparison.cashflow_change >= 0 ? '↑' : '↓' }} {{ Math.abs(comparisonData.comparison.cashflow_change) }}%
                  </span>
                </div>
                <div class="text-muted small">P1: € {{ comparisonData.period1.cashflow.toFixed(2) }}</div>
                <div class="fs-4 fw-bold text-primary mt-1">P2: € {{ comparisonData.period2.cashflow.toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <!-- Chart -->
          <div class="bg-light p-3 rounded border mt-2">
            <canvas ref="comparisonChart" style="width: 100%; height: 320px;"></canvas>
          </div>
        </div>

        <div v-else-if="!loading" class="text-center text-muted py-5">
          Select two periods and click Run Comparison
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'PeriodComparison',
  data() {
    return {
      loading: false,
      error: null,
      comparisonData: null,
      comparisonChart: null,
      period1: { start: '', end: '' },
      period2: { start: '', end: '' }
    }
  },
  mounted() {
    this.setDefaultPeriods();
    window.addEventListener('theme-change', this.handleThemeChange);
  },
  beforeUnmount() {
    window.removeEventListener('theme-change', this.handleThemeChange);
    if (this.comparisonChart) {
      this.comparisonChart.destroy();
    }
  },
  methods: {
    handleThemeChange() {
      if (this.comparisonChart) {
        this.comparisonChart.destroy();
        this.comparisonChart = null;
      }
      
      if (this.comparisonData) {
        setTimeout(() => {
          this.renderChart();
        }, 50);
      }
    },
    
    setDefaultPeriods() {
      const now = new Date();
      
      const lastMonth = new Date();
      lastMonth.setMonth(lastMonth.getMonth() - 1);
      const p1Start = new Date(lastMonth.getFullYear(), lastMonth.getMonth(), 1);
      const p1End = new Date(lastMonth.getFullYear(), lastMonth.getMonth() + 1, 0);
      
      const p2Start = new Date(now.getFullYear(), now.getMonth(), 1);
      
      this.period1.start = p1Start.toISOString().split('T')[0];
      this.period1.end = p1End.toISOString().split('T')[0];
      this.period2.start = p2Start.toISOString().split('T')[0];
      this.period2.end = now.toISOString().split('T')[0];
      
      this.fetchComparison();
    },
    
    setLastTwoMonths() {
      const now = new Date();
      const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const twoMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 2, 1);
      const lastMonthEnd = new Date(now.getFullYear(), now.getMonth(), 0);
      const twoMonthsAgoEnd = new Date(now.getFullYear(), now.getMonth() - 1, 0);
      
      this.period1.start = twoMonthsAgo.toISOString().split('T')[0];
      this.period1.end = twoMonthsAgoEnd.toISOString().split('T')[0];
      this.period2.start = lastMonth.toISOString().split('T')[0];
      this.period2.end = lastMonthEnd.toISOString().split('T')[0];
      
      this.fetchComparison();
    },
    
    setMonthVsPrevious() {
      const now = new Date();
      const currentMonthStart = new Date(now.getFullYear(), now.getMonth(), 1);
      const previousMonthStart = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const previousMonthEnd = new Date(now.getFullYear(), now.getMonth(), 0);
      
      this.period1.start = previousMonthStart.toISOString().split('T')[0];
      this.period1.end = previousMonthEnd.toISOString().split('T')[0];
      this.period2.start = currentMonthStart.toISOString().split('T')[0];
      this.period2.end = now.toISOString().split('T')[0];
      
      this.fetchComparison();
    },
    
    setYearVsPrevious() {
      const now = new Date();
      const currentYearStart = new Date(now.getFullYear(), 0, 1);
      const previousYearStart = new Date(now.getFullYear() - 1, 0, 1);
      const previousYearEnd = new Date(now.getFullYear() - 1, 11, 31);
      
      this.period1.start = previousYearStart.toISOString().split('T')[0];
      this.period1.end = previousYearEnd.toISOString().split('T')[0];
      this.period2.start = currentYearStart.toISOString().split('T')[0];
      this.period2.end = now.toISOString().split('T')[0];
      
      this.fetchComparison();
    },
    
    async fetchComparison() {
      if (!this.period1.start || !this.period1.end || !this.period2.start || !this.period2.end) {
        this.error = 'Please fill all dates';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/transactions/compare', {
          params: {
            period1_start: this.period1.start,
            period1_end: this.period1.end,
            period2_start: this.period2.start,
            period2_end: this.period2.end
          }
        });
        
        this.comparisonData = response.data;
        
        await this.$nextTick();
        this.renderChart();
      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.detail || 'Failed to fetch comparison data';
      } finally {
        this.loading = false;
      }
    },
    
    renderChart() {
      const canvas = this.$refs.comparisonChart;
      if (!canvas) return;
      
      if (this.comparisonChart) {
        this.comparisonChart.destroy();
        this.comparisonChart = null;
      }
      
      const ctx = canvas.getContext('2d');
      const data = this.comparisonData;
      
      const isDark = document.documentElement.classList.contains('dark-theme');
      const textColor = isDark ? '#ffffff' : '#1d1d1f';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
      
      this.comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Income', 'Expenses', 'Cashflow'],
          datasets: [
            {
              label: `${data.period1.start_date} → ${data.period1.end_date}`,
              data: [data.period1.income, data.period1.expense, data.period1.cashflow],
              backgroundColor: '#4f46e5',
              borderRadius: 8,
              barPercentage: 0.6,
            },
            {
              label: `${data.period2.start_date} → ${data.period2.end_date}`,
              data: [data.period2.income, data.period2.expense, data.period2.cashflow],
              backgroundColor: '#22c55e',
              borderRadius: 8,
              barPercentage: 0.6,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => `€ ${ctx.raw.toFixed(2)}`
              }
            },
            legend: {
              position: 'top',
              labels: {
                font: { size: 11 },
                color: textColor
              }
            }
          },
          scales: {
            x: {
              ticks: { color: textColor }
            },
            y: {
              ticks: { color: textColor, callback: (v) => '€ ' + v.toFixed(0) },
              grid: { color: gridColor }
            }
          }
        }
      });
    }
  }
};
</script>