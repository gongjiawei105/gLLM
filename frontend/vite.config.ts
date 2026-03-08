import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/auth': {
        target: 'http://localhost:8080',
      },
      '/admin': {
        target: 'http://localhost:8080',
      },
      '/health': {
        target: 'http://localhost:8080',
      },
      '/gllm-login': {
        target: 'http://localhost:8080',
      },
      '/docs': {
        target: 'http://localhost:8080',
      },
      '/gllm': {
        target: 'http://localhost:8080',
        ws: true,
      },
      '/assets': {
        target: 'http://localhost:8080',
      },
      '/chainlit-auth': {
        target: 'http://localhost:8080',
      }
    },
  },
})

