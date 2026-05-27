<template>
  <div class="container mt-5">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Transaction History</h2>
      <div>
        <button class="btn btn-primary btn-sm me-2" data-bs-toggle="modal" data-bs-target="#addTransactionModal">
          + Add Transaction
        </button>
        <button class="btn btn-secondary btn-sm" @click="fetchTransactions">Refresh</button>
      </div>
    </div>

    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-if="!loading && !error" class="table-responsive">
      <table class="table table-striped table-hover align-middle">
        <thead class="table-dark">
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Details</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in transactions" :key="tx.id">
            <td>{{ formatDate(tx.date) }}</td>
            <td>
              <span :class="typeBadgeClass(tx.type)">{{ tx.type }}</span>
            </td>
            <td :class="amountClass(tx.type)">
              {{ tx.type === 'expense' ? '-' : tx.type === 'income' ? '+' : '' }} {{ tx.amount.toFixed(2) }} €
            </td>
            <td>
              <small class="text-muted" v-if="tx.type === 'expense'">From: Account {{ tx.account_source_id }}</small>
              <small class="text-muted" v-if="tx.type === 'income'">To: Account {{ tx.account_destination_id }}</small>
              <small class="text-muted" v-if="tx.type === 'transfer'">From {{ tx.account_source_id }} to {{ tx.account_destination_id }}</small>
            </td>
            <td>{{ tx.notes || '-' }}</td>
          </tr>
          <tr v-if="transactions.length === 0">
            <td colspan="5" class="text-center text-muted">No transactions found. Click "+ Add Transaction" to start!</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal fade" id="addTransactionModal" tabindex="-1" aria-labelledby="addTransactionModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="addTransactionModalLabel">Record Transaction</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="closeTxModalBtn"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createTransaction">
              <div class="mb-3">
                <label for="txType" class="form-label">Type</label>
                <select class="form-select" id="txType" v-model="newTransaction.type" required>
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                  <option value="transfer">Transfer</option>
                </select>
              </div>

              <div class="mb-3">
                <label for="txAmount" class="form-label">Amount (€)</label>
                <input type="number" step="0.01" class="form-control" id="txAmount" v-model.number="newTransaction.amount" required min="0.01">
              </div>

              <div class="mb-3" v-if="newTransaction.type === 'expense' || newTransaction.type === 'transfer'">
                <label for="txSource" class="form-label">Source Account (ID)</label>
                <input type="number" class="form-control" id="txSource" v-model.number="newTransaction.account_source_id" placeholder="Enter Account ID" required>
              </div>

              <div class="mb-3" v-if="newTransaction.type === 'income' || newTransaction.type === 'transfer'">
                <label for="txDest" class="form-label">Destination Account (ID)</label>
                <input type="number" class="form-control" id="txDest" v-model.number="newTransaction.account_destination_id" placeholder="Enter Account ID" required>
              </div>

              <div class="mb-3">
                <label for="txNotes" class="form-label">Notes (Optional)</label>
                <input type="text" class="form-control" id="txNotes" v-model="newTransaction.notes" placeholder="e.g., Grocery shopping, Salary, Internal transfer">
              </div>

              <div class="modal-footer px-0 pb-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  {{ submitting ? 'Processing...' : 'Submit Transaction' }}
                </button>
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

export default {
  name: 'TransactionsList',
  data() {
    return {
      transactions: [],
      loading: false,
      submitting: false,
      error: null,
      newTransaction: {
        user_id: 1, // Mocked active user ID
        amount: 0.0,
        type: 'expense',
        notes: '',
        account_source_id: null,
        account_destination_id: null
      }
    };
  },
  mounted() {
    this.fetchTransactions();
  },
  methods: {
    // GET: Fetch all transaction logs
    async fetchTransactions() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/transactions');
        this.transactions = response.data;
      } catch (err) {
        this.error = 'Failed to fetch transactions from backend.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    // POST: Create a new transaction record
    async createTransaction() {
      this.submitting = true;
      try {
        // Prepare payload, setting unused IDs to null based on transaction type
        const payload = { ...this.newTransaction };
        if (payload.type === 'expense') payload.account_destination_id = null;
        if (payload.type === 'income') payload.account_source_id = null;

        await axios.post('http://127.0.0.1:8000/api/transactions', payload);
        
        // Refresh transaction list
        await this.fetchTransactions();
        
        // Emit an event to tell App.vue to refresh the account balances table
        this.$emit('transaction-saved');

        // Reset local form structure
        this.newTransaction.amount = 0.0;
        this.newTransaction.notes = '';
        this.newTransaction.account_source_id = null;
        this.newTransaction.account_destination_id = null;

        // Close the modal programmatically
        document.getElementById('closeTxModalBtn').click();
      } catch (err) {
        alert(err.response?.data?.detail || 'Error processing transaction. Check Account IDs and Ownership.');
        console.error(err);
      } finally {
        this.submitting = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-';
      const date = new Date(dateStr);
      return date.toLocaleString();
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
    }
  }
};
</script>