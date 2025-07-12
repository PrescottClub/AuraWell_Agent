<template>
  <transition
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
    enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
    leave-active-class="transition ease-in duration-100"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="visible" :class="['max-w-sm w-full bg-background shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden', typeClass.border]">
      <div class="p-4">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <component :is="typeClass.icon" :class="['h-6 w-6', typeClass.text]" aria-hidden="true" />
          </div>
          <div class="ml-3 w-0 flex-1 pt-0.5">
            <p class="text-sm font-medium text-text-primary">{{ message }}</p>
          </div>
          <div class="ml-4 flex-shrink-0 flex">
            <button @click="close" class="inline-flex text-text-secondary hover:text-text-primary">
              <span class="sr-only">Close</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  id: { type: [String, Number], required: true },
  message: { type: String, required: true },
  type: {
    type: String,
    default: 'info', // 'success', 'error', 'warning', 'info'
  },
  duration: { type: Number, default: 5000 },
});

const emit = defineEmits(['close']);

const visible = ref(true);

const typeClass = computed(() => {
  switch (props.type) {
    case 'success':
      return { icon: CheckCircleIcon, text: 'text-success', border: 'border-success' };
    case 'error':
      return { icon: XCircleIcon, text: 'text-error', border: 'border-error' };
    case 'warning':
      return { icon: ExclamationTriangleIcon, text: 'text-warning', border: 'border-warning' };
    case 'info':
    default:
      return { icon: InformationCircleIcon, text: 'text-primary', border: 'border-primary' };
  }
});

const close = () => {
  visible.value = false;
  setTimeout(() => emit('close', props.id), 300); // allow for transition
};

onMounted(() => {
  if (props.duration > 0) {
    setTimeout(close, props.duration);
  }
});
</script> 