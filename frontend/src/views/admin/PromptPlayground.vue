<template>
  <div class="prompt-playground">
    <h1>Prompt Playground</h1>
    <a-row :gutter="24">
      <a-col :span="12">
        <h2>Configuration</h2>
        <a-form layout="vertical">
          <a-form-item label="Model">
            <a-select v-model:value="config.model">
              <a-select-option value="deepseek-r1">deepseek-r1</a-select-option>
              <a-select-option value="gpt-4">gpt-4</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="System Prompt">
            <a-textarea v-model:value="config.system_prompt" :rows="6" />
          </a-form-item>
          <a-form-item label="Temperature">
            <a-slider v-model:value="config.temperature" :min="0" :max="2" :step="0.1" />
          </a-form-item>
          <a-form-item label="Max Tokens">
            <a-input-number v-model:value="config.max_tokens" />
          </a-form-item>
        </a-form>
      </a-col>
      <a-col :span="12">
        <h2>Test</h2>
        <a-form-item label="User Prompt">
          <a-textarea v-model:value="userPrompt" :rows="10" />
        </a-form-item>
        <a-button type="primary" @click="runTest" :loading="isLoading">
          Run Test
        </a-button>
        <div class="result-panel">
          <h3>Result</h3>
          <div v-if="isLoading" class="loading-state">
            <a-spin />
          </div>
          <pre v-else>{{ result }}</pre>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { message } from 'ant-design-vue';

const config = reactive({
  model: 'deepseek-r1',
  system_prompt: 'You are a helpful assistant.',
  temperature: 0.7,
  max_tokens: 1024,
});

const userPrompt = ref('');
const result = ref('');
const isLoading = ref(false);

const runTest = async () => {
  if (!userPrompt.value) {
    message.warning('Please enter a user prompt.');
    return;
  }
  isLoading.value = true;
  result.value = '';
  try {
    //
    // This is where you would call your API
    // e.g., const response = await api.testPrompt({ ...config, prompt: userPrompt.value });
    // result.value = response.data;
    //
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
    result.value = `Test Result for: "${userPrompt.value}" with model ${config.model}. \n\n(This is a simulated response.)`;
  } catch (error) {
    message.error('Failed to run test.');
    result.value = 'An error occurred.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.prompt-playground {
  padding: 24px;
  background: #fff;
  border-radius: 8px;
}
.result-panel {
  margin-top: 24px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
  min-height: 200px;
}
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 