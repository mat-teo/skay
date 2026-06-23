<template>
  <div class="card border-0 shadow-sm h-100 hover-card" :class="{'opacity-75 bg-light': goal.is_archived}">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div class="d-flex align-items-center gap-2">
          <span class="fs-3">{{ goal.icon || '🎯' }}</span>
          <h5 class="card-title mb-0 fw-bold text-truncate" style="max-width: 180px;">{{ goal.name }}</h5>
        </div>
        
        <!-- Native Vue Dropdown Container -->
        <div class="dropdown position-relative" ref="dropdownContainer">
          <button 
            class="btn btn-sm btn-link text-muted p-0 border-0 shadow-none" 
            type="button"
            @click.stop="toggleDropdown"
          >
            <i class="bi bi-three-dots-vertical fs-5"></i>
          </button>
          
          <!-- Explicit visibility conditional binding driven by internal state logic -->
          <ul 
            class="dropdown-menu dropdown-menu-end shadow border-0 end-0 position-absolute" 
            :class="{ show: showDropdown }"
            style="top: 100%; right: 0; z-index: 1050; min-width: 160px;"
          >
            <li>
              <a class="dropdown-item" href="#" @click.prevent="triggerAction('edit', goal)">
                ✏️ Edit Details
              </a>
            </li>
            <li v-if="!goal.is_archived">
              <a class="dropdown-item text-success" href="#" @click.prevent="triggerAction('archive', goal.id)">
                🏆 Mark as Achieved
              </a>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item text-danger" href="#" @click.prevent="triggerAction('delete', goal.id)">
                🗑️ Delete Goal
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Progress Bar Section -->
      <div class="mt-3">
        <div class="d-flex justify-content-between mb-1">
          <span class="small text-muted">Progress</span>
          <span class="small fw-bold">{{ progressPercent }}%</span>
        </div>
        <div class="progress" style="height: 8px; background-color: #e9ecef;">
          <div
            class="progress-bar"
            :style="{
              width: progressPercent + '%',
              backgroundColor: goal.is_archived ? '#6c757d' : (goal.color || '#4f46e5')
            }"
            role="progressbar"
          ></div>
        </div>
      </div>

      <!-- Financial Metrics Real Estate -->
      <div class="d-flex justify-content-between mt-3">
        <div>
          <div class="small text-muted">Saved</div>
          <div class="fw-bold" :class="goal.is_archived ? 'text-secondary' : 'text-success'">
            € {{ goal.current_amount.toFixed(2) }}
          </div>
        </div>
        <div class="text-end">
          <div class="small text-muted">Target</div>
          <div class="fw-bold">€ {{ goal.target_amount.toFixed(2) }}</div>
        </div>
      </div>

      <!-- Projections Metadata Details -->
      <div class="mt-3 pt-3 border-top">
        <div class="d-flex justify-content-between align-items-center">
          <span class="small text-muted">
            <i class="bi bi-calendar3 me-1"></i>
            {{ goal.is_archived ? 'Completed' : `${daysRemaining} days left` }}
          </span>
          <span class="small text-muted">
            <i class="bi bi-tag me-1"></i>
            {{ goal.tracking_mode === 'category' ? 'Category' : 'Account' }}
          </span>
        </div>
        <div v-if="goal.monthly_savings_needed > 0 && !goal.is_archived" class="mt-1">
          <span class="small text-warning">
            <i class="bi bi-clock me-1"></i>
            € {{ goal.monthly_savings_needed.toFixed(2) }}/month needed
          </span>
        </div>
      </div>

      <!-- Operational Status Badge -->
      <div class="mt-2 d-flex justify-content-between align-items-center">
        <span class="badge" :class="goal.is_archived || progressPercent >= 100 ? 'bg-success' : 'bg-primary-subtle text-primary'">
          {{ goal.is_archived ? '🏆 Achieved & Frozen' : (progressPercent >= 100 ? '✅ Target Met' : '🔄 Active tracking') }}
        </span>
        <span v-if="goal.allocation_percentage && !goal.is_archived" class="small text-muted fw-semibold">
          Using {{ goal.allocation_percentage }}%
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GoalCard',
  props: {
    goal: { type: Object, required: true }
  },
  emits: ['edit', 'delete', 'archive'],
  data() {
    return {
      showDropdown: false // Tracks context dropdown open state natively within the component node instances
    };
  },
  computed: {
    progressPercent() {
      if (!this.goal.target_amount || this.goal.target_amount <= 0) return 0;
      return this.goal.progress_percent !== undefined 
        ? this.goal.progress_percent 
        : Math.min(100, Math.max(0, Math.round((this.goal.current_amount / this.goal.target_amount) * 100)));
    },
    daysRemaining() {
      if (!this.goal.target_date || this.goal.is_archived) return 0;
      const now = new Date();
      now.setHours(0, 0, 0, 0);
      const target = new Date(this.goal.target_date);
      target.setHours(0, 0, 0, 0);
      const diff = Math.ceil((target - now) / (1000 * 60 * 60 * 24));
      return Math.max(diff, 0);
    }
  },
  mounted() {
    // Add event listener to capture window clicks for automatic close actions
    document.addEventListener('click', this.handleOutsideClick);
  },
  beforeUnmount() {
    // Teardown scope listener dependencies to clean memory profiles properly
    document.removeEventListener('click', this.handleOutsideClick);
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    handleOutsideClick(event) {
      // Check if reference bounds exist and close the local dropdown when clicking completely outside this container context
      if (this.$refs.dropdownContainer && !this.$refs.dropdownContainer.contains(event.target)) {
        this.showDropdown = false;
      }
    },
    triggerAction(eventEmitName, dataPayload) {
      // Fast-close menu profile context visually before executing async mutations or upstream component updates
      this.showDropdown = false;
      this.$emit(eventEmitName, dataPayload);
    }
  }
};
</script>

<style scoped>
.hover-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
}

/* Explicit CSS Override implementation rules because dropdown-menus defaults hide when lacking native bootstrap classes orchestration */
.dropdown-menu {
  display: none;
}
.dropdown-menu.show {
  display: block !important;
}
</style>