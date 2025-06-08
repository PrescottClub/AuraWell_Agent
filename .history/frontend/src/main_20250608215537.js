import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import VChart from 'vue-echarts'
import { createPinia } from 'pinia'

const app = createApp(App)
const pinia = createPinia()

app.component('v-chart', VChart)
app.use(router)
app.use(Antd)
app.use(pinia)
app.mount('#app')
