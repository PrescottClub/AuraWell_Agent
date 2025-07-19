import './assets/css/main.css' // 全局样式
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
// 移除全量导入，改用按需导入
// import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
// 导入ECharts配置（按需导入）
import './plugins/echarts.js'
import VChart from 'vue-echarts'
import { createPinia } from 'pinia'
import motionPlugin from './plugins/motion.js' // 动效插件
import i18n from './plugins/i18n.js'; // 国际化插件
import performancePlugin from './plugins/performance.js' // 性能监控插件
import * as Sentry from "@sentry/vue";
import { onCLS, onINP, onLCP } from 'web-vitals';

// 初始化Mock数据系统
import { initMockData } from './mock/index'
import './mock/devTools' // 加载开发工具

const app = createApp(App)

Sentry.init({
  app,
  dsn: "https://examplePublicKey@o0.ingest.sentry.io/0", // 请替换为您的真实 DSN
  integrations: [
    Sentry.browserTracingIntegration({ router }),
    Sentry.replayIntegration({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],
  // 性能监控
  tracesSampleRate: 1.0, 
  // Session Replay
  replaysSessionSampleRate: 0.1, 
  replaysOnErrorSampleRate: 1.0,
});

const pinia = createPinia()

// 初始化Mock数据
initMockData()

app.component('v-chart', VChart)
app.use(motionPlugin) // 注册动效插件
app.use(i18n) // 注册 i18n 插件
app.use(performancePlugin) // 注册性能监控插件
app.use(router)
// app.use(Antd) // 改用按需导入，不需要全局注册
app.use(pinia)

app.mount('#app')

// Web Vitals 应该在 Sentry 初始化后调用
onCLS(Sentry.captureFeedback);
onINP(Sentry.captureFeedback);
onLCP(Sentry.captureFeedback);
