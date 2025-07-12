<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="logo">
        <h3>AuraWell Admin</h3>
      </div>
      <nav class="menu">
        <router-link to="/admin/dashboard" class="menu-item">
          <span class="icon">📊</span>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/admin/prompt-playground" class="menu-item">
          <span class="icon">🧪</span>
          <span>Prompt Playground</span>
        </router-link>
         <router-link to="/admin/users" class="menu-item">
          <span class="icon">👥</span>
          <span>Users</span>
        </router-link>
      </nav>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
}
.sidebar {
  width: 240px;
  background-color: #001529;
  color: white;
  display: flex;
  flex-direction: column;
}
.logo {
  padding: 16px;
  text-align: center;
  font-size: 20px;
  border-bottom: 1px solid #002140;
}
.menu {
  flex-grow: 1;
  padding-top: 16px;
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  transition: all 0.3s;
}
.menu-item:hover, .router-link-exact-active {
  color: #fff;
  background-color: #1890ff;
}
.menu-item .icon {
  margin-right: 12px;
  font-size: 18px;
}
.content {
  flex-grow: 1;
  padding: 24px;
  background-color: #f0f2f5;
  overflow-y: auto;
}
</style>