import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import VChart from 'vue-echarts'
import { createPinia } from 'pinia'

// 条件性加载Mock数据系统 - 只在明确启用时使用
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

if (USE_MOCK) {
  // 只在明确配置使用Mock时才加载
  import('./mock/index.js').then(({ initMockData }) => {
    initMockData()
    console.log('🔧 Mock数据模式已启用')
  })
  import('./mock/devTools.js') // 加载开发工具
} else {
  console.log('🌐 真实API模式已启用，连接后端服务器')
}

const app = createApp(App)
const pinia = createPinia()

app.component('v-chart', VChart)
app.use(router)
app.use(Antd)
app.use(pinia)
app.mount('#app')
