<template>
  <div class="modal fade" id="addTransactionModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Record Transaction</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" id="closeTxModalBtn"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitTransaction">
            <div class="mb-3">
              <label class="form-label">Type</label>
              <select class="form-select" v-model="localTransaction.type" required @change="onTypeChange">
                <option value="expense">Expense</option>
                <option value="income">Income</option>
                <option value="transfer">Transfer</option>
              </select>
            </div>

            <div class="mb-3" v-if="localTransaction.type !== 'transfer'">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label mb-0">Category</label>
                <button type="button" class="btn btn-link p-0 small btn-sm" @click="toggleInlineCategoryForm">
                  {{ showInlineCategory ? 'Cancel' : '+ New Category' }}
                </button>
              </div>

              <div v-if="showInlineCategory" class="p-2 border rounded bg-light mb-2">
                <div class="input-group input-group-sm">
                  <input type="text" class="form-control" v-model="newCategoryName" placeholder="Category Name">
                  <button class="btn btn-success" type="button" @click="addNewCategory">Add</button>
                </div>
              </div>

              <select class="form-select" v-model="localTransaction.category_id" required>
                <option :value="null" disabled>Select a category</option>
                <option v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Amount (€)</label>
              <input type="number" step="0.01" class="form-control" v-model.number="localTransaction.amount" required min="0.01">
            </div>

            <div class="mb-3" v-if="localTransaction.type === 'expense' || localTransaction.type === 'transfer'">
              <label class="form-label">Source Account</label>
              <select class="form-select" v-model.number="localTransaction.account_source_id" required :disabled="accounts.length === 0">
                <option :value="null" disabled>Select an account</option>
                <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                  {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                </option>
              </select>
              <small v-if="accounts.length === 0" class="text-danger">No accounts found. Please create an account first.</small>
            </div>
            
            <div class="mb-3" v-if="localTransaction.type === 'income' || localTransaction.type === 'transfer'">
              <label class="form-label">Destination Account</label>
              <select class="form-select" v-model.number="localTransaction.account_destination_id" required :disabled="accounts.length === 0">
                <option :value="null" disabled>Select an account</option>
                <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                  {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                </option>
              </select>
              <small v-if="accounts.length === 0" class="text-danger">No accounts found. Please create an account first.</small>
            </div>

            <div class="mb-3">
              <label class="form-label">Notes</label>
              <input type="text" class="form-control" v-model="localTransaction.notes">
            </div>

            <div class="modal-footer px-0 pb-0">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Submit</button>
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
  name: 'AddTransactionModal',
  props: {
    accounts: { type: Array, default: () => [] },
    categories: { type: Array, default: () => [] }
  },
  emits: ['transaction-added'],
  data() {
    return {
      localTransaction: {
        amount: 0.0,
        type: 'expense',
        notes: '',
        category_id: null,
        account_source_id: null,
        account_destination_id: null
      },
      filteredCategories: [],
      showInlineCategory: false,
      newCategoryName: ''
    }
  },
  watch: {
    categories: {
      handler() {
        this.filterCategoriesByType();
      },
      immediate: true
    }
  },
  methods: {
    filterCategoriesByType() {
      this.filteredCategories = this.categories.filter(c => c.type === this.localTransaction.type);
      this.localTransaction.category_id = null;
    },
    
    onTypeChange() {
      this.filterCategoriesByType();
    },
    
    toggleInlineCategoryForm() {
      this.showInlineCategory = !this.showInlineCategory;
      this.newCategoryName = '';
    },
    
    async addNewCategory() {
      if (!this.newCategoryName.trim()) return;
      try {
        const response = await axios.post(API_URL + '/api/categories', {
          name: this.newCategoryName.trim(),
          type: this.localTransaction.type
        });
        this.$emit('category-added', response.data);
        this.filterCategoriesByType();
        this.localTransaction.category_id = response.data.id;
        this.toggleInlineCategoryForm();
      } catch (err) {
        console.error(err);
      }
    },
    
    async submitTransaction() {
      if (this.accounts.length === 0) {
        alert('Please create an account before adding transactions.');
        return;
      }
      try {
        await axios.post(API_URL + '/api/transactions', this.localTransaction);
        
        // Reset form
        this.localTransaction = {
          amount: 0.0,
          type: 'expense',
          notes: '',
          category_id: null,
          account_source_id: null,
          account_destination_id: null
        };
        
        this.$emit('transaction-added');
        document.getElementById('closeTxModalBtn').click();
      } catch (err) {
        alert(err.response?.data?.detail || 'Error saving transaction.');
      }
    }
  }
};
</script>