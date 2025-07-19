/**
 * AuraWell 可访问性检测和增强
 * 
 * 提供可访问性检测、焦点管理和键盘导航支持
 */

import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export interface AccessibilityPreferences {
  prefersReducedMotion: boolean
  prefersHighContrast: boolean
  prefersColorScheme: 'light' | 'dark' | 'no-preference'
  fontSize: 'small' | 'medium' | 'large'
}

export interface FocusManagement {
  currentFocusedElement: HTMLElement | null
  focusHistory: HTMLElement[]
  trapFocus: boolean
}

export interface AccessibilityReport {
  score: number
  issues: AccessibilityIssue[]
  recommendations: string[]
  wcagLevel: 'A' | 'AA' | 'AAA'
}

export interface AccessibilityIssue {
  type: 'contrast' | 'focus' | 'aria' | 'keyboard' | 'semantic'
  severity: 'low' | 'medium' | 'high' | 'critical'
  element: string
  description: string
  solution: string
}

/**
 * 可访问性主函数
 */
export function useAccessibility() {
  const preferences = ref<AccessibilityPreferences>({
    prefersReducedMotion: false,
    prefersHighContrast: false,
    prefersColorScheme: 'no-preference',
    fontSize: 'medium'
  })

  const focusManagement = ref<FocusManagement>({
    currentFocusedElement: null,
    focusHistory: [],
    trapFocus: false
  })

  const isKeyboardUser = ref(false)
  const announcements = ref<string[]>([])

  /**
   * 检测用户偏好设置
   */
  const detectUserPreferences = () => {
    if (typeof window === 'undefined') return

    // 检测动效偏好
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    preferences.value.prefersReducedMotion = motionQuery.matches

    // 检测对比度偏好
    const contrastQuery = window.matchMedia('(prefers-contrast: high)')
    preferences.value.prefersHighContrast = contrastQuery.matches

    // 检测颜色主题偏好
    const darkQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const lightQuery = window.matchMedia('(prefers-color-scheme: light)')
    
    if (darkQuery.matches) {
      preferences.value.prefersColorScheme = 'dark'
    } else if (lightQuery.matches) {
      preferences.value.prefersColorScheme = 'light'
    } else {
      preferences.value.prefersColorScheme = 'no-preference'
    }

    // 监听偏好变化
    motionQuery.addEventListener('change', (e) => {
      preferences.value.prefersReducedMotion = e.matches
    })

    contrastQuery.addEventListener('change', (e) => {
      preferences.value.prefersHighContrast = e.matches
    })

    darkQuery.addEventListener('change', (e) => {
      if (e.matches) {
        preferences.value.prefersColorScheme = 'dark'
      }
    })

    lightQuery.addEventListener('change', (e) => {
      if (e.matches) {
        preferences.value.prefersColorScheme = 'light'
      }
    })
  }

  /**
   * 检测键盘用户
   */
  const detectKeyboardUser = () => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        isKeyboardUser.value = true
        document.body.classList.add('keyboard-user')
      }
    }

    const handleMouseDown = () => {
      isKeyboardUser.value = false
      document.body.classList.remove('keyboard-user')
    }

    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('mousedown', handleMouseDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleMouseDown)
    }
  }

  /**
   * 焦点管理
   */
  const manageFocus = (element: HTMLElement) => {
    if (!element) return

    focusManagement.value.currentFocusedElement = element
    focusManagement.value.focusHistory.push(element)
    
    // 限制历史记录长度
    if (focusManagement.value.focusHistory.length > 10) {
      focusManagement.value.focusHistory.shift()
    }
  }

  /**
   * 焦点陷阱
   */
  const trapFocus = (container: HTMLElement) => {
    if (!container) return

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )

    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault()
            lastElement.focus()
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault()
            firstElement.focus()
          }
        }
      }

      if (e.key === 'Escape') {
        releaseFocusTrap()
      }
    }

    container.addEventListener('keydown', handleKeyDown)
    focusManagement.value.trapFocus = true
    
    // 聚焦到第一个元素
    nextTick(() => {
      firstElement?.focus()
    })

    return () => {
      container.removeEventListener('keydown', handleKeyDown)
      focusManagement.value.trapFocus = false
    }
  }

  /**
   * 释放焦点陷阱
   */
  const releaseFocusTrap = () => {
    focusManagement.value.trapFocus = false
    
    // 返回到之前的焦点元素
    const previousElement = focusManagement.value.focusHistory[focusManagement.value.focusHistory.length - 2]
    if (previousElement) {
      previousElement.focus()
    }
  }

  /**
   * 屏幕阅读器公告
   */
  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    announcements.value.push(message)
    
    // 创建临时的aria-live区域
    const liveRegion = document.createElement('div')
    liveRegion.setAttribute('aria-live', priority)
    liveRegion.setAttribute('aria-atomic', 'true')
    liveRegion.className = 'sr-only'
    liveRegion.textContent = message
    
    document.body.appendChild(liveRegion)
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(liveRegion)
    }, 1000)
  }

  /**
   * 检查颜色对比度
   */
  const checkColorContrast = (foreground: string, background: string): number => {
    // 简化的对比度计算
    const getLuminance = (color: string): number => {
      // 这里应该实现完整的颜色解析和亮度计算
      // 为了简化，基于颜色字符串长度返回一个模拟值
      // 实际应用中应该解析RGB值并计算相对亮度
      return Math.min(0.9, Math.max(0.1, color.length / 20))
    }

    const fgLuminance = getLuminance(foreground)
    const bgLuminance = getLuminance(background)
    
    const lighter = Math.max(fgLuminance, bgLuminance)
    const darker = Math.min(fgLuminance, bgLuminance)
    
    return (lighter + 0.05) / (darker + 0.05)
  }

  /**
   * 可访问性审计
   */
  const auditAccessibility = (): AccessibilityReport => {
    const issues: AccessibilityIssue[] = []
    let score = 100

    // 检查图片alt属性
    const images = document.querySelectorAll('img')
    images.forEach((img, index) => {
      if (!img.alt) {
        issues.push({
          type: 'semantic',
          severity: 'high',
          element: `img[${index}]`,
          description: '图片缺少alt属性',
          solution: '为图片添加描述性的alt属性'
        })
        score -= 10
      }
    })

    // 检查表单标签
    const inputs = document.querySelectorAll('input, textarea, select')
    inputs.forEach((input, index) => {
      const id = input.id
      const label = document.querySelector(`label[for="${id}"]`)
      
      if (!label && !input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
        issues.push({
          type: 'aria',
          severity: 'high',
          element: `input[${index}]`,
          description: '表单控件缺少标签',
          solution: '添加label元素或aria-label属性'
        })
        score -= 15
      }
    })

    // 检查按钮文本
    const buttons = document.querySelectorAll('button')
    buttons.forEach((button, index) => {
      const text = button.textContent?.trim()
      const ariaLabel = button.getAttribute('aria-label')
      
      if (!text && !ariaLabel) {
        issues.push({
          type: 'semantic',
          severity: 'high',
          element: `button[${index}]`,
          description: '按钮缺少可访问的文本',
          solution: '添加按钮文本或aria-label属性'
        })
        score -= 10
      }
    })

    // 检查标题层级
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6')
    let previousLevel = 0
    headings.forEach((heading, index) => {
      const currentLevel = parseInt(heading.tagName.charAt(1))
      
      if (currentLevel > previousLevel + 1) {
        issues.push({
          type: 'semantic',
          severity: 'medium',
          element: `${heading.tagName.toLowerCase()}[${index}]`,
          description: '标题层级跳跃',
          solution: '确保标题层级连续，不要跳级'
        })
        score -= 5
      }
      
      previousLevel = currentLevel
    })

    // 检查链接文本
    const links = document.querySelectorAll('a')
    links.forEach((link, index) => {
      const text = link.textContent?.trim()
      
      if (!text || text === 'click here' || text === 'read more') {
        issues.push({
          type: 'semantic',
          severity: 'medium',
          element: `a[${index}]`,
          description: '链接文本不够描述性',
          solution: '使用描述性的链接文本'
        })
        score -= 5
      }
    })

    // 生成建议
    const recommendations: string[] = []
    
    if (issues.some(issue => issue.type === 'contrast')) {
      recommendations.push('提高文字和背景的颜色对比度')
    }
    
    if (issues.some(issue => issue.type === 'aria')) {
      recommendations.push('添加适当的ARIA标签和属性')
    }
    
    if (issues.some(issue => issue.type === 'semantic')) {
      recommendations.push('改善HTML语义化结构')
    }
    
    if (issues.some(issue => issue.type === 'keyboard')) {
      recommendations.push('优化键盘导航体验')
    }

    if (recommendations.length === 0) {
      recommendations.push('可访问性表现良好，继续保持！')
    }

    // 确定WCAG等级
    let wcagLevel: 'A' | 'AA' | 'AAA' = 'A'
    if (score >= 80) wcagLevel = 'AA'
    if (score >= 95) wcagLevel = 'AAA'

    return {
      score: Math.max(0, score),
      issues,
      recommendations,
      wcagLevel
    }
  }

  /**
   * 添加跳过链接
   */
  const addSkipLinks = () => {
    const skipLink = document.createElement('a')
    skipLink.href = '#main-content'
    skipLink.textContent = '跳转到主要内容'
    skipLink.className = 'skip-link'
    
    document.body.insertBefore(skipLink, document.body.firstChild)
  }

  /**
   * 设置字体大小
   */
  const setFontSize = (size: 'small' | 'medium' | 'large') => {
    preferences.value.fontSize = size
    
    const root = document.documentElement
    switch (size) {
      case 'small':
        root.style.fontSize = '14px'
        break
      case 'medium':
        root.style.fontSize = '16px'
        break
      case 'large':
        root.style.fontSize = '18px'
        break
    }
  }

  // 生命周期管理
  onMounted(() => {
    detectUserPreferences()
    const cleanupKeyboardDetection = detectKeyboardUser()
    addSkipLinks()

    onUnmounted(() => {
      cleanupKeyboardDetection()
    })
  })

  return {
    preferences,
    focusManagement,
    isKeyboardUser,
    announcements,
    
    // 方法
    manageFocus,
    trapFocus,
    releaseFocusTrap,
    announce,
    checkColorContrast,
    auditAccessibility,
    setFontSize,
    
    // 工具函数
    detectUserPreferences,
    detectKeyboardUser
  }
}

