<template>
  <div class="relative w-full">
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      :class="[
        'w-full appearance-none transition-all duration-300 ease-in-out',
        'border-2 focus:ring-2 rounded-lg',
        'text-text-primary bg-background-alt',
        selectSizeClass,
        variantClass,
        { 'opacity-50 cursor-not-allowed': disabled }
      ]"
      :disabled="disabled"
      v-bind="$attrs"
    >
      <option v-if="placeholder" value="" disabled selected>{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
      <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
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
  options: {
    type: Array,
    default: () => [], // Should be an array of { value: any, label: string }
  },
  placeholder: {
    type: String,
    default: '',
  },
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
  disabled: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['update:modelValue']);

const selectSizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-2 py-1 text-sm';
    case 'lg':
      return 'px-4 py-3 text-lg';
    case 'base':
    default:
      return 'px-3 py-2 text-base';
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