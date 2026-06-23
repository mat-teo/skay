<template>
  <div class="goals-view py-4 container">
    <header class="page-header d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="page-title fw-bold">🎯 Financial Portfolio Goals</h1>
        <p class="text-muted mb-0">Track and lock your asset allocations and net saving targets</p>
      </div>
      <button class="btn btn-primary px-4 fw-semibold shadow-sm" @click="openCreateModal">
        <i class="bi bi-plus-lg me-1"></i> Create Goal
      </button>
    </header>

    <!-- Operational Top-line Aggregate Balance Metrics -->
    <div class="row g-4 mb-4" v-if="summary.total_target > 0">
      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm bg-white p-2">
          <div class="card-body">
            <h6 class="text-muted small text-uppercase fw-bold mb-1">Active Targets Count</h6>
            <h3 class="fw-bold mb-0 text-dark">{{ summary.active_goals }} Tracker Entities</h3>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm bg-white p-2">
          <div class="card-body">
            <h6 class="text-muted small text-uppercase fw-bold mb-1">Total Monitored Reserves</h6>
            <h3 class="fw-bold mb-0 text-success">€ {{ summary.total_current.toFixed(2) }}</h3>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm bg-white p-2">
          <div class="card-body">
            <h6 class="text-muted small text-uppercase fw-bold mb-1">Dynamic Engine Aggregation</h6>
            <h3 class="fw-bold mb-0 text-primary">{{ summary.total_progress.toFixed(1) }}%</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Elements Section Context View -->
    <h4 class="fw-bold text-dark mb-3">🔄 Active Tracking Metrics</h4>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="activeGoals.length === 0" class="text-center py-4 bg-white rounded shadow-sm text-muted mb-4">
      <i class="bi bi-patch-check fs-2 text-secondary d-block mb-2"></i>
      No active goals currently running. Create one or look into the achievements section below!
    </div>

    <div v-else class="row g-4 mb-5">
      <div v-for="goal in activeGoals" :key="goal.id" class="col-12 col-md-6 col-lg-4">
        <GoalCard :goal="goal" @edit="openEditModal" @delete="confirmDelete" @archive="archiveGoal" />
      </div>
    </div>

    <!-- Achieved / Completed Frozen Entities Grid Section -->
    <div v-if="archivedGoals.length > 0" class="mt-5 border-top pt-4">
      <h4 class="fw-bold text-success mb-3">🏆 Completed & Achieved Historical Milestones</h4>
      <div class="row g-4">
        <div v-for="goal in archivedGoals" :key="goal.id" class="col-12 col-md-6 col-lg-4">
          <GoalCard :goal="goal" @edit="openEditModal" @delete="confirmDelete" />
        </div>
      </div>
    </div>

    <!-- Centralized Input Modal Structure Link -->
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
      // Split the global pool dynamically into unarchived rows
      return this.goals.filter(g => !g.is_archived);
    },
    archivedGoals() {
      // Split the global pool dynamically into archived rows
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
        console.error('Failed to load goal pipelines:', err);
        this.$root.showToast('Data aggregation stream runtime crash', 'danger');
        this.goals = []
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
        this.$root.showToast('Goal baseline frozen and moved to achievements pool!', 'success');
        this.loadGoals();
      } catch (err) {
        this.$root.showToast('Failed to switch state profile for target entity', 'danger');
      }
    },
    async confirmDelete(id) {
      const confirmed = await confirm('Purge goal? Operational structures and limits will be dropped.');
      if (!confirmed) return;

      try {
        await GoalService.deleteGoal(id);
        this.$root.showToast('Target configuration dropped', 'success');
        this.loadGoals();
      } catch (err) {
        this.$root.showToast('Failed execution parameters on target entity deletion', 'danger');
      }
    }
  }
};
</script>