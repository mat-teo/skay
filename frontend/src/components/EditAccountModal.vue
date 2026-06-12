<template>
  <div class="modal fade" id="editAccountModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Account</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" id="closeEditAccountModalBtn"></button>
        </div>
        <div class="modal-body">
          <div v-if="!account">
            <div class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
          <form v-else @submit.prevent="updateAccount">
            <div class="mb-3">
              <label class="form-label">Account Name</label>
              <input type="text" class="form-control" v-model="editedAccount.name" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Type</label>
              <select class="form-select" v-model="editedAccount.type" required>
                <option value="cash">Cash</option>
                <option value="bank">Bank Account</option>
                <option value="investment">Investment</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Balance (€)</label>
              <input type="number" step="0.01" class="form-control" v-model.number="editedAccount.balance" required>
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
import { API_URL } from '../config';

export default {
  name: 'EditAccountModal',
  props: {
    account: {
      type: Object,
      default: null
    }
  },
  emits: ['account-updated'],
  data() {
    return {
      editedAccount: null,
      updating: false
    }
  },
  watch: {
    account: {
      handler(newVal) {
        if (newVal) {
          this.editedAccount = { ...newVal };
        }
      },
      immediate: true
    }
  },
  methods: {
    async updateAccount() {
      if (!this.editedAccount) return;
      
      this.updating = true;
      try {
        await axios.put(`${API_URL}/accounts/${this.editedAccount.id}`, {
          name: this.editedAccount.name,
          type: this.editedAccount.type,
          balance: this.editedAccount.balance
        });
        
        this.$emit('account-updated');
        
        const closeBtn = document.getElementById('closeEditAccountModalBtn');
        if (closeBtn) closeBtn.click();
      } catch (err) {
        console.error('Update failed:', err);
        this.$root.showToast(err.response?.data?.detail || 'Error updating account', "danger");
      } finally {
        this.updating = false;
      }
    }
  }
};
</script>