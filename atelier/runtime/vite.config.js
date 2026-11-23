import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'

export default defineConfig({
  root: fileURLToPath(new URL('.', import.meta.url)),
  base: './',
  publicDir: false,
  build: {
    outDir: 'dist',
    emptyOutDir: false,
    rolldownOptions: {
      output: {
        entryFileNames: 'assets/viewer.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name][extname]',
      },
    },
  },
})
