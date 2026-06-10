<template>
  <div class="modal fade" id="editTransactionModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Transaction</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" id="closeEditModalBtn"></button>
        </div>
        <div class="modal-body">
          <!-- MOSTRA SOLO SE editedTransaction ESISTE -->
          <div v-if="!editedTransaction">
            <div class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
          
          <form v-else @submit.prevent="updateTransaction">
            <div class="mb-3">
              <label class="form-label">Type</label>
              <select class="form-select" v-model="editedTransaction.type" required @change="filterCategoriesByType">
                <option value="expense">Expense</option>
                <option value="income">Income</option>
                <option value="transfer">Transfer</option>
              </select>
            </div>

            <div class="mb-3" v-if="editedTransaction.type !== 'transfer'">
              <label class="form-label">Category</label>
              <select class="form-select" v-model="editedTransaction.category_id" required>
                <option :value="null" disabled>Select a category</option>
                <option v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Amount (€)</label>
              <input type="number" step="0.01" class="form-control" v-model.number="editedTransaction.amount" required min="0.01">
            </div>

            <div class="mb-3">
              <label class="form-label">Date</label>
              <input type="date" class="form-control" v-model="editedTransaction.date" required>
            </div>

            <div class="mb-3" v-if="editedTransaction.type === 'expense' || editedTransaction.type === 'transfer'">
              <label class="form-label">Source Account</label>
              <select class="form-select" v-model.number="editedTransaction.account_source_id" required>
                <option :value="null" disabled>Select an account</option>
                <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                  {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                </option>
              </select>
            </div>

            <div class="mb-3" v-if="editedTransaction.type === 'income' || editedTransaction.type === 'transfer'">
              <label class="form-label">Destination Account</label>
              <select class="form-select" v-model.number="editedTransaction.account_destination_id" required>
                <option :value="null" disabled>Select an account</option>
                <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                  {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                </option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Notes</label>
              <input type="text" class="form-control" v-model="editedTransaction.notes">
            </div>

            <div class="modal-footer px-0 pb-0">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="updating">
                {{ updating ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '../../config';

export default {
  name: 'EditTransactionModal',
  props: {
    transaction: {
      type: Object,
      default: null
    }
  },
  emits: ['transaction-updated'],
  data() {
    return {
      editedTransaction: null,
      categories: [],
      filteredCategories: [],
      accounts: [],
      updating: false
    }
  },
  watch: {
    transaction: {
      handler(newVal) {
        if (newVal) {
          this.editedTransaction = { ...newVal };
          // Format date for input (YYYY-MM-DD)
          if (this.editedTransaction.date) {
            this.editedTransaction.date = this.editedTransaction.date.split('T')[0];
          }
          this.filterCategoriesByType();
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.loadCategories();
    this.loadAccounts();
  },
  methods: {
    async loadCategories() {
      try {
        const response = await axios.get(API_URL + '/api/categories');
        this.categories = response.data;
        this.filterCategoriesByType();
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    },
    
    async loadAccounts() {
      try {
        const response = await axios.get(API_URL + '/api/accounts');
        this.accounts = response.data;
      } catch (err) {
        console.error('Failed to load accounts:', err);
      }
    },
    
    filterCategoriesByType() {
      if (this.editedTransaction && this.editedTransaction.type) {
        this.filteredCategories = this.categories.filter(
          c => c.type === this.editedTransaction.type
        );
      }
    },
    
    async updateTransaction() {
      if (!this.editedTransaction) return;
      
      this.updating = true;
      try {
        await axios.put(
          `${API_URL}/api/transactions/${this.editedTransaction.id}`,
          this.editedTransaction
        );
        
        this.$emit('transaction-updated');
        document.getElementById('closeEditModalBtn').click();
      } catch (err) {
        console.error('Update failed:', err);
        this.$root.showToast(err.response?.data?.detail || 'Error updating transaction', "danger");
      } finally {
        this.updating = false;
      }
    }
  }
};
</script>