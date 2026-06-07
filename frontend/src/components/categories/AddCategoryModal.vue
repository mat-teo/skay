<template>
  <div class="modal fade" id="addCategoryModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add New Category</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" id="closeAddModalBtn"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label">Category Name</label>
              <input type="text" class="form-control" v-model="localCategory.name" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Type</label>
              <select class="form-select" v-model="localCategory.type" required>
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>
            <div class="modal-footer px-0 pb-0">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Category</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AddCategoryModal',
  props: {
    defaultType: { type: String, default: 'expense' }
  },
  emits: ['category-added'],
  data() {
    return {
      localCategory: {
        name: '',
        type: this.defaultType
      }
    }
  },
  watch: {
    defaultType(val) {
      this.localCategory.type = val;
    }
  },
  methods: {
    reset() {
      this.localCategory = {
        name: '',
        type: this.defaultType
      };
    },
    async submit() {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/categories', this.localCategory);
        this.$emit('category-added', response.data);
        this.reset();
        document.getElementById('closeAddModalBtn').click();
      } catch (err) {
        console.error('Failed to create category:', err);
        alert(err.response?.data?.detail || 'Failed to create category');
      }
    }
  }
}
</script>