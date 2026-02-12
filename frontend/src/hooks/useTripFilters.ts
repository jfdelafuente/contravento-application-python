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
import { useSearchParams } from 'react-router-dom';
import { useDebounce } from './useDebounce';
import { DEFAULT_SORT_OPTION } from '../types/sort';

interface UseTripFiltersReturn {
  /** Current search query (immediate, as user types) */
  searchQuery: string;
  /** Debounced search query (delayed 500ms for API calls) */
  debouncedSearchQuery: string;
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

  /** Currently selected visibility (null shows both) */
  selectedVisibility: 'public' | 'private' | null;
  /** Set selected visibility */
  setSelectedVisibility: (visibility: 'public' | 'private' | null) => void;

  /** Currently selected sort option */
  sortBy: string;
  /** Set sort option */
  setSortBy: (sortBy: string) => void;

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
  // Read URL search parameters
  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize filters from URL parameters
  const initialTag = searchParams.get('tag') || null;
  const initialStatus = (searchParams.get('status') as 'draft' | 'published' | null) || null;
  const initialVisibility = (searchParams.get('visibility') as 'public' | 'private' | null) || null;
  const initialSort = searchParams.get('sort') || DEFAULT_SORT_OPTION.value;

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(initialTag);
  const [selectedStatus, setSelectedStatus] = useState<'draft' | 'published' | null>(
    initialStatus
  );
  const [selectedVisibility, setSelectedVisibility] = useState<'public' | 'private' | null>(
    initialVisibility
  );
  const [sortBy, setSortBy] = useState<string>(initialSort);

  // Debounce search query to reduce API calls (500ms delay)
  const debouncedSearchQuery = useDebounce(searchQuery, 500);

  // Pagination state
  const [offset, setOffset] = useState(0);
  const [limit, setLimit] = useState(initialLimit);

  // Check if any filters are active (use immediate searchQuery for UI feedback)
  const hasActiveFilters = Boolean(searchQuery || selectedTag || selectedStatus || selectedVisibility);

  // Sync filters with URL parameters
  useEffect(() => {
    // Preserve existing params (like 'user') and only update filter params
    const params = new URLSearchParams(searchParams);

    // Update or remove 'tag' parameter
    if (selectedTag) {
      params.set('tag', selectedTag);
    } else {
      params.delete('tag');
    }

    // Update or remove 'status' parameter
    if (selectedStatus) {
      params.set('status', selectedStatus);
    } else {
      params.delete('status');
    }

    // Update or remove 'visibility' parameter
    if (selectedVisibility) {
      params.set('visibility', selectedVisibility);
    } else {
      params.delete('visibility');
    }

    // Update or remove 'sort' parameter (only if different from default)
    if (sortBy && sortBy !== DEFAULT_SORT_OPTION.value) {
      params.set('sort', sortBy);
    } else {
      params.delete('sort');
    }

    // Update URL without triggering navigation
    setSearchParams(params, { replace: true });
  }, [selectedTag, selectedStatus, selectedVisibility, sortBy, searchParams, setSearchParams]);

  // Reset pagination when filters change (use debounced search to avoid resets on every keystroke)
  useEffect(() => {
    setOffset(0);
    onFiltersChange?.();
  }, [debouncedSearchQuery, selectedTag, selectedStatus, selectedVisibility, sortBy, onFiltersChange]);

  // Reset all filters to defaults
  const resetFilters = useCallback(() => {
    setSearchQuery('');
    setSelectedTag(null);
    setSelectedStatus(null);
    setSelectedVisibility(null);
    setSortBy(DEFAULT_SORT_OPTION.value);
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

  // Wrapper for setSelectedVisibility
  const handleSelectedVisibilityChange = useCallback(
    (visibility: 'public' | 'private' | null) => {
      setSelectedVisibility(visibility);
    },
    []
  );

  // Wrapper for setSortBy
  const handleSortByChange = useCallback((newSortBy: string) => {
    setSortBy(newSortBy);
  }, []);

  return {
    searchQuery,
    debouncedSearchQuery,
    setSearchQuery: handleSearchQueryChange,
    selectedTag,
    setSelectedTag: handleSelectedTagChange,
    selectedStatus,
    setSelectedStatus: handleSelectedStatusChange,
    selectedVisibility,
    setSelectedVisibility: handleSelectedVisibilityChange,
    sortBy,
    setSortBy: handleSortByChange,
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
