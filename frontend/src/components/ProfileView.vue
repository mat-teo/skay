<template>
  <div class="container-fluid py-4 profile-view">
    <header class="mb-4">
      <h2 class="fw-bold text-secondary">Profile Settings</h2>
      <hr>
    </header>

    <div class="row g-4">
      <div class="col-lg-6">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-bold text-secondary">Account Information</h5>
          </div>
          <div class="card-body p-4">
            <div class="mb-3">
              <label class="form-label fw-semibold text-muted small text-uppercase">Email</label>
              <input type="email" class="form-control bg-light" :value="user.email" disabled>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold text-muted small text-uppercase">Base Currency</label>
              <select class="form-select shadow-sm" v-model="user.base_currency" @change="updateCurrency">
                <option value="EUR">EUR (€)</option>
                <option value="USD">USD ($)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-bold text-secondary">Password Security</h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <input type="password" class="form-control" v-model="passwordForm.current" placeholder="Current Password" required>
              </div>
              <div class="mb-3">
                <input type="password" class="form-control" v-model="passwordForm.new" placeholder="New Password" required>
              </div>
              <div class="mb-3">
                <input type="password" class="form-control" v-model="passwordForm.confirm" placeholder="Confirm New Password" required>
              </div>
              <button type="submit" class="btn btn-primary px-4 fw-bold shadow-sm" :disabled="passwordChanging">
                {{ passwordChanging ? 'Updating...' : 'Update Password' }}
              </button>
            </form>
          </div>
        </div>

        <TwoFactorSetup />
      </div>
    </div>

    <!-- Import CSV - Full width -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-bold text-secondary">
              <i class="bi bi-file-earmark-arrow-up me-2 text-primary"></i>Import Data
            </h5>
          </div>
          <div class="card-body p-4">
            <p class="text-muted small mb-3">
              Import transactions from CSV files (e.g., from your bank).
              First, select an account, then upload the CSV file.
            </p>
            <ImportCSV @imported="onImportComplete" />
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '../config';
import TwoFactorSetup from './TwoFactorSetup.vue'; // Double check your relative folder structure here
import ImportCSV from './ImportCSV.vue';


export default {
  name: 'ProfileView',
  components: {
    TwoFactorSetup, ImportCSV
  },
  data() {
    return {
      user: {
        email: '',
        base_currency: 'EUR',
        created_at: null
      },
      passwordForm: {
        current: '',
        new: '',
        confirm: ''
      },
      passwordChanging: false
    };
  },
  computed: {
    memberSince() {
      if (!this.user.created_at) return '-';
      return new Date(this.user.created_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  },
  mounted() {
    this.loadUserProfile();
  },
  methods: {
    async loadUserProfile() {
      try {
        const response = await axios.get(`${API_URL}/users/me`);
        this.user = response.data;
      } catch (err) {
        console.error('Failed to load profile:', err);
      }
    },
    async updateCurrency() {
      try {
        await axios.put(`${API_URL}/users/me/currency`, {
          base_currency: this.user.base_currency
        });
        this.$root.showToast('Currency updated successfully', 'success');
      } catch (err) {
        this.$root.showToast('Failed to update currency', 'danger');
      }
    },
    async changePassword() {
      if (this.passwordForm.new !== this.passwordForm.confirm) {
        this.$root.showToast('New passwords do not match', 'warning');
        return;
      }
      if (this.passwordForm.new.length < 6) {
        this.$root.showToast('Password must be at least 6 characters long', 'warning');
        return;
      }

      this.passwordChanging = true;
      try {
        // DEV NOTE: If your backend still returns 422 or 400 errors, cross-check 
        // if your FastAPI schema expects 'old_password' instead of 'current_password'.
        await axios.post(`${API_URL}/auth/change-password`, {
          current_password: this.passwordForm.current, 
          new_password: this.passwordForm.new
        });
        
        this.$root.showToast('Password updated successfully!', 'success');
        this.passwordForm = { current: '', new: '', confirm: '' };
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to update password';
        this.$root.showToast(errorMsg, 'danger');
      } finally {
        this.passwordChanging = false;
      }
    }, 
    onImportComplete() {
      this.$root.showToast('Import complete! Transactions updated.', 'success');
    }
  }
};
</script>

<style scoped>
.letter-spacing-lg {
  letter-spacing: 0.15em;
}
</style>