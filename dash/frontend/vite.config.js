// Smport { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [vue()],
// })

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 当请求路径以 /api 开头时，将其转发到 9000 端口
      '/api': {
        target: 'http://127.0.0.1:9000',
        changeOrigin: true,
      }
    }
  }
})