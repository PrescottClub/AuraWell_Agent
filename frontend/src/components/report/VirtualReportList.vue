<template>
  <div class="virtual-report-list">
    <!-- 搜索和筛选 -->
    <div class="list-header">
      <div class="search-section">
        <a-input-search
          v-model:value="searchKeyword"
          placeholder="搜索报告标题、类型..."
          style="width: 300px;"
          @search="handleSearch"
          @change="debouncedSearch"
        />
        
        <a-select
          v-model:value="selectedType"
          placeholder="报告类型"
          style="width: 120px; margin-left: 12px;"
          @change="handleTypeFilter"
          allowClear
        >
          <a-select-option value="weekly">周报</a-select-option>
          <a-select-option value="monthly">月报</a-select-option>
          <a-select-option value="quarterly">季报</a-select-option>
        </a-select>
        
        <a-select
          v-model:value="selectedStatus"
          placeholder="状态"
          style="width: 100px; margin-left: 12px;"
          @change="handleStatusFilter"
          allowClear
        >
          <a-select-option value="completed">已完成</a-select-option>
          <a-select-option value="generating">生成中</a-select-option>
          <a-select-option value="failed">失败</a-select-option>
        </a-select>
      </div>
      
      <div class="list-stats">
        <a-tag color="blue">总计: {{ totalCount }}</a-tag>
        <a-tag color="green">显示: {{ visibleCount }}</a-tag>
        <a-tooltip title="列表性能信息">
          <a-button 
            type="text" 
            size="small"
            @click="showStats = !showStats"
          >
            <InfoCircleOutlined />
          </a-button>
        </a-tooltip>
      </div>
    </div>
    
    <!-- 性能统计 -->
    <div v-if="showStats" class="performance-stats">
      <div class="stat-item">
        <span class="stat-label">渲染项目:</span>
        <span class="stat-value">{{ renderStats.renderedItems }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">滚动性能:</span>
        <span class="stat-value">{{ renderStats.scrollPerformance }}ms</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">内存使用:</span>
        <span class="stat-value">{{ renderStats.memoryUsage }}MB</span>
      </div>
    </div>
    
    <!-- 虚拟滚动容器 -->
    <div 
      class="virtual-container"
      ref="containerRef"
      @scroll="handleScroll"
      :style="containerStyle"
    >
      <!-- 总高度占位 -->
      <div 
        class="virtual-content"
        :style="{ height: totalHeight + 'px' }"
      >
        <!-- 可见区域 -->
        <div 
          class="virtual-visible"
          :style="visibleStyle"
        >
          <!-- 报告项目 -->
          <div
            v-for="(report, index) in visibleReports"
            :key="report.report_id"
            class="report-item"
            :class="{ 'item-selected': selectedReports.has(report.report_id) }"
            @click="handleItemClick(report)"
            @mouseenter="handleItemHover(report, true)"
            @mouseleave="handleItemHover(report, false)"
            :style="{ height: itemHeight + 'px' }"
          >
            <!-- 选择框 -->
            <div class="item-checkbox">
              <a-checkbox
                :checked="selectedReports.has(report.report_id)"
                @change="handleItemSelect(report, $event)"
                @click.stop
              />
            </div>
            
            <!-- 报告内容 -->
            <div class="item-content">
              <div class="item-header">
                <div class="item-title">{{ report.title }}</div>
                <div class="item-meta">
                  <a-tag 
                    :color="getTypeColor(report.report_type)"
                    size="small"
                  >
                    {{ getTypeLabel(report.report_type) }}
                  </a-tag>
                  <a-tag 
                    :color="getStatusColor(report.status)"
                    size="small"
                  >
                    {{ getStatusLabel(report.status) }}
                  </a-tag>
                </div>
              </div>
              
              <div class="item-body">
                <div class="item-score">
                  <div class="score-value" :class="getScoreClass(report.health_score?.overall)">
                    {{ report.health_score?.overall || '-' }}
                  </div>
                  <div class="score-label">健康评分</div>
                </div>
                
                <div class="item-details">
                  <div class="detail-item">
                    <CalendarOutlined />
                    {{ formatDate(report.created_at) }}
                  </div>
                  <div class="detail-item">
                    <EyeOutlined />
                    {{ report.insights?.length || 0 }} 个洞察
                  </div>
                  <div class="detail-item">
                    <ClockCircleOutlined />
                    {{ formatPeriod(report.period) }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="item-actions">
              <a-button 
                type="text" 
                size="small"
                @click.stop="handleViewReport(report)"
              >
                <EyeOutlined />
              </a-button>
              
              <a-dropdown>
                <a-button type="text" size="small" @click.stop>
                  <MoreOutlined />
                </a-button>
                <template #overlay>
                  <a-menu>
                    <a-menu-item @click="handleExportReport(report)">
                      <DownloadOutlined />
                      导出
                    </a-menu-item>
                    <a-menu-item @click="handleShareReport(report)">
                      <ShareAltOutlined />
                      分享
                    </a-menu-item>
                    <a-menu-item @click="handleDeleteReport(report)" danger>
                      <DeleteOutlined />
                      删除
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="report._loading" class="item-loading">
              <a-spin size="small" />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 批量操作 -->
    <div v-if="selectedReports.size > 0" class="batch-actions">
      <div class="batch-info">
        已选择 {{ selectedReports.size }} 项
      </div>
      <div class="batch-buttons">
        <a-button @click="handleBatchExport" :loading="batchExporting">
          <DownloadOutlined />
          批量导出
        </a-button>
        <a-button @click="handleBatchDelete" danger :loading="batchDeleting">
          <DeleteOutlined />
          批量删除
        </a-button>
        <a-button @click="clearSelection">
          清除选择
        </a-button>
      </div>
    </div>
    
    <!-- 加载更多 -->
    <div v-if="hasMore && !loading" class="load-more">
      <a-button @click="loadMore" :loading="loadingMore" block>
        加载更多
      </a-button>
    </div>
    
    <!-- 底部加载状态 -->
    <div v-if="loading" class="loading-footer">
      <a-spin />
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { 
  InfoCircleOutlined,
  CalendarOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  MoreOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { VirtualScroll, debounce, throttle, globalPerformanceMonitor } from '../../utils/performance.js'

// Props
const props = defineProps({
  dataSource: {
    type: Function,
    required: true
  },
  itemHeight: {
    type: Number,
    default: 120
  },
  containerHeight: {
    type: Number,
    default: 600
  },
  pageSize: {
    type: Number,
    default: 50
  },
  enableBatchActions: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['item-click', 'item-select', 'batch-action'])

// 响应式数据
const containerRef = ref(null)
const loading = ref(false)
const loadingMore = ref(false)
const batchExporting = ref(false)
const batchDeleting = ref(false)
const showStats = ref(false)

// 搜索和筛选
const searchKeyword = ref('')
const selectedType = ref(null)
const selectedStatus = ref(null)

// 数据
const allReports = ref([])
const filteredReports = ref([])
const selectedReports = ref(new Set())
const currentPage = ref(1)
const hasMore = ref(true)

// 虚拟滚动
const virtualScroll = ref(null)
const visibleReports = ref([])
const scrollTop = ref(0)

// 性能统计
const renderStats = ref({
  renderedItems: 0,
  scrollPerformance: 0,
  memoryUsage: 0
})

// 计算属性
const totalCount = computed(() => allReports.value.length)
const visibleCount = computed(() => filteredReports.value.length)

const containerStyle = computed(() => ({
  height: `${props.containerHeight}px`,
  overflow: 'auto'
}))

const totalHeight = computed(() => {
  return virtualScroll.value ? virtualScroll.value.totalHeight : 0
})

const visibleStyle = computed(() => {
  return virtualScroll.value ? virtualScroll.value.getVisibleStyle() : {}
})

// 防抖搜索
const debouncedSearch = debounce(() => {
  handleSearch(searchKeyword.value)
}, 300)

// 节流滚动
const throttledScroll = throttle((event) => {
  handleScrollUpdate(event.target.scrollTop)
}, 16) // 60fps

// 方法
const initVirtualScroll = () => {
  virtualScroll.value = new VirtualScroll({
    itemHeight: props.itemHeight,
    containerHeight: props.containerHeight,
    data: filteredReports.value,
    buffer: 5
  })
  updateVisibleItems()
}

const updateVisibleItems = () => {
  if (!virtualScroll.value) return
  
  globalPerformanceMonitor.startTiming('virtualScrollUpdate')
  
  const visibleData = virtualScroll.value.getVisibleData()
  visibleReports.value = visibleData
  
  renderStats.value.renderedItems = visibleData.length
  
  globalPerformanceMonitor.endTiming('virtualScrollUpdate')
  
  const metrics = globalPerformanceMonitor.getAllMetrics()
  renderStats.value.scrollPerformance = Math.round(metrics.virtualScrollUpdate?.duration || 0)
}

const handleScroll = throttledScroll

const handleScrollUpdate = (newScrollTop) => {
  scrollTop.value = newScrollTop
  
  if (virtualScroll.value) {
    const needsUpdate = virtualScroll.value.updateScrollTop(newScrollTop)
    if (needsUpdate) {
      updateVisibleItems()
    }
  }
  
  // 检查是否需要加载更多
  const container = containerRef.value
  if (container) {
    const { scrollTop, scrollHeight, clientHeight } = container
    if (scrollHeight - scrollTop - clientHeight < 100 && hasMore.value && !loadingMore.value) {
      loadMore()
    }
  }
}

const fetchReports = async (page = 1, append = false) => {
  if (page === 1) loading.value = true
  else loadingMore.value = true
  
  try {
    const response = await props.dataSource({
      page,
      pageSize: props.pageSize,
      search: searchKeyword.value,
      type: selectedType.value,
      status: selectedStatus.value
    })
    
    const newReports = response.data || []
    
    if (append) {
      allReports.value.push(...newReports)
    } else {
      allReports.value = newReports
    }
    
    hasMore.value = newReports.length === props.pageSize
    currentPage.value = page
    
    applyFilters()
    
  } catch (error) {
    console.error('获取报告列表失败:', error)
    message.error('获取报告列表失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const applyFilters = () => {
  let filtered = [...allReports.value]
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(report => 
      report.title.toLowerCase().includes(keyword) ||
      report.report_type.toLowerCase().includes(keyword)
    )
  }
  
  // 类型过滤
  if (selectedType.value) {
    filtered = filtered.filter(report => report.report_type === selectedType.value)
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(report => report.status === selectedStatus.value)
  }
  
  filteredReports.value = filtered
  
  // 更新虚拟滚动
  if (virtualScroll.value) {
    virtualScroll.value.updateData(filtered)
    updateVisibleItems()
  }
}

const loadMore = async () => {
  if (!hasMore.value || loadingMore.value) return
  await fetchReports(currentPage.value + 1, true)
}

const handleSearch = (keyword) => {
  searchKeyword.value = keyword
  applyFilters()
}

const handleTypeFilter = (type) => {
  selectedType.value = type
  applyFilters()
}

const handleStatusFilter = (status) => {
  selectedStatus.value = status
  applyFilters()
}

const handleItemClick = (report) => {
  emit('item-click', report)
}

const handleItemSelect = (report, event) => {
  const isSelected = event.target.checked
  
  if (isSelected) {
    selectedReports.value.add(report.report_id)
  } else {
    selectedReports.value.delete(report.report_id)
  }
  
  emit('item-select', {
    report,
    selected: isSelected,
    selectedCount: selectedReports.value.size
  })
}

const handleItemHover = (report, isEnter) => {
  // 可以在这里添加悬停效果
}

const clearSelection = () => {
  selectedReports.value.clear()
}

const handleViewReport = (report) => {
  emit('item-click', report)
}

const handleExportReport = (report) => {
  message.success(`导出报告: ${report.title}`)
}

const handleShareReport = (report) => {
  message.success(`分享报告: ${report.title}`)
}

const handleDeleteReport = (report) => {
  // 从列表中移除
  const index = allReports.value.findIndex(r => r.report_id === report.report_id)
  if (index > -1) {
    allReports.value.splice(index, 1)
    applyFilters()
    message.success('报告已删除')
  }
}

const handleBatchExport = async () => {
  batchExporting.value = true
  try {
    const selectedIds = Array.from(selectedReports.value)
    emit('batch-action', { action: 'export', ids: selectedIds })
    message.success(`批量导出 ${selectedIds.length} 个报告`)
  } finally {
    batchExporting.value = false
  }
}

const handleBatchDelete = async () => {
  batchDeleting.value = true
  try {
    const selectedIds = Array.from(selectedReports.value)
    
    // 从列表中移除选中的报告
    allReports.value = allReports.value.filter(report => 
      !selectedIds.includes(report.report_id)
    )
    
    clearSelection()
    applyFilters()
    
    emit('batch-action', { action: 'delete', ids: selectedIds })
    message.success(`批量删除 ${selectedIds.length} 个报告`)
  } finally {
    batchDeleting.value = false
  }
}

// 工具方法
const getTypeLabel = (type) => {
  const labels = { weekly: '周报', monthly: '月报', quarterly: '季报' }
  return labels[type] || type
}

const getTypeColor = (type) => {
  const colors = { weekly: 'blue', monthly: 'green', quarterly: 'orange' }
  return colors[type] || 'default'
}

const getStatusLabel = (status) => {
  const labels = { completed: '已完成', generating: '生成中', failed: '失败' }
  return labels[status] || status
}

const getStatusColor = (status) => {
  const colors = { completed: 'success', generating: 'processing', failed: 'error' }
  return colors[status] || 'default'
}

const getScoreClass = (score) => {
  if (score >= 85) return 'score-excellent'
  if (score >= 75) return 'score-good'
  if (score >= 65) return 'score-fair'
  return 'score-poor'
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString()
}

const formatPeriod = (period) => {
  if (!period) return '-'
  const start = new Date(period.start_date).toLocaleDateString()
  const end = new Date(period.end_date).toLocaleDateString()
  return `${start} - ${end}`
}

// 监听器
watch(filteredReports, () => {
  nextTick(() => {
    if (!virtualScroll.value) {
      initVirtualScroll()
    }
  })
})

// 生命周期
onMounted(async () => {
  await fetchReports()
  
  // 监听内存使用
  if (performance.memory) {
    const updateMemoryStats = () => {
      renderStats.value.memoryUsage = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)
    }
    
    updateMemoryStats()
    setInterval(updateMemoryStats, 5000)
  }
})

onUnmounted(() => {
  if (virtualScroll.value) {
    virtualScroll.value = null
  }
})

// 暴露方法给父组件
defineExpose({
  refresh: () => fetchReports(1),
  clearSelection,
  getSelectedReports: () => Array.from(selectedReports.value)
})
</script>

<style scoped>
.virtual-report-list {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.search-section {
  display: flex;
  align-items: center;
}

.list-stats {
  display: flex;
  align-items: center;
  gap: 8px;
}

.performance-stats {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
}

.stat-item {
  display: flex;
  gap: 4px;
}

.stat-label {
  color: #8c8c8c;
}

.stat-value {
  color: #262626;
  font-weight: 600;
}

.virtual-container {
  position: relative;
}

.virtual-content {
  position: relative;
}

.virtual-visible {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.report-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.report-item:hover {
  background: #fafafa;
}

.item-selected {
  background: #e6f7ff;
}

.item-checkbox {
  margin-right: 12px;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-right: 12px;
}

.item-meta {
  display: flex;
  gap: 4px;
}

.item-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.item-score {
  text-align: center;
  min-width: 60px;
}

.score-value {
  font-size: 20px;
  font-weight: 600;
  line-height: 1;
  margin-bottom: 2px;
}

.score-excellent { color: #52c41a; }
.score-good { color: #1890ff; }
.score-fair { color: #faad14; }
.score-poor { color: #ff4d4f; }

.score-label {
  font-size: 11px;
  color: #8c8c8c;
}

.item-details {
  display: flex;
  gap: 16px;
  flex: 1;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8c8c8c;
}

.item-actions {
  display: flex;
  gap: 4px;
  margin-left: 12px;
}

.item-loading {
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-top: 1px solid #f0f0f0;
}

.batch-info {
  font-size: 14px;
  color: #262626;
}

.batch-buttons {
  display: flex;
  gap: 8px;
}

.load-more {
  padding: 16px;
}

.loading-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #8c8c8c;
}
</style>
