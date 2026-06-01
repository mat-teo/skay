<template>
  <div class="card mb-4">
    <div class="card-body">
      <div class="row g-3 align-items-end">
        <div class="col-md-5">
          <label class="form-label">Start Date</label>
          <input type="date" class="form-control" v-model="localStartDate" @change="emitChange">
        </div>
        <div class="col-md-5">
          <label class="form-label">End Date</label>
          <input type="date" class="form-control" v-model="localEndDate" @change="emitChange">
        </div>
        <div class="col-md-2">
          <button class="btn btn-primary w-100" @click="emitChange">
            Apply
          </button>
        </div>
      </div>
      
      <div class="row mt-3">
        <div class="col-12">
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('week')">Last Week</button>
            <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('month')">Last Month</button>
            <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('quarter')">Last Quarter</button>
            <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('year')">Last Year</button>
            <button type="button" class="btn btn-outline-secondary" @click="setQuickRange('all')">All Time</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DateRangePicker',
  props: {
    startDate: { type: String, default: '' },
    endDate: { type: String, default: '' }
  },
  emits: ['update:startDate', 'update:endDate', 'change'],
  data() {
    return {
      localStartDate: this.startDate,
      localEndDate: this.endDate
    }
  },
  watch: {
    startDate(val) { this.localStartDate = val },
    endDate(val) { this.localEndDate = val }
  },
  methods: {
    emitChange() {
      this.$emit('update:startDate', this.localStartDate)
      this.$emit('update:endDate', this.localEndDate)
      this.$emit('change', {
        start_date: this.localStartDate,
        end_date: this.localEndDate
      })
    },
    
    setQuickRange(range) {
      const end = new Date()
      const start = new Date()
      
      switch(range) {
        case 'week':
          start.setDate(end.getDate() - 7)
          break
        case 'month':
          start.setMonth(end.getMonth() - 1)
          break
        case 'quarter':
          start.setMonth(end.getMonth() - 3)
          break
        case 'year':
          start.setFullYear(end.getFullYear() - 1)
          break
        case 'all':
          this.localStartDate = ''
          this.localEndDate = ''
          this.emitChange()
          return
      }
      
      this.localStartDate = start.toISOString().split('T')[0]
      this.localEndDate = end.toISOString().split('T')[0]
      this.emitChange()
    }
  }
}
</script>