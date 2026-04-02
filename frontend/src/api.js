import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

// Inject role header dynamically
api.interceptors.request.use(config => {
  const role = localStorage.getItem('userRole') || 'guest'
  config.headers['X-User-Role'] = role
  return config
})

export default {
  // Records
  getRecords(params) {
    return api.get('/api/records', { params })
  },
  createRecord(data) {
    return api.post('/api/records', data)
  },

  // Dashboard
  getDashboard(week) {
    return api.get(week ? `/api/dashboard/${week}` : '/api/dashboard')
  },
  archiveWeek(week) {
    return api.post('/api/dashboard/archive', { week })
  },
  resetDashboard(week) {
    return api.put('/api/dashboard/reset', { week })
  },

  // History
  getHistory(params) {
    return api.get('/api/history', { params })
  }
}
