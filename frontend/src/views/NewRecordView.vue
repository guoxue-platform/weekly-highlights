<template>
  <div>
    <div class="card">
      <h2>➕ 新增积分记录</h2>

      <div v-if="!canCreate" class="error">⚠️ 您没有权限新增记录（需要 fin 或 main 角色）</div>

      <div v-if="msg" :class="msgType === 'error' ? 'error' : 'success'" style="margin-bottom:16px">{{ msg }}</div>

      <form @submit.prevent="submit" v-if="canCreate">
        <div class="form-grid">
          <div class="form-group">
            <label>Agent *</label>
            <input v-model="form.agent" required placeholder="输入 agent 名称">
          </div>
          <div class="form-group">
            <label>积分 *</label>
            <input v-model.number="form.score" type="number" required placeholder="积分分值">
          </div>
          <div class="form-group">
            <label>类别 *</label>
            <select v-model="form.category" required>
              <option value="">请选择</option>
              <option>项目贡献</option>
              <option>日常任务</option>
              <option>临时任务</option>
              <option>其他</option>
            </select>
          </div>
          <div class="form-group">
            <label>记录人 *</label>
            <input v-model="form.recorder" required placeholder="记录人">
          </div>
          <div class="form-group">
            <label>日期 *</label>
            <input v-model="form.date" type="date" required>
          </div>
          <div class="form-group">
            <label>Summary</label>
            <input v-model="form.summary" placeholder="简要概述">
          </div>
        </div>
        <div class="form-group" style="margin-top:16px">
          <label>原因 *</label>
          <textarea v-model="form.reason" required placeholder="详细说明加分原因"></textarea>
        </div>
        <div class="form-group" style="margin-top:16px">
          <label>备注 Remark</label>
          <textarea v-model="form.remark" placeholder="其他备注信息（可选）"></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="submitting">{{ submitting ? '提交中...' : '提交' }}</button>
          <router-link to="/records" class="btn-secondary" style="text-decoration:none;padding:10px 24px;display:inline-block;color:white;background:#95a5a6;border-radius:4px;">取消</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'

const router = useRouter()
const liveWeek = '2026-W14'
const currentRole = ref(localStorage.getItem('userRole') || 'guest')
const canCreate = computed(() => ['fin', 'main'].includes(currentRole.value))

const form = ref({
  agent: '',
  score: null,
  category: '',
  recorder: '',
  date: new Date().toISOString().split('T')[0],
  reason: '',
  summary: '',
  remark: ''
})
const msg = ref('')
const msgType = ref('success')
const submitting = ref(false)

async function submit() {
  submitting.value = true
  msg.value = ''
  try {
    await api.createRecord(form.value)
    msg.value = '✅ 记录创建成功！'
    msgType.value = 'success'
    setTimeout(() => router.push('/records'), 1500)
  } catch (e) {
    msg.value = '❌ 提交失败: ' + (e.response?.data?.error || e.message)
    msgType.value = 'error'
  } finally {
    submitting.value = false
  }
}
</script>
