<template>
  <div class="card shadow-sm border-0 mb-4" style="position: relative;">
    <div class="card-header bg-white border-bottom py-3">
      <h5 class="mb-0 fw-bold text-secondary">
        <i class="bi bi-arrow-left-right me-2 text-primary"></i>Period Comparison Analysis
      </h5>
    </div>

    <div class="card-body p-4" style="position: relative; min-height: 400px;">
      
      <div v-if="loading" class="position-absolute top-50 start-50 translate-middle text-center" style="z-index: 10; background: rgba(255,255,255,0.85); width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
          <span class="visually-hidden">Loading analysis...</span>
        </div>
      </div>

      <div class="row g-3 align-items-center mb-4 bg-light p-3 rounded border">
        <div class="col-md-5">
          <label class="form-label fw-semibold text-muted small text-uppercase">Base Period (Period 1)</label>
          <div class="d-flex gap-2">
            <input type="date" class="form-control shadow-sm" v-model="period1.start">
            <span class="align-self-center text-muted">to</span>
            <input type="date" class="form-control shadow-sm" v-model="period1.end">
          </div>
        </div>

        <div class="col-md-2 text-center mt-4 mt-md-0">
          <span class="badge bg-primary px-3 py-2 rounded-pill shadow-sm fw-bold">VS</span>
        </div>

        <div class="col-md-5">
          <label class="form-label fw-semibold text-muted small text-uppercase">Comparison Period (Period 2)</label>
          <div class="d-flex gap-2">
            <input type="date" class="form-control shadow-sm" v-model="period2.start">
            <span class="align-self-center text-muted">to</span>
            <input type="date" class="form-control shadow-sm" v-model="period2.end">
          </div>
        </div>
      </div>

      <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div class="btn-group btn-group-sm shadow-sm" role="group">
          <button type="button" class="btn btn-outline-secondary px-3" @click="setLastTwoMonths">Last 2 Months</button>
          <button type="button" class="btn btn-outline-secondary px-3" @click="setMonthVsPrevious">Month vs Previous</button>
          <button type="button" class="btn btn-outline-secondary px-3" @click="setYearVsPrevious">Year vs Previous</button>
        </div>
        
        <button class="btn btn-primary px-4 shadow-sm fw-bold" @click="fetchComparison" :disabled="loading">
          <i class="bi bi-lightning-charge-fill me-1"></i> Run Comparison
        </button>
      </div>

      <div v-if="error" class="alert alert-danger d-flex align-items-center m-2 shadow-sm" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <div>{{ error }}</div>
      </div>

      <div v-else-if="comparisonData">
        
        <div class="row g-3 mb-4">
          
          <div class="col-lg-4">
            <div class="card h-100 border-0 border-start border-4 border-success shadow-sm bg-white p-3">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <span class="text-uppercase text-muted fw-bold small tracking-wider">Total Income</span>
                <span :class="comparisonData.comparison.income_change >= 0 ? 'bg-success text-white' : 'bg-danger text-white'" class="badge rounded-pill px-2 py-1 font-monospace">
                  {{ comparisonData.comparison.income_change >= 0 ? '↑' : '↓' }} {{ Math.abs(comparisonData.comparison.income_change) }}%
                </span>
              </div>
              <div class="d-flex flex-column">
                <div class="text-muted small">P1: <span class="fw-semibold text-dark">€ {{ comparisonData.period1.income.toFixed(2) }}</span></div>
                <div class="fs-4 fw-extrabold text-success mt-1">P2: € {{ comparisonData.period2.income.toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div class="col-lg-4">
            <div class="card h-100 border-0 border-start border-4 border-danger shadow-sm bg-white p-3">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <span class="text-uppercase text-muted fw-bold small tracking-wider">Total Expenses</span>
                <span :class="comparisonData.comparison.expense_change <= 0 ? 'bg-success text-white' : 'bg-danger text-white'" class="badge rounded-pill px-2 py-1 font-monospace">
                  {{ comparisonData.comparison.expense_change >= 0 ? '↑' : '↓' }} {{ Math.abs(comparisonData.comparison.expense_change) }}%
                </span>
              </div>
              <div class="d-flex flex-column">
                <div class="text-muted small">P1: <span class="fw-semibold text-dark">€ {{ comparisonData.period1.expense.toFixed(2) }}</span></div>
                <div class="fs-4 fw-extrabold text-danger mt-1">P2: € {{ comparisonData.period2.expense.toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div class="col-lg-4">
            <div class="card h-100 border-0 border-start border-4 border-primary shadow-sm bg-white p-3">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <span class="text-uppercase text-muted fw-bold small tracking-wider">Net Cash Flow</span>
                <span :class="comparisonData.comparison.cashflow_change >= 0 ? 'bg-success text-white' : 'bg-danger text-white'" class="badge rounded-pill px-2 py-1 font-monospace">
                  {{ comparisonData.comparison.cashflow_change >= 0 ? '↑' : '↓' }} {{ Math.abs(comparisonData.comparison.cashflow_change) }}%
                </span>
              </div>
              <div class="d-flex flex-column">
                <div class="text-muted small">P1: <span class="fw-semibold text-dark">€ {{ comparisonData.period1.cashflow.toFixed(2) }}</span></div>
                <div class="fs-4 fw-extrabold text-primary mt-1">P2: € {{ comparisonData.period2.cashflow.toFixed(2) }}</div>
              </div>
            </div>
          </div>
          
        </div>

        <div class="bg-light p-3 rounded border mt-2">
          <div :style="{ opacity: loading ? 0.3 : 1 }" style="position: relative; height: 320px; width: 100%; transition: opacity 0.2s ease;">
            <canvas :key="canvasKey" ref="comparisonChart"></canvas>
          </div>
        </div>

      </div>

      <div v-else-if="!loading" class="text-center text-muted py-5">
        <i class="bi bi-calendar2-range d-block display-4 mb-3 text-black-50"></i>
        <p class="mb-0">Select two periods above and click <strong>Run Comparison</strong> to generate insights.</p>
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
      period2: { start: '', end: '' },
      isUnmounted: false,
      fetchCounter: 0,
      canvasKey: 0 // Reactivity key used to isolate and safely rebuild the DOM element
    }
  },
  mounted() {
    this.setDefaultPeriods();
  },
  beforeUnmount() {
    this.isUnmounted = true;
    this.safelyDestroyChart();
  },
  methods: {
    // Gracefully clean up chart instance and detached memory structures
    safelyDestroyChart() {
      if (this.comparisonChart) {
        try {
          this.comparisonChart.destroy();
        } catch (e) {
          // Suppress runtime canvas destruction bubbles
        }
        this.comparisonChart = null;
      }
    },

    // Set default standard dates on component initialization
    setDefaultPeriods() {
      const now = new Date();
      
      // Period 1: Previous full month
      const lastMonth = new Date();
      lastMonth.setMonth(lastMonth.getMonth() - 1);
      const p1Start = new Date(lastMonth.getFullYear(), lastMonth.getMonth(), 1);
      const p1End = new Date(lastMonth.getFullYear(), lastMonth.getMonth() + 1, 0);
      
      // Period 2: Current month up to today
      const p2Start = new Date(now.getFullYear(), now.getMonth(), 1);
      
      this.period1.start = p1Start.toISOString().split('T')[0];
      this.period1.end = p1End.toISOString().split('T')[0];
      this.period2.start = p2Start.toISOString().split('T')[0];
      this.period2.end = now.toISOString().split('T')[0];
      
      this.fetchComparison();
    },
    
    // Quick Range: Previous Month vs Two Months Ago
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
    
    // Quick Range: Current Month vs Full Previous Month
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
    
    // Quick Range: Current Year vs Entire Previous Year
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
    
    // Handle API calling and token counter tracking
    async fetchComparison() {
      if (!this.period1.start || !this.period1.end || !this.period2.start || !this.period2.end) {
        this.error = 'Please fill out all start and end date variables';
        return;
      }
      
      // Settle active charts instantly before dispatching network payload
      this.safelyDestroyChart();
      
      this.fetchCounter++;
      const currentFetchId = this.fetchCounter;

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
        
        // Block out-of-order execution hooks
        if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;

        this.comparisonData = response.data;
        
        // Pivot the node key to isolate canvas renders cleanly inside the next Tick loop
        this.canvasKey++;
        await this.$nextTick();
        
        if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;
        this.renderComparisonChart();
      } catch (err) {
        if (currentFetchId !== this.fetchCounter || this.isUnmounted) return;
        console.error('Comparison extraction failure:', err);
        this.error = err.response?.data?.detail || 'Failed to retrieve period matching data';
      } finally {
        if (currentFetchId === this.fetchCounter && !this.isUnmounted) {
          this.loading = false;
        }
      }
    },
    
    // Render synchronous chart structure 
    renderComparisonChart() {
      const canvas = this.$refs.comparisonChart;
      if (!canvas || this.isUnmounted) return;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      const data = this.comparisonData;
      
      // Visual labels representing the periods
      const labelP1 = `Period 1 (${data.period1.start_date})`;
      const labelP2 = `Period 2 (${data.period2.start_date})`;
      
      this.comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Income', 'Expenses', 'Net Cashflow'],
          datasets: [
            {
              label: labelP1,
              data: [data.period1.income, data.period1.expense, data.period1.cashflow],
              backgroundColor: '#6366f1', // Premium Indigo
              hoverBackgroundColor: '#4f46e5',
              borderRadius: 6,
              borderSkipped: false
            },
            {
              label: labelP2,
              data: [data.period2.income, data.period2.expense, data.period2.cashflow],
              backgroundColor: '#10b981', // Premium Emerald Green
              hoverBackgroundColor: '#059669',
              borderRadius: 6,
              borderSkipped: false
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false, // FONDAMENTALE: Blocks background async frame cycles completely
          plugins: {
            legend: {
              position: 'top',
              labels: {
                boxWidth: 12,
                font: { weight: '600', size: 12 },
                usePointStyle: true,
                pointStyle: 'circle'
              }
            },
            tooltip: {
              padding: 12,
              cornerRadius: 8,
              backgroundColor: 'rgba(15, 23, 42, 0.9)', // Dark Slate premium look
              callbacks: {
                label: (ctx) => ` ${ctx.dataset.label}: € ${ctx.raw.toFixed(2)}`
              }
            }
          },
          scales: {
            x: {
              grid: { display: false } // Cleans up vertical chart background lines
            },
            y: {
              border: { dash: [5, 5] }, // Elegant dashed styling for horizontal lines
              ticks: {
                callback: (v) => '€ ' + Number(v).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })
              }
            }
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.tracking-wider {
  letter-spacing: 0.05em;
}
.fw-extrabold {
  font-weight: 800;
}
</style>