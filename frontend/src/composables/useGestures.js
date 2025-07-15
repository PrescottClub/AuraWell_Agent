import { ref } from 'vue'
import { gsap } from 'gsap'

export function useGestures() {
  const gestureState = ref({
    isActive: false,
    startX: 0,
    startY: 0,
    currentX: 0,
    currentY: 0,
    velocity: 0,
    direction: null
  })

  let gestureStartTime = 0
  let longPressTimer = null
  const LONG_PRESS_DURATION = 500 // 长按时长
  const SWIPE_THRESHOLD = 50 // 滑动阈值

  // 触摸/鼠标事件处理
  const handleStart = (event, element, callbacks = {}) => {
    const point = event.touches ? event.touches[0] : event
    
    gestureState.value = {
      isActive: true,
      startX: point.clientX,
      startY: point.clientY,
      currentX: point.clientX,
      currentY: point.clientY,
      velocity: 0,
      direction: null
    }
    
    gestureStartTime = Date.now()
    
    // 长按检测
    longPressTimer = setTimeout(() => {
      if (gestureState.value.isActive) {
        callbacks.onLongPress?.(element, gestureState.value)
        // 长按反馈动画
        gsap.to(element, {
          scale: 0.95,
          duration: 0.1,
          yoyo: true,
          repeat: 1,
          ease: 'power2.out'
        })
      }
    }, LONG_PRESS_DURATION)

    callbacks.onStart?.(element, gestureState.value)
  }

  const handleMove = (event, element, callbacks = {}) => {
    if (!gestureState.value.isActive) return

    const point = event.touches ? event.touches[0] : event
    
    gestureState.value.currentX = point.clientX
    gestureState.value.currentY = point.clientY
    
    // 计算速度
    const deltaTime = Date.now() - gestureStartTime
    const deltaX = gestureState.value.currentX - gestureState.value.startX
    const deltaY = gestureState.value.currentY - gestureState.value.startY
    gestureState.value.velocity = Math.sqrt(deltaX * deltaX + deltaY * deltaY) / deltaTime

    // 确定方向
    const absDeltaX = Math.abs(deltaX)
    const absDeltaY = Math.abs(deltaY)
    
    if (absDeltaX > absDeltaY && absDeltaX > SWIPE_THRESHOLD) {
      gestureState.value.direction = deltaX > 0 ? 'right' : 'left'
    } else if (absDeltaY > absDeltaX && absDeltaY > SWIPE_THRESHOLD) {
      gestureState.value.direction = deltaY > 0 ? 'down' : 'up'
    }

    callbacks.onMove?.(element, gestureState.value)
  }

  const handleEnd = (event, element, callbacks = {}) => {
    if (!gestureState.value.isActive) return

    clearTimeout(longPressTimer)
    
    const endTime = Date.now()
    const duration = endTime - gestureStartTime
    const deltaX = gestureState.value.currentX - gestureState.value.startX
    const deltaY = gestureState.value.currentY - gestureState.value.startY
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)

    // 判断手势类型
    if (duration < 200 && distance < 10) {
      // 短按/点击
      callbacks.onTap?.(element, gestureState.value)
    } else if (duration < 300 && distance > SWIPE_THRESHOLD) {
      // 滑动
      callbacks.onSwipe?.(element, gestureState.value)
      
      // 滑动反馈动画
      const swipeDirection = gestureState.value.direction
      if (swipeDirection) {
        const translateMap = {
          left: { x: -20, y: 0 },
          right: { x: 20, y: 0 },
          up: { x: 0, y: -20 },
          down: { x: 0, y: 20 }
        }
        
        const translate = translateMap[swipeDirection]
        gsap.timeline()
          .to(element, {
            x: translate.x,
            y: translate.y,
            duration: 0.2,
            ease: 'power2.out'
          })
          .to(element, {
            x: 0,
            y: 0,
            duration: 0.3,
            ease: 'elastic.out(1, 0.3)'
          })
      }
    }

    gestureState.value.isActive = false
    callbacks.onEnd?.(element, gestureState.value)
  }

  // 双击检测
  let lastTapTime = 0
  const handleDoubleTap = (element, callbacks = {}) => {
    return () => {
      const currentTime = Date.now()
      if (currentTime - lastTapTime < 300) {
        callbacks.onDoubleTap?.(element, gestureState.value)
        
        // 双击放大动画
        gsap.timeline()
          .to(element, {
            scale: 1.1,
            duration: 0.15,
            ease: 'power2.out'
          })
          .to(element, {
            scale: 1,
            duration: 0.15,
            ease: 'power2.out'
          })
      }
      lastTapTime = currentTime
    }
  }

  // 捏合缩放手势
  let initialDistance = 0
  const handlePinch = (event, element, callbacks = {}) => {
    if (event.touches && event.touches.length === 2) {
      const touch1 = event.touches[0]
      const touch2 = event.touches[1]
      const currentDistance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      )

      if (event.type === 'touchstart') {
        initialDistance = currentDistance
      } else if (event.type === 'touchmove' && initialDistance > 0) {
        const scale = currentDistance / initialDistance
        callbacks.onPinch?.(element, scale, gestureState.value)
      }
    }
  }

  // 注册手势到元素
  const bindGestures = (element, callbacks = {}) => {
    if (!element) return

    const startHandler = (e) => handleStart(e, element, callbacks)
    const moveHandler = (e) => handleMove(e, element, callbacks)
    const endHandler = (e) => handleEnd(e, element, callbacks)
    const doubleTapHandler = handleDoubleTap(element, callbacks)
    const pinchHandler = (e) => handlePinch(e, element, callbacks)

    // 触摸事件
    element.addEventListener('touchstart', startHandler, { passive: false })
    element.addEventListener('touchmove', moveHandler, { passive: false })
    element.addEventListener('touchend', endHandler, { passive: false })
    element.addEventListener('touchstart', pinchHandler, { passive: false })
    element.addEventListener('touchmove', pinchHandler, { passive: false })

    // 鼠标事件
    element.addEventListener('mousedown', startHandler)
    element.addEventListener('mousemove', moveHandler)
    element.addEventListener('mouseup', endHandler)
    element.addEventListener('click', doubleTapHandler)

    // 返回清理函数
    return () => {
      element.removeEventListener('touchstart', startHandler)
      element.removeEventListener('touchmove', moveHandler)
      element.removeEventListener('touchend', endHandler)
      element.removeEventListener('mousedown', startHandler)
      element.removeEventListener('mousemove', moveHandler)
      element.removeEventListener('mouseup', endHandler)
      element.removeEventListener('click', doubleTapHandler)
      element.removeEventListener('touchstart', pinchHandler)
      element.removeEventListener('touchmove', pinchHandler)
    }
  }

  return {
    gestureState,
    bindGestures,
    handleDoubleTap,
    handlePinch
  }
} 