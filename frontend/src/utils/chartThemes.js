// src/utils/chartThemes.js
// ECharts 主题定制 - 与 AuraWell 设计系统完美融合

// 使用我们新的 primary 和 health 色系
const lightColors = [
  '#14b8a6', // primary-500 - 青蓝绿主色
  '#10b981', // health-excellent - 生命绿
  '#84cc16', // health-good - 活力绿
  '#f59e0b', // health-normal - 警示黄
  '#f97316', // health-warning - 橙色警告
  '#ef4444', // health-danger - 危险红
  '#8b5cf6', // 紫色补充
  '#06b6d4', // 青色补充
];

const darkColors = [
  '#2dd4bf', // primary-400 - 深色模式下的青蓝绿
  '#34d399', // health-excellent 的深色版本
  '#a3e635', // health-good 的深色版本
  '#fde047', // health-normal 的深色版本
  '#fb923c', // health-warning 的深色版本
  '#fca5a5', // health-danger 的深色版本
  '#a78bfa', // 紫色补充的深色版本
  '#22d3ee', // 青色补充的深色版本
];

export const lightTheme = {
  color: lightColors,
  backgroundColor: 'transparent',
  textStyle: {
    color: '#334155', // gray-700
    fontFamily: 'Inter, SF Pro Display, -apple-system, sans-serif',
    fontSize: 12,
  },
  title: {
    textStyle: {
      color: '#1e293b', // gray-800
      fontWeight: '600',
      fontSize: 16,
    },
  },
  legend: {
    textStyle: {
      color: '#475569', // gray-600
      fontSize: 12,
    },
  },
  tooltip: {
    backgroundColor: '#ffffff',
    borderColor: '#e2e8f0', // gray-200
    borderWidth: 1,
    borderRadius: 8,
    textStyle: {
      color: '#1e293b', // gray-800
      fontSize: 12,
    },
    extraCssText: 'box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);',
  },
  grid: {
    borderColor: '#f1f5f9', // gray-100
  },
  categoryAxis: {
    axisLine: {
      lineStyle: {
        color: '#e2e8f0', // gray-200
      },
    },
    axisTick: {
      lineStyle: {
        color: '#e2e8f0',
      },
    },
    axisLabel: {
      color: '#64748b', // gray-500
    },
    splitLine: {
      lineStyle: {
        color: '#f8fafc', // gray-50
      },
    },
  },
  valueAxis: {
    axisLine: {
      lineStyle: {
        color: '#e2e8f0',
      },
    },
    axisTick: {
      lineStyle: {
        color: '#e2e8f0',
      },
    },
    axisLabel: {
      color: '#64748b',
    },
    splitLine: {
      lineStyle: {
        color: '#f8fafc',
      },
    },
  },
};

export const darkTheme = {
  color: darkColors,
  backgroundColor: 'transparent',
  textStyle: {
    color: '#cbd5e1', // gray-300
    fontFamily: 'Inter, SF Pro Display, -apple-system, sans-serif',
    fontSize: 12,
  },
  title: {
    textStyle: {
      color: '#f1f5f9', // gray-100
      fontWeight: '600',
      fontSize: 16,
    },
  },
  legend: {
    textStyle: {
      color: '#94a3b8', // gray-400
      fontSize: 12,
    },
  },
  tooltip: {
    backgroundColor: '#1e293b', // gray-800
    borderColor: '#475569', // gray-600
    borderWidth: 1,
    borderRadius: 8,
    textStyle: {
      color: '#f1f5f9', // gray-100
      fontSize: 12,
    },
    extraCssText: 'box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.3);',
  },
  grid: {
    borderColor: '#334155', // gray-700
  },
  categoryAxis: {
    axisLine: {
      lineStyle: {
        color: '#475569', // gray-600
      },
    },
    axisTick: {
      lineStyle: {
        color: '#475569',
      },
    },
    axisLabel: {
      color: '#94a3b8', // gray-400
    },
    splitLine: {
      lineStyle: {
        color: '#334155', // gray-700
      },
    },
  },
  valueAxis: {
    axisLine: {
      lineStyle: {
        color: '#475569',
      },
    },
    axisTick: {
      lineStyle: {
        color: '#475569',
      },
    },
    axisLabel: {
      color: '#94a3b8',
    },
    splitLine: {
      lineStyle: {
        color: '#334155',
      },
    },
  },
};

// 导出一个便捷函数来获取当前主题
export function getChartTheme(isDark = false) {
  return isDark ? darkTheme : lightTheme;
}

// 导出颜色数组供其他地方使用
export { lightColors, darkColors };
