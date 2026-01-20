/**
 * useComments Hook - Manage comments list for a trip (Feature 004 - US3: Comentarios)
 *
 * Fetches and manages paginated comments for a trip with:
 * - Automatic loading on mount
 * - Pagination support (limit/offset)
 * - Optimistic updates when creating/deleting comments
 * - Error handling with Spanish messages
 *
 * Related tasks: T099
 */

import { useEffect, useState, useCallback } from 'react';
import {
  Comment,
  CommentsListResponse,
  getTripComments,
} from '../services/commentService';

interface UseCommentsResult {
  comments: Comment[];
  total: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
  hasMore: boolean;
}

interface UseCommentsOptions {
  limit?: number;
  autoLoad?: boolean;
}

/**
 * Hook to fetch and manage comments for a trip
 *
 * @param tripId - Trip ID to fetch comments for
 * @param options - Configuration options
 * @returns Comments state and control functions
 *
 * @example
 * ```tsx
 * const { comments, isLoading, error, loadMore, hasMore } = useComments(tripId);
 *
 * if (isLoading) return <Spinner />;
 * if (error) return <ErrorMessage message={error} />;
 *
 * return (
 *   <div>
 *     {comments.map(comment => <CommentItem key={comment.id} comment={comment} />)}
 *     {hasMore && <button onClick={loadMore}>Cargar más</button>}
 *   </div>
 * );
 * ```
 */
export function useComments(
  tripId: string,
  options: UseCommentsOptions = {}
): UseCommentsResult {
  const { limit = 50, autoLoad = true } = options;

  const [comments, setComments] = useState<Comment[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasMore = comments.length < total;

  const fetchComments = useCallback(
    async (newOffset: number = 0, append: boolean = false) => {
      if (!tripId) return;

      setIsLoading(true);
      setError(null);

      try {
        const response: CommentsListResponse = await getTripComments(
          tripId,
          limit,
          newOffset
        );

        if (append) {
          setComments((prev) => [...prev, ...response.items]);
        } else {
          setComments(response.items);
        }

        setTotal(response.total);
        setOffset(newOffset);
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.detail ||
          err.message ||
          'Error al cargar comentarios';
        setError(errorMessage);
        console.error('Error fetching comments:', err);
      } finally {
        setIsLoading(false);
      }
    },
    [tripId, limit]
  );

  const refetch = useCallback(async () => {
    await fetchComments(0, false);
  }, [fetchComments]);

  const loadMore = useCallback(async () => {
    if (!hasMore || isLoading) return;
    await fetchComments(offset + limit, true);
  }, [hasMore, isLoading, offset, limit, fetchComments]);

  useEffect(() => {
    if (autoLoad && tripId) {
      fetchComments(0, false);
    }
  }, [tripId, autoLoad, fetchComments]);

  return {
    comments,
    total,
    isLoading,
    error,
    refetch,
    loadMore,
    hasMore,
  };
}
