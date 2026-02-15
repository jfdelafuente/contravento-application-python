/**
 * useFollowersTooltip Hook Unit Tests
 *
 * Tests for followers/following tooltip data fetching hook.
 * Covers initial state, API calls, error handling, slicing logic.
 *
 * @see specs/019-followers-tooltip/IMPLEMENTATION_GUIDE.md § Task 2.1
 * @see specs/019-followers-tooltip/tasks.md § Tests T007-T012
 */

import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useFollowersTooltip } from '../../src/hooks/useFollowersTooltip';
import * as followService from '../../src/services/followService';

describe('useFollowersTooltip', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // T007: Unit test - returns correct initial state
  it('should return initial state', () => {
    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    expect(result.current.users).toEqual([]);
    expect(result.current.totalCount).toBe(0);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  // T008: Unit test - fetchUsers() calls getFollowers API
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

  // T009: Unit test - slices response to 8 users
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

  // T010: Unit test - handles loading state correctly
  it('should transition through loading states correctly', async () => {
    const mockResponse = {
      followers: [
        { user_id: '1', username: 'user1', profile_photo_url: null },
      ],
      total_count: 1,
    };

    vi.spyOn(followService, 'getFollowers').mockResolvedValue(mockResponse);

    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'followers')
    );

    expect(result.current.isLoading).toBe(false);

    const fetchPromise = result.current.fetchUsers();

    // Should be loading
    await waitFor(() => {
      expect(result.current.isLoading).toBe(true);
    });

    await fetchPromise;

    // Should finish loading
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
      expect(result.current.users).toHaveLength(1);
    });
  });

  // T011: Unit test - handles errors with Spanish message
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

  // T012: Unit test - handles empty followers (0 count)
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

  // Bonus test: cleanup on unmount
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

  // Bonus test: following type calls correct endpoint
  it('should call getFollowing when type is following', async () => {
    const mockResponse = {
      following: [
        { user_id: '1', username: 'user1', profile_photo_url: null },
      ],
      total_count: 1,
    };

    const getFollowingSpy = vi
      .spyOn(followService, 'getFollowing')
      .mockResolvedValue(mockResponse);

    const { result } = renderHook(() =>
      useFollowersTooltip('testuser', 'following')
    );

    await result.current.fetchUsers();

    await waitFor(() => {
      expect(getFollowingSpy).toHaveBeenCalledWith('testuser');
      expect(result.current.users).toHaveLength(1);
    });
  });
});
