<template>
  <div class="flex" :class="message.sender === 'user' ? 'justify-end' : 'justify-start'">
    <div class="flex items-start gap-3 max-w-2xl">
      <!-- Avatar for AI -->
      <div v-if="message.sender === 'agent'" class="w-8 h-8 rounded-full bg-secondary flex-shrink-0 flex items-center justify-center mt-1">
        <svg class="w-5 h-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 9.75a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375m-13.5 3.01c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.184-4.183a1.14 1.14 0 01.778-.332 48.294 48.294 0 005.83-.498c1.585-.233 2.708-1.626 2.708-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
        </svg>
      </div>

      <!-- Message Bubble -->
      <div 
        class="p-4 rounded-xl bg-background-alt border border-border text-text-primary"
      >
        <!-- Message Text -->
        <div class="prose prose-sm max-w-none prose-p:my-2 first:prose-p:mt-0 last:prose-p:mb-0" v-html="formattedMessage"></div>

        <!-- RAG/MCP Data Sections -->
        <div v-if="hasSpecialContent" class="mt-4 pt-4 border-t border-border/50 space-y-4">
            <!-- Calculator Data -->
            <div v-if="hasCalculatorData" class="data-section">
                <h4 class="section-title">📊 精确数据分析</h4>
                <div class="grid grid-cols-2 gap-2 mt-2">
                    <div v-for="(value, key) in mcpData.calculatorData" :key="key" class="bg-secondary/50 p-2 rounded-lg">
                        <div class="text-xs text-text-secondary">{{ getMetricLabel(key) }}</div>
                        <div class="text-base font-semibold text-text-primary">{{ formatMetricValue(value) }}</div>
                    </div>
                </div>
            </div>

            <!-- Chart Data -->
            <div v-if="hasChartUrls" class="data-section">
                <h4 class="section-title">📈 数据可视化</h4>
                <div class="mt-2 space-y-2">
                    <iframe v-for="(chartUrl, index) in mcpData.chartUrls" :key="index" :src="chartUrl" class="w-full h-64 border-none rounded-lg bg-white" frameborder="0"></iframe>
                </div>
            </div>

            <!-- Research Evidence -->
            <div v-if="hasResearchEvidence" class="data-section">
                <h4 class="section-title">🔬 科学依据</h4>
                <div class="mt-2 space-y-3">
                    <div v-for="(evidence, index) in mcpData.researchEvidence" :key="index" class="bg-secondary/50 p-3 rounded-lg">
                        <p class="font-semibold text-text-primary text-sm">{{ evidence.title }}</p>
                        <p class="text-text-secondary text-xs mt-1">{{ evidence.summary }}</p>
                        <a :href="evidence.url" target="_blank" rel="noopener noreferrer" class="text-primary text-xs font-medium mt-2 inline-block hover:underline">
                            查看原文
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Replies -->
        <div v-if="message.quickReplies && message.quickReplies.length > 0" class="mt-4 flex flex-wrap gap-2">
          <button 
            v-for="(reply, index) in message.quickReplies" 
            :key="index"
            @click="handleQuickReply(reply)"
            class="px-3 py-1.5 text-sm font-medium text-primary bg-secondary rounded-full hover:bg-primary/20 transition-colors"
          >
            {{ reply.text }}
          </button>
        </div>
      </div>

      <!-- Avatar for User -->
       <div v-if="message.sender === 'user'" class="w-8 h-8 rounded-full bg-secondary flex-shrink-0 flex items-center justify-center mt-1">
         <UserOutlined class="w-5 h-5 text-primary" />
       </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { UserOutlined } from '@ant-design/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  enableMcpFeatures: {
    type: Boolean,
    default: true
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  loadingType: {
    type: String,
    default: 'mcp'
  },
  loadingText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['quick-reply'])

// Configure `marked` with `highlight.js`
marked.setOptions({
  highlight: function (code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  },
  gfm: true,
  breaks: true,
})

const formattedMessage = computed(() => {
  if (!props.message.content) return ''
  const rawHtml = marked.parse(props.message.content)
  const sanitizedHtml = DOMPurify.sanitize(rawHtml, { ADD_ATTR: ['class'] })
  return sanitizedHtml
})

const mcpData = computed(() => props.message.mcpData || {})

const hasCalculatorData = computed(() => 
  mcpData.value.calculatorData && Object.keys(mcpData.value.calculatorData).length > 0
)

const hasChartUrls = computed(() => 
  mcpData.value.chartUrls && mcpData.value.chartUrls.length > 0
)

const hasResearchEvidence = computed(() => 
  mcpData.value.researchEvidence && mcpData.value.researchEvidence.length > 0
)

const formatMetricValue = (value) => {
  if (typeof value === 'number') {
    return value.toFixed(1)
  }
  return value
}

const getMetricLabel = (key) => {
  const labels = {
    bmi: 'BMI',
    bmr: '基础代谢率 (BMR)',
    calories_burnt: '卡路里消耗'
  }
  return labels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const handleQuickReply = (reply) => {
  emit('quick-reply', reply)
}

const hasSpecialContent = computed(() => hasCalculatorData.value || hasChartUrls.value || hasResearchEvidence.value)
</script>

<style>
/* Scoped styles for markdown content to avoid global conflicts */
.prose {
  color: inherit;
}

.prose pre {
  background-color: #282c34;
  color: #abb2bf;
  padding: 1em;
  border-radius: 8px;
  overflow-x: auto;
}

.prose code {
  font-family: 'Fira Code', 'Courier New', monospace;
}
</style>
