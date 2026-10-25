import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1', port: Number(process.env.SAWTNA_WEB_PORT || 5175), strictPort: true,
    proxy: { '/api': process.env.SAWTNA_API_URL || 'http://127.0.0.1:8010' },
  },
})
