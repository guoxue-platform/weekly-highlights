<template>
  <div>
    <div class="card">
      <h2>📦 历史归档</h2>
      <div class="filters">
        <label>从: <input type="date" v-model="filters.date_from"></label>
        <label>到: <input type="date" v-model="filters.date_to"></label>
        <button @click="search">查询</button>
        <button @click="reset" style="background:#95a5a6">重置</button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <table v-else>
        <thead><tr><th>周</th><th>总积分</th><th>记录数</th><th>积分最高者</th><th>概述</th><th>归档时间</th></tr></thead>
        <tbody>
          <tr v-for="h in history" :key="h.week">
            <td><router-link :to="`/?week=${h.week}`">{{ h.week }}</router-link></td>
            <td>{{ h.total_score }}</td>
            <td>{{ h.record_count }}</td>
            <td>{{ h.top_agent }}</td>
            <td>{{ h.summary }}</td>
            <td>{{ h.archived_at }}</td>
          </tr>
          <tr v-if="history.length === 0"><td colspan="6" style="text-align:center;color:#999">暂无归档记录</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'

const filters = ref({ date_from: '', date_to: '' })
const history = ref([])
const loading = ref(false)
const error = ref('')

async function search() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    const res = await api.getHistory(params)
    history.value = res.data.history || res.data || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function reset() {
  filters.value = { date_from: '', date_to: '' }
  search()
}

onMounted(search)
</script>
