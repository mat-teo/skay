<template>
  <div class="budgets-view">
    <header class="page-header d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title"> Budgets</h1>
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addBudgetModal">
        + New Budget
      </button>
    </header>

    <!-- Budget progress cards -->
    <div class="row g-4">
      <div v-for="budget in budgetProgress" :key="budget.id" class="col-md-6 col-lg-4">
        <div class="card h-100" :class="{ 'border-danger': budget.is_exceeded }">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>{{ budget.name }}</span>
            <div class="small text-muted mt-1">
                <span v-if="budget.category_name">
                <i class="bi bi-tag me-1"></i>{{ budget.category_name }}
                </span>
                <span v-else class="text-primary">
                <i class="bi bi-globe me-1"></i>Global budget
                </span>
            </div>
            <span class="badge" :class="budget.is_exceeded ? 'bg-danger' : 'bg-secondary'">
              {{ budget.period }}
            </span>
          </div>
          <div class="card-body">
            <div class="d-flex justify-content-between mb-2">
              <span>Budget: <strong>€ {{ budget.amount.toFixed(2) }}</strong></span>
              <span>Spent: <strong :class="{ 'text-danger': budget.is_exceeded }">€ {{ budget.spent.toFixed(2) }}</strong></span>
            </div>
            <div class="progress mb-3" style="height: 10px;">
              <div 
                class="progress-bar" 
                :class="budget.percentage > 100 ? 'bg-danger' : 'bg-success'"
                :style="{ width: Math.min(budget.percentage, 100) + '%' }"
                role="progressbar"
              ></div>
            </div>
            <div class="d-flex justify-content-between">
              <span class="small text-muted">
                Remaining: € {{ budget.remaining.toFixed(2) }}
              </span>
              <span class="small fw-bold" :class="budget.percentage > 100 ? 'text-danger' : 'text-success'">
                {{ budget.percentage }}%
              </span>
            </div>
          </div>
          <div class="card-footer bg-transparent d-flex justify-content-end gap-2">
            <button class="btn btn-sm btn-outline-primary" @click="editBudget(budget)">Edit</button>
            <button class="btn btn-sm btn-outline-danger" @click="deleteBudget(budget)">Delete</button>
          </div>
        </div>
      </div>
      
      <div v-if="budgetProgress.length === 0" class="col-12">
        <div class="alert alert-info text-center">
          No budgets yet. Click "New Budget" to start planning!
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal fade" id="addBudgetModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingBudget ? 'Edit Budget' : 'New Budget' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveBudget">
              <div class="mb-3">
                <label class="form-label">Name</label>
                <input type="text" class="form-control" v-model="form.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Category (optional)</label>
                <select class="form-select" v-model="form.category_id">
                  <option :value="null">All categories (global budget)</option>
                  <option v-for="cat in expenseCategories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Amount (€)</label>
                  <input type="number" step="10" class="form-control" v-model.number="form.amount" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Period</label>
                  <select class="form-select" v-model="form.period">
                    <option value="monthly">Monthly</option>
                    <option value="weekly">Weekly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Start Date</label>
                  <input type="date" class="form-control" v-model="form.start_date">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">End Date (optional)</label>
                  <input type="date" class="form-control" v-model="form.end_date">
                </div>
              </div>
              <div class="modal-footer px-0 pb-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Budget</button>
              </div>
            </form>
          </div>
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
  name: 'BudgetsView',
  data() {
    return {
      budgets: [],
      budgetProgress: [],
      categories: [],
      editingBudget: null,
      form: {
        name: '',
        category_id: null,
        amount: 0,
        period: 'monthly',
        start_date: new Date().toISOString().split('T')[0],
        end_date: '',
        is_active: true
      }
    }
  },
  computed: {
    expenseCategories() {
      return this.categories.filter(c => c.type === 'expense');
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      try {
        const [budgetsRes, progressRes, categoriesRes] = await Promise.all([
          axios.get(API_URL + '/budgets/'),
          axios.get(API_URL+'/budgets/progress'),
          axios.get(API_URL+'/categories')
        ]);
        this.budgets = budgetsRes.data;
        this.budgetProgress = progressRes.data;
        this.categories = categoriesRes.data;
      } catch (err) {
        console.error('Failed to load budgets:', err);
      }
    },
    
    async saveBudget() {
        try {
            
            const payload = {
            name: this.form.name,
            category_id: this.form.category_id,
            amount: this.form.amount,
            period: this.form.period,
            start_date: new Date(this.form.start_date).toISOString(),
            end_date: this.form.end_date ? new Date(this.form.end_date).toISOString() : null,
            is_active: true
            };
            
            if (this.editingBudget) {
            await axios.put(`${API_URL}/budgets/${this.editingBudget.id}`, payload);
            this.$root.showToast('Budget updated', 'success');
            } else {
            await axios.post(`${API_URL}/budgets/`, payload);
            this.$root.showToast('Budget created', 'success');
            }
            this.resetForm();
            document.querySelector('#addBudgetModal .btn-close').click();
            this.loadData();
        } catch (err) {
            console.error('Save error:', err.response?.data);
            this.$root.showToast(err.response?.data?.detail || 'Failed to save budget', 'danger');
        }
        },
    
    editBudget(budget) {
      this.editingBudget = budget;
      this.form = {
        name: budget.name,
        category_id: budget.category_id,
        amount: budget.amount,
        period: budget.period,
        start_date: budget.start_date?.split('T')[0] || new Date().toISOString().split('T')[0],
        end_date: budget.end_date?.split('T')[0] || '',
        is_active: budget.is_active
      };
      const modal = new Modal(document.getElementById('addBudgetModal'));
      modal.show();
    },
    
    async deleteBudget(budget) {
      if (confirm(`Delete budget "${budget.name}"?`)) {
        try {
          await axios.delete(`${API_URL}/budgets/${budget.id}`);
          this.$root.showToast('Budget deleted', 'success');
          this.loadData();
        } catch (err) {
          this.$root.showToast('Failed to delete budget', 'danger');
        }
      }
    },
    
    resetForm() {
      this.editingBudget = null;
      this.form = {
        name: '',
        category_id: null,
        amount: 0,
        period: 'monthly',
        start_date: new Date().toISOString().split('T')[0],
        end_date: '',
        is_active: true
      };
    }
  }
};
</script>