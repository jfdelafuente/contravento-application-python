/**
 * useTripStatusCounts Hook
 *
 * Fetches trip counts by status (all, published, draft) for status filter buttons.
 * Only runs when showStatusFilter is true (viewing own trips).
 *
 * @example
 * const { allCount, publishedCount, draftCount, isLoading } = useTripStatusCounts({
 *   username: 'testuser',
 *   enabled: showStatusFilter,
 * });
 */

import { useState, useEffect } from 'react';
import { getUserTrips } from '../services/tripService';

interface UseTripStatusCountsParams {
  /** Username to get counts for */
  username: string;
  /** Whether to fetch counts (only when viewing own trips) */
  enabled: boolean;
}

interface UseTripStatusCountsReturn {
  /** Total count (all statuses) */
  allCount: number;
  /** Published trips count */
  publishedCount: number;
  /** Draft trips count */
  draftCount: number;
  /** Loading state */
  isLoading: boolean;
}

export const useTripStatusCounts = ({
  username,
  enabled,
}: UseTripStatusCountsParams): UseTripStatusCountsReturn => {
  const [allCount, setAllCount] = useState(0);
  const [publishedCount, setPublishedCount] = useState(0);
  const [draftCount, setDraftCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!enabled || !username) {
      return;
    }

    const fetchCounts = async () => {
      setIsLoading(true);
      try {
        // Fetch counts for each status in parallel
        const [allResponse, publishedResponse, draftResponse] = await Promise.all([
          getUserTrips(username, { limit: 1, offset: 0 }), // All
          getUserTrips(username, { limit: 1, offset: 0, status: 'published' }),
          getUserTrips(username, { limit: 1, offset: 0, status: 'draft' }),
        ]);

        setAllCount(allResponse.total);
        setPublishedCount(publishedResponse.total);
        setDraftCount(draftResponse.total);
      } catch (error) {
        console.error('Error fetching status counts:', error);
        // Keep zeros on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchCounts();
  }, [username, enabled]);

  return {
    allCount,
    publishedCount,
    draftCount,
    isLoading,
  };
};
