<template>
  <div v-if="visible" class="absolute bottom-full mb-2 w-full bg-white rounded-lg shadow-lg border border-border max-h-60 overflow-y-auto">
    <ul>
      <li
        v-for="(command, index) in filteredCommands"
        :key="command.name"
        :class="[
          'p-3 cursor-pointer hover:bg-secondary',
          { 'bg-secondary': index === selectedIndex }
        ]"
        @click="selectCommand(command)"
      >
        <div class="font-semibold text-text-primary">{{ command.name }}</div>
        <div class="text-sm text-text-secondary">{{ command.description }}</div>
      </li>
      <li v-if="filteredCommands.length === 0" class="p-3 text-center text-text-secondary">
        无匹配命令
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  visible: Boolean,
  commands: {
    type: Array,
    default: () => [], // [{ name: '/rag', description: '...' }]
  },
  filter: String,
});

const emit = defineEmits(['select']);

const selectedIndex = ref(0);

const filteredCommands = computed(() => {
  if (!props.filter) return props.commands;
  return props.commands.filter(cmd => cmd.name.toLowerCase().startsWith(props.filter.toLowerCase()));
});

watch(filteredCommands, () => {
  selectedIndex.value = 0;
});

const selectCommand = (command) => {
  emit('select', command.name);
};

// Expose methods to parent
const onArrowUp = () => {
  selectedIndex.value = (selectedIndex.value - 1 + filteredCommands.value.length) % filteredCommands.value.length;
};

const onArrowDown = () => {
  selectedIndex.value = (selectedIndex.value + 1) % filteredCommands.value.length;
};

const onEnter = () => {
  if (filteredCommands.value[selectedIndex.value]) {
    selectCommand(filteredCommands.value[selectedIndex.value]);
  }
};

defineExpose({ onArrowUp, onArrowDown, onEnter });
</script> 