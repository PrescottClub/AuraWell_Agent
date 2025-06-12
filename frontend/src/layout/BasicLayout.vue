<template>
    <div id="basicLayout">
        <a-layout class="layout">
            <a-layout-header class="header">
                <GlobalHeader />
            </a-layout-header>
            <a-layout-content class="content">
                <router-view />
            </a-layout-content>
            <a-layout-footer class="footer">
                Ant Design ©2018 Created by Ant UED
            </a-layout-footer>
        </a-layout>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { RouterView } from 'vue-router';
import GlobalHeader from '../components/GlobalHeader.vue';
</script>
<style scoped>
#basicLayout .footer{
    background: #efefef;
    text-align: center;
    position:fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 16px;
}

#basicLayout .content {
    padding: 0;
    margin-bottom: 60px; /* 为固定footer留出空间 */
    border-color: #fff;
    background-color: linear-gradient(to right,#fefefe,#fff);
    min-height: calc(100vh - 120px); /* 减去header和footer的高度 */
}

#basicLayout .header{
    background: white;
    margin-bottom: 0;
    color: unset;
    padding: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 响应式设计 */
@media (min-width: 1200px) {
    #basicLayout .content {
        padding: 0 50px;
    }

    #basicLayout .header {
        padding: 0 50px;
    }
}

@media (max-width: 768px) {
    #basicLayout .content {
        padding: 0 16px;
        margin-bottom: 80px;
    }

    #basicLayout .header {
        padding: 0 16px;
    }

    #basicLayout .footer {
        padding: 12px 16px;
    }
}


</style>