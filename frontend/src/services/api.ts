// src/services/api.ts

import axios, { AxiosError, AxiosRequestConfig } from 'axios';

// Extend Axios config to track retry attempts
declare module 'axios' {
  export interface AxiosRequestConfig {
    _retry?: boolean;
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true, // CRITICAL: Send HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Response interceptor for automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig;

    // Don't retry on these endpoints (they are used for initial auth check)
    const noRetryEndpoints = ['/auth/me', '/auth/refresh-token', '/auth/login', '/auth/register'];
    const isNoRetryEndpoint = noRetryEndpoints.some((endpoint) =>
      originalRequest?.url?.includes(endpoint)
    );

    // If 401 and not already retrying and not a no-retry endpoint
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isNoRetryEndpoint
    ) {
      originalRequest._retry = true;

      try {
        // Call refresh endpoint (backend sets new access token cookie)
        await api.post('/auth/refresh-token');

        // Retry original request with new access token
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - user needs to login again
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Request interceptor for logging (development only)
if (import.meta.env.VITE_DEBUG === 'true') {
  api.interceptors.request.use(
    (config) => {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
      return config;
    },
    (error) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  api.interceptors.response.use(
    (response) => {
      console.log(`[API Response] ${response.config.url}`, response.data);
      return response;
    },
    (error) => {
      console.error('[API Response Error]', error.response?.data || error.message);
      return Promise.reject(error);
    }
  );
}

export { api };
