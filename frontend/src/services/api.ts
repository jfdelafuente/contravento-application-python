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
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor to add access token to headers
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig;

    // Don't retry on these endpoints (they are used for initial auth check)
    const noRetryEndpoints = ['/auth/me', '/auth/refresh', '/auth/login', '/auth/register'];
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
        // Get refresh token from localStorage
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          // No refresh token available - user needs to login again
          localStorage.clear();
          window.location.href = '/login';
          return Promise.reject(new Error('No refresh token available'));
        }

        // Call refresh endpoint with refresh token as query parameter
        const response = await api.post('/auth/refresh', null, {
          params: {
            refresh_token: refreshToken,
          },
        });

        // Store new tokens if provided
        if (response.data?.data?.access_token) {
          localStorage.setItem('access_token', response.data.data.access_token);
        }
        if (response.data?.data?.refresh_token) {
          localStorage.setItem('refresh_token', response.data.data.refresh_token);
        }

        // Retry original request with new access token
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - clear storage and redirect to login
        localStorage.clear();
        window.location.href = '/login';
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
