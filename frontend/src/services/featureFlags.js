import { ref, readonly } from 'vue';

// In a real scenario, this would come from a service like LaunchDarkly, Optimizely, etc.
// For this example, we can simulate it with a simple object or by reading URL query params.
const flags = ref({});

const initializeFlags = () => {
  const mockFlags = {
    'new-family-challenges-page': true,
    'show-admin-debug-tools': false,
  };

  // Allow overriding via URL for testing: ?ff_new-family-challenges-page=false
  const urlParams = new URLSearchParams(window.location.search);
  urlParams.forEach((value, key) => {
    if (key.startsWith('ff_')) {
      const flagName = key.substring(3);
      mockFlags[flagName] = value === 'true';
    }
  });

  flags.value = mockFlags;
};

// Initialize on load
initializeFlags();

export function useFeatureFlags() {
  const getFlag = key => {
    return readonly(flags).value[key] || false;
  };

  return {
    getFlag,
    allFlags: readonly(flags),
  };
}
