<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60"
        @click.self="closeModal"
      >
        <div :class="['relative mx-4 my-8 bg-background rounded-2xl shadow-xl transition-transform duration-300', modalSizeClass]">
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-border">
            <slot name="header">
              <h3 class="text-xl font-semibold text-text-primary">{{ title }}</h3>
            </slot>
            <button @click="closeModal" class="p-1 rounded-full text-text-secondary hover:bg-background-alt">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>

          <!-- Body -->
          <div class="p-6 overflow-y-auto">
            <slot></slot>
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="flex items-center justify-end p-4 border-t border-border">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: 'Modal Title',
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg, xl
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value),
  },
  persistent: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue']);

const closeModal = () => {
  if (!props.persistent) {
    emit('update:modelValue', false);
  }
};

const modalSizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'max-w-sm';
    case 'md': return 'max-w-md';
    case 'lg': return 'max-w-lg';
    case 'xl': return 'max-w-xl';
    default: return 'max-w-md';
  }
});

watch(() => props.modelValue, (show) => {
  if (show) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-active .modal-content,
.modal-fade-leave-active .modal-content {
  transition: transform 0.3s ease;
}
.modal-fade-enter-from .modal-content,
.modal-fade-leave-to .modal-content {
  transform: scale(0.95);
}
</style> 