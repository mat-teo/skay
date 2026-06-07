<template>
  <div class="modal fade" id="deleteCategoryModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title">Delete Category</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div v-if="category">
            <p>Are you sure you want to delete category <strong>{{ category.name }}</strong>?</p>
            <div v-if="transactionCount > 0" class="alert alert-warning">
              ⚠️ This category has {{ transactionCount }} transaction(s).
              These transactions will become "Uncategorized".
            </div>
            <p class="mb-0 small text-muted">This action cannot be undone.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-danger" @click="confirmDelete" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Delete Category' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';

export default {
  name: 'DeleteCategoryModal',
  props: {
    category: { type: Object, default: null },
    transactionCount: { type: Number, default: 0 }
  },
  emits: ['category-deleted'],
  data() {
    return {
      deleting: false
    }
  },
  methods: {
    async confirmDelete() {
      if (!this.category) return;
      this.deleting = true;
      try {
        await axios.delete(`http://127.0.0.1:8000/api/categories/${this.category.id}`);
        this.$emit('category-deleted', this.category.id);
        const modalElement = document.getElementById('deleteCategoryModal');
        if (modalElement) {
            const modal = Modal.getInstance(modalElement);
            if(modal){
                modal.hide();
            }else{
                 // Fallback: just hide manually
                modalElement.classList.remove('show');
                modalElement.style.display = 'none';
                document.body.classList.remove('modal-open');
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) backdrop.remove();
            }
        }
      } catch (err) {
        console.error('Failed to delete category:', err);
        alert(err.response?.data?.detail || 'Failed to delete category');
      } finally {
        this.deleting = false;
      }
    }
  }
}
</script>