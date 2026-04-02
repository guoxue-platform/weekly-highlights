<template>
  <div>
    <div class="week-nav">
      <button class="btn-secondary" @click="prevWeek">◀ 上周</button>
      <h2>📊 {{ currentWeek }} 周看板</h2>
      <button class="btn-secondary" @click="nextWeek">下周 ▶</button>
      <router-link v-if="currentWeek !== liveWeek" to="/" class="btn-primary" style="text-decoration:none;text-align:center;padding:8px 16px;">回到本周</router-link>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <div class="stats">
        <div class="stat-box"><div class="num">{{ stats.total_score }}</div><div class="label">总积分</div></div>
        <div class="stat-box"><div class="num">{{ stats.record_count }}</div><div class="label">记录数</div></div>
        <div class="stat-box"><div class="num">{{ stats.top_agent || '-' }}</div><div class="label">积分最高者</div></div>
      </div>

      <div class="card">
        <h2>📋 本周原始记录</h2>
        <table>
          <thead>
            <tr><th>Agent</th><th>积分</th><th>原因</th><th>类别</th><th>记录人</th><th>日期</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>{{ r.agent }}</td>
              <td>{{ r.score }}</td>
              <td>{{ r.reason }}</td>
              <td>{{ r.category }}</td>
              <td>{{ r.recorder }}</td>
              <td>{{ r.date }}</td>
            </tr>
            <tr v-if="records.length === 0"><td colspan="6" style="text-align:center;color:#999">暂无记录</td></tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api.js'

const liveWeek = '2026-W14'
const currentWeek = ref(liveWeek)
const records = ref([])
const stats = ref({ total_score: 0, record_count: 0, top_agent: '' })
const loading = ref(false)
const error = ref('')

function weekOffset(offset) {
  const [y, w] = liveWeek.split('-').map(Number)
  let targetW = w + offset
  let targetY = y
  if (targetW < 1) { targetW = 52 + targetW; targetY-- }
  if (targetW > 52) { targetW = targetW - 52; targetY++ }
  return `${targetY}-W${String(targetW).padStart(2, '0')}`
}

function prevWeek() { currentWeek.value = weekOffset(-1) }
function nextWeek() { currentWeek.value = weekOffset(1) }

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.getDashboard(currentWeek.value)
    records.value = res.data.records || []
    stats.value = {
      total_score: res.data.total_score || 0,
      record_count: res.data.record_count || records.value.length,
      top_agent: res.data.top_agent || ''
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
