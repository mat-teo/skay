<template>
  <div class="transactions-view">
    <header class="page-header d-flex justify-content-between align-items-center mb-4 pb-2">
      <div>
        <h1 class="page-title mt-1 mb-0">Transactions</h1>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" @click="openRecurringModal">
          <i class="bi bi-clock-history me-1"></i> New Recurring
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addTransactionModal" @click="loadFormData">
          + New Transaction
        </button>
        <button class="btn btn-outline-secondary btn-sm" @click="exportCSV">
          Export
        </button>
      </div>
    </header>

    <!-- Planned Payments -->
    <PlannedPayments
      :payments="upcomingRecurring"
      :categories="categories"
      @pay="payRecurring"
      @skip="skipRecurring"
      @edit="editRecurring"
      @delete="deleteRecurring"
    />

    <!-- Period Selector -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label">Period Type</label>
            <select class="form-select" v-model="periodType" @change="onPeriodTypeChange">
              <option value="month">Monthly</option>
              <option value="week">Weekly</option>
              <option value="year">Yearly</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
          
          <div class="col-md-4" v-if="periodType !== 'custom'">
            <div class="btn-group" role="group">
              <button class="btn btn-outline-secondary" @click="navigatePeriod(-1)">← Previous</button>
              <button class="btn btn-outline-secondary" @click="navigatePeriod(1)">Next →</button>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="text-end">
              <span class="badge bg-secondary fs-6 p-2">
                {{ periodLabel }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- Custom date range -->
        <div class="row mt-3" v-if="periodType === 'custom'">
          <div class="col-md-5">
            <label class="form-label">Start Date</label>
            <input type="date" class="form-control" v-model="customStartDate">
          </div>
          <div class="col-md-5">
            <label class="form-label">End Date</label>
            <input type="date" class="form-control" v-model="customEndDate">
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary w-100" @click="applyCustomRange">Apply</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <TransactionFilters 
      :categories="categories"
      :accounts="accounts"
      @filter-change="applyFilters"
      @reset="resetFilters"
    />

    <!-- Transactions Table -->
    <TransactionTable 
      :transactions="filteredTransactions"
      :categories="categories"
      :accounts="accounts"
      :loading="loading"
      @edit="openEditModal"
      @delete="openDeleteModal"
    />

    <!-- Modals -->
    <EditTransactionModal 
      :transaction="selectedTransaction"
      @transaction-updated="onTransactionUpdated"
    />
    
    <DeleteTransactionModal 
      :transaction="selectedDeleteTransaction"
      @transaction-deleted="onTransactionDeleted"
    />

    <!-- Add Transaction Modal -->
    <AddTransactionModal
      :accounts="accounts"
      :categories="categories"
      @transaction-added="onTransactionAdded"
    />

    <!-- Recurring Modal -->
    <RecurringModal
      ref="recurringModal"
      :editing="editingRecurring"
      :categories="categories"
      :accounts="accounts"
      @saved="onRecurringSaved"
      @deleted="onRecurringDeleted"
    />
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '../../config.js';
import { Modal } from 'bootstrap';
import TransactionFilters from './TransactionFilters.vue';
import TransactionTable from './TransactionTable.vue';
import DeleteTransactionModal from './DeleteTransactionModal.vue';
import EditTransactionModal from './EditTransactionModal.vue';
import AddTransactionModal from './AddTransactionModal.vue';
import PlannedPayments from './PlannedPayments.vue';
import RecurringModal from './RecurringModal.vue';

export default {
  name: 'TransactionsView',
  components: { 
    TransactionFilters, 
    TransactionTable, 
    DeleteTransactionModal, 
    EditTransactionModal, 
    AddTransactionModal, 
    PlannedPayments, 
    RecurringModal
  },
  data() {
    return {
      transactions: [],
      categories: [],
      accounts: [],
      upcomingRecurring: [],
      loading: false,
      
      // Period state
      periodType: 'month',
      currentOffset: 0,
      customStartDate: '',
      customEndDate: '',
      activeStartDate: null,
      activeEndDate: null,
      
      // Filter state
      filters: {
        type: '',
        category_id: null,
        account_id: null,
        min_amount: null,
        max_amount: null,
        search: ''
      },
      
      // Modal state
      selectedTransaction: null,
      selectedDeleteTransaction: null,
      editingRecurring: null
    }
  },
  computed: {
    periodLabel() {
      if (this.periodType === 'custom') {
        return `${this.activeStartDate || this.customStartDate} → ${this.activeEndDate || this.customEndDate}`;
      }
      
      const now = new Date();
      const target = new Date(now);
      
      switch(this.periodType) {
        case 'week':
          target.setDate(now.getDate() + (this.currentOffset * 7));
          const weekStart = this.getWeekStart(target);
          const weekEnd = this.getWeekEnd(target);
          return `${weekStart.toLocaleDateString()} - ${weekEnd.toLocaleDateString()}`;
        case 'month':
          target.setMonth(now.getMonth() + this.currentOffset);
          return target.toLocaleDateString('default', { month: 'long', year: 'numeric' });
        case 'year':
          return (target.getFullYear() + this.currentOffset).toString();
        default:
          return '';
      }
    },
    
    filteredTransactions() {
      let result = [...this.transactions];
      
      if (this.filters.type) {
        result = result.filter(t => t.type === this.filters.type);
      }
      if (this.filters.category_id) {
        result = result.filter(t => t.category_id === this.filters.category_id);
      }
      if (this.filters.account_id) {
        result = result.filter(t => 
          t.account_source_id === this.filters.account_id || 
          t.account_destination_id === this.filters.account_id
        );
      }
      if (this.filters.min_amount) {
        result = result.filter(t => t.amount >= this.filters.min_amount);
      }
      if (this.filters.max_amount) {
        result = result.filter(t => t.amount <= this.filters.max_amount);
      }
      if (this.filters.search) {
        const searchLower = this.filters.search.toLowerCase();
        result = result.filter(t => 
          t.notes?.toLowerCase().includes(searchLower) ||
          t.type?.toLowerCase().includes(searchLower)
        );
      }
      
      return result;
    }
  },
  mounted() {
    this.loadInitialData();
    this.loadFormData();
    this.loadRecurring();
  },
  methods: {
    editRecurring(item) {
      this.editingRecurring = { ...item };
      this.$refs.recurringModal.open();
    },

    async deleteRecurring(id) {
      if (!confirm('Delete this recurring transaction?')) return;
      try {
        await axios.delete(`${API_URL}/recurring/${id}`);
        this.loadRecurring();
        this.$root.showToast('Recurring transaction deleted', 'success');
      } catch (err) {
        this.$root.showToast('Failed to delete', 'danger');
      }
    },
    
    async loadRecurring() {
      try {
        const response = await axios.get(`${API_URL}/recurring/upcoming?limit=10`);
        this.upcomingRecurring = response.data;
      } catch (err) {
        console.error('Failed to load recurring:', err);
      }
    },
    
    openRecurringModal() {
      this.editingRecurring = null;
      this.$refs.recurringModal.open();
    },
    
    onRecurringSaved() {
      this.editingRecurring = null;
      this.loadRecurring();
      this.loadTransactions();
    },
    
    onRecurringDeleted() {
      this.editingRecurring = null;
      this.loadRecurring();
      this.loadTransactions();
    },
    
    async payRecurring(id) {
      if (!confirm(`Pay this recurring transaction? This will update your account balance.`)) return;
      try {
        await axios.post(`${API_URL}/recurring/${id}/pay`);
        this.loadRecurring();
        this.loadTransactions();
        this.$root.showToast('Payment recorded!', 'success');
      } catch (err) {
        this.$root.showToast('Failed to record payment', 'danger');
      }
    },
    
    async skipRecurring(id) {
      if (!confirm(`Skip this occurrence? The next one will be scheduled.`)) return;
      try {
        await axios.post(`${API_URL}/recurring/${id}/skip`);
        this.loadRecurring();
        this.$root.showToast('Occurrence skipped', 'info');
      } catch (err) {
        this.$root.showToast('Failed to skip', 'danger');
      }
    },
    
    getWeekStart(date) {
      const d = new Date(date);
      const day = d.getDay();
      const diff = d.getDate() - day + (day === 0 ? -6 : 1);
      return new Date(d.setDate(diff));
    },
    
    getWeekEnd(date) {
      const start = this.getWeekStart(date);
      const end = new Date(start);
      end.setDate(start.getDate() + 6);
      return end;
    },
    
    getDateRange() {
      const now = new Date();
      
      switch(this.periodType) {
        case 'week': {
          const baseDate = new Date(now);
          baseDate.setDate(now.getDate() + (this.currentOffset * 7));
          const start = this.getWeekStart(baseDate);
          const end = this.getWeekEnd(baseDate);
          start.setHours(0, 0, 0, 0);
          end.setHours(23, 59, 59, 999);
          return { start_date: start, end_date: end };
        }
        case 'month': {
          const target = new Date(now);
          target.setMonth(now.getMonth() + this.currentOffset);
          const start = new Date(target.getFullYear(), target.getMonth(), 1);
          const end = new Date(target.getFullYear(), target.getMonth() + 1, 0);
          start.setHours(0, 0, 0, 0);
          end.setHours(23, 59, 59, 999);
          return { start_date: start, end_date: end };
        }
        case 'year': {
          const year = now.getFullYear() + this.currentOffset;
          const start = new Date(year, 0, 1);
          const end = new Date(year, 11, 31);
          start.setHours(0, 0, 0, 0);
          end.setHours(23, 59, 59, 999);
          return { start_date: start, end_date: end };
        }
        case 'custom': {
          if (!this.activeStartDate || !this.activeEndDate) return null;
          return {
            start_date: new Date(this.activeStartDate),
            end_date: new Date(this.activeEndDate)
          };
        }
        default:
          return null;
      }
    },
    
    onTransactionAdded() {
      this.loadTransactions();
      this.$emit('transaction-saved');
    },
    
    async loadInitialData() {
      await this.loadTransactions();
      await this.loadCategories();
      await this.loadAccounts();
    },
    
    async loadTransactions() {
      this.loading = true;
      try {
        const range = this.getDateRange();
        let url = API_URL + '/transactions';
        
        if (range) {
          const params = new URLSearchParams();
          params.append('start_date', range.start_date.toISOString());
          params.append('end_date', range.end_date.toISOString());
          url += `?${params.toString()}`;
        }
        
        const response = await axios.get(url);
        this.transactions = response.data.sort((a, b) => 
          new Date(b.date) - new Date(a.date)
        );
      } catch (err) {
        console.error('Failed to load transactions:', err);
      } finally {
        this.loading = false;
      }
    },
    
    async loadCategories() {
      try {
        const response = await axios.get(API_URL + '/categories');
        this.categories = response.data;
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    },
    
    async loadAccounts() {
      try {
        const response = await axios.get(API_URL + '/accounts');
        this.accounts = response.data;
      } catch (err) {
        console.error('Failed to load accounts:', err);
      }
    },
    
    loadFormData() {
      this.loadCategories();
      this.loadAccounts();
    },
    
    navigatePeriod(direction) {
      this.currentOffset += direction;
      this.loadTransactions();
    },
    
    onPeriodTypeChange() {
      this.currentOffset = 0;
      if (this.periodType !== 'custom') {
        this.loadTransactions();
      }
    },
    
    applyCustomRange() {
      this.activeStartDate = this.customStartDate;
      this.activeEndDate = this.customEndDate;
      this.loadTransactions();
    },
    
    applyFilters(filters) {
      this.filters = { ...this.filters, ...filters };
    },
    
    resetFilters() {
      this.filters = {
        type: '',
        category_id: null,
        account_id: null,
        min_amount: null,
        max_amount: null,
        search: ''
      };
    },
    
    openEditModal(transaction) {
      this.selectedTransaction = transaction;
      const modalElement = document.getElementById('editTransactionModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    },
    
    openDeleteModal(transaction) {
      this.selectedDeleteTransaction = transaction;
      const modalElement = document.getElementById('deleteTransactionModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    },
    
    onTransactionUpdated() {
      this.loadTransactions();
      this.$emit('transaction-saved');
    },
    
    onTransactionDeleted() {
      this.loadTransactions();
      this.$emit('transaction-saved');
      this.selectedDeleteTransaction = null;
    },
    
    async exportCSV() {
      try {
        const range = this.getDateRange();
        let url = API_URL + '/transactions/export';
        
        if (range) {
          const params = new URLSearchParams();
          params.append('start_date', range.start_date.toISOString());
          params.append('end_date', range.end_date.toISOString());
          url += `?${params.toString()}`;
        }
        
        const token = localStorage.getItem('token');
        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        
        this.$root.showToast('Export completed successfully', 'success');
      } catch (err) {
        console.error('Export failed:', err);
        this.$root.showToast('Export failed', 'danger');
      }
    }
  }
};
</script>

<style scoped>
.transactions-view {
  padding-bottom: 40px;
}
</style>