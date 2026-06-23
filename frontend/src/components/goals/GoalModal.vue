<template>
  <div class="modal fade" id="goalModal" tabindex="-1" ref="modal">
    <div class="modal-dialog">
      <div class="modal-content border-0 shadow">
        <div class="modal-header">
          <h5 class="modal-title fw-bold">{{ editingId ? '🔧 Edit Financial Goal' : '🎯 Create New Goal' }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label fw-semibold">Goal Name</label>
              <input type="text" class="form-control" v-model="form.name" required placeholder="e.g., New Electric Car Fund">
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label fw-semibold">Target Amount (€)</label>
                <input type="number" step="0.01" class="form-control" v-model.number="form.target_amount" required min="0.01">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label fw-semibold">Target Date</label>
                <input type="date" class="form-control" v-model="form.target_date" required>
              </div>
            </div>

            <div class="row">
              <div class="col-6 mb-3">
                <label class="form-label fw-semibold">Icon (Emoji)</label>
                <input type="text" class="form-control text-center fs-5" v-model="form.icon" placeholder="🎯">
              </div>
              <div class="col-6 mb-3">
                <label class="form-label fw-semibold">Card Tint Color</label>
                <input type="color" class="form-control form-control-color w-100" v-model="form.color">
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold">Tracking Architecture Method</label>
              <select class="form-select" v-model="form.tracking_mode" @change="onTrackingModeChange" :disabled="!!editingId">
                <option value="category">Category Inflows/Outflows Volume</option>
                <option value="account">Account Asset Distribution Fractional Share</option>
              </select>
              <small class="text-muted d-block mt-1" v-if="editingId">Tracking architecture types cannot be mutated after instantiation.</small>
            </div>

            <!-- Dynamic Category Content View block -->
            <div v-if="form.tracking_mode === 'category'" class="mb-3 card bg-light p-3 border-0">
              <label class="form-label fw-semibold">Target Transaction Category</label>
              <select class="form-select" v-model="form.category_id" required>
                <option :value="null" disabled>Select standard target index category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>

            <!-- Dynamic Account Content View block -->
            <div v-if="form.tracking_mode === 'account'" class="mb-3 card bg-light p-3 border-0">
              <div class="mb-2">
                <label class="form-label fw-semibold">Linked Treasury Account</label>
                <select class="form-select" v-model="form.account_id" required>
                  <option :value="null" disabled>Select linked cash pool origin</option>
                  <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                    {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                  </option>
                </select>
              </div>
              <div>
                <label class="form-label fw-semibold">Allocation Percentage Share ({{ form.allocation_percentage }}%)</label>
                <input type="range" class="form-range" min="1" max="100" step="0.5" v-model.number="form.allocation_percentage" required>
              </div>
            </div>

            <div class="modal-footer px-0 pb-0 d-flex justify-content-between mt-4">
              <div>
                <!-- Inline alternative execution path context trigger for deletion inside modal -->
                <button v-if="editingId" type="button" class="btn btn-outline-danger" @click="handleDeleteFromModal">
                  <i class="bi bi-trash3 me-1"></i> Delete
                </button>
              </div>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  {{ submitting ? 'Processing Write...' : 'Save Changes' }}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import { GoalService } from './GoalService';

export default {
  name: 'GoalModal',
  props: {
    editing: { type: Object, default: null },
    categories: { type: Array, default: () => [] },
    accounts: { type: Array, default: () => [] }
  },
  emits: ['saved', 'request-delete'],
  data() {
    return {
      form: {
        name: '',
        target_amount: 0,
        target_date: new Date().toISOString().split('T')[0],
        icon: '🎯',
        color: '#4f46e5',
        tracking_mode: 'category',
        category_id: null,
        account_id: null,
        allocation_percentage: 10,
        is_archived: false
      },
      submitting: false,
      modalInstance: null,
      editingId: null
    }
  },
  watch: {
    editing: {
      handler(val) {
        if (val) {
          this.editingId = val.id;
          this.form = {
            name: val.name,
            target_amount: val.target_amount,
            target_date: new Date(val.target_date).toISOString().split('T')[0],
            icon: val.icon || '🎯',
            color: val.color || '#4f46e5',
            tracking_mode: val.tracking_mode,
            category_id: val.category_id,
            account_id: val.account_id,
            allocation_percentage: val.allocation_percentage || 10,
            is_archived: val.is_archived || false
          };
        } else {
          this.resetForm();
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.modalInstance = new Modal(this.$refs.modal);
  },
  methods: {
    open() { this.modalInstance.show(); },
    close() { this.modalInstance.hide(); },
    resetForm() {
      this.form = {
        name: '',
        target_amount: 0,
        target_date: new Date().toISOString().split('T')[0],
        icon: '🎯',
        color: '#4f46e5',
        tracking_mode: 'category',
        category_id: null,
        account_id: null,
        allocation_percentage: 10,
        is_archived: false
      };
      this.editingId = null;
    },
    onTrackingModeChange() {
      this.form.category_id = null;
      this.form.account_id = null;
      this.form.allocation_percentage = this.form.tracking_mode === 'account' ? 10 : null;
    },
    handleDeleteFromModal() {
      this.close();
      this.$emit('request-delete', this.editingId);
    },
    async submit() {
      if (this.form.target_amount <= 0) {
        this.$root.showToast('Target metrics boundary must exceed zero floor limits', 'warning');
        return;
      }
      
      this.submitting = true;
      try {
        const payload = {
          name: this.form.name,
          target_amount: parseFloat(this.form.target_amount),
          target_date: new Date(this.form.target_date).toISOString(),
          icon: this.form.icon || '🎯',
          color: this.form.color || '#4f46e5',
          tracking_mode: this.form.tracking_mode,
          is_archived: this.form.is_archived,
          category_id: this.form.tracking_mode === 'category' ? parseInt(this.form.category_id) : null,
          account_id: this.form.tracking_mode === 'account' ? parseInt(this.form.account_id) : null,
          allocation_percentage: this.form.tracking_mode === 'account' ? parseFloat(this.form.allocation_percentage) : null
        };

        if (this.editingId) {
          await GoalService.updateGoal(this.editingId, payload);
        } else {
          await GoalService.createGoal(payload);
        }

        this.close();
        this.$emit('saved');
        this.$root.showToast(this.editingId ? 'Goal parameters successfully updated' : 'Goal initialized successfully', 'success');
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to save financial goal payload';
        this.$root.showToast(errorMsg, 'danger');
        console.error(err);
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>