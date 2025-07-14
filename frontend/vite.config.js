import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers';
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false, // css in js
        }),
      ],
    }),
    process.env.VISUALIZER && visualizer({
      open: true,
      filename: 'stats.html',
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    open: true,
    cors: true,
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    // 启用更好的Tree Shaking
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Vue核心库
            if (id.includes('vue') && !id.includes('ant-design-vue')) {
              return 'vendor_vue';
            }
            // 图表库
            if (id.includes('echarts') || id.includes('zrender')) {
              return 'vendor_charts';
            }
            // UI组件库
            if (id.includes('ant-design-vue') || id.includes('@ant-design')) {
              return 'vendor_ui';
            }
            // 工具库
            if (id.includes('lodash') || id.includes('dayjs') || id.includes('axios')) {
              return 'vendor_utils';
            }
            // 图标库
            if (id.includes('@heroicons') || id.includes('icons')) {
              return 'vendor_icons';
            }
            // 其他第三方库
            return 'vendor';
          }

          // 应用代码分割
          if (id.includes('/src/views/')) {
            return 'pages';
          }
          if (id.includes('/src/components/')) {
            return 'components';
          }
          if (id.includes('/src/stores/')) {
            return 'stores';
          }
        },
      }
    }
  }
})