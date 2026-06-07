<template>
  <div class="card mb-4">
    <div class="card-header">
      <h5 class="mb-0">Period Comparison</h5>
    </div>
    <div class="card-body">
      <!-- Period Selectors -->
      <div class="row g-3 mb-4">
        <div class="col-md-5">
          <label class="form-label">Period 1</label>
          <div class="d-flex gap-2">
            <input type="date" class="form-control" v-model="period1.start">
            <span class="align-self-center">→</span>
            <input type="date" class="form-control" v-model="period1.end">
          </div>
        </div>
        <div class="col-md-5">
          <label class="form-label">Period 2</label>
          <div class="d-flex gap-2">
            <input type="date" class="form-control" v-model="period2.start">
            <span class="align-self-center">→</span>
            <input type="date" class="form-control" v-model="period2.end">
          </div>
        </div>
        <div class="col-md-2 d-flex align-items-end">
          <button class="btn btn-primary w-100" @click="fetchComparison" :disabled="loading">
            {{ loading ? 'Loading...' : 'Compare' }}
          </button>
        </div>
      </div>
      
      <!-- Quick select buttons -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-outline-secondary" @click="setLastTwoMonths">Last 2 Months</button>
            <button type="button" class="btn btn-outline-secondary" @click="setMonthVsPrevious">Current Month vs Previous</button>
            <button type="button" class="btn btn-outline-secondary" @click="setYearVsPrevious">Current Year vs Previous</button>
          </div>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>
      
      <!-- Results -->
      <div v-else-if="comparisonData" class="row">
        <!-- Period Labels -->
        <div class="col-12 mb-3">
          <div class="row text-center fw-bold">
            <div class="col-5 offset-1">{{ comparisonData.period1.start_date }} → {{ comparisonData.period1.end_date }}</div>
            <div class="col-5">{{ comparisonData.period2.start_date }} → {{ comparisonData.period2.end_date }}</div>
          </div>
        </div>
        
        <!-- Income Row -->
        <div class="col-12 mb-3">
          <div class="row align-items-center">
            <div class="col-5 text-end">
              <span class="text-success fw-bold">+€ {{ comparisonData.period1.income.toFixed(2) }}</span>
            </div>
            <div class="col-2 text-center">
              <i class="bi bi-arrow-right"></i> Income
            </div>
            <div class="col-5 text-start">
              <span class="text-success fw-bold">+€ {{ comparisonData.period2.income.toFixed(2) }}</span>
              <span :class="comparisonData.comparison.income_change >= 0 ? 'text-success' : 'text-danger'" class="ms-2 small">
                ({{ comparisonData.comparison.income_change >= 0 ? '+' : '' }}{{ comparisonData.comparison.income_change }}%)
              </span>
            </div>
          </div>
        </div>
        
        <!-- Expense Row -->
        <div class="col-12 mb-3">
          <div class="row align-items-center">
            <div class="col-5 text-end">
              <span class="text-danger fw-bold">-€ {{ comparisonData.period1.expense.toFixed(2) }}</span>
            </div>
            <div class="col-2 text-center">
              <i class="bi bi-arrow-right"></i> Expenses
            </div>
            <div class="col-5 text-start">
              <span class="text-danger fw-bold">-€ {{ comparisonData.period2.expense.toFixed(2) }}</span>
              <span :class="comparisonData.comparison.expense_change <= 0 ? 'text-success' : 'text-danger'" class="ms-2 small">
                ({{ comparisonData.comparison.expense_change >= 0 ? '+' : '' }}{{ comparisonData.comparison.expense_change }}%)
              </span>
            </div>
          </div>
        </div>
        
        <!-- Cashflow Row (highlighted) -->
        <div class="col-12 mb-3 p-3 bg-light rounded">
          <div class="row align-items-center">
            <div class="col-5 text-end">
              <span :class="comparisonData.period1.cashflow >= 0 ? 'text-success' : 'text-danger'" class="fw-bold fs-5">
                € {{ comparisonData.period1.cashflow.toFixed(2) }}
              </span>
            </div>
            <div class="col-2 text-center fw-bold">
              Cashflow
            </div>
            <div class="col-5 text-start">
              <span :class="comparisonData.period2.cashflow >= 0 ? 'text-success' : 'text-danger'" class="fw-bold fs-5">
                € {{ comparisonData.period2.cashflow.toFixed(2) }}
              </span>
              <span :class="comparisonData.comparison.cashflow_change >= 0 ? 'text-success' : 'text-danger'" class="ms-2 small fw-bold">
                ({{ comparisonData.comparison.cashflow_change >= 0 ? '+' : '' }}{{ comparisonData.comparison.cashflow_change }}%)
              </span>
            </div>
          </div>
        </div>
        
        <!-- Bar Chart Comparison -->
        <div class="col-12 mt-3">
          <canvas ref="comparisonChart" style="height: 300px;"></canvas>
        </div>
      </div>
      
      <!-- No Data State -->
      <div v-else-if="!loading && !error" class="text-center text-muted py-5">
        Select two periods and click Compare
      </div>
      
      <!-- Error State -->
      <div v-if="error" class="alert alert-danger mt-3">
        {{ error }}
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
      period1: {
        start: '',
        end: ''
      },
      period2: {
        start: '',
        end: ''
      }
    }
  },
  mounted() {
    this.setDefaultPeriods();
  },
  beforeUnmount() {
    if (this.comparisonChart) {
      this.comparisonChart.destroy();
    }
  },
  methods: {
    setDefaultPeriods() {
      // Period 1: Last month
      const lastMonth = new Date();
      lastMonth.setMonth(lastMonth.getMonth() - 1);
      const p1Start = new Date(lastMonth.getFullYear(), lastMonth.getMonth(), 1);
      const p1End = new Date(lastMonth.getFullYear(), lastMonth.getMonth() + 1, 0);
      
      // Period 2: Current month
      const now = new Date();
      const p2Start = new Date(now.getFullYear(), now.getMonth(), 1);
      const p2End = now;
      
      this.period1.start = p1Start.toISOString().split('T')[0];
      this.period1.end = p1End.toISOString().split('T')[0];
      this.period2.start = p2Start.toISOString().split('T')[0];
      this.period2.end = p2End.toISOString().split('T')[0];
      
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
        this.error = 'Please select both periods';
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
        this.renderComparisonChart();
      } catch (err) {
        console.error('Comparison failed:', err);
        this.error = err.response?.data?.detail || 'Failed to fetch comparison data';
      } finally {
        this.loading = false;
      }
    },
    
    renderComparisonChart() {
      const canvas = this.$refs.comparisonChart;
      if (!canvas) return;
      
      if (this.comparisonChart) {
        this.comparisonChart.destroy();
      }
      
      const ctx = canvas.getContext('2d');
      const data = this.comparisonData;
      
      this.comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Income', 'Expenses', 'Cashflow'],
          datasets: [
            {
              label: `${data.period1.start_date} → ${data.period1.end_date}`,
              data: [data.period1.income, data.period1.expense, data.period1.cashflow],
              backgroundColor: '#3b82f6',
              borderRadius: 4
            },
            {
              label: `${data.period2.start_date} → ${data.period2.end_date}`,
              data: [data.period2.income, data.period2.expense, data.period2.cashflow],
              backgroundColor: '#22c55e',
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
      });
    }
  }
};
</script>