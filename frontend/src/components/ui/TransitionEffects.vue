<!--
  AuraWell 过渡动画组件
  提供统一的页面和元素过渡效果
-->

<template>
  <transition
    :name="transitionName"
    :mode="mode"
    :duration="duration"
    @before-enter="onBeforeEnter"
    @enter="onEnter"
    @after-enter="onAfterEnter"
    @before-leave="onBeforeLeave"
    @leave="onLeave"
    @after-leave="onAfterLeave"
  >
    <slot />
  </transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'fade',
    validator: (value) => [
      'fade', 'slide-up', 'slide-down', 'slide-left', 'slide-right',
      'scale', 'flip', 'bounce', 'elastic', 'health-pulse'
    ].includes(value)
  },
  mode: {
    type: String,
    default: 'out-in',
    validator: (value) => ['in-out', 'out-in'].includes(value)
  },
  duration: {
    type: [Number, Object],
    default: () => ({ enter: 300, leave: 200 })
  },
  delay: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'before-enter', 'enter', 'after-enter',
  'before-leave', 'leave', 'after-leave'
])

const transitionName = computed(() => `aura-${props.type}`)

// 事件处理
const onBeforeEnter = (el) => {
  if (props.delay > 0) {
    el.style.animationDelay = `${props.delay}ms`
  }
  emit('before-enter', el)
}

const onEnter = (el, done) => {
  emit('enter', el, done)
  done()
}

const onAfterEnter = (el) => {
  if (props.delay > 0) {
    el.style.animationDelay = ''
  }
  emit('after-enter', el)
}

const onBeforeLeave = (el) => {
  emit('before-leave', el)
}

const onLeave = (el, done) => {
  emit('leave', el, done)
  done()
}

const onAfterLeave = (el) => {
  emit('after-leave', el)
}
</script>

<style scoped>
/* 基础淡入淡出 */
.aura-fade-enter-active,
.aura-fade-leave-active {
  transition: opacity var(--duration-base) var(--ease-out);
}

.aura-fade-enter-from,
.aura-fade-leave-to {
  opacity: 0;
}

/* 向上滑动 */
.aura-slide-up-enter-active,
.aura-slide-up-leave-active {
  transition: all var(--duration-base) var(--ease-out);
}

.aura-slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.aura-slide-up-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 向下滑动 */
.aura-slide-down-enter-active,
.aura-slide-down-leave-active {
  transition: all var(--duration-base) var(--ease-out);
}

.aura-slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.aura-slide-down-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 向左滑动 */
.aura-slide-left-enter-active,
.aura-slide-left-leave-active {
  transition: all var(--duration-base) var(--ease-out);
}

.aura-slide-left-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.aura-slide-left-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 向右滑动 */
.aura-slide-right-enter-active,
.aura-slide-right-leave-active {
  transition: all var(--duration-base) var(--ease-out);
}

.aura-slide-right-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.aura-slide-right-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 缩放效果 */
.aura-scale-enter-active,
.aura-scale-leave-active {
  transition: all var(--duration-base) var(--ease-out);
}

.aura-scale-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.aura-scale-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

/* 翻转效果 */
.aura-flip-enter-active,
.aura-flip-leave-active {
  transition: all var(--duration-base) var(--ease-out);
}

.aura-flip-enter-from {
  opacity: 0;
  transform: rotateY(-90deg);
}

.aura-flip-leave-to {
  opacity: 0;
  transform: rotateY(90deg);
}

/* 弹跳效果 */
.aura-bounce-enter-active {
  animation: bounceIn var(--duration-slow) var(--ease-out);
}

.aura-bounce-leave-active {
  animation: bounceOut var(--duration-base) var(--ease-in);
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes bounceOut {
  0% {
    transform: scale(1);
  }
  25% {
    transform: scale(0.95);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 0;
    transform: scale(0.3);
  }
}

/* 弹性效果 */
.aura-elastic-enter-active {
  animation: elasticIn var(--duration-slower) var(--ease-out);
}

.aura-elastic-leave-active {
  animation: elasticOut var(--duration-base) var(--ease-in);
}

@keyframes elasticIn {
  0% {
    opacity: 0;
    transform: scale(0);
  }
  55% {
    opacity: 1;
    transform: scale(1.1);
  }
  75% {
    transform: scale(0.95);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes elasticOut {
  0% {
    transform: scale(1);
  }
  25% {
    transform: scale(0.95);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 0;
    transform: scale(0);
  }
}

/* 健康脉冲效果 */
.aura-health-pulse-enter-active {
  animation: healthPulseIn 0.8s var(--ease-out);
}

.aura-health-pulse-leave-active {
  animation: healthPulseOut 0.4s var(--ease-in);
}

@keyframes healthPulseIn {
  0% {
    opacity: 0;
    transform: scale(0.8);
    box-shadow: 0 0 0 0 rgba(45, 125, 50, 0.4);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(45, 125, 50, 0);
  }
  100% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(45, 125, 50, 0);
  }
}

@keyframes healthPulseOut {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.8);
  }
}

/* 响应式动效 - 尊重用户偏好 */
@media (prefers-reduced-motion: reduce) {
  .aura-fade-enter-active,
  .aura-fade-leave-active,
  .aura-slide-up-enter-active,
  .aura-slide-up-leave-active,
  .aura-slide-down-enter-active,
  .aura-slide-down-leave-active,
  .aura-slide-left-enter-active,
  .aura-slide-left-leave-active,
  .aura-slide-right-enter-active,
  .aura-slide-right-leave-active,
  .aura-scale-enter-active,
  .aura-scale-leave-active,
  .aura-flip-enter-active,
  .aura-flip-leave-active {
    transition-duration: 0.01ms !important;
  }

  .aura-bounce-enter-active,
  .aura-bounce-leave-active,
  .aura-elastic-enter-active,
  .aura-elastic-leave-active,
  .aura-health-pulse-enter-active,
  .aura-health-pulse-leave-active {
    animation-duration: 0.01ms !important;
  }

  .aura-slide-up-enter-from,
  .aura-slide-up-leave-to,
  .aura-slide-down-enter-from,
  .aura-slide-down-leave-to,
  .aura-slide-left-enter-from,
  .aura-slide-left-leave-to,
  .aura-slide-right-enter-from,
  .aura-slide-right-leave-to,
  .aura-scale-enter-from,
  .aura-scale-leave-to,
  .aura-flip-enter-from,
  .aura-flip-leave-to {
    transform: none !important;
  }
}
</style>
