import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,      // pick any free port
    strictPort: true // fail loudly instead of silently bumping
  }
})
