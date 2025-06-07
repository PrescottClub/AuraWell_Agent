<template>
    <div id="globalHeader">
        <a-row :wrap="false">
            <a-col felx="100px">
                <div class="title-bar">
                <img src="../../public/vite.svg" class="logo">
                <div class="title">title</div>
            </div>
            </a-col>
            <a-col flex="auto">
                <a-menu v-model:selectedKeys="current" mode="horizontal" :items="items" />
            </a-col>
            <a-col felx="100px">
                <div class="user-login-status">
                <a-button type="primary" href="/user/login">LoginIn</a-button>
            </div>
            </a-col>
        </a-row>
    </div>
</template>
<script setup>
import { h, ref } from 'vue';
import { MailOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons-vue';
const current = ref(['mail']);
const items = ref([
    {
        key: 'mail',
        icon: () => h(MailOutlined),
        label: 'Navigation One',
        title: 'Navigation One',
    },
    {
        key: 'app',
        icon: () => h(AppstoreOutlined),
        label: 'Navigation Two',
        title: 'Navigation Two',
    },
    {
        key: 'sub1',
        icon: () => h(SettingOutlined),
        label: 'Navigation Three - Submenu',
        title: 'Navigation Three - Submenu',
        children: [
            {
                type: 'group',
                label: 'Item 1',
                children: [
                    {
                        label: 'Option 1',
                        key: 'setting:1',
                    },
                    {
                        label: 'Option 2',
                        key: 'setting:2',
                    },
                ],
            },
            {
                type: 'group',
                label: 'Item 2',
                children: [
                    {
                        label: 'Option 3',
                        key: 'setting:3',
                    },
                    {
                        label: 'Option 4',
                        key: 'setting:4',
                    },
                ],
            },
        ],
    },

]);
</script>

<style scoped>
.title-bar {
    display: flex;
    align-items: center;
}

.title {
    color: black;
    font-size: 18px;
    margin-left: 16px;
}

.logo {
    height: 18px;
}


</style>