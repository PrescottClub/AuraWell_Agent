<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">系统设置</h1>
    <a-form
      :model="formState"
      :label-col="{ span: 4 }"
      :wrapper-col="{ span: 16 }"
    >
      <a-form-item label="系统名称">
        <a-input v-model:value="formState.systemName" />
      </a-form-item>
      <a-form-item label="系统描述">
        <a-textarea v-model:value="formState.description" :rows="4" />
      </a-form-item>
      <a-form-item label="维护模式">
        <a-switch v-model:checked="formState.maintenance" />
      </a-form-item>
      <a-form-item :wrapper-col="{ offset: 4 }">
        <a-button type="primary" @click="handleSave">保存设置</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { message } from 'ant-design-vue';

const formState = reactive({
  systemName: 'AuraWell',
  description: '这是一个示例系统描述',
  maintenance: false,
});

const handleSave = () => {
  message.success('设置已保存');
  console.log('保存设置:', formState);
};
</script> 