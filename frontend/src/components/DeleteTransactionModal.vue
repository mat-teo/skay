<template>
  <div class="modal fade" id="deleteTransactionModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-sm">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title">Confirm Delete</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" id="closeDeleteModalBtn"></button>
        </div>
        <div class="modal-body">
          <div v-if="!transaction">
            <div class="text-center py-3">
              <div class="spinner-border text-danger" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
          <div v-else>
            <p class="mb-2">Are you sure you want to delete this transaction?</p>
            <div class="alert alert-warning p-2 mb-2">
              <strong>{{ transaction.amount.toFixed(2) }} €</strong>
              <span class="badge ms-2" :class="typeBadgeClass(transaction.type)">
                {{ transaction.type }}
              </span>
            </div>
            <div class="small text-muted">
              <div> {{ formatDate(transaction.date) }}</div>
              <div> {{ getCategoryName(transaction.category_id) }}</div>
              <div v-if="transaction.notes">{{ transaction.notes }}</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-danger" @click="handleDelete" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Delete Permanently' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DeleteTransactionModal',
  props: {
    transaction: {
      type: Object,
      default: null
    }
  },
  emits: ['transaction-deleted'],
  data() {
    return {
      deleting: false,
      categories: []
    }
  },
  mounted() {
    this.loadCategories();
  },
  methods: {
    async loadCategories() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/categories');
        this.categories = response.data;
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    },
    
    getCategoryName(id) {
      if (!id) return '-';
      const cat = this.categories.find(c => c.id === id);
      return cat ? cat.name : 'Unknown';
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Date(dateStr).toLocaleDateString();
    },
    
    typeBadgeClass(type) {
      return {
        'badge bg-danger': type === 'expense',
        'badge bg-success': type === 'income',
        'badge bg-warning text-dark': type === 'transfer'
      };
    },
    
    async handleDelete() {
      if (!this.transaction) return;
      
      this.deleting = true;
      try {
        await axios.delete(`http://127.0.0.1:8000/api/transactions/${this.transaction.id}`);
        
        this.$emit('transaction-deleted');
        
        // Close modal
        const modalElement = document.getElementById('deleteTransactionModal');
        const closeBtn = document.getElementById('closeDeleteModalBtn');
        if (closeBtn) {
          closeBtn.click();
        }
      } catch (err) {
        console.error('Delete failed:', err);
        alert(err.response?.data?.detail || 'Error deleting transaction');
      } finally {
        this.deleting = false;
      }
    }
  }
};
</script>