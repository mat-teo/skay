<template>
  <div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center" 
         role="button" 
         @click="toggleFilters"
         style="cursor: pointer;">
      <div class="d-flex align-items-center gap-2">
        <i :class="isExpanded ? 'bi bi-chevron-down' : 'bi bi-chevron-right'"></i>
        <span>Filters</span>
        <span v-if="activeFiltersCount > 0" class="badge bg-primary rounded-pill">
          {{ activeFiltersCount }}
        </span>
      </div>
      <button class="btn btn-sm btn-outline-secondary" @click.stop="reset">
        Reset All
      </button>
    </div>
    
    <div v-show="isExpanded" class="card-body">
      <div class="row g-3">
        <!-- Type filter -->
        <div class="col-md-2">
          <label class="form-label">Type</label>
          <select class="form-select" v-model="localFilters.type" @change="emitChange">
            <option value="">All</option>
            <option value="expense">Expense</option>
            <option value="income">Income</option>
            <option value="transfer">Transfer</option>
          </select>
        </div>
        
        <!-- Category filter -->
        <div class="col-md-3">
          <label class="form-label">Category</label>
          <select class="form-select" v-model="localFilters.category_id" @change="emitChange">
            <option :value="null">All</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>
        
        <!-- Account filter -->
        <div class="col-md-3">
          <label class="form-label">Account</label>
          <select class="form-select" v-model="localFilters.account_id" @change="emitChange">
            <option :value="null">All</option>
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
              {{ acc.name }}
            </option>
          </select>
        </div>
        
        <!-- Amount range -->
        <div class="col-md-2">
          <label class="form-label">Min Amount (€)</label>
          <input type="number" step="0.01" class="form-control" v-model.number="localFilters.min_amount" @input="emitChange">
        </div>
        <div class="col-md-2">
          <label class="form-label">Max Amount (€)</label>
          <input type="number" step="0.01" class="form-control" v-model.number="localFilters.max_amount" @input="emitChange">
        </div>
      </div>
      
      <div class="row mt-3">
        <div class="col-12">
          <label class="form-label">Search in Notes</label>
          <input type="text" class="form-control" v-model="localFilters.search" @input="emitChange" 
                 placeholder="Search by keyword...">
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TransactionFilters',
  props: {
    categories: { type: Array, default: () => [] },
    accounts: { type: Array, default: () => [] }
  },
  emits: ['filter-change', 'reset'],
  data() {
    return {
      isExpanded: false,
      localFilters: {
        type: '',
        category_id: null,
        account_id: null,
        min_amount: null,
        max_amount: null,
        search: ''
      }
    }
  },
  computed: {
    activeFiltersCount() {
      let count = 0;
      if (this.localFilters.type) count++;
      if (this.localFilters.category_id) count++;
      if (this.localFilters.account_id) count++;
      if (this.localFilters.min_amount !== null && this.localFilters.min_amount !== '') count++;
      if (this.localFilters.max_amount !== null && this.localFilters.max_amount !== '') count++;
      if (this.localFilters.search && this.localFilters.search.trim()) count++;
      return count;
    }
  },
  methods: {
    toggleFilters() {
      this.isExpanded = !this.isExpanded;
    },
    
    emitChange() {
      this.$emit('filter-change', { ...this.localFilters });
    },
    
    reset() {
      this.localFilters = {
        type: '',
        category_id: null,
        account_id: null,
        min_amount: null,
        max_amount: null,
        search: ''
      };
      this.$emit('reset');
    }
  }
};
</script>

<style scoped>
.card-header {
  transition: background-color 0.2s ease;
}

.card-header:hover {
  background-color: #f8f9fa;
}
</style>