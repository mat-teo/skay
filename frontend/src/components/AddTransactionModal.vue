<template>
  <div class="modal fade" id="addTransactionModal" tabindex="-1" aria-labelledby="addTransactionModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-dark text-white">
          <h5 class="modal-title fw-bold" id="addTransactionModalLabel">New Transaction</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <form @submit.prevent="submitTransaction">
          <div class="modal-body p-4">
            
            <div class="mb-3">
              <label class="form-label fw-semibold text-secondary">Amount (€)</label>
              <input type="number" step="0.01" class="form-control form-control-lg" v-model.number="newTx.amount" required placeholder="0.00">
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold text-secondary">Transaction Type</label>
              <select class="form-select" v-model="newTx.type" required>
                <option value="expense">Expense (-)</option>
                <option value="income">Income (+)</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold text-secondary">Category</label>
              
              <div v-if="!showInlineCategoryInput" class="input-group">
                <select class="form-select" v-model="newTx.category" required>
                  <option value="" disabled>Select a category</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.name">
                    {{ cat.name }}
                  </option>
                </select>
                <button type="button" class="btn btn-outline-primary" @click="showInlineCategoryInput = true">
                  <i class="bi bi-plus-lg"></i> Add
                </button>
              </div>

              <div v-else class="input-group">
                <input type="text" class="form-control" v-model="newCategoryName" placeholder="New category name..." ref="catInput">
                <button type="button" class="btn btn-success" @click="submitCategory">Save</button>
                <button type="button" class="btn btn-secondary" @click="showInlineCategoryInput = false">Cancel</button>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold text-secondary">Date</label>
              <input type="date" class="form-control" v-model="newTx.date" required>
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold text-secondary">Account ID</label>
              <input type="number" class="form-control" v-model.number="newTx.account_id" required placeholder="e.g., 1">
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold text-secondary">Notes (Optional)</label>
              <input type="text" class="form-control" v-model="newTx.notes" placeholder="Groceries, Monthly Salary, Rent...">
            </div>

          </div>
          <div class="modal-footer bg-light border-0">
            <button type="button" class="btn btn-secondary px-4" data-bs-dismiss="modal" ref="closeModalButton">Cancel</button>
            <button type="submit" class="btn btn-primary px-4 fw-medium">Save Transaction</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AddTransactionModal',
  data() {
    return {
      categories: [],
      newCategoryName: '',
      showInlineCategoryInput: false,
      newTx: {
        amount: null,
        type: 'expense',
        category: '',
        date: new Date().toISOString().split('T')[0],
        notes: '',
        account_id: 1,
        user_id: 1
      }
    };
  },
  methods: {
    /**
     * Pulls category array from database pipeline
     */
    async fetchCategories() {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/categories');
        this.categories = res.data;
      } catch (err) {
        console.error("Failed to load categories:", err);
      }
    },

    /**
     * Submits an inline category add request to the backend database
     */
    async submitCategory() {
      const name = this.newCategoryName.trim();
      if (!name) return;
      try {
        await axios.post('http://127.0.0.1:8000/api/categories', { name });
        await this.fetchCategories();
        this.newTx.category = name; // Pre-select the newly created category
        this.newCategoryName = '';
        this.showInlineCategoryInput = false;
        this.$emit('notify', { message: `Category "${name}" created!`, type: 'success' });
      } catch (err) {
        console.error("Failed to save category:", err);
        this.$emit('notify', { message: "Failed to create category.", type: 'danger' });
      }
    },

    /**
     * Dispatches payload to append transaction data row
     */
    async submitTransaction() {
      try {
        await axios.post('http://127.0.0.1:8000/api/transactions', this.newTx);
        
        // Emit refresh signal to parent components
        this.$emit('transaction-saved');
        this.$emit('notify', { message: "Transaction saved successfully!", type: 'success' });

        // Reset state data model parameters safely
        this.newTx = {
          amount: null,
          type: 'expense',
          category: '',
          date: new Date().toISOString().split('T')[0],
          notes: '',
          account_id: 1,
          user_id: 1
        };

        // Close the modal native frame
        if (this.$refs.closeModalButton) {
          this.$refs.closeModalButton.click();
        }
      } catch (err) {
        console.error("API error during transaction storage:", err);
        this.$emit('notify', { message: "Failed to save transaction.", type: 'danger' });
      }
    }
  },
  mounted() {
    this.fetchCategories();
  }
};
</script>