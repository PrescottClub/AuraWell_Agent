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
        class="p-4 rounded-xl"
        :class="{
          'bg-primary text-white': message.sender === 'user',
          'bg-background-alt border border-border text-text-primary': message.sender === 'agent'
        }"
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

        <!-- Feedback Buttons (only for AI messages) -->
        <div v-if="message.sender === 'agent'" class="mt-3 flex items-center gap-2 pt-2 border-t border-border/30">
          <span class="text-xs text-text-secondary">这个回答对您有帮助吗？</span>
          <div class="flex gap-1">
            <button
              @click="submitFeedback('like')"
              :class="[
                'p-1.5 rounded-full transition-all duration-200',
                userFeedback === 'like'
                  ? 'bg-green-100 text-green-600 hover:bg-green-200'
                  : 'text-text-secondary hover:bg-secondary hover:text-green-600'
              ]"
              :title="userFeedback === 'like' ? '已点赞' : '点赞'"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
              </svg>
            </button>
            <button
              @click="submitFeedback('dislike')"
              :class="[
                'p-1.5 rounded-full transition-all duration-200',
                userFeedback === 'dislike'
                  ? 'bg-red-100 text-red-600 hover:bg-red-200'
                  : 'text-text-secondary hover:bg-secondary hover:text-red-600'
              ]"
              :title="userFeedback === 'dislike' ? '已点踩' : '点踩'"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.106-1.79l-.05-.025A4 4 0 0011.057 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
              </svg>
            </button>
          </div>
          <!-- Feedback submitted indicator -->
          <span v-if="feedbackSubmitted" class="text-xs text-green-600 ml-2">
            ✓ 感谢您的反馈
          </span>
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
       <div v-if="message.sender === 'user'" class="w-8 h-8 rounded-full bg-blue-200 flex-shrink-0 flex items-center justify-center mt-1">
         <UserOutlined class="w-5 h-5 text-blue-600" />
       </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
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

const emit = defineEmits(['quick-reply', 'feedback'])

// Feedback state
const userFeedback = ref(null) // 'like' | 'dislike' | null
const feedbackSubmitted = ref(false)

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

// Feedback handling
const submitFeedback = async (type) => {
  if (feedbackSubmitted.value) return

  userFeedback.value = type
  feedbackSubmitted.value = true

  // Emit feedback event to parent component
  emit('feedback', {
    messageId: props.message.id,
    sessionId: props.message.sessionId,
    feedbackType: type,
    rating: type === 'like' ? 5 : 1, // Convert to 1-5 scale
    timestamp: new Date().toISOString()
  })

  // Auto-hide feedback confirmation after 3 seconds
  setTimeout(() => {
    feedbackSubmitted.value = false
  }, 3000)
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
