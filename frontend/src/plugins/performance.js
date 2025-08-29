/**
 * 性能监控插件
 * 提供全局性能监控和优化功能
 */

import { useMemoryOptimization } from '../composables/useMemoryOptimization.js';
import { useCacheOptimization } from '../composables/useCacheOptimization.js';

class PerformanceManager {
  constructor() {
    this.memoryOptimizer = null;
    this.cacheOptimizer = null;
    this.performanceObserver = null;
    this.metrics = {
      navigation: {},
      resources: [],
      vitals: {},
      custom: {},
    };
    this.isInitialized = false;
  }

  /**
   * 初始化性能监控
   */
  init() {
    if (this.isInitialized) return;

    this.memoryOptimizer = useMemoryOptimization();
    this.cacheOptimizer = useCacheOptimization();

    this.setupPerformanceObserver();
    this.setupWebVitals();
    this.setupResourceMonitoring();
    this.setupNavigationTiming();
    this.startMemoryMonitoring();
    this.startCacheCleanup();

    this.isInitialized = true;
    console.log('性能监控已启动');
  }

  /**
   * 设置性能观察器
   */
  setupPerformanceObserver() {
    if (!('PerformanceObserver' in window)) return;

    try {
      // 监控长任务
      const longTaskObserver = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) {
            console.warn('检测到长任务:', {
              duration: entry.duration,
              startTime: entry.startTime,
              name: entry.name,
            });

            this.metrics.custom.longTasks = this.metrics.custom.longTasks || [];
            this.metrics.custom.longTasks.push({
              duration: entry.duration,
              startTime: entry.startTime,
              timestamp: Date.now(),
            });
          }
        }
      });

      longTaskObserver.observe({ entryTypes: ['longtask'] });

      // 监控布局偏移
      const layoutShiftObserver = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          if (entry.value > 0.1) {
            console.warn('检测到布局偏移:', {
              value: entry.value,
              startTime: entry.startTime,
            });
          }
        }
      });

      layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
    } catch (error) {
      console.warn('性能观察器设置失败:', error);
    }
  }

  /**
   * 设置Web Vitals监控
   */
  setupWebVitals() {
    // 监控LCP (Largest Contentful Paint)
    this.observeVital('largest-contentful-paint', entry => {
      this.metrics.vitals.lcp = entry.startTime;
      if (entry.startTime > 2500) {
        console.warn('LCP过慢:', entry.startTime + 'ms');
      }
    });

    // 监控FID (First Input Delay)
    this.observeVital('first-input', entry => {
      this.metrics.vitals.fid = entry.processingStart - entry.startTime;
      if (entry.processingStart - entry.startTime > 100) {
        console.warn(
          'FID过慢:',
          entry.processingStart - entry.startTime + 'ms'
        );
      }
    });

    // 监控CLS (Cumulative Layout Shift)
    let clsValue = 0;
    this.observeVital('layout-shift', entry => {
      if (!entry.hadRecentInput) {
        clsValue += entry.value;
        this.metrics.vitals.cls = clsValue;
        if (clsValue > 0.1) {
          console.warn('CLS过高:', clsValue);
        }
      }
    });
  }

  /**
   * 观察特定的性能指标
   */
  observeVital(type, callback) {
    try {
      const observer = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          callback(entry);
        }
      });
      observer.observe({ entryTypes: [type] });
    } catch (error) {
      console.warn(`无法观察 ${type}:`, error);
    }
  }

  /**
   * 设置资源监控
   */
  setupResourceMonitoring() {
    // 监控资源加载
    const resourceObserver = new PerformanceObserver(list => {
      for (const entry of list.getEntries()) {
        const resourceInfo = {
          name: entry.name,
          type: entry.initiatorType,
          size: entry.transferSize,
          duration: entry.duration,
          startTime: entry.startTime,
        };

        this.metrics.resources.push(resourceInfo);

        // 检查慢资源
        if (entry.duration > 1000) {
          console.warn('慢资源加载:', resourceInfo);
        }

        // 检查大资源
        if (entry.transferSize > 1024 * 1024) {
          // 1MB
          console.warn('大资源文件:', resourceInfo);
        }
      }
    });

    resourceObserver.observe({ entryTypes: ['resource'] });
  }

  /**
   * 设置导航时序监控
   */
  setupNavigationTiming() {
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
          this.metrics.navigation = {
            dns: navigation.domainLookupEnd - navigation.domainLookupStart,
            tcp: navigation.connectEnd - navigation.connectStart,
            request: navigation.responseStart - navigation.requestStart,
            response: navigation.responseEnd - navigation.responseStart,
            dom:
              navigation.domContentLoadedEventEnd -
              navigation.domContentLoadedEventStart,
            load: navigation.loadEventEnd - navigation.loadEventStart,
            total: navigation.loadEventEnd - navigation.navigationStart,
          };

          console.log('页面加载时序:', this.metrics.navigation);
        }
      }, 0);
    });
  }

  /**
   * 启动内存监控
   */
  startMemoryMonitoring() {
    if (this.memoryOptimizer) {
      this.memoryOptimizer.startMemoryMonitoring(10000); // 10秒检查一次
    }
  }

  /**
   * 启动缓存清理
   */
  startCacheCleanup() {
    if (this.cacheOptimizer) {
      this.cacheOptimizer.startAutoCleanup();
    }
  }

  /**
   * 记录自定义性能指标
   */
  mark(name, detail = {}) {
    performance.mark(name);
    this.metrics.custom[name] = {
      timestamp: Date.now(),
      detail,
    };
  }

  /**
   * 测量两个标记之间的时间
   */
  measure(name, startMark, endMark) {
    try {
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name, 'measure')[0];
      this.metrics.custom[name] = {
        duration: measure.duration,
        startTime: measure.startTime,
      };
      return measure.duration;
    } catch (error) {
      console.warn('性能测量失败:', error);
      return null;
    }
  }

  /**
   * 获取性能报告
   */
  getPerformanceReport() {
    return {
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      metrics: { ...this.metrics },
      memory: this.memoryOptimizer?.getMemoryInfo(),
      cache: this.cacheOptimizer?.getCacheStats(),
    };
  }

  /**
   * 发送性能数据到服务器
   */
  async sendPerformanceData() {
    try {
      const report = this.getPerformanceReport();

      // 使用sendBeacon API发送数据（不阻塞页面卸载）
      if (navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(report)], {
          type: 'application/json',
        });
        navigator.sendBeacon('/api/v1/performance', blob);
      } else {
        // 降级到fetch
        fetch('/api/v1/performance', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(report),
          keepalive: true,
        }).catch(error => {
          console.warn('性能数据发送失败:', error);
        });
      }
    } catch (error) {
      console.warn('性能数据发送失败:', error);
    }
  }

  /**
   * 优化建议
   */
  getOptimizationSuggestions() {
    const suggestions = [];

    // 检查LCP
    if (this.metrics.vitals.lcp > 2500) {
      suggestions.push({
        type: 'LCP',
        message: 'Largest Contentful Paint过慢，建议优化关键资源加载',
        priority: 'high',
      });
    }

    // 检查FID
    if (this.metrics.vitals.fid > 100) {
      suggestions.push({
        type: 'FID',
        message: 'First Input Delay过长，建议减少主线程阻塞',
        priority: 'high',
      });
    }

    // 检查CLS
    if (this.metrics.vitals.cls > 0.1) {
      suggestions.push({
        type: 'CLS',
        message: 'Cumulative Layout Shift过高，建议固定元素尺寸',
        priority: 'medium',
      });
    }

    // 检查内存使用
    const memoryInfo = this.memoryOptimizer?.getMemoryInfo();
    if (memoryInfo && memoryInfo.usage > 80) {
      suggestions.push({
        type: 'Memory',
        message: '内存使用率过高，建议清理不必要的对象',
        priority: 'high',
      });
    }

    return suggestions;
  }

  /**
   * 销毁监控
   */
  destroy() {
    if (this.memoryOptimizer) {
      this.memoryOptimizer.stopMemoryMonitoring();
    }

    this.isInitialized = false;
  }
}

// 创建全局实例
const performanceManager = new PerformanceManager();

// Vue插件
export default {
  install(app) {
    // 在开发环境中启用详细监控
    if (import.meta.env.DEV) {
      performanceManager.init();
    }

    // 提供全局访问
    app.config.globalProperties.$performance = performanceManager;
    app.provide('performance', performanceManager);

    // 页面卸载时发送数据
    window.addEventListener('beforeunload', () => {
      performanceManager.sendPerformanceData();
    });

    // 页面隐藏时发送数据
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        performanceManager.sendPerformanceData();
      }
    });
  },
};

export { performanceManager };
