<template>
  <div class="app">
    <nav class="navbar">
      <div class="nav-brand">🏆 高光积分系统</div>
      <div class="nav-links">
        <router-link to="/">看板</router-link>
        <router-link to="/records">记录查询</router-link>
        <router-link to="/history">历史归档</router-link>
        <router-link to="/admin" v-if="isMain">管理</router-link>
      </div>
      <div class="nav-role">
        <label>角色：</label>
        <select v-model="currentRole" @change="changeRole">
          <option value="guest">guest（访客）</option>
          <option value="fin">fin</option>
          <option value="main">main</option>
        </select>
      </div>
    </nav>
    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const currentRole = ref(localStorage.getItem('userRole') || 'guest')
const isMain = computed(() => currentRole.value === 'main')

function changeRole() {
  localStorage.setItem('userRole', currentRole.value)
  location.reload()
}

onMounted(() => {
  // Sync from localStorage
  currentRole.value = localStorage.getItem('userRole') || 'guest'
})
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }

.navbar {
  background: #2c3e50;
  color: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 30px;
  height: 56px;
}
.nav-brand { font-weight: bold; font-size: 18px; }
.nav-links { display: flex; gap: 20px; flex: 1; }
.nav-links a { color: #ecf0f1; text-decoration: none; padding: 8px 0; border-bottom: 2px solid transparent; }
.nav-links a.router-link-active { border-bottom-color: #3498db; }
.nav-role { display: flex; align-items: center; gap: 8px; }
.nav-role select { padding: 4px 8px; border-radius: 4px; border: none; }

.content { padding: 20px; max-width: 1200px; margin: 0 auto; }

.card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.card h2 { margin-bottom: 16px; font-size: 18px; color: #2c3e50; }

.stats { display: flex; gap: 20px; margin-bottom: 20px; }
.stat-box { background: white; border-radius: 8px; padding: 20px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.stat-box .num { font-size: 32px; font-weight: bold; color: #3498db; }
.stat-box .label { color: #7f8c8d; margin-top: 4px; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
th { background: #f8f9fa; font-weight: 600; color: #2c3e50; }
tr:hover { background: #f8f9fa; }

.filters { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }
.filters label { display: flex; align-items: center; gap: 4px; font-size: 14px; }
.filters select, .filters input { padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px; }
.filters button { padding: 6px 16px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
.filters button:hover { background: #2980b9; }

.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group label { font-size: 14px; font-weight: 500; color: #2c3e50; }
.form-group input, .form-group select, .form-group textarea { padding: 8px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.form-group textarea { resize: vertical; min-height: 80px; }
.form-actions { margin-top: 20px; display: flex; gap: 12px; }
.btn-primary { padding: 10px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-primary:hover { background: #2980b9; }
.btn-danger { padding: 10px 24px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-secondary { padding: 10px 24px; background: #95a5a6; color: white; border: none; border-radius: 4px; cursor: pointer; }
.loading { text-align: center; padding: 40px; color: #7f8c8d; }
.error { color: #e74c3c; padding: 10px; background: #fdf2f2; border-radius: 4px; margin-bottom: 16px; }
.success { color: #27ae60; padding: 10px; background: #f0fdf4; border-radius: 4px; margin-bottom: 16px; }

.week-nav { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.week-nav h2 { flex: 1; }

.admin-actions { display: flex; gap: 16px; flex-wrap: wrap; }
</style>
