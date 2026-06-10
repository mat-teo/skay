<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>
        <i class="bi bi-clock-history me-2"></i>
        Recent Transactions
      </span>
      <router-link to="/transactions" class="btn btn-sm btn-link">
        View all <i class="bi bi-arrow-right"></i>
      </router-link>
    </div>
    <div class="card-body p-0">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="transactions.length === 0" class="text-center py-4 text-muted">
        <i class="bi bi-receipt fs-1"></i>
        <p class="mt-2 mb-0">No transactions yet</p>
      </div>
      <div v-else class="table-responsive">
        <table class="table table-hover mb-0">
          <tbody>
            <tr v-for="tx in transactions" :key="tx.id">
              <td class="text-nowrap small text-muted">
                {{ formatDate(tx.date) }}
              </td>
              <td>
                <span :class="typeBadgeClass(tx.type)">
                  {{ tx.type }}
                </span>
              </td>
              <td>
                <span class="badge bg-light text-dark border">
                  {{ getCategoryName(tx.category_id) }}
                </span>
              </td>
              <td class="text-end" :class="amountClass(tx.type)">
                {{ tx.type === 'expense' ? '-' : '+' }} {{ tx.amount.toFixed(2) }} €
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RecentTransactions',
  props: {
    limit: { type: Number, default: 5 },
    startDate: { type: String, default: '' },
    endDate: { type: String, default: '' }
  },
  data() {
    return {
      transactions: [],
      categories: [],
      loading: false
    };
  },
  mounted() {
    this.fetchData();
    this.loadCategories();
  },
  watch: {
    startDate() { this.fetchData(); },
    endDate() { this.fetchData(); }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        let url = 'http://localhost:8000/api/transactions';
        const params = new URLSearchParams();
        
        if (this.startDate) params.append('start_date', this.startDate);
        if (this.endDate) params.append('end_date', this.endDate);
        if (params.toString()) url += `?${params.toString()}`;
        
        const response = await axios.get(url);
        // Sort by date descending and take first 'limit' entries
        this.transactions = response.data
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, this.limit);
      } catch (err) {
        console.error('Failed to load recent transactions:', err);
      } finally {
        this.loading = false;
      }
    },
    
    async loadCategories() {
      try {
        const response = await axios.get('http://localhost:8000/api/categories');
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
    
    amountClass(type) {
      return {
        'text-danger fw-bold': type === 'expense',
        'text-success fw-bold': type === 'income'
      };
    }
  }
};
</script>