/**
 * SocialStatTooltip Component Unit Tests
 *
 * Tests for tooltip presentation component rendering.
 * Covers loading, error, empty, and populated states.
 *
 * @see specs/019-followers-tooltip/IMPLEMENTATION_GUIDE.md § Task 2.2
 * @see specs/019-followers-tooltip/tasks.md § Tests T013-T018
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import SocialStatTooltip from '../../src/components/dashboard/SocialStatTooltip';
import type { UserSummaryForFollow } from '../../src/types/follow';

const mockUsers: UserSummaryForFollow[] = [
  { user_id: '1', username: 'user1', profile_photo_url: 'photo1.jpg' },
  { user_id: '2', username: 'user2', profile_photo_url: null },
];

const renderWithRouter = (ui: React.ReactElement) => {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe('SocialStatTooltip', () => {
  // T013: Unit test - renders loading state with spinner
  it('should show loading state', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={[]}
        totalCount={0}
        type="followers"
        username="testuser"
        isLoading={true}
        error={null}
        visible={true}
      />
    );

    expect(screen.getByText('Cargando...')).toBeInTheDocument();
    expect(screen.getByRole('tooltip')).toHaveAttribute('aria-live', 'polite');
  });

  // T014: Unit test - renders user list with 8 users
  it('should render user list with avatars', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={mockUsers}
        totalCount={2}
        type="followers"
        username="testuser"
        isLoading={false}
        error={null}
        visible={true}
      />
    );

    expect(screen.getByText('user1')).toBeInTheDocument();
    expect(screen.getByText('user2')).toBeInTheDocument();
    expect(screen.getByAltText('user1')).toHaveAttribute('src', expect.stringContaining('photo1.jpg'));
    expect(screen.getByText('U')).toBeInTheDocument(); // Placeholder for user2
  });

  // T015: Unit test - renders empty state message
  it('should show empty state for followers', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={[]}
        totalCount={0}
        type="followers"
        username="testuser"
        isLoading={false}
        error={null}
        visible={true}
      />
    );

    expect(screen.getByText('No tienes seguidores aún')).toBeInTheDocument();
  });

  it('should show empty state for following', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={[]}
        totalCount={0}
        type="following"
        username="testuser"
        isLoading={false}
        error={null}
        visible={true}
      />
    );

    expect(screen.getByText('No sigues a nadie aún')).toBeInTheDocument();
  });

  // T016: Unit test - renders "Ver todos" link when remaining > 0
  it('should show "Ver todos" link when more users exist', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={mockUsers}
        totalCount={10}
        type="followers"
        username="testuser"
        isLoading={false}
        error={null}
        visible={true}
      />
    );

    const link = screen.getByText(/\+ 8 más · Ver todos/);
    expect(link).toHaveAttribute('href', '/users/testuser/followers');
  });

  // T017: Unit test - does not render "Ver todos" when totalCount ≤ 8
  it('should NOT show "Ver todos" link when all users shown', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={mockUsers}
        totalCount={2}
        type="followers"
        username="testuser"
        isLoading={false}
        error={null}
        visible={true}
      />
    );

    expect(screen.queryByText(/Ver todos/)).not.toBeInTheDocument();
  });

  // T018: Unit test - hides when visible=false
  it('should return null when not visible', () => {
    const { container } = renderWithRouter(
      <SocialStatTooltip
        users={[]}
        totalCount={0}
        type="followers"
        username="testuser"
        isLoading={false}
        error={null}
        visible={false}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  // Bonus tests
  it('should show error state', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={[]}
        totalCount={0}
        type="followers"
        username="testuser"
        isLoading={false}
        error="Error al cargar usuarios"
        visible={true}
      />
    );

    expect(screen.getByText('Error al cargar usuarios')).toBeInTheDocument();
  });

  it('should have correct ARIA attributes', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={mockUsers}
        totalCount={2}
        type="followers"
        username="testuser"
        isLoading={false}
        error={null}
        visible={true}
      />
    );

    const tooltip = screen.getByRole('tooltip');
    expect(tooltip).toHaveAttribute('aria-live', 'polite');
  });

  it('should link to following page for following type', () => {
    renderWithRouter(
      <SocialStatTooltip
        users={mockUsers}
        totalCount={10}
        type="following"
        username="testuser"
        isLoading={false}
        error={null}
        visible={true}
      />
    );

    const link = screen.getByText(/\+ 8 más · Ver todos/);
    expect(link).toHaveAttribute('href', '/users/testuser/following');
  });
});
