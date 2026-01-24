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
        // Dynamic target based on environment:
        // - Docker: 'http://backend:8000' (via VITE_PROXY_TARGET env var)
        // - Host: 'http://localhost:8000' (default)
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Rewrite /api/* to /* because backend routes don't include /api prefix
        // Example: /api/auth/me → /auth/me
        rewrite: (path) => path.replace(/^\/api/, ''),
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
