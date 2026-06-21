<template>
  <div class="stocks-view">
    <header class="page-header d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="page-title">Portfolio</h1>
        <p class="text-muted">Track your stock investments</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary btn-sm" @click="refreshPrices" :disabled="refreshing">
          <i class="bi bi-arrow-clockwise"></i> {{ refreshing ? 'Refreshing...' : 'Refresh Prices' }}
        </button>
        <button class="btn btn-primary btn-sm" @click="openAddModal">
          <i class="bi bi-plus"></i> Add Stock
        </button>
      </div>
    </header>

    <div v-if="portfolio.has_pricing_errors" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      One or more asset tickers could not be found. Please ensure you provided the proper exchange suffix (e.g. <strong>.DE</strong> for European equities).
    </div>

    <StockSummary :summary="portfolio.summary" :hasData="portfolio.stocks && portfolio.stocks.length > 0" />

    <StockTable
      :stocks="portfolio.stocks"
      :loading="loading"
      @edit="openEditModal"
      @delete="confirmDelete"
    />

    <StockModal
      ref="stockModal"
      :editing="editingStock"
      @saved="loadPortfolio"
    />
  </div>
</template>

<script>
import { StockService } from './StockService.js';
import StockSummary from './StockSummary.vue';
import StockTable from './StockTable.vue';
import StockModal from './StockModal.vue';

export default {
  name: 'StocksView',
  components: { StockSummary, StockTable, StockModal },
  data() {
    return {
      loading: false,
      refreshing: false,
      portfolio: {
        stocks: [],
        summary: { total_value: 0, total_cost: 0, total_gain: 0, total_gain_percent: 0 },
        has_pricing_errors: false
      },
      editingStock: null
    };
  },
  mounted() {
    this.loadPortfolio();
  },
  methods: {
    async loadPortfolio() {
      this.loading = true;
      try {
        this.portfolio = await StockService.getPortfolio();
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to load portfolio';
        this.$root.showToast(errorMsg, 'danger');
      } finally {
        this.loading = false;
      }
    },
    
    async refreshPrices() {
      this.refreshing = true;
      try {
        await StockService.refreshPrices();
        this.$root.showToast('Prices refreshed!', 'success');
        await this.loadPortfolio();
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to refresh prices';
        this.$root.showToast(errorMsg, 'danger');
      } finally {
        this.refreshing = false;
      }
    },
    
    openAddModal() {
      this.editingStock = null;
      this.$refs.stockModal.open();
    },
    
    openEditModal(stock) {
      this.editingStock = stock;
      this.$refs.stockModal.open();
    },
    
    async confirmDelete(id) {
      if (await confirm('Delete this stock from your portfolio?')) {
        try {
          await StockService.deleteStock(id);
          this.$root.showToast('Stock deleted', 'success');
          await this.loadPortfolio();
        } catch (err) {
          this.$root.showToast('Failed to delete stock', 'danger');
        }
      }
    }
  }
};
</script>

<style scoped>
.stocks-view {
  padding-bottom: 40px;
}
</style>