<template>
  <div class="modal fade" id="confirmModal" tabindex="-1" ref="modal">
    <div class="modal-dialog modal-sm modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header" :class="type === 'danger' ? 'bg-danger text-white' : 'bg-white'">
          <h5 class="modal-title fw-bold">
            🤔
            {{ title }}
          </h5>
          <button type="button" class="btn-close" :class="type === 'danger' ? 'btn-close-white' : ''" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body p-4">
          <p class="mb-0">{{ message }}</p>
        </div>
        <div class="modal-footer border-0 bg-light">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn" :class="confirmClass" @click="confirm" :disabled="processing">
            {{ processing ? '...' : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';

export default {
  name: 'ConfirmModal',
  data() {
    return {
      modalInstance: null,
      resolvePromise: null,
      rejectPromise: null,
      title: 'Confirm',
      message: 'Are you sure?',
      confirmText: 'Confirm',
      type: 'primary',
      processing: false
    }
  },
  computed: {
    iconClass() {
      const icons = {
        primary: 'bi bi-question-circle',
        danger: 'bi bi-exclamation-triangle',
        warning: 'bi bi-exclamation-circle'
      };
      return icons[this.type] || icons.primary;
    },
    confirmClass() {
      const classes = {
        primary: 'btn-primary',
        danger: 'btn-danger',
        warning: 'btn-warning'
      };
      return classes[this.type] || classes.primary;
    }
  },
  mounted() {
    this.modalInstance = new Modal(this.$refs.modal);
  },
  methods: {
    show(options = {}) {
      this.title = options.title || 'Confirm';
      this.message = options.message || 'Are you sure?';
      this.confirmText = options.confirmText || 'Confirm';
      this.type = options.type || 'primary';
      this.processing = false;
      
      this.modalInstance.show();
      
      return new Promise((resolve) => {
        this.resolvePromise = resolve;
      });
    },
    
    async confirm() {
      this.processing = true;
      try {
        if (this.resolvePromise) {
          this.resolvePromise(true);
        }
        this.modalInstance.hide();
      } catch (err) {
        console.error('Confirm error:', err);
        if (this.resolvePromise) {
          this.resolvePromise(false);
        }
      } finally {
        this.processing = false;
      }
    },
    
    close() {
      if (this.resolvePromise) {
        this.resolvePromise(false);
      }
      this.modalInstance.hide();
    }
  }
};
</script>