<template>
  <button
    v-motion
    :initial="{ scale: 1 }"
    :hovered="{ scale: 1.02 }"
    :tapped="{ scale: 0.98 }"
    :class="[
      'aura-btn',
      variantClasses
    ]"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'primary', // 'primary', 'secondary', 'danger'
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['click']);

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'secondary':
      return 'aura-btn--secondary';
    case 'danger':
      return 'aura-btn--error';
    case 'success':
      return 'aura-btn--success';
    case 'warning':
      return 'aura-btn--warning';
    case 'primary':
    default:
      return 'aura-btn--primary';
  }
});
</script> 