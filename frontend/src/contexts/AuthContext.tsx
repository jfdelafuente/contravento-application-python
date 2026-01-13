// src/contexts/AuthContext.tsx

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '../services/authService';
import type { User } from '../types/user';
import type { AuthContextType } from '../types/auth';
import type { RegisterFormData } from '../types/forms';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check auth status on mount (validates HttpOnly cookie)
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        // Not authenticated or token expired
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const register = async (data: RegisterFormData): Promise<void> => {
    const newUser = await authService.register(data);
    // Don't set user yet - email needs to be verified
    // User will login after email verification
  };

  const login = async (
    email: string,
    password: string,
    rememberMe: boolean
  ): Promise<void> => {
    const userData = await authService.login(email, password, rememberMe);
    setUser(userData);
  };

  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
    } catch (error) {
      // Ignore logout errors - just clear local state
      console.warn('Logout request failed, clearing local state anyway:', error);
    } finally {
      setUser(null);
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      setUser(null);
    }
  };

  const updateUser = (userData: Partial<User>): void => {
    setUser(prev => prev ? { ...prev, ...userData } : null);
  };

  const requestPasswordReset = async (email: string): Promise<void> => {
    // This is handled in the component with CAPTCHA token
    // Just a placeholder in context
  };

  const resetPassword = async (token: string, newPassword: string): Promise<void> => {
    await authService.resetPassword(token, newPassword);
  };

  const resendVerificationEmail = async (): Promise<void> => {
    await authService.resendVerificationEmail();
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
    updateUser,
    requestPasswordReset,
    resetPassword,
    resendVerificationEmail,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Hook to use auth context
 * @throws Error if used outside AuthProvider
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
