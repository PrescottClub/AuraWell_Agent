/**
 * AuraWell 性能监控组合式函数
 * 
 * 提供前端性能监控和优化建议
 */

import { ref, onMounted, onUnmounted } from 'vue'

export interface PerformanceMetrics {
  // 页面加载性能
  loadTime: number
  domContentLoaded: number
  firstContentfulPaint: number
  largestContentfulPaint: number
  firstInputDelay: number
  cumulativeLayoutShift: number
  
  // 运行时性能
  memoryUsage: number
  frameRate: number
  
  // 网络性能
  connectionType: string
  effectiveType: string
  downlink: number
  rtt: number
  
  // 用户体验指标
  timeToInteractive: number
  totalBlockingTime: number
}

export interface PerformanceThresholds {
  loadTime: { good: number; poor: number }
  firstContentfulPaint: { good: number; poor: number }
  largestContentfulPaint: { good: number; poor: number }
  firstInputDelay: { good: number; poor: number }
  cumulativeLayoutShift: { good: number; poor: number }
  memoryUsage: { good: number; poor: number }
  frameRate: { good: number; poor: number }
}

export interface PerformanceReport {
  metrics: PerformanceMetrics
  score: number
  recommendations: string[]
  timestamp: number
}

/**
 * 性能监控主函数
 */
