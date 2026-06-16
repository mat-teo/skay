<template>
  <div class="card mb-4" v-if="payments.length > 0">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>
        <i class="bi bi-clock-history me-2"></i>
        Planned Payments
      </span>
      <button class="btn btn-sm btn-outline-primary" @click="toggleExpand">
        {{ expanded ? 'Show less' : 'View all' }}
      </button>
    </div>
    <div class="card-body p-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Amount</th>
              <th>Due</th>
              <th>Category</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in displayedPayments" :key="item.id">
              <td>{{ item.name }}</td>
              <td class="fw-bold">€ {{ item.amount.toFixed(2) }}</td>
              <td>
                <span :class="getDaysUntilClass(item.next_date)">
                  {{ getDaysUntilText(item.next_date) }}
                </span>
              </td>
              <td>{{ getCategoryName(item.category_id) || '-' }}</td>
              <td class="text-center">
                <button class="btn btn-sm btn-outline-primary me-1" @click="$emit('edit', item)" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger me-1" @click="$emit('delete', item.id)" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
                <button class="btn btn-sm btn-success me-1" @click="$emit('pay', item.id)" title="Pay now">
                    <i class="bi bi-check2"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" @click="$emit('skip', item.id)" title="Skip">
                    <i class="bi bi-forward"></i>
                </button>
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
  name: 'PlannedPayments',
  props: {
    payments: { type: Array, default: () => [] },
    categories: { type: Array, default: () => [] },
    defaultLimit: { type: Number, default: 3 }
  },
  emits: ['pay', 'skip'],
  data() {
    return {
      expanded: false
    }
  },
  computed: {
    displayedPayments() {
      return this.expanded ? this.payments : this.payments.slice(0, this.defaultLimit);
    }
  },
  methods: {
    toggleExpand() {
      this.expanded = !this.expanded;
    },
    getDaysUntil(dateStr) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const date = new Date(dateStr);
      date.setHours(0, 0, 0, 0);
      return Math.ceil((date - today) / (1000 * 60 * 60 * 24));
    },
    getDaysUntilText(dateStr) {
      const days = this.getDaysUntil(dateStr);
      if (days < 0) return ` Overdue (${Math.abs(days)} days)`;
      if (days === 0) return 'Today';
      if (days === 1) return ' Tomorrow';
      return `📅 ${days} days`;
    },
    getDaysUntilClass(dateStr) {
      const days = this.getDaysUntil(dateStr);
      if (days < 0) return 'text-danger fw-bold';
      if (days <= 2) return 'text-warning fw-bold';
      return 'text-muted';
    },
    getCategoryName(id) {
      if (!id) return null;
      const cat = this.categories.find(c => c.id === id);
      return cat ? cat.name : null;
    }
  }
}
</script>