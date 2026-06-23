import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../components/Dashboard.vue'
import TransactionsView from '../components/transactions/TransactionsView.vue'
import AdvancedStats from '../components/advanced-stats/AdvancedStats.vue'
import CategoriesView from '../components/categories/CategoriesView.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import { auth } from '../auth'
import BudgetsView from '../components/budgets/BudgetsView.vue'
import ProfileView from '../components/ProfileView.vue'
import StocksView from '../components/stocks/StocksView.vue'
import GoalsView from '../components/goals/GoalsView.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: TransactionsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/stats',
    name: 'AdvancedStats',
    component: AdvancedStats,
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: CategoriesView,
    meta: { requiresAuth: true }
  },
  {
    path:"/budgets",
    name:"Budgets",
    component: BudgetsView,
    meta:{
      requiresAuth: true
    }
  },
  { 
    path: '/profile', 
    name: 'Profile', 
    component: ProfileView,
    meta: { requiresAuth: true } 
  },
   { path: '/stocks', 
    name: 'Stocks', 
    component: StocksView, 
    meta: { requiresAuth: true } 
  },{
    path: "/goals",
    name: "Goals",
    component: GoalsView,
    meta: {
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = auth.isAuthenticated()
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router