export function usePerformanceMonitor() {
  const metrics = ref<Partial<PerformanceMetrics>>({})
  const isMonitoring = ref(false)
  const performanceScore = ref(0)
  const recommendations = ref<string[]>([])

  // 性能阈值定义
  const thresholds: PerformanceThresholds = {
    loadTime: { good: 2000, poor: 4000 },
    firstContentfulPaint: { good: 1800, poor: 3000 },
    largestContentfulPaint: { good: 2500, poor: 4000 },
    firstInputDelay: { good: 100, poor: 300 },
    cumulativeLayoutShift: { good: 0.1, poor: 0.25 },
    memoryUsage: { good: 50, poor: 100 }, // MB
    frameRate: { good: 55, poor: 30 } // FPS
  }

  /**
   * 收集页面加载性能指标
   */
  const collectLoadMetrics = () => {
    if (!window.performance) return

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    const paint = performance.getEntriesByType('paint')

    if (navigation) {
      metrics.value.loadTime = navigation.loadEventEnd - navigation.fetchStart
      metrics.value.domContentLoaded = navigation.domContentLoadedEventEnd - navigation.fetchStart
    }

    // First Contentful Paint
    const fcp = paint.find(entry => entry.name === 'first-contentful-paint')
    if (fcp) {
      metrics.value.firstContentfulPaint = fcp.startTime
    }

    // Largest Contentful Paint
    if ('PerformanceObserver' in window) {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]
        metrics.value.largestContentfulPaint = lastEntry.startTime
      })
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })

      // First Input Delay
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry: any) => {
          metrics.value.firstInputDelay = entry.processingStart - entry.startTime
        })
      })
      fidObserver.observe({ entryTypes: ['first-input'] })

      // Cumulative Layout Shift
      const clsObserver = new PerformanceObserver((list) => {
        let clsValue = 0
        const entries = list.getEntries()
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        })
        metrics.value.cumulativeLayoutShift = clsValue
      })
      clsObserver.observe({ entryTypes: ['layout-shift'] })
    }
  }

  /**
   * 收集内存使用情况
   */
  const collectMemoryMetrics = () => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      metrics.value.memoryUsage = memory.usedJSHeapSize / (1024 * 1024) // MB
    }
  }

  /**
   * 收集网络信息
   */
  const collectNetworkMetrics = () => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection
      metrics.value.connectionType = connection.type || 'unknown'
      metrics.value.effectiveType = connection.effectiveType || 'unknown'
      metrics.value.downlink = connection.downlink || 0
      metrics.value.rtt = connection.rtt || 0
    }
  }

  /**
   * 监控帧率
   */
  const monitorFrameRate = () => {
    let frameCount = 0
    let lastTime = performance.now()

    const countFrames = () => {
      frameCount++
      const currentTime = performance.now()
      
      if (currentTime - lastTime >= 1000) {
        metrics.value.frameRate = frameCount
        frameCount = 0
        lastTime = currentTime
      }
      
      if (isMonitoring.value) {
        requestAnimationFrame(countFrames)
      }
    }

    requestAnimationFrame(countFrames)
  }

  /**
   * 计算性能分数
   */
  const calculatePerformanceScore = (): number => {
    let score = 100
    const weights = {
      loadTime: 0.25,
      firstContentfulPaint: 0.15,
      largestContentfulPaint: 0.25,
      firstInputDelay: 0.15,
      cumulativeLayoutShift: 0.15,
      memoryUsage: 0.05
    }

    Object.entries(weights).forEach(([metric, weight]) => {
      const value = metrics.value[metric as keyof PerformanceMetrics]
      const threshold = thresholds[metric as keyof PerformanceThresholds]
      
      if (value !== undefined && threshold) {
        let metricScore = 100
        
        if (value > threshold.poor) {
          metricScore = 0
        } else if (value > threshold.good) {
          metricScore = 50 * (1 - (value - threshold.good) / (threshold.poor - threshold.good))
        }
        
        score -= (100 - metricScore) * weight
      }
    })

    return Math.max(0, Math.round(score))
  }

  /**
   * 生成性能建议
   */
  const generateRecommendations = (): string[] => {
    const recs: string[] = []

    if (metrics.value.loadTime && metrics.value.loadTime > thresholds.loadTime.poor) {
      recs.push('页面加载时间过长，建议优化资源加载和代码分割')
    }

    if (metrics.value.firstContentfulPaint && metrics.value.firstContentfulPaint > thresholds.firstContentfulPaint.poor) {
      recs.push('首次内容绘制时间过长，建议优化关键渲染路径')
    }

    if (metrics.value.largestContentfulPaint && metrics.value.largestContentfulPaint > thresholds.largestContentfulPaint.poor) {
      recs.push('最大内容绘制时间过长，建议优化图片和字体加载')
    }

    if (metrics.value.firstInputDelay && metrics.value.firstInputDelay > thresholds.firstInputDelay.poor) {
      recs.push('首次输入延迟过长，建议减少主线程阻塞')
    }

    if (metrics.value.cumulativeLayoutShift && metrics.value.cumulativeLayoutShift > thresholds.cumulativeLayoutShift.poor) {
      recs.push('累积布局偏移过大，建议为图片和广告预留空间')
    }

    if (metrics.value.memoryUsage && metrics.value.memoryUsage > thresholds.memoryUsage.poor) {
      recs.push('内存使用过高，建议检查内存泄漏和优化数据结构')
    }

    if (metrics.value.frameRate && metrics.value.frameRate < thresholds.frameRate.poor) {
      recs.push('帧率过低，建议优化动画和减少重绘重排')
    }

    if (recs.length === 0) {
      recs.push('性能表现良好，继续保持！')
    }

    return recs
  }

  /**
   * 开始性能监控
   */
  const startMonitoring = () => {
    if (isMonitoring.value) return

    isMonitoring.value = true
    
    // 等待页面加载完成后收集指标
    if (document.readyState === 'complete') {
      collectLoadMetrics()
    } else {
      window.addEventListener('load', collectLoadMetrics)
    }

    collectMemoryMetrics()
    collectNetworkMetrics()
    monitorFrameRate()

    // 定期更新指标
    const interval = setInterval(() => {
      if (!isMonitoring.value) {
        clearInterval(interval)
        return
      }

      collectMemoryMetrics()
      performanceScore.value = calculatePerformanceScore()
      recommendations.value = generateRecommendations()
    }, 5000)
  }

  /**
   * 停止性能监控
   */
  const stopMonitoring = () => {
    isMonitoring.value = false
  }

  /**
   * 生成性能报告
   */
  const generateReport = (): PerformanceReport => {
    return {
      metrics: metrics.value as PerformanceMetrics,
      score: performanceScore.value,
      recommendations: recommendations.value,
      timestamp: Date.now()
    }
  }

  /**
   * 发送性能数据到服务器
   */
  const sendMetricsToServer = async (report: PerformanceReport) => {
    try {
      // 这里可以发送到你的分析服务
      console.log('Performance Report:', report)
      
      // 示例：发送到服务器
      // await fetch('/api/performance', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(report)
      // })
    } catch (error) {
      console.error('Failed to send performance metrics:', error)
    }
  }

  // 生命周期管理
  onMounted(() => {
    startMonitoring()
  })

  onUnmounted(() => {
    stopMonitoring()
  })

  return {
    metrics,
    isMonitoring,
    performanceScore,
    recommendations,
    startMonitoring,
    stopMonitoring,
    generateReport,
    sendMetricsToServer,
    thresholds
  }
}

/**
 * 资源加载优化
 */
export function useResourceOptimization() {
  /**
   * 预加载关键资源
   */
  const preloadResource = (href: string, as: string, crossorigin?: string) => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = href
    link.as = as
    if (crossorigin) link.crossOrigin = crossorigin
    document.head.appendChild(link)
  }

  /**
   * 预连接到外部域名
   */
  const preconnect = (href: string, crossorigin?: boolean) => {
    const link = document.createElement('link')
    link.rel = 'preconnect'
    link.href = href
    if (crossorigin) link.crossOrigin = 'anonymous'
    document.head.appendChild(link)
  }

  /**
   * 懒加载图片
   */
  const lazyLoadImages = () => {
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement
            img.src = img.dataset.src || ''
            img.classList.remove('lazy')
            imageObserver.unobserve(img)
          }
        })
      })

      document.querySelectorAll('img[data-src]').forEach((img) => {
        imageObserver.observe(img)
      })
    }
  }

  return {
    preloadResource,
    preconnect,
    lazyLoadImages
  }
}
