<template>
  <div>
    <div class="card">
      <h2>⚙️ 管理操作</h2>

      <div v-if="!isMain" class="error">⚠️ 您没有权限访问管理页面（需要 main 角色）</div>

      <div v-if="msg" :class="msgType === 'error' ? 'error' : 'success'" style="margin-bottom:16px">{{ msg }}</div>

      <div v-if="isMain" class="admin-actions">
        <div>
          <h3 style="margin-bottom:8px">📦 周结归档</h3>
          <p style="color:#7f8c8d;margin-bottom:12px;font-size:14px">将指定周的数据归档到历史记录</p>
          <div style="display:flex;gap:12px;align-items:center">
            <select v-model="archiveWeek">
              <option v-for="w in weeks" :key="w">{{ w }}</option>
            </select>
            <button class="btn-primary" @click="doArchive" :disabled="actionLoading">归档本周</button>
          </div>
        </div>

        <div style="border-left:1px solid #ecf0f1;padding-left:30px">
          <h3 style="margin-bottom:8px">🔄 重置看板</h3>
          <p style="color:#7f8c8d;margin-bottom:12px;font-size:14px">清空当前周的看板数据（谨慎操作）</p>
          <div style="display:flex;gap:12px;align-items:center">
            <select v-model="resetWeek">
              <option v-for="w in weeks" :key="w">{{ w }}</option>
            </select>
            <button class="btn-danger" @click="doReset" :disabled="actionLoading">重置看板</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api.js'

const liveWeek = '2026-W14'
const currentRole = ref(localStorage.getItem('userRole') || 'guest')
const isMain = computed(() => currentRole.value === 'main')

const weeks = ref([liveWeek, '2026-W13', '2026-W12', '2026-W11', '2026-W10'])
const archiveWeek = ref(liveWeek)
const resetWeek = ref(liveWeek)
const actionLoading = ref(false)
const msg = ref('')
const msgType = ref('success')

async function doArchive() {
  actionLoading.value = true
  msg.value = ''
  try {
    await api.archiveWeek(archiveWeek.value)
    msg.value = `✅ ${archiveWeek.value} 归档成功！`
    msgType.value = 'success'
  } catch (e) {
    msg.value = '❌ 归档失败: ' + (e.response?.data?.error || e.message)
    msgType.value = 'error'
  } finally {
    actionLoading.value = false
  }
}

async function doReset() {
  if (!confirm(`确定要重置 ${resetWeek.value} 的看板数据吗？此操作不可恢复！`)) return
  actionLoading.value = true
  msg.value = ''
  try {
    await api.resetDashboard(resetWeek.value)
    msg.value = `✅ ${resetWeek.value} 看板已重置！`
    msgType.value = 'success'
  } catch (e) {
    msg.value = '❌ 重置失败: ' + (e.response?.data?.error || e.message)
    msgType.value = 'error'
  } finally {
    actionLoading.value = false
  }
}
</script>
