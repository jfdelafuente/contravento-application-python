/**
 * Unit tests for PublicHeader component (Feature 013 - T038)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PublicHeader } from '../../src/components/layout/PublicHeader';
import * as AuthContext from '../../src/contexts/AuthContext';
import type { User } from '../../src/types/user';

// Mock useNavigate from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Wrapper component for router context
const RouterWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('PublicHeader', () => {
  const mockLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
    mockLogout.mockClear();
  });

  describe('Anonymous User State', () => {
    beforeEach(() => {
      // Mock anonymous user state (not authenticated)
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        register: vi.fn(),
        logout: mockLogout,
        refreshUser: vi.fn(),
        requestPasswordReset: vi.fn(),
        resetPassword: vi.fn(),
        resendVerificationEmail: vi.fn(),
      });
    });

    it('renders logo and login button for anonymous users', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      // Check logo
      expect(screen.getByText('ContraVento')).toBeInTheDocument();

      // Check login button
      const loginButton = screen.getByText('Iniciar sesión');
      expect(loginButton).toBeInTheDocument();
      expect(loginButton.tagName).toBe('BUTTON');
    });

    it('navigates to /login when login button is clicked', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const loginButton = screen.getByText('Iniciar sesión');
      fireEvent.click(loginButton);

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });

    it('does not show user profile or logout button for anonymous users', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      // Profile section should not exist
      expect(screen.queryByLabelText(/Ir al perfil de/i)).not.toBeInTheDocument();
      expect(screen.queryByText('Cerrar sesión')).not.toBeInTheDocument();
    });

    it('navigates to home when logo is clicked', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const logo = screen.getByText('ContraVento');
      fireEvent.click(logo.closest('.public-header__logo')!);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Authenticated User State', () => {
    const mockUser: User = {
      user_id: '123e4567-e89b-12d3-a456-426614174000',
      username: 'testuser',
      email: 'test@example.com',
      is_verified: true,
      created_at: '2024-01-01T00:00:00Z',
      profile: {
        full_name: 'Test User',
        photo_url: '/storage/profile_photos/testuser.jpg',
        bio: 'Test bio',
        location: 'Test City',
      },
    };

    beforeEach(() => {
      // Mock authenticated user state
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: mockUser,
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        register: vi.fn(),
        logout: mockLogout,
        refreshUser: vi.fn(),
        requestPasswordReset: vi.fn(),
        resetPassword: vi.fn(),
        resendVerificationEmail: vi.fn(),
      });
    });

    it('renders logo, profile, and logout button for authenticated users', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      // Check logo
      expect(screen.getByText('ContraVento')).toBeInTheDocument();

      // Check username
      expect(screen.getByText('testuser')).toBeInTheDocument();

      // Check logout button
      expect(screen.getByText('Cerrar sesión')).toBeInTheDocument();
    });

    it('displays user profile photo when available', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const profilePhoto = screen.getByAltText('testuser');
      expect(profilePhoto).toBeInTheDocument();
      expect(profilePhoto).toHaveAttribute('src', '/storage/profile_photos/testuser.jpg');
      expect(profilePhoto).toHaveClass('public-header__profile-photo');
    });

    it('displays user initial avatar when photo not available', () => {
      // Mock user without photo
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: {
          ...mockUser,
          profile: undefined,
        },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        register: vi.fn(),
        logout: mockLogout,
        refreshUser: vi.fn(),
        requestPasswordReset: vi.fn(),
        resetPassword: vi.fn(),
        resendVerificationEmail: vi.fn(),
      });

      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      // Should show first letter of username
      const avatar = screen.getByLabelText(/Avatar de testuser/i);
      expect(avatar).toBeInTheDocument();
      expect(avatar).toHaveTextContent('T'); // First letter of "testuser"
    });

    it('navigates to dashboard when profile button is clicked', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const dashboardButton = screen.getByLabelText(/Ir al dashboard de testuser/i);
      fireEvent.click(dashboardButton);

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });

    it('calls logout when logout button is clicked', async () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const logoutButton = screen.getByText('Cerrar sesión');
      fireEvent.click(logoutButton);

      // Should call logout
      await vi.waitFor(() => {
        expect(mockLogout).toHaveBeenCalled();
      });
    });

    it('handles logout errors gracefully', async () => {
      // Mock logout to reject
      mockLogout.mockRejectedValueOnce(new Error('Logout failed'));

      // Spy on console.error to verify error handling
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const logoutButton = screen.getByText('Cerrar sesión');
      fireEvent.click(logoutButton);

      // Should log error
      await vi.waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith('Logout error:', expect.any(Error));
      });

      consoleErrorSpy.mockRestore();
    });

    it('does not show login button for authenticated users', () => {
      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      expect(screen.queryByText('Iniciar sesión')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels for buttons', () => {
      // Mock anonymous state
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        register: vi.fn(),
        logout: mockLogout,
        refreshUser: vi.fn(),
        requestPasswordReset: vi.fn(),
        resetPassword: vi.fn(),
        resendVerificationEmail: vi.fn(),
      });

      render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const loginButton = screen.getByLabelText('Iniciar sesión');
      expect(loginButton).toBeInTheDocument();
    });

    it('has semantic HTML structure', () => {
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        register: vi.fn(),
        logout: mockLogout,
        refreshUser: vi.fn(),
        requestPasswordReset: vi.fn(),
        resetPassword: vi.fn(),
        resendVerificationEmail: vi.fn(),
      });

      const { container } = render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      // Should use <header> element
      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('public-header');
    });
  });

  describe('Logo Behavior', () => {
    it('navigates to homepage when logo is clicked', () => {
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        register: vi.fn(),
        logout: mockLogout,
        refreshUser: vi.fn(),
        requestPasswordReset: vi.fn(),
        resetPassword: vi.fn(),
        resendVerificationEmail: vi.fn(),
      });

      const { container } = render(
        <RouterWrapper>
          <PublicHeader />
        </RouterWrapper>
      );

      const logoElement = container.querySelector('.public-header__logo');
      expect(logoElement).toBeInTheDocument();

      fireEvent.click(logoElement!);
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });
});