/**
 * 键盘导航增强
 */
export function useKeyboardNavigation() {
  const currentFocusIndex = ref(0)
  const focusableElements = ref<HTMLElement[]>([])

  /**
   * 更新可聚焦元素列表
   */
  const updateFocusableElements = (container: HTMLElement = document.body) => {
    const elements = container.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    
    focusableElements.value = Array.from(elements) as HTMLElement[]
  }

  /**
   * 聚焦到下一个元素
   */
  const focusNext = () => {
    if (focusableElements.value.length === 0) return
    
    currentFocusIndex.value = (currentFocusIndex.value + 1) % focusableElements.value.length
    focusableElements.value[currentFocusIndex.value]?.focus()
  }

  /**
   * 聚焦到上一个元素
   */
  const focusPrevious = () => {
    if (focusableElements.value.length === 0) return
    
    currentFocusIndex.value = currentFocusIndex.value === 0 
      ? focusableElements.value.length - 1 
      : currentFocusIndex.value - 1
    
    focusableElements.value[currentFocusIndex.value]?.focus()
  }

  /**
   * 聚焦到第一个元素
   */
  const focusFirst = () => {
    if (focusableElements.value.length === 0) return
    
    currentFocusIndex.value = 0
    focusableElements.value[0]?.focus()
  }

  /**
   * 聚焦到最后一个元素
   */
  const focusLast = () => {
    if (focusableElements.value.length === 0) return
    
    currentFocusIndex.value = focusableElements.value.length - 1
    focusableElements.value[currentFocusIndex.value]?.focus()
  }

  return {
    currentFocusIndex,
    focusableElements,
    updateFocusableElements,
    focusNext,
    focusPrevious,
    focusFirst,
    focusLast
  }
}
