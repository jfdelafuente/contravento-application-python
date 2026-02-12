// src/types/env.d.ts

/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend API base URL */
  readonly VITE_API_URL: string;

  /** Cloudflare Turnstile site key */
  readonly VITE_TURNSTILE_SITE_KEY: string;

  /** Environment (development/staging/production) */
  readonly VITE_ENV: 'development' | 'staging' | 'production';

  /** Enable debug logging */
  readonly VITE_DEBUG?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
