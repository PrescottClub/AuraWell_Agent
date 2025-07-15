/**
 * AuraWell 浏览器兼容性检测
 *
 * 检测浏览器特性支持情况并提供兼容性方案
 */

import { ref, computed, onMounted } from 'vue'

export interface BrowserInfo {
  name: string
  version: string
  engine: string
  platform: string
  mobile: boolean
  supported: boolean
}

export interface FeatureSupport {
  // CSS 特性
  cssGrid: boolean
  cssFlexbox: boolean
  cssCustomProperties: boolean
  cssContainerQueries: boolean
  cssSubgrid: boolean

  // JavaScript 特性
  es6Modules: boolean
  asyncAwait: boolean
  intersectionObserver: boolean
  resizeObserver: boolean
  webComponents: boolean

  // Web APIs
  webGL: boolean
  webGL2: boolean
  webWorkers: boolean
  serviceWorkers: boolean
  pushNotifications: boolean
  geolocation: boolean

  // 媒体特性
  webP: boolean
  avif: boolean
  webM: boolean

  // 存储特性
  localStorage: boolean
  sessionStorage: boolean
  indexedDB: boolean

  // 网络特性
  fetch: boolean
  websockets: boolean
  webRTC: boolean
}

export interface CompatibilityReport {
  browser: BrowserInfo
  features: FeatureSupport
  warnings: string[]
  recommendations: string[]
  score: number
}

/**
 * 浏览器兼容性检测主函数
 */
