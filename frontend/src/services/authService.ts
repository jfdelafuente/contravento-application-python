// src/services/authService.ts

import { api } from './api';
import type { User } from '../types/user';
import type {
  RegisterFormData,
  RegisterRequestPayload,
  ForgotPasswordFormData,
} from '../types/forms';
import type {
  ApiResponse,
  RegisterResponse,
  LoginResponse,
  LogoutResponse,
  CurrentUserResponse,
  VerifyEmailResponse,
  ResendVerificationResponse,
  ForgotPasswordResponse,
  ResetPasswordResponse,
  EmailAvailabilityResponse,
  UsernameAvailabilityResponse,
} from '../types/api';

export const authService = {
  /**
   * Register a new user
   */
  async register(formData: RegisterFormData): Promise<User> {
    const payload: RegisterRequestPayload = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      turnstile_token: formData.turnstileToken,
    };

    const { data } = await api.post<ApiResponse<RegisterResponse>>(
      '/auth/register',
      payload
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || 'Registration failed');
    }

    // Backend returns UserResponse directly (not nested under 'user')
    // Fields: user_id, username, email, is_verified, created_at, etc.
    return data.data as User;
  },

  /**
   * Login user
   *
   * Note: Backend does not support remember_me or turnstile_token yet.
   * These parameters are kept for future implementation.
   */
  async login(
    email: string,
    password: string,
    _rememberMe: boolean, // Prefixed with _ to indicate intentionally unused
    _turnstileToken?: string // Prefixed with _ to indicate intentionally unused
  ): Promise<User> {
    // Backend expects 'login' field (username or email), not 'email'
    const payload = {
      login: email, // Backend accepts email in 'login' field
      password,
    };

    const { data } = await api.post<ApiResponse<LoginResponse>>(
      '/auth/login',
      payload
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || 'Login failed');
    }

    // Store tokens in localStorage for authentication
    if (data.data.access_token) {
      localStorage.setItem('access_token', data.data.access_token);
    }
    if (data.data.refresh_token) {
      localStorage.setItem('refresh_token', data.data.refresh_token);
    }

    return data.data.user;
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');

    // Clear tokens from localStorage immediately
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // If no refresh token, just clear locally and return
    if (!refreshToken) {
      return;
    }

    try {
      const { data } = await api.post<ApiResponse<LogoutResponse>>('/auth/logout', null, {
        params: {
          refresh_token: refreshToken,
        },
      });

      if (!data.success) {
        throw new Error(data.error?.message || 'Logout failed');
      }
    } catch (error) {
      // Even if backend logout fails, local tokens are already cleared
      console.error('Logout error:', error);
    }
  },

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<User> {
    const { data } = await api.get<ApiResponse<CurrentUserResponse>>('/auth/me');

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || 'Failed to get current user');
    }

    return data.data;
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<void> {
    await api.post('/auth/refresh');
  },

  /**
   * Verify email with token
   */
  async verifyEmail(token: string): Promise<User> {
    const { data } = await api.post<ApiResponse<VerifyEmailResponse>>(
      '/auth/verify-email',
      { token }
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || 'Email verification failed');
    }

    return data.data.user;
  },

  /**
   * Resend verification email
   */
  async resendVerificationEmail(): Promise<string> {
    const { data } = await api.post<ApiResponse<ResendVerificationResponse>>(
      '/auth/resend-verification'
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || 'Failed to resend verification email');
    }

    return data.data.email_sent_to;
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string, turnstileToken: string): Promise<string> {
    const payload: ForgotPasswordFormData = {
      email,
      turnstileToken,
    };

    const { data } = await api.post<ApiResponse<ForgotPasswordResponse>>(
      '/auth/forgot-password',
      {
        email: payload.email,
        turnstile_token: payload.turnstileToken,
      }
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || 'Password reset request failed');
    }

    return data.data.email_sent_to;
  },

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    const { data } = await api.post<ApiResponse<ResetPasswordResponse>>(
      '/auth/reset-password',
      {
        token,
        new_password: newPassword,
      }
    );

    if (!data.success) {
      throw new Error(data.error?.message || 'Password reset failed');
    }
  },

  /**
   * Check email availability
   */
  async checkEmailAvailability(email: string): Promise<boolean> {
    const { data } = await api.get<ApiResponse<EmailAvailabilityResponse>>(
      `/auth/check-email?email=${encodeURIComponent(email)}`
    );

    if (!data.success || !data.data) {
      return false;
    }

    return data.data.available;
  },

  /**
   * Check username availability
   */
  async checkUsernameAvailability(username: string): Promise<boolean> {
    const { data } = await api.get<ApiResponse<UsernameAvailabilityResponse>>(
      `/auth/check-username?username=${encodeURIComponent(username)}`
    );

    if (!data.success || !data.data) {
      return false;
    }

    return data.data.available;
  },
};
