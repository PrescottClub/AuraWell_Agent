<template>
  <button
    v-motion
    :initial="{ scale: 1 }"
    :hovered="{ scale: 1.05 }"
    :tapped="{ scale: 0.95 }"
    :class="[
      'px-6 py-3 font-semibold rounded-lg shadow-soft-lg transition-all duration-300 ease-in-out',
      'focus:outline-none focus:ring-4 focus:ring-primary/30',
      'disabled:opacity-50 disabled:cursor-not-allowed',
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
      return 'bg-secondary text-text-primary hover:bg-secondary-hover';
    case 'danger':
      return 'bg-error text-white hover:bg-opacity-90';
    case 'primary':
    default:
      // Apply gradient background using the new theme colors
      return 'text-white bg-gradient-to-r from-gemini-blue to-gemini-purple hover:opacity-90';
  }
});
</script> 