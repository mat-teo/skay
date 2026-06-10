<template>
  <div class="categories-view">
    <header class="page-header d-flex justify-content-between align-items-center mb-4 pb-2">
      <div>
        <h1 class="page-title mt-1 mb-0">Categories</h1>
      </div>
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCategoryModal" @click="resetCategoryForm">
        + New Category
      </button>
    </header>

    <CategoryTabs v-model="activeTab" />

    <CategoryTable 
      :categories="filteredCategories"
      :type="activeTab"
      :transactions="transactions"
      @edit="openEditModal"
      @delete="openDeleteModal"
    />

    <AddCategoryModal 
      :defaultType="activeTab"
      @category-added="onCategoryAdded"
    />

    <EditCategoryModal 
      :category="selectedCategory"
      @category-updated="onCategoryUpdated"
    />

    <DeleteCategoryModal 
      :category="categoryToDelete"
      :transactionCount="getTransactionCount(categoryToDelete?.id)"
      @category-deleted="onCategoryDeleted"
    />
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';
import CategoryTabs from './CategoryTabs.vue';
import CategoryTable from './CategoryTable.vue';
import AddCategoryModal from './AddCategoryModal.vue';
import EditCategoryModal from './EditCategoryModal.vue';
import DeleteCategoryModal from './DeleteCategoryModal.vue';
import { API_URL } from '../../config.js';

export default {
  name: 'CategoriesView',
  components: {
    CategoryTabs,
    CategoryTable,
    AddCategoryModal,
    EditCategoryModal,
    DeleteCategoryModal
  },
  data() {
    return {
      activeTab: 'expense',
      categories: [],
      transactions: [],
      selectedCategory: null,
      categoryToDelete: null
    }
  },
  computed: {
    filteredCategories() {
      return this.categories.filter(c => c.type === this.activeTab);
    }
  },
  mounted() {
    this.loadCategories();
    this.loadTransactions();
  },
  methods: {
    async loadCategories() {
      try {
        const response = await axios.get(API_URL +  '/api/categories');
        this.categories = response.data;
      } catch (err) {
        console.error('Failed to load categories:', err);
        this.$root.showToast('Failed to load categories', 'danger');
      }
    },
    
    async loadTransactions() {
      try {
        const response = await axios.get(API_URL + '/api/transactions');
        this.transactions = response.data;
      } catch (err) {
        console.error('Failed to load transactions:', err);
      }
    },
    
    getTransactionCount(categoryId) {
      if (!categoryId) return 0;
      return this.transactions.filter(t => t.category_id === categoryId).length;
    },
    
    resetAddModal() {
      // Reset will be handled by the modal itself
    },
    
    onCategoryAdded(newCategory) {
      this.categories.push(newCategory);
      this.$root.showToast('Category created successfully', 'success');
    },
    
    openEditModal(category) {
      this.selectedCategory = category;
      const modalElement = document.getElementById('editCategoryModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    },
    
    onCategoryUpdated(updatedCategory) {
      const index = this.categories.findIndex(c => c.id === updatedCategory.id);
      if (index !== -1) {
        this.categories[index] = updatedCategory;
      }
      this.$root.showToast('Category updated successfully', 'success');
      this.selectedCategory = null;
    },
    
    openDeleteModal(category) {
        const transactionCount = this.getTransactionCount(category.id);
  
        if (transactionCount > 0) {
            // Show toast warning instead of opening modal
            this.$root.showToast(
            `Cannot delete "${category.name}" because it has ${transactionCount} transaction(s).`, 
            'warning'
            );
            return;
        }
        
        this.categoryToDelete = category;
        const modalElement = document.getElementById('deleteCategoryModal');
        if (modalElement) {
            const modal = new Modal(modalElement);
            modal.show();
        }
    },
    
    onCategoryDeleted(deletedId) {
      this.categories = this.categories.filter(c => c.id !== deletedId);
      this.$root.showToast('Category deleted successfully', 'success');
      this.categoryToDelete = null;
    }
  }
}
</script>

<style scoped>
.categories-view {
  padding-bottom: 40px;
}
</style>