<template>
  <div class="modal fade" id="addStockModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditing ? 'Edit Stock' : 'Add Stock' }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" @click="close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submit">
            
            <div v-if="errorMessage" class="alert alert-danger border-0 small mb-3" role="alert">
              <i class="bi bi-exclamation-circle-fill me-2"></i>
              {{ errorMessage }}
            </div>

            <div class="mb-3">
              <label class="form-label">Ticker</label>
              <input 
                type="text" 
                class="form-control text-uppercase" 
                v-model="form.ticker" 
                placeholder="e.g., AAPL, SXR8.DE" 
                required
                @input="errorMessage = null" 
              >
              <small class="text-muted">For European assets, remember the exchange suffix (e.g., <strong>SXR8.DE</strong>, <strong>VWCE.MI</strong>).</small>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Quantity</label>
                <input type="number" step="any" class="form-control" v-model.number="form.quantity" required min="0.000001">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Avg Buy Price (€)</label>
                <input type="number" step="any" class="form-control" v-model.number="form.average_buy_price" required min="0.000001">
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Currency</label>
              <select class="form-select" v-model="form.currency">
                <option value="EUR">EUR (€)</option>
                <option value="USD">USD ($)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
            <div class="modal-footer px-0 pb-0">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" @click="close">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
                {{ submitting ? 'Validating...' : 'Save' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import { StockService } from './StockService';

export default {
  name: 'StockModal',
  props: {
    editing: { type: Object, default: null }
  },
  emits: ['saved'],
  data() {
    return {
      form: {
        ticker: '',
        quantity: 0,
        average_buy_price: 0,
        currency: 'EUR'
      },
      modalInstance: null,
      isEditing: false,
      editingId: null,
      submitting: false,
      errorMessage: null 
    }
  },
  watch: {
    editing: {
      handler(val) {
        this.errorMessage = null; 
        if (val) {
          this.isEditing = true;
          this.editingId = val.id;
          this.form = {
            ticker: val.ticker,
            quantity: val.quantity,
            average_buy_price: val.average_buy_price,
            currency: val.currency || 'EUR'
          };
        } else {
          this.isEditing = false;
          this.editingId = null;
          this.resetForm();
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.modalInstance = new Modal(document.getElementById('addStockModal'));
  },
  methods: {
    open() {
      this.errorMessage = null;
      this.modalInstance.show();
    },
    close() {
      this.errorMessage = null;
      this.modalInstance.hide();
    },
    resetForm() {
      this.form = {
        ticker: '',
        quantity: 0,
        average_buy_price: 0,
        currency: 'EUR'
      };
    },
    async submit() {
      this.submitting = true;
      this.errorMessage = null; 
      
      try {
        const payload = {
          ticker: this.form.ticker.trim().toUpperCase(),
          quantity: this.form.quantity,
          average_buy_price: this.form.average_buy_price,
          currency: this.form.currency
        };
        
        if (this.isEditing) {
          await StockService.updateStock(this.editingId, payload);
        } else {
          await StockService.addStock(payload);
        }
        
        this.close();
        this.$emit('saved');
        this.$root.showToast(this.isEditing ? 'Stock updated!' : 'Stock added!', 'success');
      } catch (err) {
        if (err.response && err.response.data && err.response.data.detail) {
          this.errorMessage = err.response.data.detail;
        } else {
          this.errorMessage = "An unexpected error occurred while validating the stock. Please try again.";
        }
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>