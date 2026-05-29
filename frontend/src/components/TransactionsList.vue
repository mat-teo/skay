<template>
  <div class="container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2 class="text-black">Transaction History</h2>
      <div>
        <button class="btn btn-primary btn-sm me-2" data-bs-toggle="modal" data-bs-target="#addTransactionModal" @click="loadCategories; fetchAccounts()">
          + Add Transaction
        </button>
      </div>
    </div>

    <div class="table-responsive">
      <table class="table table-striped table-hover align-middle">
        <thead class="table-dark">
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Details</th>
            <th>Actions</th>  
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in transactions" :key="tx.id">
            <td>{{ formatDate(tx.date) }}</td>
            <td><span :class="typeBadgeClass(tx.type)">{{ tx.type }}</span></td>
            <td><span class="badge bg-light text-dark border">{{ getCategoryName(tx.category_id) }}</span></td>
            <td :class="amountClass(tx.type)">
              {{ tx.type === 'expense' ? '-' : tx.type === 'income' ? '+' : '' }} {{ tx.amount.toFixed(2) }} €
            </td>
            <td><small class="text-muted">{{ tx.notes || '-' }}</small></td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" 
                data-bs-toggle="modal" 
                data-bs-target="#editTransactionModal"
                @click="selectedTransaction = tx">
                Edit
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="openDeleteModal(tx)" title="Delete">
                 Delete
              </button>
            </td>
          </tr>
          <tr v-if="transactions.length === 0">
            <td colspan="6" class="text-center text-muted">No transactions registered for this period.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Modal Component -->
    <EditTransactionModal 
      ref="editModal"
      :transaction="selectedTransaction"
      @transaction-updated="onTransactionUpdated"
    />

     <!-- Delete Modal -->
    <DeleteTransactionModal
      ref="deleteModal"
      :transaction="selectedDeleteTransaction"
      @transaction-deleted="onTransactionDeleted"
    />

    <!-- Add Transaction Modal -->
    <div class="modal fade" id="addTransactionModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Record Transaction</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" id="closeTxModalBtn"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createTransaction">
              <div class="mb-3">
                <label class="form-label">Type</label>
                <select class="form-select" v-model="newTransaction.type" required @change="filterCategoriesByType">
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                  <option value="transfer">Transfer</option>
                </select>
              </div>

              <div class="mb-3" v-if="newTransaction.type !== 'transfer'">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <label class="form-label mb-0">Category</label>
                  <button type="button" class="btn btn-link p-0 small btn-sm" @click="toggleInlineCategoryForm">
                    {{ showInlineCategory ? 'Cancel' : '+ New Category' }}
                  </button>
                </div>

                <div v-if="showInlineCategory" class="p-2 border rounded bg-light mb-2">
                  <div class="input-group input-group-sm">
                    <input type="text" class="form-control" v-model="newCategoryName" placeholder="Category Name (e.g., Netflix)">
                    <button class="btn btn-success" type="button" @click="addNewCategory">Add</button>
                  </div>
                </div>

                <select class="form-select" v-model="newTransaction.category_id" required>
                  <option :value="null" disabled>Select a category</option>
                  <option v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Amount (€)</label>
                <input type="number" step="0.01" class="form-control" v-model.number="newTransaction.amount" required min="0.01">
              </div>

              <div class="mb-3" v-if="newTransaction.type === 'expense' || newTransaction.type === 'transfer'">
                <label class="form-label">Source Account</label>
                <select class="form-select" v-model.number="newTransaction.account_source_id" required :disabled="accounts.length === 0">
                  <option :value="null" disabled>Select an account</option>
                  <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                    {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                  </option>
                </select>
                <small v-if="accounts.length === 0" class="text-danger">
                  No accounts found. Please create an account first.
                </small>
              </div>
              
              <div class="mb-3" v-if="newTransaction.type === 'income' || newTransaction.type === 'transfer'">
                <label class="form-label">Destination Account</label>
                <select class="form-select" v-model.number="newTransaction.account_destination_id" required :disabled="accounts.length === 0">
                  <option :value="null" disabled>Select an account</option>
                  <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                    {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                  </option>
                </select>
                <small v-if="accounts.length === 0" class="text-danger">
                  No accounts found. Please create an account first.
                </small>
              </div>

              <div class="mb-3">
                <label class="form-label">Notes</label>
                <input type="text" class="form-control" v-model="newTransaction.notes">
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
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';
import EditTransactionModal from './EditTransactionModal.vue';
import DeleteTransactionModal from './DeleteTransactionModal.vue';

export default {
  name: 'TransactionsList',
  components: { EditTransactionModal, DeleteTransactionModal },
  data() {
    return {
      transactions: [],
      categories: [],
      accounts: [],
      filteredCategories: [],
      showInlineCategory: false,
      newCategoryName: '',
      selectedTransaction: null,
      selectedDeleteTransaction: null,
      newTransaction: {
        amount: 0.0, 
        type: 'expense', 
        notes: '',
        category_id: null, 
        account_source_id: null, 
        account_destination_id: null
      }
    };
  },
  mounted() {
    this.fetchTransactions();
    this.loadCategories();
    this.fetchAccounts();  // Added missing fetchAccounts
  },
  methods: {
    async fetchTransactions(startDate = null) {
      try {
        let url = 'http://127.0.0.1:8000/api/transactions';
        if (startDate) url += `?start_date=${startDate}`;
        const response = await axios.get(url);
        this.transactions = response.data;
      } catch (err) {
        console.error(err);
      }
    },
    
    async loadCategories() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/categories');
        this.categories = response.data;
        this.filterCategoriesByType();
      } catch (err) {
        console.error(err);
      }
    },
    
    async fetchAccounts() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/accounts');
        this.accounts = response.data;
      } catch (err) {
        console.error("Failed to load accounts:", err);
      }
    },
    
    filterCategoriesByType() {
      this.filteredCategories = this.categories.filter(c => c.type === this.newTransaction.type);
      this.newTransaction.category_id = null;
    },
    
    toggleInlineCategoryForm() {
      this.showInlineCategory = !this.showInlineCategory;
      this.newCategoryName = '';
    },
    
    async addNewCategory() {
      if (!this.newCategoryName.trim()) return;
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/categories', {
          name: this.newCategoryName.trim(),
          type: this.newTransaction.type
        });
        this.categories.push(response.data);
        this.filterCategoriesByType();
        this.newTransaction.category_id = response.data.id;
        this.toggleInlineCategoryForm();
      } catch (err) {
        console.error(err);
      }
    },
    
    getCategoryName(id) {
      if (!id) return '-';
      const cat = this.categories.find(c => c.id === id);
      return cat ? cat.name : 'Unknown';
    },
    
    async createTransaction() {
      if (this.accounts.length === 0) {
        alert('Please create an account before adding transactions.');
        return;
      }
      try {
        const payload = { ...this.newTransaction };
        await axios.post('http://127.0.0.1:8000/api/transactions', payload);
        this.$emit('transaction-saved');
        
        this.newTransaction.amount = 0.0;
        this.newTransaction.notes = '';
        this.newTransaction.category_id = null;
        this.newTransaction.account_source_id = null;
        this.newTransaction.account_destination_id = null;
        
        document.getElementById('closeTxModalBtn').click();
      } catch (err) {
        alert(err.response?.data?.detail || 'Error saving transaction.');
      }
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
    
    amountClass(type) {
      return { 
        'text-danger fw-bold': type === 'expense', 
        'text-success fw-bold': type === 'income', 
        'text-warning fw-bold': type === 'transfer' 
      };
    },
    
    openEditModal(transaction) {
      this.selectedTransaction = transaction;
      // Open the modal using Bootstrap JS
      const modalElement = document.getElementById('editTransactionModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    },
    
    onTransactionUpdated() {
      this.fetchTransactions();
      this.$emit('transaction-saved');
    }, 
    openDeleteModal(transaction) {
      this.selectedDeleteTransaction = transaction;
      const modalElement = document.getElementById('deleteTransactionModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    },
    
    onTransactionDeleted() {
      this.fetchTransactions();
      this.$emit('transaction-saved');
      this.selectedDeleteTransaction = null;
    }
  }
};
</script>