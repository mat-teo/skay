<template>
  <div class="goals-view py-4 container">
    <header class="page-header d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="page-title fw-bold">🎯 My Goals</h1>
        <p class="text-muted mb-0">Track your savings and reach your financial targets</p>
      </div>
      <button class="btn btn-primary px-4 fw-semibold shadow-sm" @click="openCreateModal">
        <i class="bi bi-plus-lg me-1"></i> New Goal
      </button>
    </header>

    <!-- Simple Dashboard Overview -->
    <div class="row g-4 mb-4" v-if="summary.total_target > 0">
      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm bg-white p-2">
          <div class="card-body">
            <h6 class="text-muted small text-uppercase fw-bold mb-1">Active Goals</h6>
            <h3 class="fw-bold mb-0 text-dark">{{ summary.active_goals }} in progress</h3>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm bg-white p-2">
          <div class="card-body">
            <h6 class="text-muted small text-uppercase fw-bold mb-1">Total Saved</h6>
            <h3 class="fw-bold mb-0 text-success">€ {{ summary.total_current.toFixed(2) }}</h3>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm bg-white p-2">
          <div class="card-body">
            <h6 class="text-muted small text-uppercase fw-bold mb-1">Total Progress</h6>
            <h3 class="fw-bold mb-0 text-primary">{{ summary.total_progress.toFixed(1) }}%</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Goals Section -->
    <h4 class="fw-bold text-dark mb-3">🔄 In Progress</h4>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="activeGoals.length === 0" class="text-center py-4 bg-white rounded shadow-sm text-muted mb-4">
      <i class="bi bi-patch-check fs-2 text-secondary d-block mb-2"></i>
      No active goals yet. Create a new one or check your achievements below!
    </div>

    <div v-else class="row g-4 mb-5">
      <div v-for="goal in activeGoals" :key="goal.id" class="col-12 col-md-6 col-lg-4">
        <GoalCard :goal="goal" @edit="openEditModal" @delete="confirmDelete" @archive="archiveGoal" />
      </div>
    </div>

    <!-- Achieved / Completed Section -->
    <div v-if="archivedGoals.length > 0" class="mt-5 border-top pt-4">
      <h4 class="fw-bold text-success mb-3">🏆 Goals Achieved!</h4>
      <div class="row g-4">
        <div v-for="goal in archivedGoals" :key="goal.id" class="col-12 col-md-6 col-lg-4">
          <GoalCard :goal="goal" @edit="openEditModal" @delete="confirmDelete" />
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <GoalModal
      ref="goalModal"
      :editing="editingGoal"
      :categories="categories"
      :accounts="accounts"
      @saved="onModalSaved"
      @request-delete="confirmDelete"
    />
  </div>
</template>

<script>
import { GoalService } from './GoalService';
import GoalCard from './GoalCard.vue';
import GoalModal from './GoalModal.vue';
import axios from 'axios';
import { API_URL } from '../../config';

export default {
  name: 'GoalsView',
  components: { GoalCard, GoalModal },
  data() {
    return {
      goals: [],
      categories: [],
      accounts: [],
      loading: false,
      editingGoal: null,
      summary: { active_goals: 0, total_current: 0, total_target: 0, total_progress: 0 }
    };
  },
  computed: {
    activeGoals() {
      return this.goals.filter(g => !g.is_archived);
    },
    archivedGoals() {
      return this.goals.filter(g => g.is_archived);
    }
  },
  mounted() {
    this.loadGoals();
    this.loadCategories();
    this.loadAccounts();
  },
  methods: {
    async loadGoals() {
      this.loading = true;
      try {
        const [goalsRes, summaryRes] = await Promise.all([
          GoalService.getGoalsStatus(),
          GoalService.getGoalsSummary()
        ]);
        this.goals = Array.isArray(goalsRes) ? goalsRes : [];
        this.summary = summaryRes;
      } catch (err) {
        console.error('Failed to load goals:', err);
        this.$root.showToast('Could not load goals. Please try again later.', 'danger');
        this.goals = [];
      } finally {
        this.loading = false;
      }
    },
    async loadCategories() {
      try {
        const response = await axios.get(`${API_URL}/categories`);
        this.categories = response.data;
      } catch (err) { console.error(err); }
    },
    async loadAccounts() {
      try {
        const response = await axios.get(`${API_URL}/accounts`);
        this.accounts = response.data;
      } catch (err) { console.error(err); }
    },
    openCreateModal() {
      this.editingGoal = null;
      this.$refs.goalModal.open();
    },
    openEditModal(goal) {
      this.editingGoal = goal;
      this.$refs.goalModal.open();
    },
    onModalSaved() {
      this.loadGoals();
    },
    async archiveGoal(id) {
      try {
        await GoalService.archiveGoal(id);
        this.$root.showToast('Congratulations! Goal moved to achievements! 🏆', 'success');
        this.loadGoals();
      } catch (err) {
        this.$root.showToast('Could not update goal status.', 'danger');
      }
    },
    async confirmDelete(id) {
      const confirmed = await confirm('Are you sure you want to delete this goal? This action cannot be undone.');
      if (!confirmed) return;

      try {
        await GoalService.deleteGoal(id);
        this.$root.showToast('Goal deleted successfully.', 'success');
        this.loadGoals();
      } catch (err) {
        this.$root.showToast('Could not delete this goal.', 'danger');
      }
    }
  }
};
</script>