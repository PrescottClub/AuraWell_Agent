import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./src/test-setup.js'],
    include: ['src/**/*.{test,spec}.{js,ts,vue}'],
    exclude: ['node_modules', 'dist'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test-setup.js',
        '**/*.d.ts',
        '**/*.config.js',
        '**/*.config.ts'
      ]
    },
    // 处理 Rollup 架构问题
    server: {
      deps: {
        external: ['@rollup/rollup-linux-x64-gnu']
      }
    },
    // 为不同平台提供回退选项
    onConsoleLog: (log, type) => {
      if (log.includes('@rollup/rollup-') && log.includes('Cannot find module')) {
        return false // 抑制 Rollup 平台特定模块的错误日志
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  // 为了兼容性，确保正确处理 ESM
  esbuild: {
    target: 'node14'
  }
})
