import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import VChart from 'vue-echarts'
import { createPinia } from 'pinia'

// 初始化Mock数据系统
import { initMockData } from './mock/index'
import './mock/devTools' // 加载开发工具

const app = createApp(App)
const pinia = createPinia()

// 初始化Mock数据
initMockData()

app.component('v-chart', VChart)
app.use(router)
app.use(Antd)
app.use(pinia)
app.mount('#app')
