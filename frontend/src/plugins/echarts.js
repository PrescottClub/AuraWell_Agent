/**
 * ECharts 按需导入配置
 * 只导入项目中实际使用的图表类型和组件，减少Bundle大小
 */

import { use } from 'echarts/core';

// 渲染器
import { CanvasRenderer } from 'echarts/renderers';

// 图表类型
import {
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
  HeatmapChart,
  ScatterChart,
} from 'echarts/charts';

// 组件
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  BrushComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent,
  MarkAreaComponent,
  CalendarComponent,
} from 'echarts/components';

// 注册必要的组件
use([
  // 渲染器
  CanvasRenderer,

  // 图表类型
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
  HeatmapChart,
  ScatterChart,

  // 组件
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  BrushComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent,
  MarkAreaComponent,
  CalendarComponent,
]);

export default use;
