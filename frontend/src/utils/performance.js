/**
 * 性能优化工具函数
 * 提供数据分页、抽样、懒加载等性能优化功能
 */

// 数据分页处理
export class DataPagination {
  constructor(data, pageSize = 50) {
    this.data = data || [];
    this.pageSize = pageSize;
    this.currentPage = 1;
    this.totalPages = Math.ceil(this.data.length / pageSize);
  }

  // 获取当前页数据
  getCurrentPageData() {
    const startIndex = (this.currentPage - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    return this.data.slice(startIndex, endIndex);
  }

  // 获取指定页数据
  getPageData(page) {
    this.currentPage = Math.max(1, Math.min(page, this.totalPages));
    return this.getCurrentPageData();
  }

  // 获取分页信息
  getPaginationInfo() {
    return {
      currentPage: this.currentPage,
      totalPages: this.totalPages,
      totalItems: this.data.length,
      pageSize: this.pageSize,
      hasNext: this.currentPage < this.totalPages,
      hasPrev: this.currentPage > 1,
    };
  }

  // 更新数据
  updateData(newData) {
    this.data = newData || [];
    this.totalPages = Math.ceil(this.data.length / this.pageSize);
    this.currentPage = Math.min(this.currentPage, this.totalPages || 1);
  }
}

// 数据抽样处理
export class DataSampling {
  // 时间序列数据抽样
  static timeSeriesSampling(data, maxPoints = 100) {
    if (!data || data.length <= maxPoints) {
      return data;
    }

    const step = Math.ceil(data.length / maxPoints);
    const sampled = [];

    for (let i = 0; i < data.length; i += step) {
      sampled.push(data[i]);
    }

    // 确保包含最后一个数据点
    if (sampled[sampled.length - 1] !== data[data.length - 1]) {
      sampled.push(data[data.length - 1]);
    }

    return sampled;
  }

  // 智能抽样（保留关键点）
  static intelligentSampling(data, maxPoints = 100, keyField = 'value') {
    if (!data || data.length <= maxPoints) {
      return data;
    }

    // 计算数据的变化率
    const changes = [];
    for (let i = 1; i < data.length; i++) {
      const change = Math.abs(data[i][keyField] - data[i - 1][keyField]);
      changes.push({ index: i, change });
    }

    // 按变化率排序，保留变化较大的点
    changes.sort((a, b) => b.change - a.change);

    const keyIndices = new Set([0, data.length - 1]); // 始终保留首尾
    const keepCount = Math.min(maxPoints - 2, changes.length);

    for (let i = 0; i < keepCount; i++) {
      keyIndices.add(changes[i].index);
    }

    // 按原始顺序返回数据
    const indices = Array.from(keyIndices).sort((a, b) => a - b);
    return indices.map(i => data[i]);
  }

  // 均匀抽样
  static uniformSampling(data, maxPoints = 100) {
    if (!data || data.length <= maxPoints) {
      return data;
    }

    const ratio = data.length / maxPoints;
    const sampled = [];

    for (let i = 0; i < maxPoints; i++) {
      const index = Math.floor(i * ratio);
      sampled.push(data[index]);
    }

    return sampled;
  }
}

// 懒加载管理器
export class LazyLoadManager {
  constructor() {
    this.observers = new Map();
    this.loadedItems = new Set();
  }

  // 创建懒加载观察器
  createObserver(callback, options = {}) {
    const defaultOptions = {
      root: null,
      rootMargin: '50px',
      threshold: 0.1,
    };

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.dataset.lazyId;
            if (!this.loadedItems.has(id)) {
              this.loadedItems.add(id);
              callback(entry.target, id);
            }
          }
        });
      },
      { ...defaultOptions, ...options }
    );

    return observer;
  }

  // 注册懒加载元素
  observe(element, id, observer) {
    element.dataset.lazyId = id;
    observer.observe(element);

    if (!this.observers.has(observer)) {
      this.observers.set(observer, new Set());
    }
    this.observers.get(observer).add(element);
  }

  // 取消观察
  unobserve(element, observer) {
    observer.unobserve(element);
    const elements = this.observers.get(observer);
    if (elements) {
      elements.delete(element);
    }
  }

  // 清理所有观察器
  cleanup() {
    this.observers.forEach((elements, observer) => {
      elements.forEach(element => observer.unobserve(element));
      observer.disconnect();
    });
    this.observers.clear();
    this.loadedItems.clear();
  }
}

// 防抖函数
export function debounce(func, wait, immediate = false) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(this, args);
  };
}

// 节流函数
export function throttle(func, limit) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// 虚拟滚动处理
export class VirtualScroll {
  constructor(options = {}) {
    this.itemHeight = options.itemHeight || 50;
    this.containerHeight = options.containerHeight || 400;
    this.buffer = options.buffer || 5;
    this.data = options.data || [];

    this.visibleCount = Math.ceil(this.containerHeight / this.itemHeight);
    this.totalHeight = this.data.length * this.itemHeight;

    this.startIndex = 0;
    this.endIndex = Math.min(this.visibleCount + this.buffer, this.data.length);
  }

