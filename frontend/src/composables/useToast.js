import { ref, readonly } from 'vue';

const toasts = ref([]);
let idCounter = 0;

/**
 * A composable for managing a global toast notification system.
 */
export function useToast() {
  /**
   * Shows a new toast message.
   * @param {string} message The message to display.
   * @param {Object} options Optional settings for the toast.
   * @param {string} options.type Type of the toast ('success', 'error', 'warning', 'info').
   * @param {number} options.duration Duration in ms. 0 for permanent.
   */
  const showToast = (message, options = {}) => {
    const id = idCounter++;
    toasts.value.push({
      id,
      message,
      type: options.type || 'info',
      duration: options.duration === 0 ? 0 : (options.duration || 5000),
    });
  };

  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  };

  return {
    toasts: readonly(toasts),
    showToast,
    removeToast,
  };
} 