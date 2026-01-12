import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  server: {
    port: 5173, // Vite default port
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Do NOT rewrite path - backend expects /api/* routes
      },
    },
  },
  build: {
    target: 'es2020',
    minify: 'terser',
    // Enable source maps for staging, disable for production
    sourcemap: mode === 'staging',
    // CSS minification
    cssMinify: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks for better caching
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'form-vendor': ['react-hook-form', '@hookform/resolvers', 'zod'],
          'map-vendor': ['react-leaflet', 'leaflet'],
        },
      },
    },
    chunkSizeWarningLimit: 500, // Warn if chunk > 500KB
  },
}));