  // 更新滚动位置
  updateScrollTop(scrollTop) {
    const newStartIndex = Math.floor(scrollTop / this.itemHeight);
    const newEndIndex = Math.min(
      newStartIndex + this.visibleCount + this.buffer,
      this.data.length
    );

    if (newStartIndex !== this.startIndex || newEndIndex !== this.endIndex) {
      this.startIndex = Math.max(0, newStartIndex - this.buffer);
      this.endIndex = newEndIndex;
      return true; // 需要更新
    }

    return false; // 不需要更新
  }

  // 获取可见数据
  getVisibleData() {
    return this.data.slice(this.startIndex, this.endIndex);
  }

  // 获取偏移量
  getOffset() {
    return this.startIndex * this.itemHeight;
  }

  // 更新数据
  updateData(newData) {
    this.data = newData;
    this.totalHeight = this.data.length * this.itemHeight;
    this.endIndex = Math.min(this.visibleCount + this.buffer, this.data.length);
  }

  // 获取容器样式
  getContainerStyle() {
    return {
      height: `${this.containerHeight}px`,
      overflow: 'auto',
    };
  }

  // 获取内容样式
  getContentStyle() {
    return {
      height: `${this.totalHeight}px`,
      position: 'relative',
    };
  }

  // 获取可见区域样式
  getVisibleStyle() {
    return {
      transform: `translateY(${this.getOffset()}px)`,
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
    };
  }
}

// 内存管理工具
export class MemoryManager {
  constructor() {
    this.cache = new Map();
    this.maxCacheSize = 100;
    this.accessOrder = [];
  }

  // 设置缓存
  set(key, value) {
    if (this.cache.has(key)) {
      // 更新访问顺序
      const index = this.accessOrder.indexOf(key);
      this.accessOrder.splice(index, 1);
      this.accessOrder.push(key);
    } else {
      // 检查缓存大小
      if (this.cache.size >= this.maxCacheSize) {
        const oldestKey = this.accessOrder.shift();
        this.cache.delete(oldestKey);
      }

      this.cache.set(key, value);
      this.accessOrder.push(key);
    }
  }

  // 获取缓存
  get(key) {
    if (this.cache.has(key)) {
      // 更新访问顺序
      const index = this.accessOrder.indexOf(key);
      this.accessOrder.splice(index, 1);
      this.accessOrder.push(key);

      return this.cache.get(key);
    }
    return null;
  }

  // 清理缓存
  clear() {
    this.cache.clear();
    this.accessOrder = [];
  }

  // 获取缓存统计
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      keys: Array.from(this.cache.keys()),
    };
  }
}

// 性能监控
export class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = [];
  }

  // 开始计时
  startTiming(name) {
    this.metrics.set(name, {
      startTime: performance.now(),
      endTime: null,
      duration: null,
    });
  }

  // 结束计时
  endTiming(name) {
    const metric = this.metrics.get(name);
    if (metric) {
      metric.endTime = performance.now();
      metric.duration = metric.endTime - metric.startTime;

      // 通知观察者
      this.notifyObservers(name, metric);
    }
  }

  // 添加观察者
  addObserver(callback) {
    this.observers.push(callback);
  }

  // 通知观察者
  notifyObservers(name, metric) {
    this.observers.forEach(callback => {
      try {
        callback(name, metric);
      } catch (error) {
        console.error('Performance observer error:', error);
      }
    });
  }

  // 获取所有指标
  getAllMetrics() {
    const result = {};
    this.metrics.forEach((value, key) => {
      result[key] = { ...value };
    });
    return result;
  }

  // 清理指标
  clear() {
    this.metrics.clear();
  }
}

// 创建全局实例
export const globalLazyLoader = new LazyLoadManager();
export const globalMemoryManager = new MemoryManager();
export const globalPerformanceMonitor = new PerformanceMonitor();

// 工具函数
export const performanceUtils = {
  // 批量处理
  batchProcess: (items, batchSize, processor, delay = 0) => {
    return new Promise(resolve => {
      const results = [];
      let index = 0;

      const processBatch = () => {
        const batch = items.slice(index, index + batchSize);
        const batchResults = batch.map(processor);
        results.push(...batchResults);

        index += batchSize;

        if (index < items.length) {
          if (delay > 0) {
            setTimeout(processBatch, delay);
          } else {
            requestAnimationFrame(processBatch);
          }
        } else {
          resolve(results);
        }
      };

      processBatch();
    });
  },

  // 检查设备性能
  getDevicePerformance: () => {
    const memory = navigator.deviceMemory || 4;
    const cores = navigator.hardwareConcurrency || 4;
    const connection = navigator.connection;

    let score = 0;

    // 内存评分
    if (memory >= 8) score += 3;
    else if (memory >= 4) score += 2;
    else score += 1;

    // CPU评分
    if (cores >= 8) score += 3;
    else if (cores >= 4) score += 2;
    else score += 1;

    // 网络评分
    if (connection) {
      if (connection.effectiveType === '4g') score += 2;
      else if (connection.effectiveType === '3g') score += 1;
    }

    return {
      memory,
      cores,
      connection: connection?.effectiveType || 'unknown',
      score,
      level: score >= 7 ? 'high' : score >= 4 ? 'medium' : 'low',
    };
  },
};

export default {
  DataPagination,
  DataSampling,
  LazyLoadManager,
  VirtualScroll,
  MemoryManager,
  PerformanceMonitor,
  debounce,
  throttle,
  performanceUtils,
};
