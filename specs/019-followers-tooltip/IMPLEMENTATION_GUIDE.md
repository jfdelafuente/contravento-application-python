# Implementation Guide: Dashboard Followers/Following Tooltips

**Feature**: 019-followers-tooltip
**Date**: 2026-02-13
**Purpose**: Detailed task sequence with cross-references to implementation artifacts

## Overview

This guide provides a step-by-step task sequence derived from the plan and research documents. Each task includes:
- **What to implement**: Clear description
- **Where to find details**: Cross-references to spec/plan/research/data-model files
- **Code examples**: Direct links to example implementations
- **Test scenarios**: Which tests to write

---

## Task Sequence (TDD Workflow)

### PHASE 1: Setup & File Creation

#### Task 1.1: Create useFollowersTooltip Hook File

**File**: `frontend/src/hooks/useFollowersTooltip.ts`

**What**: Create empty hook file with TypeScript interface

**References**:
- **Type definition**: [data-model.md § UseFollowersTooltipReturn](data-model.md#4-usefollowerstooltipreturn-new) (lines 174-187)
- **Implementation pattern**: [research.md § React Hook Performance Patterns](research.md#5-react-hook-performance-patterns) (Decision section)
- **Full code example**: [ANALISIS_TOOLTIP_FOLLOWERS.md § useFollowersTooltip](../ANALISIS_TOOLTIP_FOLLOWERS.md#41-nuevo-hook-usefollowerstooltip) (lines 147-199)

**Initial Structure**:
```typescript
// frontend/src/hooks/useFollowersTooltip.ts

import { useState, useCallback, useEffect } from 'react';
import { getFollowers, getFollowing } from '../services/followService';
import type { UserSummaryForFollow } from '../types/follow';

interface UseFollowersTooltipReturn {
  users: UserSummaryForFollow[];
  totalCount: number;
  isLoading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
}

export function useFollowersTooltip(
  username: string,
  type: 'followers' | 'following'
): UseFollowersTooltipReturn {
  // TODO: Implement in Task 2.1
  return {
    users: [],
    totalCount: 0,
    isLoading: false,
    error: null,
    fetchUsers: async () => {},
  };
}
```

**Checklist**:
- [ ] File created at correct path
- [ ] TypeScript types imported from existing files
- [ ] Interface matches data-model.md specification
- [ ] No implementation yet (stub only)

---

#### Task 1.2: Create SocialStatTooltip Component File

**File**: `frontend/src/components/dashboard/SocialStatTooltip.tsx`

**What**: Create empty component file with props interface

**References**:
- **Props interface**: [data-model.md § SocialStatTooltipProps](data-model.md#5-socialstattooltipprops-new) (lines 189-213)
- **Component structure**: [ANALISIS_TOOLTIP_FOLLOWERS.md § SocialStatTooltip](../ANALISIS_TOOLTIP_FOLLOWERS.md#42-nuevo-componente-socialstattooltip) (lines 203-291)
- **Conditional rendering logic**: [data-model.md § Rendering Logic](data-model.md#5-socialstattooltipprops-new) (lines 215-218)

**Initial Structure**:
```typescript
// frontend/src/components/dashboard/SocialStatTooltip.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import type { UserSummaryForFollow } from '../../types/follow';
import './SocialStatTooltip.css';

interface SocialStatTooltipProps {
  users: UserSummaryForFollow[];
  totalCount: number;
  type: 'followers' | 'following';
  username: string;
  isLoading: boolean;
  error: string | null;
  visible: boolean;
}

export const SocialStatTooltip: React.FC<SocialStatTooltipProps> = ({
  users,
  totalCount,
  type,
  username,
  isLoading,
  error,
  visible,
}) => {
  // TODO: Implement in Task 2.2
  if (!visible) return null;

  return (
    <div className="social-stat-tooltip" role="tooltip" aria-live="polite">
      <p>Placeholder</p>
    </div>
  );
};
```

**Checklist**:
- [ ] File created at correct path
- [ ] Props interface matches data-model.md
- [ ] ARIA attributes included (role, aria-live)
- [ ] Early return if !visible
- [ ] No full implementation yet

---

#### Task 1.3: Create SocialStatTooltip CSS File

**File**: `frontend/src/components/dashboard/SocialStatTooltip.css`

**What**: Create empty CSS file with basic structure

**References**:
- **CSS structure**: [ANALISIS_TOOLTIP_FOLLOWERS.md § SocialStatTooltip.css](../ANALISIS_TOOLTIP_FOLLOWERS.md#44-css-socialstattooltip.css) (lines 447-622)
- **Positioning strategy**: [research.md § Tooltip Positioning Strategy](research.md#2-tooltip-positioning-strategy) (Decision section)
- **Animation timing**: [research.md § Hover Timing Best Practices](research.md#1-hover-timing-best-practices) (150ms fade)

**Initial Structure**:
```css
/* frontend/src/components/dashboard/SocialStatTooltip.css */

.social-stat-card--with-tooltip {
  position: relative;
  cursor: pointer;
}

.social-stat-tooltip {
  /* TODO: Implement in Task 3.1 */
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--surface-elevated);
  border: 1px solid var(--border-emphasis);
  z-index: 1000;
}
```

**Checklist**:
- [ ] File created at correct path
- [ ] Uses CSS custom properties (--surface-elevated, etc.)
- [ ] Basic positioning skeleton
- [ ] No full styles yet (Task 3.1)

---

### PHASE 2: Core Implementation (TDD)

#### Task 2.1: Implement useFollowersTooltip Hook (Test First)

**Test File**: `frontend/tests/unit/useFollowersTooltip.test.ts` (create new)

**What**: Write tests FIRST, then implement hook logic

**Test Scenarios** (from [quickstart.md § Test Tooltip Feature](quickstart.md#5-verify-followers-tooltip)):
1. Initial state: users=[], totalCount=0, isLoading=false, error=null
2. Loading state: isLoading=true while fetching
3. Success state: users populated with first 8, totalCount set
4. Error state: error="Error al cargar usuarios" on network failure
5. Empty state: users=[], totalCount=0 when user has 0 followers
6. Cleanup: state cleared on unmount

**Test Code Example**:
```typescript
// frontend/tests/unit/useFollowersTooltip.test.ts

import { renderHook, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { useFollowersTooltip } from '../../src/hooks/useFollowersTooltip';
import * as followService from '../../src/services/followService';

describe('useFollowersTooltip', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return initial state', () => {
    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    expect(result.current.users).toEqual([]);
    expect(result.current.totalCount).toBe(0);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should set loading state when fetching', async () => {
    vi.spyOn(followService, 'getFollowers').mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    result.current.fetchUsers();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(true);
    });
  });

  it('should populate users with first 8 on success', async () => {
    const mockResponse = {
      followers: Array.from({ length: 12 }, (_, i) => ({
        user_id: `user-${i}`,
        username: `user${i}`,
        profile_photo_url: null,
      })),
      total_count: 12,
    };

    vi.spyOn(followService, 'getFollowers').mockResolvedValue(mockResponse);

    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    await result.current.fetchUsers();

    await waitFor(() => {
      expect(result.current.users).toHaveLength(8); // Sliced to 8
      expect(result.current.totalCount).toBe(12);
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('should set error state on network failure', async () => {
    vi.spyOn(followService, 'getFollowers').mockRejectedValue(
      new Error('Network error')
    );

    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    await result.current.fetchUsers();

    await waitFor(() => {
      expect(result.current.error).toBe('Error al cargar usuarios');
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('should handle empty followers list', async () => {
    vi.spyOn(followService, 'getFollowers').mockResolvedValue({
      followers: [],
      total_count: 0,
    });

    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    await result.current.fetchUsers();

    await waitFor(() => {
      expect(result.current.users).toEqual([]);
      expect(result.current.totalCount).toBe(0);
    });
  });

  it('should cleanup state on unmount', () => {
    const { result, unmount } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    // Populate some state
    result.current.fetchUsers();

    unmount();

    // State should be cleared (no memory leaks)
    // (Tested via no errors/warnings in console)
  });
});
```

**Implementation** (after tests fail - RED):

**References**:
- **Full implementation**: [ANALISIS_TOOLTIP_FOLLOWERS.md § useFollowersTooltip](../ANALISIS_TOOLTIP_FOLLOWERS.md#41-nuevo-hook-usefollowerstooltip) (lines 172-199)
- **useCallback pattern**: [research.md § React Hook Performance Patterns](research.md#5-react-hook-performance-patterns) (useCallback section)
- **Cleanup pattern**: [research.md § React Hook Performance Patterns](research.md#5-react-hook-performance-patterns) (Memory Leak Prevention)

**Implementation Steps**:
1. Add useState for users, totalCount, isLoading, error
2. Implement fetchUsers with useCallback
3. Call getFollowers or getFollowing based on type
4. Slice response to first 8 users
5. Handle errors with Spanish message
6. Add useEffect cleanup to reset state on unmount
7. Run tests → should PASS (GREEN)

**Checklist**:
- [ ] Tests written FIRST (6 test cases)
- [ ] Tests fail initially (RED)
- [ ] Implementation makes tests pass (GREEN)
- [ ] useCallback used for fetchUsers
- [ ] Cleanup in useEffect return
- [ ] Coverage ≥90% for hook file

---

#### Task 2.2: Implement SocialStatTooltip Component (Test First)

**Test File**: `frontend/tests/unit/SocialStatTooltip.test.tsx` (create new)

**What**: Write tests FIRST, then implement component rendering logic

**Test Scenarios**:
1. Hidden state: returns null when visible=false
2. Loading state: shows spinner + "Cargando..."
3. Error state: shows error message
4. Empty state (0 followers): shows "No tienes seguidores aún"
5. Empty state (0 following): shows "No sigues a nadie aún"
6. User list: renders 8 users with avatars + usernames
7. "Ver todos" link: shown when totalCount > users.length
8. No "Ver todos" link: hidden when totalCount === users.length
9. ARIA attributes: role="tooltip", aria-live="polite"

**Test Code Example**:
```typescript
// frontend/tests/unit/SocialStatTooltip.test.tsx

import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { SocialStatTooltip } from '../../src/components/dashboard/SocialStatTooltip';
import type { UserSummaryForFollow } from '../../src/types/follow';

const mockUsers: UserSummaryForFollow[] = [
  { user_id: '1', username: 'user1', profile_photo_url: 'photo1.jpg' },
  { user_id: '2', username: 'user2', profile_photo_url: null },
];

const renderWithRouter = (ui: React.ReactElement) => {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe('SocialStatTooltip', () => {
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
    expect(screen.getByAltText('user1')).toHaveAttribute('src', 'photo1.jpg');
    expect(screen.getByText('U')).toBeInTheDocument(); // Placeholder for user2
  });

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
});
```

**Implementation** (after tests fail - RED):

**References**:
- **Full implementation**: [ANALISIS_TOOLTIP_FOLLOWERS.md § SocialStatTooltip](../ANALISIS_TOOLTIP_FOLLOWERS.md#42-nuevo-componente-socialstattooltip) (lines 222-290)
- **Conditional rendering**: [data-model.md § Rendering Logic](data-model.md#5-socialstattooltipprops-new) (lines 215-218)

**Implementation Steps**:
1. Add early return if !visible
2. Calculate `remaining = totalCount - users.length`
3. Render loading state if isLoading
4. Render error state if error
5. Render empty state if users.length === 0
6. Render user list with map()
7. Render "Ver todos" link if remaining > 0
8. Add ARIA attributes
9. Run tests → should PASS (GREEN)

**Checklist**:
- [ ] Tests written FIRST (9 test cases)
- [ ] Tests fail initially (RED)
- [ ] Implementation makes tests pass (GREEN)
- [ ] All states handled (loading, error, empty, list)
- [ ] ARIA attributes correct
- [ ] Coverage ≥90% for component file

---

### PHASE 3: Styling & Polish

#### Task 3.1: Implement Tooltip CSS

**File**: `frontend/src/components/dashboard/SocialStatTooltip.css`

**What**: Implement complete CSS with positioning, animations, responsive design

**References**:
- **Complete CSS**: [ANALISIS_TOOLTIP_FOLLOWERS.md § SocialStatTooltip.css](../ANALISIS_TOOLTIP_FOLLOWERS.md#44-css-socialstattooltip.css) (lines 448-622)
- **Positioning strategy**: [research.md § Tooltip Positioning Strategy](research.md#2-tooltip-positioning-strategy) (absolute positioning, arrow, max-width)
- **Animation timing**: [research.md § Hover Timing Best Practices](research.md#1-hover-timing-best-practices) (150ms fade-in/out)
- **Accessibility colors**: [research.md § Accessibility Patterns](research.md#3-accessibility-patterns-for-tooltips) (color contrast section)

**Implementation Sections**:

1. **Tooltip Container** (positioning, sizing, shadows):
```css
.social-stat-tooltip {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);

  background: var(--surface-elevated);
  border: 1px solid var(--border-emphasis);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

  padding: var(--space-3);
  min-width: 220px;
  max-width: min(280px, 90vw); /* Responsive */
  z-index: 1000;

  animation: tooltip-fade-in 150ms ease-out;
}
```

2. **Arrow** (pointing up to card):
```css
.social-stat-tooltip::before {
  content: '';
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 8px solid var(--border-emphasis);
}

.social-stat-tooltip::after {
  content: '';
  position: absolute;
  top: -7px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 8px solid var(--surface-elevated);
}
```

3. **Animation** (fade-in/out):
```css
@keyframes tooltip-fade-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
```

4. **User List** (avatars, usernames, hover effects):
```css
.social-stat-tooltip__user-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--text-primary);
  transition: background 0.15s ease;
}

.social-stat-tooltip__user-link:hover {
  background: var(--surface-hover);
}

.social-stat-tooltip__avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.social-stat-tooltip__avatar--placeholder {
  background: var(--accent-moss);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.social-stat-tooltip__username {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* Truncate long usernames */
}
```

5. **"Ver todos" Link**:
```css
.social-stat-tooltip__view-all {
  display: block;
  margin-top: var(--space-2);
  padding: var(--space-2);
  text-align: center;
  font-size: 12px;
  font-weight: 500;
  color: var(--accent-amber);
  text-decoration: none;
  border-top: 1px solid var(--border-soft);
  transition: color 0.15s ease;
}

.social-stat-tooltip__view-all:hover {
  color: var(--accent-amber-hover);
  text-decoration: underline;
}
```

6. **Responsive** (mobile):
```css
@media (max-width: 768px) {
  .social-stat-tooltip {
    min-width: 200px;
    max-width: 240px;
  }
}
```

**Testing** (manual in browser):
- [ ] Tooltip appears centered below card
- [ ] Arrow points up to card
- [ ] Fade-in animation smooth (150ms)
- [ ] Usernames truncate with ellipsis if too long
- [ ] "Ver todos" link has hover effect
- [ ] Responsive on mobile (max-width adapts)
- [ ] No layout shift (CLS = 0)

**Checklist**:
- [ ] All CSS sections implemented
- [ ] Uses CSS custom properties (--surface-*, --space-*, etc.)
- [ ] Animations smooth (150ms timing)
- [ ] Responsive breakpoint at 768px
- [ ] Tested in browser (no visual bugs)

---

### PHASE 4: Integration

#### Task 4.1: Modify SocialStatsSection Component

**File**: `frontend/src/components/dashboard/SocialStatsSection.tsx` (MODIFY existing)

**What**: Integrate tooltip hooks and components with hover handlers

**References**:
- **Full integration code**: [ANALISIS_TOOLTIP_FOLLOWERS.md § SocialStatsSection](../ANALISIS_TOOLTIP_FOLLOWERS.md#43-modificación-de-socialstatssectiontsx) (lines 297-441)
- **Hover timing**: [research.md § Hover Timing Best Practices](research.md#1-hover-timing-best-practices) (500ms entry, 200ms exit)
- **Mobile detection**: [research.md § Mobile Touch Device Fallback](research.md#4-mobile-touch-device-fallback) (window.matchMedia)

**Implementation Steps**:

1. **Import new dependencies**:
```typescript
import { useState } from 'react';
import { useFollowersTooltip } from '../../hooks/useFollowersTooltip';
import { SocialStatTooltip } from './SocialStatTooltip';
```

2. **Add state for tooltip visibility**:
```typescript
const [activeTooltip, setActiveTooltip] = useState<'followers' | 'following' | null>(null);
const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);
```

3. **Initialize tooltip hooks**:
```typescript
const followersTooltip = useFollowersTooltip(user?.username || '', 'followers');
const followingTooltip = useFollowersTooltip(user?.username || '', 'following');
```

4. **Add hover handlers** (500ms delay):
```typescript
const handleMouseEnter = (type: 'followers' | 'following') => {
  if (hoverTimeout) clearTimeout(hoverTimeout);

  const timeout = setTimeout(() => {
    setActiveTooltip(type);

    if (type === 'followers') {
      followersTooltip.fetchUsers();
    } else {
      followingTooltip.fetchUsers();
    }
  }, 500); // 500ms delay

  setHoverTimeout(timeout);
};

const handleMouseLeave = () => {
  if (hoverTimeout) clearTimeout(hoverTimeout);

  const timeout = setTimeout(() => {
    setActiveTooltip(null);
  }, 200); // 200ms delay

  setHoverTimeout(timeout);
};
```

5. **Add cleanup on unmount**:
```typescript
useEffect(() => {
  return () => {
    if (hoverTimeout) clearTimeout(hoverTimeout);
  };
}, [hoverTimeout]);
```

6. **Update card markup** (add hover handlers + tooltip):
```typescript
<div
  className="social-stat-card social-stat-card--with-tooltip"
  onMouseEnter={() => handleMouseEnter('followers')}
  onMouseLeave={handleMouseLeave}
  onFocus={() => handleMouseEnter('followers')} // Keyboard accessibility
  onBlur={handleMouseLeave}
  tabIndex={0} // Make focusable
  aria-describedby={activeTooltip === 'followers' ? 'followers-tooltip' : undefined}
>
  {/* Existing card content */}

  {/* NEW: Tooltip */}
  <SocialStatTooltip
    users={followersTooltip.users}
    totalCount={followersTooltip.totalCount}
    type="followers"
    username={user?.username || ''}
    isLoading={followersTooltip.isLoading}
    error={followersTooltip.error}
    visible={activeTooltip === 'followers'}
  />
</div>
```

7. **Repeat for "Siguiendo" card** (change type to 'following')

**Testing** (manual in browser):
- [ ] Hover over "Seguidores" card for 500ms → tooltip appears
- [ ] Move mouse away → tooltip disappears after 200ms
- [ ] Move mouse from card to tooltip → tooltip stays open
- [ ] Tab to card → tooltip appears after 500ms (keyboard)
- [ ] Press Escape → tooltip closes immediately
- [ ] Quick hover (<500ms) → no tooltip appears

**Checklist**:
- [ ] Hooks imported and initialized
- [ ] State for activeTooltip and hoverTimeout added
- [ ] Hover handlers with correct timing (500ms, 200ms)
- [ ] Cleanup in useEffect
- [ ] Both cards updated (followers + following)
- [ ] ARIA attributes added
- [ ] CSS import added for SocialStatTooltip.css
- [ ] Manual testing passes

---

### PHASE 5: E2E Testing

#### Task 5.1: Write E2E Tests (Playwright)

**File**: `frontend/tests/e2e/dashboard-tooltips.spec.ts` (create new)

**What**: End-to-end tests for tooltip behavior in real browser

**Test Scenarios** (from [quickstart.md § Test Tooltip Feature](quickstart.md#5-verify-followers-tooltip)):
1. Hover followers card → tooltip appears
2. Tooltip shows user list
3. Click username → navigate to user profile
4. Click "Ver todos" → navigate to full list page
5. Quick hover (<500ms) → no tooltip
6. Mouse leave → tooltip disappears after 200ms
7. Keyboard Tab → tooltip appears
8. Press Escape → tooltip closes

**Test Code**:
```typescript
// frontend/tests/e2e/dashboard-tooltips.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Dashboard Tooltips', () => {
  test.beforeEach(async ({ page }) => {
    // Login as test user with followers
    await page.goto('/login');
    await page.fill('input[name="username"]', 'maria_garcia');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should show followers tooltip on hover', async ({ page }) => {
    const followersCard = page.locator('.social-stat-card').first();

    // Hover over card
    await followersCard.hover();

    // Wait for 500ms hover delay
    await page.waitForTimeout(600);

    // Tooltip should be visible
    const tooltip = page.locator('.social-stat-tooltip');
    await expect(tooltip).toBeVisible();
    await expect(tooltip).toContainText('Seguidores');
  });

  test('should show user list in tooltip', async ({ page }) => {
    const followersCard = page.locator('.social-stat-card').first();
    await followersCard.hover();
    await page.waitForTimeout(600);

    // Should show user links
    const userLinks = page.locator('.social-stat-tooltip__user-link');
    expect(await userLinks.count()).toBeGreaterThan(0);

    // Should show usernames
    await expect(page.locator('.social-stat-tooltip__username').first()).toBeVisible();
  });

  test('should navigate to user profile on username click', async ({ page }) => {
    const followersCard = page.locator('.social-stat-card').first();
    await followersCard.hover();
    await page.waitForTimeout(600);

    // Click first username
    const firstUser = page.locator('.social-stat-tooltip__user-link').first();
    const username = await firstUser.locator('.social-stat-tooltip__username').textContent();
    await firstUser.click();

    // Should navigate to user profile
    await expect(page).toHaveURL(new RegExp(`/users/${username}`));
  });

  test('should navigate to full list on "Ver todos" click', async ({ page }) => {
    // Assuming user has > 8 followers
    const followersCard = page.locator('.social-stat-card').first();
    await followersCard.hover();
    await page.waitForTimeout(600);

    const viewAllLink = page.locator('.social-stat-tooltip__view-all');
    if (await viewAllLink.isVisible()) {
      await viewAllLink.click();
      await expect(page).toHaveURL(/\/users\/.*\/followers/);
    }
  });

  test('should NOT show tooltip on quick hover', async ({ page }) => {
    const followersCard = page.locator('.social-stat-card').first();

    // Quick hover (less than 500ms)
    await followersCard.hover();
    await page.waitForTimeout(300); // Only 300ms
    await page.mouse.move(0, 0); // Move away

    // Tooltip should NOT be visible
    const tooltip = page.locator('.social-stat-tooltip');
    await expect(tooltip).not.toBeVisible();
  });

  test('should hide tooltip after mouse leave', async ({ page }) => {
    const followersCard = page.locator('.social-stat-card').first();
    await followersCard.hover();
    await page.waitForTimeout(600);

    // Tooltip visible
    const tooltip = page.locator('.social-stat-tooltip');
    await expect(tooltip).toBeVisible();

    // Move mouse away
    await page.mouse.move(0, 0);

    // Wait for 200ms leave delay
    await page.waitForTimeout(300);

    // Tooltip should be hidden
    await expect(tooltip).not.toBeVisible();
  });

  test('should show tooltip on keyboard focus', async ({ page }) => {
    // Tab to followers card
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab'); // May need multiple tabs depending on page structure

    // Wait for 500ms focus delay
    await page.waitForTimeout(600);

    // Tooltip should be visible
    const tooltip = page.locator('.social-stat-tooltip');
    await expect(tooltip).toBeVisible();
  });

  test('should close tooltip on Escape key', async ({ page }) => {
    const followersCard = page.locator('.social-stat-card').first();
    await followersCard.hover();
    await page.waitForTimeout(600);

    // Tooltip visible
    const tooltip = page.locator('.social-stat-tooltip');
    await expect(tooltip).toBeVisible();

    // Press Escape
    await page.keyboard.press('Escape');

    // Tooltip should close immediately
    await expect(tooltip).not.toBeVisible();
  });
});
```

**Checklist**:
- [ ] All 8 test scenarios pass
- [ ] Tests run in real browser (not JSDOM)
- [ ] 500ms hover delay verified
- [ ] 200ms leave delay verified
- [ ] Keyboard navigation works
- [ ] Navigation assertions pass

---

### PHASE 6: Accessibility Validation

#### Task 6.1: Validate WCAG 2.1 AA Compliance

**What**: Run automated accessibility tests and manual validation

**References**:
- **WCAG requirements**: [research.md § Accessibility Patterns](research.md#3-accessibility-patterns-for-tooltips) (ARIA attributes, keyboard navigation, color contrast)
- **Manual testing**: [quickstart.md § Test Accessibility](quickstart.md#11-keyboard-navigation) (keyboard nav, screen reader)

**Automated Tests** (axe-core):

1. Install axe Playwright plugin (if not already):
```bash
npm install --save-dev @axe-core/playwright
```

2. Create accessibility test file:
```typescript
// frontend/tests/e2e/dashboard-tooltips-a11y.spec.ts

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Dashboard Tooltips Accessibility', () => {
  test('should have no accessibility violations', async ({ page }) => {
    await page.goto('/dashboard');

    // Trigger tooltip
    const followersCard = page.locator('.social-stat-card').first();
    await followersCard.hover();
    await page.waitForTimeout(600);

    // Run axe scan
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
```

**Manual Validation Checklist**:

- [ ] **ARIA Attributes**:
  - [ ] Tooltip has `role="tooltip"`
  - [ ] Card has `aria-describedby` when tooltip visible
  - [ ] Loading state has `aria-live="polite"`
  - [ ] Tooltip has `aria-hidden` when not visible

- [ ] **Keyboard Navigation**:
  - [ ] Tab key focuses on card
  - [ ] Focus triggers tooltip after 500ms
  - [ ] Tab moves focus to first username link in tooltip
  - [ ] Tab cycles through all links in tooltip
  - [ ] Escape key closes tooltip immediately
  - [ ] Enter key activates focused link

- [ ] **Color Contrast** (use browser DevTools):
  - [ ] Body text: ≥4.5:1 contrast ratio
  - [ ] Link text: ≥4.5:1 contrast ratio
  - [ ] UI components: ≥3:1 contrast ratio

- [ ] **Screen Reader** (optional, use NVDA/JAWS/VoiceOver):
  - [ ] Card announces "Seguidores, 4, tarjeta"
  - [ ] Loading state announces "Cargando..."
  - [ ] Username links announce "Juan Perez, enlace"
  - [ ] "Ver todos" link announces "Ver todos, enlace"

**Checklist**:
- [ ] Axe automated tests pass (0 violations)
- [ ] All ARIA attributes validated
- [ ] Keyboard navigation works completely
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader testing done (optional but recommended)

---

### PHASE 7: Performance & Polish

#### Task 7.1: Verify Performance Requirements

**What**: Validate performance metrics match success criteria

**References**:
- **Success criteria**: [spec.md § Success Criteria](spec.md#success-criteria-mandatory) (SC-001, SC-010, SC-013)
- **Performance testing**: [quickstart.md § Test Performance](quickstart.md#14-verify-lazy-loading)

**Performance Checks**:

1. **SC-001: <1s tooltip display**:
   - [ ] Open DevTools Network tab
   - [ ] Hover over card
   - [ ] Measure time from hover to tooltip display
   - [ ] Target: <1s (500ms delay + <500ms API response)

2. **SC-010: <100ms loading state**:
   - [ ] Throttle network to Slow 3G
   - [ ] Hover over card
   - [ ] Loading spinner appears within 100ms of hover trigger
   - [ ] Target: <100ms (should be ~0ms due to immediate setState)

3. **SC-013: No dashboard load impact**:
   - [ ] Open DevTools Network tab
   - [ ] Navigate to /dashboard
   - [ ] Verify NO API calls to /users/.../followers or /users/.../following
   - [ ] Hover over card → API call happens ONLY after hover
   - [ ] Target: 0 API calls on dashboard load

4. **CLS = 0 (no layout shift)**:
   - [ ] Open DevTools Performance tab
   - [ ] Record page load + tooltip trigger
   - [ ] Check Cumulative Layout Shift metric
   - [ ] Target: CLS = 0 (tooltip uses absolute positioning)

**Network Efficiency**:
- [ ] Tooltip response size ≤2KB (~200 bytes/user × 8 users)
- [ ] No redundant API calls (cache for 200ms leave delay window)

**Checklist**:
- [ ] All performance criteria met
- [ ] Lazy loading verified (no calls on mount)
- [ ] Response times <1s
- [ ] CLS = 0 (no layout shift)
- [ ] Network requests optimized

---

#### Task 7.2: Mobile Testing & Touch Fallback

**What**: Verify progressive enhancement on touch devices

**References**:
- **Mobile fallback**: [research.md § Mobile Touch Device Fallback](research.md#4-mobile-touch-device-fallback) (direct navigation)
- **Testing**: [quickstart.md § Test Mobile Touch Devices](quickstart.md#13-touch-device-fallback)

**Mobile Simulation** (Chrome DevTools):

1. Open DevTools → Toggle device toolbar (Ctrl+Shift+M)
2. Select "iPhone 12 Pro"
3. Navigate to /dashboard
4. Tap "Seguidores" card
5. Expected: Navigate directly to `/users/{username}/followers` (no tooltip)

**Implementation Check**:
```typescript
// Verify this code exists in SocialStatsSection.tsx
const isTouchDevice = window.matchMedia('(hover: none)').matches;

const handleInteraction = isTouchDevice
  ? () => navigate(`/users/${username}/followers`)
  : () => handleMouseEnter('followers');
```

**Checklist**:
- [ ] Touch device detection implemented
- [ ] Tap on touch → direct navigation (no tooltip)
- [ ] Hover on desktop → tooltip appears
- [ ] Tested on real mobile device (optional)

---

### PHASE 8: Documentation & Final Checklist

#### Task 8.1: Update Feature Documentation

**What**: Document implementation patterns in CLAUDE.md (already done)

**References**:
- **Pattern examples**: See CLAUDE.md § Dashboard Followers/Following Tooltips (already updated)

**Checklist**:
- [X] CLAUDE.md updated with tooltip patterns (completed in commit a85fbc7)
- [X] Active Technologies section updated
- [X] Common Pitfalls documented

---

#### Task 8.2: Final Quality Checklist

**What**: Verify all requirements before merging to develop

**Functional Requirements** (from [spec.md § Requirements](spec.md#requirements-mandatory)):

FR-001 to FR-025:
- [ ] FR-001: Tooltip appears on hover after 500ms (Seguidores)
- [ ] FR-002: Tooltip appears on hover after 500ms (Siguiendo)
- [ ] FR-003: Lazy loading (no fetch on dashboard load)
- [ ] FR-004: Shows first 5-8 users
- [ ] FR-005: Avatar + username shown for each user
- [ ] FR-006: "Ver todos" link when totalCount > preview
- [ ] FR-007: Click username → navigate to /users/{username}
- [ ] FR-008: "Ver todos" → navigate to /users/{username}/followers
- [ ] FR-009: "Ver todos" → navigate to /users/{username}/following
- [ ] FR-010: Tooltip disappears 200ms after mouse leave
- [ ] FR-011: Tooltip stays open when mouse moves to tooltip
- [ ] FR-012: Loading state with spinner + "Cargando..."
- [ ] FR-013: Error message "Error al cargar usuarios"
- [ ] FR-014: Empty state "No tienes seguidores aún"
- [ ] FR-015: Empty state "No sigues a nadie aún"
- [ ] FR-016: Uses existing endpoints (no backend changes)
- [ ] FR-017: Placeholder avatar when no photo
- [ ] FR-018: Centered below card with 8px spacing
- [ ] FR-019: Arrow pointing to card
- [ ] FR-020: Truncates long usernames with ellipsis
- [ ] FR-021: Fade-in animation 150ms
- [ ] FR-022: Fade-out animation 150ms
- [ ] FR-023: Touch devices navigate directly (no tooltip)
- [ ] FR-024: Keyboard navigation (Tab, focus, Escape)
- [ ] FR-025: ARIA attributes (role, aria-live, aria-describedby)

**Success Criteria** (from [spec.md § Success Criteria](spec.md#success-criteria-mandatory)):

- [ ] SC-001: <1s tooltip display
- [ ] SC-002: No visual jank or layout shift
- [ ] SC-003: 90% organic discovery (user testing - optional)
- [ ] SC-004: 2 clicks to profile (hover → click username)
- [ ] SC-005: 60% reduced navigation (analytics - post-launch)
- [ ] SC-006: Works on Chrome, Firefox, Safari, Edge
- [ ] SC-007: Graceful mobile degradation
- [ ] SC-008: Keyboard accessibility
- [ ] SC-009: Screen reader announces content
- [ ] SC-010: <100ms loading state appearance
- [ ] SC-011: <5% accidental triggers (500ms delay)
- [ ] SC-012: Mouse can move to tooltip without closing
- [ ] SC-013: No dashboard load time impact
- [ ] SC-014: Handles edge cases (0 followers, errors, long names)
- [ ] SC-015: WCAG 2.1 AA compliance (axe-core)

**Testing Coverage**:
- [ ] Unit tests: useFollowersTooltip (6 tests)
- [ ] Unit tests: SocialStatTooltip (9 tests)
- [ ] E2E tests: Tooltip behavior (8 tests)
- [ ] Accessibility tests: axe-core scan
- [ ] Manual testing: All quickstart scenarios
- [ ] Coverage: ≥90% for new files

**Code Quality**:
- [ ] TypeScript strict mode (no `any` types)
- [ ] ESLint passes (0 warnings)
- [ ] Prettier formatted
- [ ] No console.log statements
- [ ] All imports organized

**Git**:
- [ ] All commits follow conventional format
- [ ] Co-authored by Claude
- [ ] Meaningful commit messages
- [ ] No merge conflicts

---

## Summary of Cross-References

### Research → Implementation

| Implementation Step | Research Section | File Location |
|---------------------|------------------|---------------|
| Hover timing (500ms/200ms) | Hover Timing Best Practices | [research.md § 1](research.md#1-hover-timing-best-practices) |
| CSS positioning (absolute) | Tooltip Positioning Strategy | [research.md § 2](research.md#2-tooltip-positioning-strategy) |
| ARIA attributes | Accessibility Patterns | [research.md § 3](research.md#3-accessibility-patterns-for-tooltips) |
| Mobile fallback | Mobile Touch Device Fallback | [research.md § 4](research.md#4-mobile-touch-device-fallback) |
| useCallback + cleanup | React Hook Performance Patterns | [research.md § 5](research.md#5-react-hook-performance-patterns) |

### Data Model → Implementation

| Implementation Step | Data Model Section | File Location |
|---------------------|---------------------|---------------|
| Hook return type | UseFollowersTooltipReturn | [data-model.md § 4](data-model.md#4-usefollowerstooltipreturn-new) |
| Component props | SocialStatTooltipProps | [data-model.md § 5](data-model.md#5-socialstattooltipprops-new) |
| Rendering logic | Rendering Logic | [data-model.md § 5](data-model.md#5-socialstattooltipprops-new) |
| Edge cases | Edge Cases | [data-model.md § Edge Cases](data-model.md#edge-cases) |

### Code Examples → Implementation

| Implementation Step | Example Code | File Location |
|---------------------|--------------|---------------|
| useFollowersTooltip full implementation | Hook example (172-199) | [ANALISIS § 4.1](../ANALISIS_TOOLTIP_FOLLOWERS.md#41-nuevo-hook-usefollowerstooltip) |
| SocialStatTooltip full implementation | Component example (222-290) | [ANALISIS § 4.2](../ANALISIS_TOOLTIP_FOLLOWERS.md#42-nuevo-componente-socialstattooltip) |
| SocialStatsSection integration | Integration example (297-441) | [ANALISIS § 4.3](../ANALISIS_TOOLTIP_FOLLOWERS.md#43-modificación-de-socialstatssectiontsx) |
| Complete CSS | CSS example (448-622) | [ANALISIS § 4.4](../ANALISIS_TOOLTIP_FOLLOWERS.md#44-css-socialstattooltip.css) |

### Test Scenarios → Implementation

| Test Type | Scenarios | File Location |
|-----------|-----------|---------------|
| Manual testing | 18 scenarios (hover, empty, error, etc.) | [quickstart.md § 5-13](quickstart.md#5-verify-followers-tooltip) |
| Unit tests (hook) | 6 test cases | This guide § Task 2.1 |
| Unit tests (component) | 9 test cases | This guide § Task 2.2 |
| E2E tests | 8 test cases | This guide § Task 5.1 |
| Accessibility | 4 validation areas | This guide § Task 6.1 |

---

## Estimated Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Setup | 1.1 - 1.3 | 30 min |
| Phase 2: Core (TDD) | 2.1 - 2.2 | 2-3 hours |
| Phase 3: Styling | 3.1 | 1 hour |
| Phase 4: Integration | 4.1 | 1 hour |
| Phase 5: E2E Testing | 5.1 | 1 hour |
| Phase 6: Accessibility | 6.1 | 1 hour |
| Phase 7: Performance | 7.1 - 7.2 | 30 min |
| Phase 8: Documentation | 8.1 - 8.2 | 30 min |
| **Total** | **16 tasks** | **7-8 hours** |

---

**Last Updated**: 2026-02-13
**Related Files**:
- [plan.md](plan.md) - High-level implementation plan
- [research.md](research.md) - Technical decisions and rationale
- [data-model.md](data-model.md) - TypeScript interfaces
- [quickstart.md](quickstart.md) - Local testing guide
- [spec.md](spec.md) - Feature requirements
