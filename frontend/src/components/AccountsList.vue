<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Your Financial Accounts</h2>
      <div>
        <button class="btn btn-success btn-sm me-2" data-bs-toggle="modal" data-bs-target="#addAccountModal">
          + Add Account
        </button>
        <button class="btn btn-secondary btn-sm" @click="fetchAccounts">Refresh</button>
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
            <th>ID</th>
            <th>Name</th>
            <th>Type</th>
            <th class="text-end">Current Balance</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.id">
            <td>{{ account.id }}</td>
            <td><strong>{{ account.name }}</strong></td>
            <td>
              <span :class="badgeClass(account.type)">{{ account.type }}</span>
            </td>
            <td class="text-end" :class="balanceClass(account.balance)">
              {{ account.balance.toFixed(2) }} €
            </td>
          </tr>
          <tr v-if="accounts.length === 0">
            <td colspan="4" class="text-center text-muted">No accounts found. Click "+ Add Account" to create one!</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal fade" id="addAccountModal" tabindex="-1" aria-labelledby="addAccountModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="addAccountModalLabel">Create New Account</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="closeModalBtn"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createAccount">
              <div class="mb-3">
                <label for="accountName" class="form-label">Account Name</label>
                <input type="text" class="form-control" id="accountName" v-model="newAccount.name" placeholder="e.g., Revolut, Cash Wallet" required>
              </div>
              
              <div class="mb-3">
                <label for="accountType" class="form-label">Account Type</label>
                <select class="form-select" id="accountType" v-model="newAccount.type" required>
                  <option value="cash">Cash</option>
                  <option value="bank">Bank Account</option>
                  <option value="investment">Investment/Trading</option>
                </select>
              </div>

              <div class="mb-3">
                <label for="accountBalance" class="form-label">Initial Balance (€)</label>
                <input type="number" step="0.01" class="form-control" id="accountBalance" v-model.number="newAccount.balance" required>
              </div>

              <div class="modal-footer px-0 pb-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-success" :disabled="submitting">
                  {{ submitting ? 'Saving...' : 'Save Account' }}
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
  name: 'AccountsList',
  data() {
    return {
      accounts: [],
      loading: false,
      submitting: false,
      error: null,
      newAccount: {
        name: '',
        type: 'bank',
        balance: 0.0
      }
    };
  },
  mounted() {
    this.fetchAccounts();
  },
  methods: {
    // GET: Fetch all accounts from API
    async fetchAccounts() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/accounts');
        this.accounts = response.data;
      } catch (err) {
        this.error = 'Failed to fetch accounts from backend. Is FastAPI running?';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    // POST: Create a new account
    async createAccount() {
      this.submitting = true;
      try {
        await axios.post('http://127.0.0.1:8000/api/accounts', this.newAccount);
        
        // Refresh the list immediately
        await this.fetchAccounts();
        
        // Reset the form fields
        this.newAccount.name = '';
        this.newAccount.type = 'bank';
        this.newAccount.balance = 0.0;
        
        // Close the bootstrap modal programmatically by triggering click on close button
        document.getElementById('closeModalBtn').click();
      } catch (err) {
        alert('Error creating account.');
        console.error(err);
      } finally {
        this.submitting = false;
      }
    },
    badgeClass(type) {
      return {
        'badge bg-success': type === 'cash',
        'badge bg-primary': type === 'bank',
        'badge bg-info text-dark': type === 'investment'
      };
    },
    balanceClass(balance) {
      return {
        'text-success fw-bold': balance > 0,
        'text-danger fw-bold': balance < 0,
        'text-muted': balance === 0
      };
    }
  }
};
</script>