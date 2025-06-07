<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style scoped>

</style>
<script setup>

  import BasicLayout from './layout/BasicLayout.vue';
  import { RouterView, useRoute } from 'vue-router'
  import { computed } from 'vue'
  const route = useRoute()
  const isLoginPage = computed(() => route.path === '/login')
</script>