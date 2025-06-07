<template>
    <div id="basicLayout">
        <a-layout class="layout">
            <a-layout-header class="header">
                <GlobalHeader />
            </a-layout-header>
            <a-layout-content class="content">
                
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
    padding: 20px;
    margin-bottom: 20px;
    background-color: linear-gradient(to right,#fefefe,#fff);
}

#basicLayout .header{
    background: white;
    margin-bottom: 16px;
    color: unset;
    padding-inline: 20px;
}
</style>