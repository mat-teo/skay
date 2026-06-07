<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>Transactions ({{ transactions.length }})</span>
      <span class="text-muted small">Scroll horizontally →</span>
    </div>
    <div class="card-body p-0">
      <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
        <table class="table table-striped table-hover mb-0">
          <thead class="table-dark sticky-top">
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Category</th>
              <th>Account</th>
              <th class="text-end">Amount</th>
              <th>Notes</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tx in transactions" :key="tx.id">
              <td style="white-space: nowrap;">{{ formatDate(tx.date) }}</td>
              <td><span :class="typeBadgeClass(tx.type)">{{ tx.type }}</span></td>
              <td><span class="badge bg-light text-dark border">{{ getCategoryName(tx.category_id) }}</span></td>
              <td>
                <span v-if="tx.type === 'expense'">from: {{ getAccountName(tx.account_source_id) }}</span>
                <span v-if="tx.type === 'income'">to: {{ getAccountName(tx.account_destination_id) }}</span>
                <span v-if="tx.type === 'transfer'">
                  {{ getAccountName(tx.account_source_id) }} → {{ getAccountName(tx.account_destination_id) }}
                </span>
              </td>
              <td class="text-end" :class="amountClass(tx.type)">
                {{ tx.type === 'expense' ? '-' : '+' }} {{ tx.amount.toFixed(2) }} €
              </td>
              <td><small class="text-muted">{{ tx.notes || '-' }}</small></td>
              <td class="text-center" style="white-space: nowrap;">
                <button class="btn btn-sm btn-outline-primary me-1" @click="$emit('edit', tx)" title="Edit">
                  ✏️
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="$emit('delete', tx)" title="Delete">
                  🗑️
                </button>
              </td>
            </tr>
            <tr v-if="transactions.length === 0 && !loading">
              <td colspan="7" class="text-center text-muted py-5">
                No transactions found for this period
              </td>
            </tr>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TransactionTable',
  props: {
    transactions: { type: Array, default: () => [] },
    categories: { type: Array, default: () => [] },
    accounts: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  emits: ['edit', 'delete'],
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Date(dateStr).toLocaleDateString();
    },
    
    getCategoryName(id) {
      if (!id) return '-';
      const cat = this.categories.find(c => c.id === id);
      return cat ? cat.name : 'Unknown';
    },
    
    getAccountName(id) {
      if (!id) return '-';
      const acc = this.accounts.find(a => a.id === id);
      return acc ? acc.name : 'Unknown';
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

<style scoped>
.sticky-top {
  position: sticky;
  top: 0;
  z-index: 10;
}
</style>