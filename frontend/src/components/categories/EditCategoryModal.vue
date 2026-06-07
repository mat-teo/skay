<template>
  <div class="modal fade" id="editCategoryModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Category</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" id="closeEditModalBtn"></button>
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
              <button type="submit" class="btn btn-primary">Save Changes</button>
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
  name: 'EditCategoryModal',
  props: {
    category: { type: Object, default: null }
  },
  emits: ['category-updated'],
  data() {
    return {
      localCategory: {name:'', type:'expense'}
    }
  },
  watch: {
    category: {
      handler(val) {
        if (val) {
          this.localCategory = { ...val };
        }
      },
      immediate: true
    }
  },
  methods: {
    async submit() {
      if (!this.localCategory) return;
      try {
        await axios.put(`http://127.0.0.1:8000/api/categories/${this.localCategory.id}`, this.localCategory);
        this.$emit('category-updated', this.localCategory);
        document.getElementById('closeEditModalBtn').click();
      } catch (err) {
        console.error('Failed to update category:', err);
        alert(err.response?.data?.detail || 'Failed to update category');
      }
    }
  }
}
</script>