<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>{{ title }}</span>
      <span class="badge bg-secondary">{{ categories.length }} categories</span>
    </div>
    <div class="card-body p-0">
      <div class="table-responsive">
        <table class="table table-striped table-hover mb-0">
          <thead class="table-dark">
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Transaction Count</th>
              <th>Total Amount</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in categories" :key="cat.id">
              <td><strong>{{ cat.name }}</strong></td>
              <td>
                <span :class="cat.type === 'expense' ? 'badge bg-danger' : 'badge bg-success'">
                  {{ cat.type }}
                </span>
              </td>
              <td>{{ getTransactionCount(cat.id) }}</td>
              <td :class="cat.type === 'expense' ? 'text-danger' : 'text-success'">
                {{ formatAmount(getTotalAmount(cat.id)) }}
              </td>
              <td class="text-center">
                <button class="btn btn-sm btn-outline-primary me-1" @click="$emit('edit', cat)" title="Edit">
                  ✏️ 
                </button>
                <button 
                  class="btn btn-sm btn-outline-danger" 
                  @click="$emit('delete', cat)" 
                  title="Delete">
                  🗑️ 
                </button>
              </td>
            </tr>
            <tr v-if="categories.length === 0">
              <td colspan="5" class="text-center text-muted py-5">
                No {{ type }} categories found. Click "+ New Category" to create one.
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
  name: 'CategoryTable',
  props: {
    categories: { type: Array, default: () => [] },
    type: { type: String, default: 'expense' },
    transactions: { type: Array, default: () => [] }
  },
  emits: ['edit', 'delete'],
  computed: {
    title() {
      return this.type === 'expense' ? 'Expense Categories' : 'Income Categories';
    }
  },
  methods: {
    getTransactionCount(categoryId) {
      return this.transactions.filter(t => t.category_id === categoryId).length;
    },
    getTotalAmount(categoryId) {
      const filtered = this.transactions.filter(t => t.category_id === categoryId);
      return filtered.reduce((sum, t) => sum + t.amount, 0);
    },
    formatAmount(amount) {
      return `€ ${amount.toFixed(2)}`;
    }
  }
}
</script>