export function useBrowserCompatibility() {
  const browserInfo = ref<BrowserInfo>({
    name: '',
    version: '',
    engine: '',
    platform: '',
    mobile: false,
    supported: true
  })

  const featureSupport = ref<FeatureSupport>({
    // CSS 特性
    cssGrid: false,
    cssFlexbox: false,
    cssCustomProperties: false,
    cssContainerQueries: false,
    cssSubgrid: false,

    // JavaScript 特性
    es6Modules: false,
    asyncAwait: false,
    intersectionObserver: false,
    resizeObserver: false,
    webComponents: false,

    // Web APIs
    webGL: false,
    webGL2: false,
    webWorkers: false,
    serviceWorkers: false,
    pushNotifications: false,
    geolocation: false,

    // 媒体特性
    webP: false,
    avif: false,
    webM: false,

    // 存储特性
    localStorage: false,
    sessionStorage: false,
    indexedDB: false,

    // 网络特性
    fetch: false,
    websockets: false,
    webRTC: false
  })

  const warnings = ref<string[]>([])
  const recommendations = ref<string[]>([])

  /**
   * 检测浏览器信息
   */
  const detectBrowser = (): BrowserInfo => {
    const ua = navigator.userAgent
    const platform = navigator.platform

    let name = 'Unknown'
    let version = 'Unknown'
    let engine = 'Unknown'

    // 检测浏览器名称和版本
    if (ua.includes('Chrome') && !ua.includes('Edg')) {
      name = 'Chrome'
      const match = ua.match(/Chrome\/(\d+)/)
      version = match?.[1] ?? 'Unknown'
      engine = 'Blink'
    } else if (ua.includes('Firefox')) {
      name = 'Firefox'
      const match = ua.match(/Firefox\/(\d+)/)
      version = match?.[1] ?? 'Unknown'
      engine = 'Gecko'
    } else if (ua.includes('Safari') && !ua.includes('Chrome')) {
      name = 'Safari'
      const match = ua.match(/Version\/(\d+)/)
      version = match?.[1] ?? 'Unknown'
      engine = 'WebKit'
    } else if (ua.includes('Edg')) {
      name = 'Edge'
      const match = ua.match(/Edg\/(\d+)/)
      version = match?.[1] ?? 'Unknown'
      engine = 'Blink'
    }

    const mobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)

    // 判断是否支持
    const supported = checkBrowserSupport(name, parseInt(version))

    return {
      name,
      version,
      engine,
      platform,
      mobile,
      supported
    }
  }

  /**
   * 检查浏览器支持情况
   */
  const checkBrowserSupport = (name: string, version: number): boolean => {
    const minVersions: Record<string, number> = {
      Chrome: 80,
      Firefox: 75,
      Safari: 13,
      Edge: 80
    }

    return version >= (minVersions[name] || 999)
  }

  /**
   * 检测CSS特性支持
   */
  const detectCSSFeatures = (): Partial<FeatureSupport> => {
    const features: Partial<FeatureSupport> = {}

    // CSS Grid
    features.cssGrid = CSS.supports('display', 'grid')

    // CSS Flexbox
    features.cssFlexbox = CSS.supports('display', 'flex')

    // CSS Custom Properties
    features.cssCustomProperties = CSS.supports('--custom', 'property')

    // CSS Container Queries
    features.cssContainerQueries = CSS.supports('container-type', 'inline-size')

    // CSS Subgrid
    features.cssSubgrid = CSS.supports('grid-template-rows', 'subgrid')

    return features
  }

  /**
   * 检测JavaScript特性支持
   */
  const detectJSFeatures = (): Partial<FeatureSupport> => {
    const features: Partial<FeatureSupport> = {}

    // ES6 Modules
    features.es6Modules = 'noModule' in document.createElement('script')

    // Async/Await
    try {
      eval('(async () => {})')
      features.asyncAwait = true
    } catch {
      features.asyncAwait = false
    }

    // Intersection Observer
    features.intersectionObserver = 'IntersectionObserver' in window

    // Resize Observer
    features.resizeObserver = 'ResizeObserver' in window

    // Web Components
    features.webComponents = 'customElements' in window

    return features
  }

  /**
   * 检测Web API支持
   */
  const detectWebAPIFeatures = (): Partial<FeatureSupport> => {
    const features: Partial<FeatureSupport> = {}

    // WebGL
    try {
      const canvas = document.createElement('canvas')
      features.webGL = !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
      features.webGL2 = !!canvas.getContext('webgl2')
    } catch {
      features.webGL = false
      features.webGL2 = false
    }

    // Web Workers
    features.webWorkers = 'Worker' in window

    // Service Workers
    features.serviceWorkers = 'serviceWorker' in navigator

    // Push Notifications
    features.pushNotifications = 'PushManager' in window

    // Geolocation
    features.geolocation = 'geolocation' in navigator

    return features
  }

  /**
   * 检测媒体格式支持
   */
  const detectMediaFeatures = async (): Promise<Partial<FeatureSupport>> => {
    const features: Partial<FeatureSupport> = {}

    // WebP 支持检测
    features.webP = await new Promise((resolve) => {
      const img = new Image()
      img.onload = () => resolve(true)
      img.onerror = () => resolve(false)
      img.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA'
    })

    // AVIF 支持检测
    features.avif = await new Promise((resolve) => {
      const img = new Image()
      img.onload = () => resolve(true)
      img.onerror = () => resolve(false)
      img.src = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgABogQEAwgMg8f8D///8WfhwB8+ErK42A='
    })

    // WebM 支持检测
    const video = document.createElement('video')
    features.webM = video.canPlayType('video/webm') !== ''

    return features
  }

  /**
   * 检测存储特性支持
   */
  const detectStorageFeatures = (): Partial<FeatureSupport> => {
    const features: Partial<FeatureSupport> = {}

    // Local Storage
    try {
      localStorage.setItem('test', 'test')
      localStorage.removeItem('test')
      features.localStorage = true
    } catch {
      features.localStorage = false
    }

    // Session Storage
    try {
      sessionStorage.setItem('test', 'test')
      sessionStorage.removeItem('test')
      features.sessionStorage = true
    } catch {
      features.sessionStorage = false
    }

    // IndexedDB
    features.indexedDB = 'indexedDB' in window

    return features
  }

  /**
   * 检测网络特性支持
   */
  const detectNetworkFeatures = (): Partial<FeatureSupport> => {
    const features: Partial<FeatureSupport> = {}

    // Fetch API
    features.fetch = 'fetch' in window

    // WebSockets
    features.websockets = 'WebSocket' in window

    // WebRTC
    features.webRTC = 'RTCPeerConnection' in window

    return features
  }

  /**
   * 生成兼容性警告
   */
  const generateWarnings = (browser: BrowserInfo, features: FeatureSupport): string[] => {
    const warns: string[] = []

    if (!browser.supported) {
      warns.push(`您的浏览器版本 ${browser.name} ${browser.version} 可能不完全支持所有功能`)
    }

    if (!features.cssGrid) {
      warns.push('您的浏览器不支持 CSS Grid，布局可能显示异常')
    }

    if (!features.cssFlexbox) {
      warns.push('您的浏览器不支持 CSS Flexbox，布局可能显示异常')
    }

    if (!features.intersectionObserver) {
      warns.push('您的浏览器不支持 Intersection Observer，滚动动画可能无法正常工作')
    }

    if (!features.fetch) {
      warns.push('您的浏览器不支持 Fetch API，网络请求可能使用降级方案')
    }

    if (!features.webP) {
      warns.push('您的浏览器不支持 WebP 格式，图片加载可能较慢')
    }

    return warns
  }

  /**
   * 生成兼容性建议
   */
  const generateRecommendations = (browser: BrowserInfo, features: FeatureSupport): string[] => {
    const recs: string[] = []

    if (!browser.supported) {
      recs.push(`建议升级到 ${browser.name} 最新版本以获得最佳体验`)
    }

    if (browser.name === 'Chrome' && parseInt(browser.version) < 90) {
      recs.push('建议升级 Chrome 到 90+ 版本以支持更多现代特性')
    }

    if (browser.name === 'Safari' && parseInt(browser.version) < 14) {
      recs.push('建议升级 Safari 到 14+ 版本以获得更好的性能')
    }

    if (!features.serviceWorkers) {
      recs.push('您的浏览器不支持 Service Workers，无法使用离线功能')
    }

    if (recs.length === 0) {
      recs.push('您的浏览器兼容性良好，可以正常使用所有功能')
    }

    return recs
  }

  /**
   * 计算兼容性分数
   */
  const calculateCompatibilityScore = (features: FeatureSupport): number => {
    const totalFeatures = Object.keys(features).length
    const supportedFeatures = Object.values(features).filter(Boolean).length
    return Math.round((supportedFeatures / totalFeatures) * 100)
  }

  /**
   * 执行完整的兼容性检测
   */
  const runCompatibilityCheck = async (): Promise<CompatibilityReport> => {
    const browser = detectBrowser()

    const cssFeatures = detectCSSFeatures()
    const jsFeatures = detectJSFeatures()
    const webAPIFeatures = detectWebAPIFeatures()
    const mediaFeatures = await detectMediaFeatures()
    const storageFeatures = detectStorageFeatures()
    const networkFeatures = detectNetworkFeatures()

    const features = {
      ...featureSupport.value,
      ...cssFeatures,
      ...jsFeatures,
      ...webAPIFeatures,
      ...mediaFeatures,
      ...storageFeatures,
      ...networkFeatures
    } as FeatureSupport

    const warns = generateWarnings(browser, features)
    const recs = generateRecommendations(browser, features)
    const score = calculateCompatibilityScore(features)

    // 更新响应式数据
    browserInfo.value = browser
    featureSupport.value = features
    warnings.value = warns
    recommendations.value = recs

    return {
      browser,
      features,
      warnings: warns,
      recommendations: recs,
      score
    }
  }

  // 计算属性
  const isModernBrowser = computed(() => {
    return browserInfo.value.supported &&
           featureSupport.value.cssGrid &&
           featureSupport.value.cssFlexbox &&
           featureSupport.value.fetch
  })

  const compatibilityScore = computed(() => {
    return calculateCompatibilityScore(featureSupport.value)
  })

  // 生命周期
  onMounted(() => {
    runCompatibilityCheck()
  })

  return {
    browserInfo,
    featureSupport,
    warnings,
    recommendations,
    isModernBrowser,
    compatibilityScore,
    runCompatibilityCheck
  }
}