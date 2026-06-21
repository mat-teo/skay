<template>
  <div class="modal fade" id="recurringModal" tabindex="-1" ref="modal">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditing ? 'Edit Recurring' : 'New Recurring Transaction' }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label">Name</label>
              <input type="text" class="form-control" v-model="form.name" required>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Amount (€)</label>
                <input type="number" step="0.01" class="form-control" v-model.number="form.amount" required min="0.01">
                <small class="text-danger" v-if="form.amount < 0.01">Amount must be greater than 0.01</small>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Type</label>
                <select class="form-select" v-model="form.type" required>
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Category <span class="text-danger">*</span></label>
              <select class="form-select" v-model="form.category_id" required>
                <option :value="null" disabled>Select a category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
              <small class="text-danger" v-if="!form.category_id && submitted">Category is required</small>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Account <span class="text-danger">*</span></label>
              <select class="form-select" v-model="form.account_id" required>
                <option :value="null" disabled>Select an account</option>
                <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                  {{ acc.name }} ({{ acc.balance.toFixed(2) }} €)
                </option>
              </select>
              <small class="text-danger" v-if="!form.account_id && submitted">Account is required</small>
            </div>
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Frequency</label>
                <select class="form-select" v-model="form.frequency" @change="onFrequencyChange">
                  <option value="monthly">Monthly</option>
                  <option value="weekly">Weekly</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div class="col-md-6 mb-3" v-if="form.frequency === 'monthly'">
                <label class="form-label">Day of Month</label>
                <input type="number" class="form-control" v-model.number="form.day_of_month" min="1" max="31">
              </div>
              <div class="col-md-6 mb-3" v-if="form.frequency === 'weekly'">
                <label class="form-label">Day of Week</label>
                <select class="form-select" v-model="form.day_of_week">
                  <option :value="0">Monday</option>
                  <option :value="1">Tuesday</option>
                  <option :value="2">Wednesday</option>
                  <option :value="3">Thursday</option>
                  <option :value="4">Friday</option>
                  <option :value="5">Saturday</option>
                  <option :value="6">Sunday</option>
                </select>
              </div>
              <div class="col-md-6 mb-3" v-if="form.frequency === 'custom'">
                <label class="form-label">Every X Months</label>
                <input type="number" class="form-control" v-model.number="form.custom_interval_months" min="1">
              </div>
            </div>
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Start Date</label>
                <input type="date" class="form-control" v-model="form.start_date" required>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">End Date</label>
                <input type="date" class="form-control" v-model="form.end_date">
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Notes</label>
              <input type="text" class="form-control" v-model="form.notes" placeholder="Optional notes">
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-danger me-2" v-if="isEditing" @click="confirmDelete">
            <i class="bi bi-trash"></i> Delete
          </button>
          <button type="submit" class="btn btn-primary" @click="submit" :disabled="submitting || !isValid">
            {{ submitting ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';
import { API_URL } from '../../config';

export default {
  name: 'RecurringModal',
  props: {
    categories: { type: Array, default: () => [] },
    accounts: { type: Array, default: () => [] },
    editing: { type: Object, default: null }
  },
  emits: ['saved', 'deleted', 'update:editing'],
  data() {
    return {
      form: {
        name: '',
        amount: 0,
        type: 'expense',
        category_id: null,
        account_id: null,
        frequency: 'monthly',
        day_of_month: 1,
        day_of_week: 0,
        custom_interval_months: null,
        start_date: new Date().toISOString().split('T')[0],
        end_date: null,
        notes: '',
        is_active: true
      },
      submitting: false,
      submitted: false,
      modalInstance: null,
      isEditing: false,
      editingId: null
    }
  },
  computed: {
    isValid() {
      return this.form.amount >= 0.01 && this.form.category_id && this.form.account_id && this.form.name.trim();
    }
  },
  watch: {
    editing: {
      handler(val) {
        if (val) {
          this.isEditing = true;
          this.editingId = val.id;
          this.form = {
            name: val.name,
            amount: val.amount,
            type: val.type,
            category_id: val.category_id,
            account_id: val.account_id,
            frequency: val.frequency || 'monthly',
            day_of_month: val.day_of_month || 1,
            day_of_week: val.day_of_week || 0,
            custom_interval_months: val.custom_interval_months || null,
            start_date: val.start_date?.split('T')[0] || new Date().toISOString().split('T')[0],
            end_date: val.end_date?.split('T')[0] || null,
            notes: val.notes || '',
            is_active: val.is_active !== undefined ? val.is_active : true
          };
        } else {
          this.isEditing = false;
          this.editingId = null;
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
    open() {
      this.submitted = false;
      this.modalInstance.show();
    },
    close() {
      this.modalInstance.hide();
      this.$emit('update:editing', null);
    },
    resetForm() {
      this.form = {
        name: '',
        amount: 0,
        type: 'expense',
        category_id: null,
        account_id: null,
        frequency: 'monthly',
        day_of_month: 1,
        day_of_week: 0,
        custom_interval_months: null,
        start_date: new Date().toISOString().split('T')[0],
        end_date: null,
        notes: '',
        is_active: true
      };
      this.submitted = false;
      this.isEditing = false;
      this.editingId = null;
    },
    onFrequencyChange() {
      if (this.form.frequency === 'monthly') {
        this.form.day_of_month = 1;
        this.form.day_of_week = null;
        this.form.custom_interval_months = null;
      } else if (this.form.frequency === 'weekly') {
        this.form.day_of_month = null;
        this.form.day_of_week = 0;
        this.form.custom_interval_months = null;
      } else {
        this.form.day_of_month = null;
        this.form.day_of_week = null;
        this.form.custom_interval_months = 1;
      }
    },
    async submit() {
      this.submitted = true;
      if (!this.isValid) {
        this.$root.showToast('Please fill all required fields', 'warning');
        return;
      }
      
      this.submitting = true;
      try {
        const payload = { ...this.form };
        if (this.editingId) {
          await axios.put(`${API_URL}/recurring/${this.editingId}`, payload);
        } else {
          await axios.post(`${API_URL}/recurring`, payload);
        }
        this.close();
        this.$emit('saved');
        this.$root.showToast('Recurring transaction saved!', 'success');
      } catch (err) {
        this.$root.showToast(err.response?.data?.detail || 'Failed to save', 'danger');
      } finally {
        this.submitting = false;
      }
    },
    async confirmDelete() {
      if (await confirm('Delete this recurring transaction?')) {
        this.deleteRecurring();
      }
    },
    async deleteRecurring() {
      try {
        await axios.delete(`${API_URL}/recurring/${this.editingId}`);
        this.close();
        this.$emit('deleted');
        this.$root.showToast('Recurring transaction deleted', 'success');
      } catch (err) {
        this.$root.showToast('Failed to delete', 'danger');
      }
    }
  }
};
</script>