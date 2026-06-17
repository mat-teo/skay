<template>
  <div class="card shadow-sm border-0">
    <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Holdings</h5>
      <span class="text-muted small">{{ stocks.length }} positions</span>
    </div>
    <div class="card-body p-0">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>
      <div v-else-if="stocks.length === 0" class="text-center py-5 text-muted">
        <i class="bi bi-box fs-1 d-block"></i>
        <p>No stocks in your portfolio yet. Add your first stock!</p>
      </div>
      <div v-else class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-dark">
            <tr>
              <th>Ticker</th>
              <th>Quantity</th>
              <th>Avg Price</th>
              <th>Current Price</th>
              <th class="text-end">Value</th>
              <th class="text-end">Gain/Loss</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stock in stocks" :key="stock.id">
              <td><strong>{{ stock.ticker }}</strong></td>
              <td>{{ stock.quantity }}</td>
              <td>€ {{ stock.average_buy_price.toFixed(2) }}</td>
              <td>
                <span v-if="stock.current_price">
                  € {{ stock.current_price.toFixed(2) }}
                  <span class="small ms-1" :class="stock.current_price >= stock.average_buy_price ? 'text-success' : 'text-danger'">
                    {{ ((stock.current_price - stock.average_buy_price) / stock.average_buy_price * 100).toFixed(1) }}%
                  </span>
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="text-end fw-bold">€ {{ stock.current_value.toFixed(2) }}</td>
              <td class="text-end" :class="stock.gain >= 0 ? 'text-success' : 'text-danger'">
                {{ stock.gain >= 0 ? '+' : '' }}€ {{ stock.gain.toFixed(2) }}
                <span class="small">({{ stock.gain_percent }}%)</span>
              </td>
              <td class="text-center" style="white-space: nowrap;">
                <button class="btn btn-sm btn-outline-primary me-1" @click="$emit('edit', stock)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="$emit('delete', stock.id)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockTable',
  props: {
    stocks: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  emits: ['edit', 'delete']
};
</script>