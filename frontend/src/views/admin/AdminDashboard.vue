<template>
    <div class="dashboard-container p-6 bg-background-alt min-h-screen">
        <div class="chart-header flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-text-primary">数据统计</h2>
            <a-select
                v-model:value="selectedChartType"
                style="width: 200px"
                @change="handleChartTypeChange"
                size="large"
            >
                <a-select-option value="line">折线图</a-select-option>
                <a-select-option value="bar">柱状图</a-select-option>
                <a-select-option value="pie">饼图</a-select-option>
            </a-select>
        </div>
        <div class="chart-container bg-background p-6 rounded-2xl shadow-soft-lg flex-1 flex flex-col">
            <v-chart class="chart flex-1 w-full min-h-0" :option="chartOption" autoresize />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart, PieChart } from 'echarts/charts';
import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { useTheme } from '../../composables/useTheme.js';
import { getChartTheme } from '../../utils/chartThemes.js';

// 注册必要的组件
use([
    CanvasRenderer,
    LineChart,
    BarChart,
    PieChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent
]);

// 主题相关
const { isDark } = useTheme();

const selectedChartType = ref('line');
const chartOption = ref({});

// 模拟数据
const mockData = {
    line: {
        xAxis: {
            type: 'category',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        yAxis: {
            type: 'value'
        },
        series: [{
            data: [150, 230, 224, 218, 135, 147, 260],
            type: 'line',
            smooth: true
        }]
    },
    bar: {
        xAxis: {
            type: 'category',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        yAxis: {
            type: 'value'
        },
        series: [{
            data: [120, 200, 150, 80, 70, 110, 130],
            type: 'bar'
        }]
    },
    pie: {
        tooltip: {
            trigger: 'item'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [{
            type: 'pie',
            radius: '50%',
            data: [
                { value: 1048, name: '搜索引擎' },
                { value: 735, name: '直接访问' },
                { value: 580, name: '邮件营销' },
                { value: 484, name: '联盟广告' },
                { value: 300, name: '视频广告' }
            ],
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    }
};

const handleChartTypeChange = (value) => {
    const baseOption = mockData[value];
    const currentTheme = getChartTheme(isDark.value);

    // 合并主题配置
    chartOption.value = {
        ...currentTheme,
        ...baseOption,
        // 确保series使用主题颜色
        series: baseOption.series.map((serie, index) => ({
            ...serie,
            itemStyle: {
                color: currentTheme.color[index % currentTheme.color.length]
            }
        }))
    };
};

// 监听主题变化
watch(isDark, () => {
    // 主题变化时重新应用当前图表类型
    handleChartTypeChange(selectedChartType.value);
});

onMounted(() => {
    // 初始化显示折线图
    handleChartTypeChange('line');
});
</script>

<style scoped>
/* Keeping scoped styles for v-chart specifics if any, but layout is now handled by Tailwind */
</style> 