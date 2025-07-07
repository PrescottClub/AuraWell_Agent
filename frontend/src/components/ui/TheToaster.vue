<template>
  <div aria-live="assertive" class="fixed inset-0 z-[100] flex items-end px-4 py-6 pointer-events-none sm:p-6 sm:items-start">
    <div class="w-full flex flex-col items-center space-y-4 sm:items-end">
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :id="toast.id"
        :message="toast.message"
        :type="toast.type"
        :duration="toast.duration"
        @close="removeToast"
      />
    </div>
  </div>
</template>

<script setup>
import Toast from './Toast.vue';
import { useToast } from '../../composables/useToast';

const { toasts, removeToast } = useToast();
</script> 