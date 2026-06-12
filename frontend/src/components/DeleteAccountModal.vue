<template>
  <div class="modal fade" id="deleteAccountModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title">Delete Account</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" id="closeDeleteAccountModalBtn"></button>
        </div>
        <div class="modal-body">
          <div v-if="!account">
            <div class="text-center py-3">
              <div class="spinner-border text-danger" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
          <div v-else>
            <p>Are you sure you want to delete <strong>{{ account.name }}</strong>?</p>
            
            <div v-if="hasTransactions" class="alert alert-danger">
              <strong>⚠️ WARNING:</strong> This account has {{ transactionCount }} transaction(s).<br>
              All transactions linked to this account will be permanently deleted!
            </div>
            
            <div v-else class="alert alert-warning">
              This account has no transactions. You can safely delete it.
            </div>
            
            <div v-if="account.balance !== 0 && !hasTransactions" class="alert alert-warning">
              This account has a balance of {{ account.balance.toFixed(2) }} €.
              Deleting it will remove this balance from your net worth.
            </div>
            
            <p class="mb-0 small text-muted">This action cannot be undone.</p>
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
import { API_URL } from '../config';

export default {
  name: 'DeleteAccountModal',
  props: {
    account: {
      type: Object,
      default: null
    }
  },
  emits: ['account-deleted'],
  data() {
    return {
      deleting: false,
      transactionCount: 0,
      hasTransactions: false
    }
  },
  watch: {
    account: {
      handler(newVal) {
        if (newVal) {
          this.checkTransactions();
        }
      },
      immediate: true
    }
  },
  methods: {
    async checkTransactions() {
      try {
        const response = await axios.get(API_URL +  '/transactions');
        const transactions = response.data;
        this.transactionCount = transactions.filter(t => 
          t.account_source_id === this.account?.id || 
          t.account_destination_id === this.account?.id
        ).length;
        this.hasTransactions = this.transactionCount > 0;
      } catch (err) {
        console.error('Failed to check transactions:', err);
      }
    },
    
    async handleDelete() {
      this.deleting = true;
      try {
        await axios.delete(`${API_URL}/accounts/${this.account.id}`);
        this.$emit('account-deleted');
        
        const closeBtn = document.getElementById('closeDeleteAccountModalBtn');
        if (closeBtn) closeBtn.click();
      } catch (err) {
        console.error('Delete failed:', err);
        this.$root.showToast(err.response?.data?.detail || 'Error deleting account', "danger");
      } finally {
        this.deleting = false;
      }
    }
  }
};
</script>