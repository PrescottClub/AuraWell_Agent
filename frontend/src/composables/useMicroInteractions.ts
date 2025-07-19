/**
 * AuraWell 微交互组合式函数
 * 
 * 提供统一的微交互管理和动效控制
 */

import { ref, onMounted, onUnmounted } from 'vue'

export interface MicroInteractionOptions {
  duration?: number
  easing?: string
  delay?: number
  disabled?: boolean
}

export interface AnimationState {
  isAnimating: boolean
  progress: number
  direction: 'forward' | 'reverse'
}

/**
 * 微交互管理器
 */
export function useMicroInteractions() {
  const animationState = ref<AnimationState>({
    isAnimating: false,
    progress: 0,
    direction: 'forward'
  })

  const prefersReducedMotion = ref(false)

  // 检测用户动效偏好
  const checkMotionPreference = () => {
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      prefersReducedMotion.value = mediaQuery.matches
      
      mediaQuery.addEventListener('change', (e) => {
        prefersReducedMotion.value = e.matches
      })
    }
  }

  onMounted(() => {
    checkMotionPreference()
  })

  /**
   * 卡片悬浮动效
   */
  const cardHover = (element: HTMLElement, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    const { duration = 200, easing = 'ease-out' } = options

    element.style.transition = `transform ${duration}ms ${easing}, box-shadow ${duration}ms ${easing}`
    element.style.transform = 'translateY(-2px) translateZ(0)'
    element.style.boxShadow = '0 8px 25px rgba(26, 54, 93, 0.12)'
  }

  const cardLeave = (element: HTMLElement, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    element.style.transform = 'translateY(0) translateZ(0)'
    element.style.boxShadow = ''
  }

  /**
   * 按钮点击动效
   */
  const buttonClick = (element: HTMLElement, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    const { duration = 150 } = options

    animationState.value.isAnimating = true
    
    element.style.transform = 'translateY(0) scale(0.98) translateZ(0)'
    element.style.transition = `transform ${duration}ms ease-in`

    setTimeout(() => {
      element.style.transform = 'translateY(-1px) scale(1) translateZ(0)'
      element.style.transition = `transform ${duration * 2}ms ease-out`
      animationState.value.isAnimating = false
    }, duration)
  }

  /**
   * 波纹点击效果
   */
  const rippleEffect = (element: HTMLElement, event: MouseEvent, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    const { duration = 300 } = options
    const rect = element.getBoundingClientRect()
    const size = Math.max(rect.width, rect.height)
    const x = event.clientX - rect.left - size / 2
    const y = event.clientY - rect.top - size / 2

    const ripple = document.createElement('div')
    ripple.style.cssText = `
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      transform: scale(0);
      animation: ripple ${duration}ms ease-out;
      left: ${x}px;
      top: ${y}px;
      width: ${size}px;
      height: ${size}px;
      pointer-events: none;
    `

    // 添加ripple动画关键帧（如果不存在）
    if (!document.querySelector('#ripple-keyframes')) {
      const style = document.createElement('style')
      style.id = 'ripple-keyframes'
      style.textContent = `
        @keyframes ripple {
          to {
            transform: scale(2);
            opacity: 0;
          }
        }
      `
      document.head.appendChild(style)
    }

    element.style.position = 'relative'
    element.style.overflow = 'hidden'
    element.appendChild(ripple)

    setTimeout(() => {
      ripple.remove()
    }, duration)
  }

  /**
   * 输入框聚焦动效
   */
  const inputFocus = (element: HTMLElement, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    const { duration = 200 } = options

    element.style.transition = `all ${duration}ms ease-out`
    element.style.transform = 'scale(1.01) translateZ(0)'
    element.style.boxShadow = '0 0 0 3px rgba(26, 54, 93, 0.1)'
  }

  const inputBlur = (element: HTMLElement, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    element.style.transform = 'scale(1) translateZ(0)'
    element.style.boxShadow = ''
  }

  /**
   * 数值变化动画
   */
  const animateNumber = (
    element: HTMLElement,
    from: number,
    to: number,
    options: MicroInteractionOptions & { formatter?: (value: number) => string } = {}
  ) => {
    if (prefersReducedMotion.value || options.disabled) {
      element.textContent = options.formatter ? options.formatter(to) : to.toString()
      return
    }

    const { duration = 600, formatter = (v) => Math.round(v).toString() } = options
    const startTime = performance.now()
    const difference = to - from

    animationState.value.isAnimating = true

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // 使用easeOutCubic缓动函数
      const easeProgress = 1 - Math.pow(1 - progress, 3)
      const currentValue = from + difference * easeProgress

      element.textContent = formatter(currentValue)
      animationState.value.progress = progress

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        animationState.value.isAnimating = false
        animationState.value.progress = 1
      }
    }

    requestAnimationFrame(animate)
  }

  /**
   * 页面进入动画
   */
  const pageEnter = (element: HTMLElement, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    const { duration = 300, delay = 0 } = options

    element.style.opacity = '0'
    element.style.transform = 'translateY(20px)'
    element.style.transition = `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`

    setTimeout(() => {
      element.style.opacity = '1'
      element.style.transform = 'translateY(0)'
    }, delay)
  }

  /**
   * 滚动视差效果
   */
  const parallaxScroll = (element: HTMLElement, intensity: number = 0.5) => {
    if (prefersReducedMotion.value) return

    const handleScroll = () => {
      const scrolled = window.pageYOffset
      const rate = scrolled * -intensity
      element.style.transform = `translateY(${rate}px) translateZ(0)`
    }

    window.addEventListener('scroll', handleScroll, { passive: true })

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })
  }

  /**
   * 健康指标脉冲动画
   */
  const healthPulse = (element: HTMLElement, status: 'excellent' | 'good' | 'normal' | 'warning' | 'danger') => {
    if (prefersReducedMotion.value) return

    const colors = {
      excellent: 'rgba(45, 125, 50, 0.4)',
      good: 'rgba(56, 142, 60, 0.4)',
      normal: 'rgba(251, 192, 45, 0.4)',
      warning: 'rgba(245, 124, 0, 0.4)',
      danger: 'rgba(198, 40, 40, 0.4)'
    }

    element.style.animation = `statusPulse 2s infinite ease-in-out`
    element.style.setProperty('--pulse-color', colors[status])
  }

  /**
   * 数据流动效果
   */
  const dataFlow = (element: HTMLElement, options: MicroInteractionOptions = {}) => {
    if (prefersReducedMotion.value || options.disabled) return

    const { duration = 2000 } = options

    element.style.position = 'relative'
    element.style.overflow = 'hidden'

    const flowElement = document.createElement('div')
    flowElement.style.cssText = `
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
      animation: dataFlow ${duration}ms infinite ease-in-out;
    `

    element.appendChild(flowElement)

    return () => {
      flowElement.remove()
    }
  }

  return {
    animationState: animationState.value,
    prefersReducedMotion,
    
    // 基础交互
    cardHover,
    cardLeave,
    buttonClick,
    rippleEffect,
    inputFocus,
    inputBlur,
    
    // 高级动画
    animateNumber,
    pageEnter,
    parallaxScroll,
    healthPulse,
    dataFlow,
  }
}

/**
 * 滚动进度指示器
 */
export function useScrollProgress() {
  const progress = ref(0)

  const updateProgress = () => {
    const scrollTop = window.pageYOffset
    const docHeight = document.documentElement.scrollHeight - window.innerHeight
    progress.value = (scrollTop / docHeight) * 100
  }

  onMounted(() => {
    window.addEventListener('scroll', updateProgress, { passive: true })
    updateProgress()
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', updateProgress)
  })

  return { progress }
}

/**
 * 元素可见性检测
 */
export function useIntersectionObserver(
  callback: (isVisible: boolean) => void,
  options: IntersectionObserverInit = {}
) {
  const target = ref<HTMLElement>()
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    if (target.value) {
      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            callback(entry.isIntersecting)
          })
        },
        {
          threshold: 0.1,
          ...options
        }
      )
      observer.observe(target.value)
    }
  })

  onUnmounted(() => {
    if (observer) {
      observer.disconnect()
    }
  })

  return { target }
}
