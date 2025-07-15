import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'
import { useDataTransition } from './useDataTransition'
import { useGestures } from './useGestures'

export function useSmartAnimations() {
  const { pulseOnUpdate, animateTrend, refreshCardData } = useDataTransition()
  const { bindGestures } = useGestures()

  // 用户行为追踪
  const userBehavior = reactive({
    clickCount: 0,
    scrollVelocity: 0,
    hoverDuration: 0,
    interactionPattern: 'normal', // normal, energetic, calm
    preferredAnimationSpeed: 1.0
  })

  // 健康数据状态
  const healthDataState = reactive({
    currentValues: {},
    previousValues: {},
    trends: {},
    achievements: [],
    lastUpdateTime: Date.now()
  })

  // 动画配置
  const animationConfig = ref({
    reducedMotion: false,
    performanceMode: 'balanced', // high, balanced, low
    adaptiveSpeed: true,
    contextualEffects: true
  })

  let scrollHandler = null
  let performanceObserver = null

  // 检测用户偏好
  const detectUserPreferences = () => {
    // 检测减少动效偏好
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    animationConfig.value.reducedMotion = prefersReducedMotion.matches

    prefersReducedMotion.addEventListener('change', () => {
      animationConfig.value.reducedMotion = prefersReducedMotion.matches
    })

    // 检测设备性能
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
    if (connection) {
      const effectiveType = connection.effectiveType
      if (effectiveType === 'slow-2g' || effectiveType === '2g') {
        animationConfig.value.performanceMode = 'low'
      } else if (effectiveType === '4g') {
        animationConfig.value.performanceMode = 'high'
      }
    }
  }

  // 用户行为分析
  const analyzeUserBehavior = () => {
    const clickRate = userBehavior.clickCount / (Date.now() / 1000 / 60) // clicks per minute
    
    if (clickRate > 10) {
      userBehavior.interactionPattern = 'energetic'
      userBehavior.preferredAnimationSpeed = 1.3
    } else if (clickRate < 3) {
      userBehavior.interactionPattern = 'calm'
      userBehavior.preferredAnimationSpeed = 0.8
    } else {
      userBehavior.interactionPattern = 'normal'
      userBehavior.preferredAnimationSpeed = 1.0
    }
  }

  // 自适应动画速度
  const getAdaptiveSpeed = (baseSpeed = 1.0) => {
    if (animationConfig.value.reducedMotion) return 0.3
    if (!animationConfig.value.adaptiveSpeed) return baseSpeed

    let speed = baseSpeed * userBehavior.preferredAnimationSpeed

    // 根据性能模式调整
    switch (animationConfig.value.performanceMode) {
      case 'low':
        speed *= 0.7
        break
      case 'high':
        speed *= 1.2
        break
    }

    return speed
  }

  // 智能健康数据动画
  const animateHealthDataUpdate = (element, newValue, oldValue, dataType) => {
    const speed = getAdaptiveSpeed(1.2)
    const difference = newValue - oldValue
    const percentChange = oldValue ? (difference / oldValue) * 100 : 0

    // 更新内部状态
    healthDataState.currentValues[dataType] = newValue
    healthDataState.previousValues[dataType] = oldValue
    healthDataState.trends[dataType] = percentChange

    if (animationConfig.value.reducedMotion) {
      // 简化动画
      pulseOnUpdate(element, { scale: 1.02, duration: 0.2 })
      return
    }

    // 根据数据变化程度选择动画强度
    if (Math.abs(percentChange) > 10) {
      // 显著变化 - 强烈动画
      gsap.timeline()
        .to(element, {
          scale: 1.1,
          duration: 0.3 / speed,
          ease: 'back.out(1.7)'
        })
        .to(element, {
          scale: 1,
          duration: 0.4 / speed,
          ease: 'elastic.out(1, 0.3)'
        })
        .to(element, {
          backgroundColor: percentChange > 0 ? '#10B981' : '#EF4444',
          duration: 0.2 / speed,
          yoyo: true,
          repeat: 1
        }, '-=0.3')
    } else if (Math.abs(percentChange) > 3) {
      // 中等变化 - 中等动画
      pulseOnUpdate(element, { 
        scale: 1.05, 
        duration: 0.4 / speed,
        color: percentChange > 0 ? '#10B981' : '#F59E0B'
      })
    } else {
      // 轻微变化 - 轻微动画
      pulseOnUpdate(element, { 
        scale: 1.02, 
        duration: 0.3 / speed 
      })
    }
  }

  // 成就庆祝智能动画
  const celebrateAchievement = (achievementType, intensity = 'normal') => {
    if (animationConfig.value.reducedMotion) return

    const speed = getAdaptiveSpeed()
    let animationIntensity = intensity

    // 根据用户行为调整庆祝强度
    if (userBehavior.interactionPattern === 'energetic') {
      animationIntensity = 'high'
    } else if (userBehavior.interactionPattern === 'calm') {
      animationIntensity = 'low'
    }

    // 触发对应的庆祝动画
    const celebrationEvent = new CustomEvent('celebration', {
      detail: {
        type: achievementType,
        intensity: animationIntensity,
        speed: speed
      }
    })
    document.dispatchEvent(celebrationEvent)
  }

  // 情境化动画效果
  const applyContextualAnimation = (element) => {
    if (!animationConfig.value.contextualEffects) return

    const speed = getAdaptiveSpeed()
    const currentHour = new Date().getHours()

    // 根据时间调整动画风格
    let timeBasedStyle = 'default'
    if (currentHour >= 6 && currentHour < 12) {
      timeBasedStyle = 'morning' // 清新、活跃
    } else if (currentHour >= 12 && currentHour < 18) {
      timeBasedStyle = 'afternoon' // 稳定、专注
    } else {
      timeBasedStyle = 'evening' // 温和、舒缓
    }

    const animations = {
      morning: {
        bounce: 'back.out(1.7)',
        color: '#10B981',
        scale: 1.08
      },
      afternoon: {
        bounce: 'power2.out',
        color: '#3B82F6',
        scale: 1.05
      },
      evening: {
        bounce: 'sine.out',
        color: '#8B5CF6',
        scale: 1.03
      }
    }

    const style = animations[timeBasedStyle]
    
    gsap.to(element, {
      scale: style.scale,
      duration: 0.6 / speed,
      ease: style.bounce,
      yoyo: true,
      repeat: 1
    })
  }

  // 性能优化动画
  const optimizedAnimation = (element, animationFn, options = {}) => {
    const {
      skipOnLowPerf = false
    } = options

    // 跳过低优先级动画
    if (skipOnLowPerf && animationConfig.value.performanceMode === 'low') {
      return
    }

    // 使用 RAF 优化
    requestAnimationFrame(() => {
      animationFn(element)
    })
  }

  // 初始化性能监控
  const initPerformanceMonitoring = () => {
    if ('PerformanceObserver' in window) {
      performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const longTasks = entries.filter(entry => entry.duration > 50)
        
        if (longTasks.length > 3) {
          // 检测到性能问题，降低动画质量
          animationConfig.value.performanceMode = 'low'
          userBehavior.preferredAnimationSpeed = 0.7
        }
      })
      
      performanceObserver.observe({ entryTypes: ['longtask'] })
    }
  }

  // 绑定智能交互
  const bindSmartInteractions = (element, options = {}) => {
    const {
      enableGestures = true,
      enableHover = true,
      enableClick = true
    } = options

    let cleanup = []

    if (enableClick) {
      const clickHandler = () => {
        userBehavior.clickCount++
        analyzeUserBehavior()
        
        refreshCardData(element, {
          duration: 0.4 / getAdaptiveSpeed()
        })
      }
      element.addEventListener('click', clickHandler)
      cleanup.push(() => element.removeEventListener('click', clickHandler))
    }

    if (enableHover) {
      let hoverStartTime = 0
      
             const mouseEnterHandler = () => {
         hoverStartTime = Date.now()
         applyContextualAnimation(element)
       }
      
      const mouseLeaveHandler = () => {
        if (hoverStartTime) {
          userBehavior.hoverDuration += Date.now() - hoverStartTime
          hoverStartTime = 0
        }
      }
      
      element.addEventListener('mouseenter', mouseEnterHandler)
      element.addEventListener('mouseleave', mouseLeaveHandler)
      cleanup.push(() => {
        element.removeEventListener('mouseenter', mouseEnterHandler)
        element.removeEventListener('mouseleave', mouseLeaveHandler)
      })
    }

         if (enableGestures) {
       const gestureCleanup = bindGestures(element, {
         onSwipe: (el) => {
           applyContextualAnimation(el)
         },
         onLongPress: (el) => {
           applyContextualAnimation(el)
         }
       })
       cleanup.push(gestureCleanup)
     }

    return () => cleanup.forEach(fn => fn())
  }

  // 组件挂载时初始化
  onMounted(() => {
    detectUserPreferences()
    initPerformanceMonitoring()
    
    // 滚动监听
    scrollHandler = () => {
      const scrollY = window.scrollY
      userBehavior.scrollVelocity = Math.abs(scrollY - (userBehavior.lastScrollY || 0))
      userBehavior.lastScrollY = scrollY
    }
    window.addEventListener('scroll', scrollHandler, { passive: true })
  })

  // 组件卸载时清理
  onUnmounted(() => {
    if (scrollHandler) {
      window.removeEventListener('scroll', scrollHandler)
    }
    if (performanceObserver) {
      performanceObserver.disconnect()
    }
  })

  return {
    // 状态
    userBehavior,
    healthDataState,
    animationConfig,
    
    // 方法
    animateHealthDataUpdate,
    celebrateAchievement,
    applyContextualAnimation,
    optimizedAnimation,
    bindSmartInteractions,
    getAdaptiveSpeed,
    analyzeUserBehavior,
    
    // 工具函数
    pulseOnUpdate,
    animateTrend,
    refreshCardData
  }
} 