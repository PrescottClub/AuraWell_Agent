/**
 * 内存优化组合式函数
 * 提供内存监控、清理和优化功能
 */

import { ref, onUnmounted, nextTick } from 'vue'

export function useMemoryOptimization() {
  const memoryInfo = ref({
    usedJSHeapSize: 0,
    totalJSHeapSize: 0,
    jsHeapSizeLimit: 0,
    usage: 0
  })

  const isMonitoring = ref(false)
  const monitoringInterval = ref(null)
  const cleanupTasks = ref([])

  /**
   * 获取内存使用信息
   */
  const getMemoryInfo = () => {
    if (performance.memory) {
      const memory = performance.memory
      const usage = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
      
      memoryInfo.value = {
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit,
        usage: Math.round(usage * 100) / 100
      }
      
      return memoryInfo.value
    }
    return null
  }

  /**
   * 开始内存监控
   */
  const startMemoryMonitoring = (interval = 5000) => {
    if (isMonitoring.value) return
    
    isMonitoring.value = true
    monitoringInterval.value = setInterval(() => {
      const info = getMemoryInfo()
      
      // 内存使用率超过80%时触发清理
      if (info && info.usage > 80) {
        console.warn('内存使用率过高:', info.usage + '%')
        performMemoryCleanup()
      }
    }, interval)
  }

  /**
   * 停止内存监控
   */
  const stopMemoryMonitoring = () => {
    if (monitoringInterval.value) {
      clearInterval(monitoringInterval.value)
      monitoringInterval.value = null
    }
    isMonitoring.value = false
  }

  /**
   * 执行内存清理
   */
  const performMemoryCleanup = async () => {
    console.log('开始内存清理...')
    
    // 1. 清理DOM事件监听器
    cleanupEventListeners()
    
    // 2. 清理定时器
    cleanupTimers()
    
    // 3. 清理缓存
    cleanupCaches()
    
    // 4. 清理大型对象
    cleanupLargeObjects()
    
    // 5. 强制垃圾回收（如果支持）
    if (window.gc) {
      window.gc()
    }
    
    // 6. 等待下一个事件循环
    await nextTick()
    
    console.log('内存清理完成')
    
    // 执行注册的清理任务
    cleanupTasks.value.forEach(task => {
      try {
        task()
      } catch (error) {
        console.error('清理任务执行失败:', error)
      }
    })
  }

  /**
   * 清理DOM事件监听器
   */
  const cleanupEventListeners = () => {
    // 移除可能泄漏的全局事件监听器
    const events = ['resize', 'scroll', 'mousemove', 'touchmove']
    events.forEach(event => {
      const listeners = window.getEventListeners?.(window)?.[event] || []
      listeners.forEach(listener => {
        if (listener.useCapture === false) {
          window.removeEventListener(event, listener.listener)
        }
      })
    })
  }

  /**
   * 清理定时器
   */
  const cleanupTimers = () => {
    // 清理可能遗留的定时器
    // 注意：这里只是示例，实际应用中需要更精确的定时器管理
    const highestTimeoutId = setTimeout(() => {}, 0)
    for (let i = 0; i < highestTimeoutId; i++) {
      clearTimeout(i)
    }
    
    const highestIntervalId = setInterval(() => {}, 1000)
    clearInterval(highestIntervalId)
    for (let i = 0; i < highestIntervalId; i++) {
      clearInterval(i)
    }
  }

  /**
   * 清理缓存
   */
  const cleanupCaches = () => {
    // 清理图片缓存
    const images = document.querySelectorAll('img')
    images.forEach(img => {
      if (!img.isConnected) {
        img.src = ''
        img.srcset = ''
      }
    })
    
    // 清理Canvas缓存
    const canvases = document.querySelectorAll('canvas')
    canvases.forEach(canvas => {
      if (!canvas.isConnected) {
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height)
        }
      }
    })
  }

  /**
   * 清理大型对象
   */
  const cleanupLargeObjects = () => {
    // 清理可能的大型数据结构
    if (window.__LARGE_DATA_CACHE__) {
      window.__LARGE_DATA_CACHE__.clear?.()
    }
    
    // 清理ECharts实例
    if (window.echarts) {
      const charts = window.echarts.getInstanceByDom ? 
        document.querySelectorAll('[_echarts_instance_]') : []
      charts.forEach(chart => {
        if (!chart.isConnected) {
          const instance = window.echarts.getInstanceByDom(chart)
          if (instance) {
            instance.dispose()
          }
        }
      })
    }
  }

  /**
   * 注册清理任务
   */
  const registerCleanupTask = (task) => {
    if (typeof task === 'function') {
      cleanupTasks.value.push(task)
    }
  }

  /**
   * 移除清理任务
   */
  const unregisterCleanupTask = (task) => {
    const index = cleanupTasks.value.indexOf(task)
    if (index > -1) {
      cleanupTasks.value.splice(index, 1)
    }
  }

  /**
   * 检测内存泄漏
   */
  const detectMemoryLeaks = () => {
    const initialMemory = getMemoryInfo()
    if (!initialMemory) return null
    
    return new Promise((resolve) => {
      setTimeout(() => {
        const currentMemory = getMemoryInfo()
        if (currentMemory) {
          const memoryIncrease = currentMemory.usedJSHeapSize - initialMemory.usedJSHeapSize
          const leakDetected = memoryIncrease > 10 * 1024 * 1024 // 10MB阈值
          
          resolve({
            leakDetected,
            memoryIncrease,
            initialMemory,
            currentMemory
          })
        } else {
          resolve(null)
        }
      }, 5000) // 5秒后检测
    })
  }

  /**
   * 优化大型列表渲染
   */
  const optimizeListRendering = (listRef, itemHeight = 50, visibleCount = 10) => {
    if (!listRef.value) return
    
    const container = listRef.value
    const totalHeight = container.scrollHeight
    const containerHeight = container.clientHeight
    const scrollTop = container.scrollTop
    
    // 计算可见范围
    const startIndex = Math.floor(scrollTop / itemHeight)
    const endIndex = Math.min(
      startIndex + visibleCount,
      Math.floor(totalHeight / itemHeight)
    )
    
    // 隐藏不可见的元素
    const items = container.children
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (i < startIndex || i > endIndex) {
        item.style.display = 'none'
      } else {
        item.style.display = ''
      }
    }
  }

  /**
   * 防抖函数
   */
  const debounce = (func, wait) => {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }

  /**
   * 节流函数
   */
  const throttle = (func, limit) => {
    let inThrottle
    return function executedFunction(...args) {
      if (!inThrottle) {
        func.apply(this, args)
        inThrottle = true
        setTimeout(() => inThrottle = false, limit)
      }
    }
  }

  // 组件卸载时清理
  onUnmounted(() => {
    stopMemoryMonitoring()
    performMemoryCleanup()
  })

  return {
    // 状态
    memoryInfo,
    isMonitoring,
    
    // 方法
    getMemoryInfo,
    startMemoryMonitoring,
    stopMemoryMonitoring,
    performMemoryCleanup,
    registerCleanupTask,
    unregisterCleanupTask,
    detectMemoryLeaks,
    optimizeListRendering,
    debounce,
    throttle
  }
}
