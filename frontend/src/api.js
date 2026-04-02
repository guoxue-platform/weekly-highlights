import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'https://weekly-highlights.up.railway.app'

const api = axios.create({
  baseURL: API_BASE
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
    return api.get('/api/v1/points/records', { params })
  },
  createRecord(data) {
    return api.post('/api/v1/points/record', data)
  },

  // Dashboard
  getDashboard(week) {
    return api.get('/api/v1/points/weekly')
  },
  archiveWeek(week) {
    return api.post('/api/v1/points/archive', { week })
  },
  resetDashboard(week) {
    return api.post('/api/v1/points/reset', { week })
  },

  // History
  getHistory(params) {
    return api.get('/api/v1/points/history', { params })
  }
}
