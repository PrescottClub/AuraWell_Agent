<template>
  <Transition
    :name="transitionName"
    :mode="mode"
    @before-enter="beforeEnter"
    @enter="enter"
    @after-enter="afterEnter"
    @before-leave="beforeLeave"
    @leave="leave"
    @after-leave="afterLeave"
  >
    <slot />
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  name: {
    type: String,
    default: 'page'
  },
  mode: {
    type: String,
    default: 'out-in',
    validator: (value) => ['in-out', 'out-in', 'default'].includes(value)
  },
  direction: {
    type: String,
    default: 'forward',
    validator: (value) => ['forward', 'backward', 'up', 'down'].includes(value)
  },
  duration: {
    type: Number,
    default: 0.6
  },
  easing: {
    type: String,
    default: 'power2.out'
  }
})

const transitionName = computed(() => `${props.name}-${props.direction}`)

// 过渡动画配置
const getTransitionConfig = (direction) => {
  const configs = {
    forward: {
      enter: { x: '100%', opacity: 0 },
      enterTo: { x: '0%', opacity: 1 },
      leave: { x: '0%', opacity: 1 },
      leaveTo: { x: '-100%', opacity: 0 }
    },
    backward: {
      enter: { x: '-100%', opacity: 0 },
      enterTo: { x: '0%', opacity: 1 },
      leave: { x: '0%', opacity: 1 },
      leaveTo: { x: '100%', opacity: 0 }
    },
    up: {
      enter: { y: '100%', opacity: 0 },
      enterTo: { y: '0%', opacity: 1 },
      leave: { y: '0%', opacity: 1 },
      leaveTo: { y: '-100%', opacity: 0 }
    },
    down: {
      enter: { y: '-100%', opacity: 0 },
      enterTo: { y: '0%', opacity: 1 },
      leave: { y: '0%', opacity: 1 },
      leaveTo: { y: '100%', opacity: 0 }
    }
  }
  return configs[direction]
}

// 过渡生命周期钩子
const beforeEnter = (el) => {
  const config = getTransitionConfig(props.direction)
  gsap.set(el, {
    ...config.enter,
    transformOrigin: 'center center'
  })
}

const enter = (el, done) => {
  const config = getTransitionConfig(props.direction)
  
  // 创建入场动画时间线
  const tl = gsap.timeline({
    onComplete: done
  })

  // 主容器动画
  tl.to(el, {
    ...config.enterTo,
    duration: props.duration,
    ease: props.easing
  })

  // 子元素错位动画
  const children = el.querySelectorAll('.animate-child')
  if (children.length > 0) {
    tl.fromTo(children,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: props.duration * 0.8,
        stagger: 0.1,
        ease: props.easing
      },
      `-=${props.duration * 0.5}`
    )
  }
}

const afterEnter = (el) => {
  // 入场完成后的清理
  gsap.set(el, { clearProps: 'all' })
}

const beforeLeave = (el) => {
  const config = getTransitionConfig(props.direction)
  gsap.set(el, config.leave)
}

const leave = (el, done) => {
  const config = getTransitionConfig(props.direction)
  
  // 创建离场动画时间线
  const tl = gsap.timeline({
    onComplete: done
  })

  // 子元素先淡出
  const children = el.querySelectorAll('.animate-child')
  if (children.length > 0) {
    tl.to(children, {
      opacity: 0,
      y: -20,
      duration: props.duration * 0.3,
      stagger: 0.05,
      ease: props.easing
    })
  }

  // 主容器动画
  tl.to(el, {
    ...config.leaveTo,
    duration: props.duration * 0.7,
    ease: props.easing
  }, `-=${props.duration * 0.1}`)
}

const afterLeave = (el) => {
  // 离场完成后的清理
  gsap.set(el, { clearProps: 'all' })
}
</script>

<style scoped>
/* 确保过渡容器定位正确 */
.v-enter-active,
.v-leave-active {
  position: relative;
  overflow: hidden;
}

.v-enter-from,
.v-leave-to {
  position: absolute;
  width: 100%;
}

/* 防止布局闪烁 */
.transition-wrapper {
  will-change: transform, opacity;
}
</style> 