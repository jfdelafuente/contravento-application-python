/**
 * useTripFilters Hook
 *
 * Custom hook for managing trip filter state (search, tags, status, pagination).
 * Provides handlers for updating filters and resetting pagination when filters change.
 *
 * Used in:
 * - TripsListPage (main trips grid)
 */

import { useState, useCallback, useEffect } from 'react';

interface UseTripFiltersReturn {
  /** Current search query */
  searchQuery: string;
  /** Set search query */
  setSearchQuery: (query: string) => void;

  /** Currently selected tag (null if none) */
  selectedTag: string | null;
  /** Set selected tag */
  setSelectedTag: (tag: string | null) => void;

  /** Currently selected status (null shows both) */
  selectedStatus: 'draft' | 'published' | null;
  /** Set selected status */
  setSelectedStatus: (status: 'draft' | 'published' | null) => void;

  /** Current page offset for pagination */
  offset: number;
  /** Set page offset */
  setOffset: (offset: number) => void;

  /** Items per page */
  limit: number;
  /** Set items per page */
  setLimit: (limit: number) => void;

  /** Reset all filters to defaults */
  resetFilters: () => void;

  /** Go to next page */
  nextPage: () => void;

  /** Go to previous page */
  previousPage: () => void;

  /** Go to specific page (1-indexed) */
  goToPage: (page: number) => void;

  /** Whether any filters are active */
  hasActiveFilters: boolean;
}

interface UseTripFiltersParams {
  /** Initial limit (default: 12) */
  initialLimit?: number;

  /** Callback when filters change (useful for refetching) */
  onFiltersChange?: () => void;
}

export const useTripFilters = ({
  initialLimit = 12,
  onFiltersChange,
}: UseTripFiltersParams = {}): UseTripFiltersReturn => {
  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<'draft' | 'published' | null>(
    null
  );

  // Pagination state
  const [offset, setOffset] = useState(0);
  const [limit, setLimit] = useState(initialLimit);

  // Check if any filters are active
  const hasActiveFilters = Boolean(searchQuery || selectedTag || selectedStatus);

  // Reset pagination when filters change
  useEffect(() => {
    setOffset(0);
    onFiltersChange?.();
  }, [searchQuery, selectedTag, selectedStatus, onFiltersChange]);

  // Reset all filters to defaults
  const resetFilters = useCallback(() => {
    setSearchQuery('');
    setSelectedTag(null);
    setSelectedStatus(null);
    setOffset(0);
  }, []);

  // Pagination handlers
  const nextPage = useCallback(() => {
    setOffset((prev) => prev + limit);
  }, [limit]);

  const previousPage = useCallback(() => {
    setOffset((prev) => Math.max(0, prev - limit));
  }, [limit]);

  const goToPage = useCallback(
    (page: number) => {
      // Convert 1-indexed page to 0-indexed offset
      const newOffset = (page - 1) * limit;
      setOffset(Math.max(0, newOffset));
    },
    [limit]
  );

  // Wrapper for setSearchQuery that debounces updates
  const handleSearchQueryChange = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Wrapper for setSelectedTag
  const handleSelectedTagChange = useCallback((tag: string | null) => {
    setSelectedTag(tag);
  }, []);

  // Wrapper for setSelectedStatus
  const handleSelectedStatusChange = useCallback(
    (status: 'draft' | 'published' | null) => {
      setSelectedStatus(status);
    },
    []
  );

  return {
    searchQuery,
    setSearchQuery: handleSearchQueryChange,
    selectedTag,
    setSelectedTag: handleSelectedTagChange,
    selectedStatus,
    setSelectedStatus: handleSelectedStatusChange,
    offset,
    setOffset,
    limit,
    setLimit,
    resetFilters,
    nextPage,
    previousPage,
    goToPage,
    hasActiveFilters,
  };
};
