<template>
  <div class="relative w-full">
    <input
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :class="[
        'w-full transition-all duration-300 ease-in-out',
        'border-2 focus:ring-2',
        'text-text-primary bg-background-alt',
        'placeholder-text-disabled',
        inputSizeClass,
        variantClass,
        { 'opacity-50 cursor-not-allowed': disabled || loading },
        { 'pl-10': !!icon }
      ]"
      :disabled="disabled || loading"
      v-bind="$attrs"
    />
    <div v-if="icon" class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
      <component :is="icon" class="h-5 w-5 text-text-secondary" />
    </div>
    <div v-if="loading" class="absolute inset-y-0 right-0 flex items-center pr-3">
      <svg class="animate-spin h-5 w-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

defineOptions({
  inheritAttrs: false
});

const props = defineProps({
  modelValue: [String, Number],
  size: {
    type: String,
    default: 'base', // sm, base, lg
    validator: (value) => ['sm', 'base', 'lg'].includes(value),
  },
  variant: {
    type: String,
    default: 'default', // default, ghost
    validator: (value) => ['default', 'ghost'].includes(value),
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  icon: {
    type: Object, // Vue component for the icon
    default: null,
  }
});

defineEmits(['update:modelValue']);

const inputSizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-2 py-1 text-sm rounded-md';
    case 'lg':
      return 'px-4 py-3 text-lg rounded-lg';
    case 'base':
    default:
      return 'px-3 py-2 text-base rounded-lg';
  }
});

const variantClass = computed(() => {
    switch(props.variant) {
        case 'ghost':
            return 'border-transparent bg-transparent focus:border-primary focus:ring-primary/20';
        case 'default':
        default:
            return 'border-border focus:border-primary focus:ring-primary/20';
    }
});
</script> 