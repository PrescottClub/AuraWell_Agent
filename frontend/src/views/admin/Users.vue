<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">用户管理</h1>
    <a-table :columns="columns" :data-source="data" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除这个用户吗？"
              @confirm="handleDelete(record)"
            >
              <a class="text-red-500">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const loading = ref(false);
const columns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '注册时间',
    dataIndex: 'registerTime',
    key: 'registerTime',
  },
  {
    title: '操作',
    key: 'action',
  },
];

const data = ref([
  {
    key: '1',
    username: 'John Brown',
    email: 'john@example.com',
    registerTime: '2024-01-01',
  },
  {
    key: '2',
    username: 'Jim Green',
    email: 'jim@example.com',
    registerTime: '2024-01-02',
  },
]);

const handleEdit = (record) => {
  console.log('编辑用户:', record);
};

const handleDelete = (record) => {
  console.log('删除用户:', record);
};
</script> 