<template>
  <ul class="nav nav-tabs mb-4">
    <li class="nav-item">
      <button 
        class="nav-link" 
        :class="{ active: modelValue === 'expense' }" 
        @click="$emit('update:modelValue', 'expense')">
         Expenses
      </button>
    </li>
    <li class="nav-item">
      <button 
        class="nav-link" 
        :class="{ active: modelValue === 'income' }" 
        @click="$emit('update:modelValue', 'income')">
         Income
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  name: 'CategoryTabs',
  props: {
    modelValue: {
      type: String,
      default: 'expense'
    }
  },
  emits: ['update:modelValue']
}
</script>