/**
 * 缓存优化组合式函数
 * 提供智能缓存管理和优化策略
 */

import { ref, computed } from 'vue'

export function useCacheOptimization() {
  const cacheStore = ref(new Map())
  const cacheStats = ref({
    hits: 0,
    misses: 0,
    size: 0,
    maxSize: 100
  })

  /**
   * 缓存配置
   */
  const cacheConfig = ref({
    maxSize: 100,
    defaultTTL: 5 * 60 * 1000, // 5分钟
    cleanupInterval: 60 * 1000, // 1分钟清理一次
    compressionThreshold: 1024 // 1KB以上启用压缩
  })

  /**
   * 缓存命中率
   */
  const hitRate = computed(() => {
    const total = cacheStats.value.hits + cacheStats.value.misses
    return total > 0 ? (cacheStats.value.hits / total * 100).toFixed(2) : 0
  })

  /**
   * 生成缓存键
   */
  const generateCacheKey = (prefix, params = {}) => {
    const paramStr = JSON.stringify(params, Object.keys(params).sort())
    return `${prefix}:${btoa(paramStr).replace(/[+/=]/g, '')}`
  }

  /**
   * 压缩数据
   */
  const compressData = (data) => {
    try {
      const jsonStr = JSON.stringify(data)
      if (jsonStr.length < cacheConfig.value.compressionThreshold) {
        return { compressed: false, data: jsonStr }
      }
      
      // 简单的LZ压缩算法
      const compressed = lzCompress(jsonStr)
      return { compressed: true, data: compressed }
    } catch (error) {
      console.warn('数据压缩失败:', error)
      return { compressed: false, data: JSON.stringify(data) }
    }
  }

  /**
   * 解压数据
   */
  const decompressData = (cacheItem) => {
    try {
      if (cacheItem.compressed) {
        const decompressed = lzDecompress(cacheItem.data)
        return JSON.parse(decompressed)
      } else {
        return JSON.parse(cacheItem.data)
      }
    } catch (error) {
      console.warn('数据解压失败:', error)
      return null
    }
  }

  /**
   * 简单的LZ压缩
   */
  const lzCompress = (str) => {
    const dict = {}
    let data = str.split('')
    let result = []
    let dictSize = 256
    let w = ''

    for (let i = 0; i < data.length; i++) {
      const c = data[i]
      const wc = w + c
      
      if (dict[wc]) {
        w = wc
      } else {
        result.push(dict[w] || w.charCodeAt(0))
        dict[wc] = dictSize++
        w = c
      }
    }
    
    if (w) {
      result.push(dict[w] || w.charCodeAt(0))
    }
    
    return result
  }

  /**
   * 简单的LZ解压
   */
  const lzDecompress = (data) => {
    const dict = {}
    let result = []
    let dictSize = 256
    let w = String.fromCharCode(data[0])
    result.push(w)

    for (let i = 1; i < data.length; i++) {
      const k = data[i]
      let entry
      
      if (dict[k]) {
        entry = dict[k]
      } else if (k === dictSize) {
        entry = w + w.charAt(0)
      } else {
        throw new Error('解压错误')
      }
      
      result.push(entry)
      dict[dictSize++] = w + entry.charAt(0)
      w = entry
    }
    
    return result.join('')
  }

  /**
   * 设置缓存
   */
  const setCache = (key, data, ttl = cacheConfig.value.defaultTTL) => {
    try {
      // 检查缓存大小限制
      if (cacheStore.value.size >= cacheConfig.value.maxSize) {
        evictOldestCache()
      }

      const compressed = compressData(data)
      const cacheItem = {
        ...compressed,
        timestamp: Date.now(),
        ttl,
        accessCount: 0,
        lastAccess: Date.now()
      }

      cacheStore.value.set(key, cacheItem)
      cacheStats.value.size = cacheStore.value.size
      
      return true
    } catch (error) {
      console.error('缓存设置失败:', error)
      return false
    }
  }

  /**
   * 获取缓存
   */
  const getCache = (key) => {
    const cacheItem = cacheStore.value.get(key)
    
    if (!cacheItem) {
      cacheStats.value.misses++
      return null
    }

    // 检查TTL
    if (Date.now() - cacheItem.timestamp > cacheItem.ttl) {
      cacheStore.value.delete(key)
      cacheStats.value.size = cacheStore.value.size
      cacheStats.value.misses++
      return null
    }

    // 更新访问信息
    cacheItem.accessCount++
    cacheItem.lastAccess = Date.now()
    cacheStats.value.hits++

    return decompressData(cacheItem)
  }

  /**
   * 删除缓存
   */
  const deleteCache = (key) => {
    const deleted = cacheStore.value.delete(key)
    if (deleted) {
      cacheStats.value.size = cacheStore.value.size
    }
    return deleted
  }

  /**
   * 清空缓存
   */
  const clearCache = () => {
    cacheStore.value.clear()
    cacheStats.value.size = 0
    cacheStats.value.hits = 0
    cacheStats.value.misses = 0
  }

  /**
   * 淘汰最旧的缓存项
   */
  const evictOldestCache = () => {
    let oldestKey = null
    let oldestTime = Date.now()

    for (const [key, item] of cacheStore.value) {
      if (item.lastAccess < oldestTime) {
        oldestTime = item.lastAccess
        oldestKey = key
      }
    }

    if (oldestKey) {
      cacheStore.value.delete(oldestKey)
      cacheStats.value.size = cacheStore.value.size
    }
  }

  /**
   * 清理过期缓存
   */
  const cleanupExpiredCache = () => {
    const now = Date.now()
    const keysToDelete = []

    for (const [key, item] of cacheStore.value) {
      if (now - item.timestamp > item.ttl) {
        keysToDelete.push(key)
      }
    }

    keysToDelete.forEach(key => {
      cacheStore.value.delete(key)
    })

    cacheStats.value.size = cacheStore.value.size
    
    return keysToDelete.length
  }

  /**
   * 缓存装饰器
   */
  const withCache = (fn, options = {}) => {
    const {
      keyGenerator = (...args) => JSON.stringify(args),
      ttl = cacheConfig.value.defaultTTL,
      prefix = 'fn'
    } = options

    return async (...args) => {
      const cacheKey = generateCacheKey(prefix, keyGenerator(...args))
      
      // 尝试从缓存获取
      const cached = getCache(cacheKey)
      if (cached !== null) {
        return cached
      }

      // 执行函数并缓存结果
      try {
        const result = await fn(...args)
        setCache(cacheKey, result, ttl)
        return result
      } catch (error) {
        // 不缓存错误结果
        throw error
      }
    }
  }

  /**
   * 预加载缓存
   */
  const preloadCache = async (keys, loader) => {
    const promises = keys.map(async (key) => {
      if (!getCache(key)) {
        try {
          const data = await loader(key)
          setCache(key, data)
        } catch (error) {
          console.warn(`预加载缓存失败 ${key}:`, error)
        }
      }
    })

    return Promise.allSettled(promises)
  }

  /**
   * 获取缓存统计信息
   */
  const getCacheStats = () => ({
    ...cacheStats.value,
    hitRate: hitRate.value,
    memoryUsage: estimateMemoryUsage()
  })

  /**
   * 估算内存使用量
   */
  const estimateMemoryUsage = () => {
    let totalSize = 0
    
    for (const [key, item] of cacheStore.value) {
      totalSize += key.length * 2 // 字符串按2字节计算
      totalSize += JSON.stringify(item).length * 2
    }
    
    return {
      bytes: totalSize,
      kb: (totalSize / 1024).toFixed(2),
      mb: (totalSize / 1024 / 1024).toFixed(2)
    }
  }

  /**
   * 启动自动清理
   */
  const startAutoCleanup = () => {
    return setInterval(() => {
      const cleaned = cleanupExpiredCache()
      if (cleaned > 0) {
        console.log(`自动清理了 ${cleaned} 个过期缓存项`)
      }
    }, cacheConfig.value.cleanupInterval)
  }

  return {
    // 状态
    cacheStats,
    cacheConfig,
    hitRate,

    // 方法
    generateCacheKey,
    setCache,
    getCache,
    deleteCache,
    clearCache,
    cleanupExpiredCache,
    withCache,
    preloadCache,
    getCacheStats,
    startAutoCleanup
  }
}
