/**
 * useFollowersTooltip Hook
 *
 * Custom hook for fetching and managing followers/following tooltip data.
 * Implements lazy loading on hover with proper error handling.
 *
 * @see specs/019-followers-tooltip/IMPLEMENTATION_GUIDE.md § Task 2.1
 * @see specs/019-followers-tooltip/research.md § 5 (React Hook Performance Patterns)
 * @see specs/019-followers-tooltip/data-model.md § 4 (UseFollowersTooltipReturn interface)
 * @see specs/ANALISIS_TOOLTIP_FOLLOWERS.md lines 147-198
 */

import { useState, useCallback } from 'react';
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
  const [users, setUsers] = useState<UserSummaryForFollow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    if (!username) return;

    setIsLoading(true);
    setError(null);

    try {
      const response =
        type === 'followers'
          ? await getFollowers(username)
          : await getFollowing(username);

      // Solo primeros 8 para tooltip
      const userList = type === 'followers' ? response.followers : response.following;
      const topUsers = (userList || []).slice(0, 8);

      setUsers(topUsers);
      setTotalCount(response.total_count || 0);
    } catch (err: any) {
      // Always use Spanish error message
      setError('Error al cargar usuarios');
      console.error(`Error fetching ${type}:`, err);
    } finally {
      setIsLoading(false);
    }
  }, [username, type]);

  return { users, totalCount, isLoading, error, fetchUsers };
}
