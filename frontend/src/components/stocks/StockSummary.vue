<template>
  <div class="row g-4 mb-4" v-if="hasData">
    <div class="col-12 col-sm-6 col-lg-3">
      <div class="card h-100 border-0 shadow-sm bg-white">
        <div class="card-body">
          <h6 class="text-muted small text-uppercase">Total Value</h6>
          <h3 class="fw-bold">€ {{ summary.total_value.toFixed(2) }}</h3>
        </div>
      </div>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
      <div class="card h-100 border-0 shadow-sm bg-white">
        <div class="card-body">
          <h6 class="text-muted small text-uppercase">Total Cost</h6>
          <h3 class="fw-bold">€ {{ summary.total_cost.toFixed(2) }}</h3>
        </div>
      </div>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
      <div class="card h-100 border-0 shadow-sm bg-white">
        <div class="card-body">
          <h6 class="text-muted small text-uppercase">Total Gain/Loss</h6>
          <h3 class="fw-bold" :class="summary.total_gain >= 0 ? 'text-success' : 'text-danger'">
            {{ summary.total_gain >= 0 ? '+' : '' }}€ {{ summary.total_gain.toFixed(2) }}
          </h3>
        </div>
      </div>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
      <div class="card h-100 border-0 shadow-sm bg-white">
        <div class="card-body">
          <h6 class="text-muted small text-uppercase">Return</h6>
          <h3 class="fw-bold" :class="summary.total_gain_percent >= 0 ? 'text-success' : 'text-danger'">
            {{ summary.total_gain_percent >= 0 ? '+' : '' }}{{ summary.total_gain_percent.toFixed(1) }}%
          </h3>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockSummary',
  props: {
    summary: {
      type: Object,
      default: () => ({
        total_value: 0,
        total_cost: 0,
        total_gain: 0,
        total_gain_percent: 0
      })
    },
    hasData: {
      type: Boolean,
      default: false
    }
  }
};
</script>