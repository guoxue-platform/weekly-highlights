<template>
  <div>
    <div class="card">
      <h2>🔍 原始记录查询</h2>
      <div class="filters">
        <label>Agent: <select v-model="filters.agent"><option value="">全部</option><option v-for="a in agents" :key="a">{{ a }}</option></select></label>
        <label>Week: <select v-model="filters.week"><option value="">全部</option><option v-for="w in weeks" :key="w">{{ w }}</option></select></label>
        <label>从: <input type="date" v-model="filters.date_from"></label>
        <label>到: <input type="date" v-model="filters.date_to"></label>
        <button @click="search">查询</button>
        <button @click="reset" style="background:#95a5a6">重置</button>
        <router-link to="/records/new" class="btn-primary" style="text-decoration:none;padding:6px 16px;" v-if="canCreate">+ 新增记录</router-link>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <table v-else>
        <thead><tr><th>Agent</th><th>积分</th><th>原因</th><th>类别</th><th>记录人</th><th>日期</th><th>周</th></tr></thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td>{{ r.agent }}</td><td>{{ r.score }}</td><td>{{ r.reason }}</td><td>{{ r.category }}</td><td>{{ r.recorder }}</td><td>{{ r.date }}</td><td>{{ r.week }}</td>
          </tr>
          <tr v-if="records.length === 0"><td colspan="7" style="text-align:center;color:#999">暂无记录</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api.js'

const liveWeek = '2026-W14'
const currentRole = ref(localStorage.getItem('userRole') || 'guest')
const canCreate = computed(() => ['fin', 'main'].includes(currentRole.value))

const filters = ref({ agent: '', week: '', date_from: '', date_to: '' })
const records = ref([])
const agents = ref(['agent-alpha', 'agent-beta', 'agent-gamma'])
const weeks = ref([liveWeek])
const loading = ref(false)
const error = ref('')

async function search() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.agent) params.agent = filters.value.agent
    if (filters.value.week) params.week = filters.value.week
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    const res = await api.getRecords(params)
    records.value = res.data.records || res.data || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function reset() {
  filters.value = { agent: '', week: '', date_from: '', date_to: '' }
  search()
}

onMounted(search)
</script>
