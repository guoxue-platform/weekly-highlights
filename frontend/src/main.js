import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'

// Views
import DashboardView from './views/DashboardView.vue'
import RecordsView from './views/RecordsView.vue'
import NewRecordView from './views/NewRecordView.vue'
import HistoryView from './views/HistoryView.vue'
import AdminView from './views/AdminView.vue'

const routes = [
  { path: '/', component: DashboardView },
  { path: '/records', component: RecordsView },
  { path: '/records/new', component: NewRecordView },
  { path: '/history', component: HistoryView },
  { path: '/admin', component: AdminView },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

createApp(App).use(router).mount('#app')
