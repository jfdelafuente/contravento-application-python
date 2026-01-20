/**
 * useComment Hook - Manage individual comment operations (Feature 004 - US3: Comentarios)
 *
 * Provides functions to:
 * - Create new comments with rate limiting (10/hour)
 * - Update comments (author-only) with is_edited marker
 * - Delete comments (author or trip owner)
 * - Optimistic UI updates with error rollback
 *
 * Related tasks: T100
 */

import { useState } from 'react';
import {
  Comment,
  createComment,
  updateComment,
  deleteComment,
  CreateCommentInput,
  UpdateCommentInput,
} from '../services/commentService';

interface UseCommentResult {
  isSubmitting: boolean;
  error: string | null;
  create: (tripId: string, data: CreateCommentInput) => Promise<Comment | null>;
  update: (commentId: string, data: UpdateCommentInput) => Promise<Comment | null>;
  remove: (commentId: string) => Promise<boolean>;
  clearError: () => void;
}

/**
 * Hook to manage comment CRUD operations
 *
 * @returns Comment operation functions and state
 *
 * @example
 * ```tsx
 * const { create, update, remove, isSubmitting, error } = useComment();
 *
 * const handleSubmit = async (content: string) => {
 *   const newComment = await create(tripId, { content });
 *   if (newComment) {
 *     onCommentCreated(newComment); // Callback to update parent state
 *   }
 * };
 *
 * const handleEdit = async (commentId: string, newContent: string) => {
 *   const updated = await update(commentId, { content: newContent });
 *   if (updated) {
 *     onCommentUpdated(updated);
 *   }
 * };
 *
 * const handleDelete = async (commentId: string) => {
 *   const success = await remove(commentId);
 *   if (success) {
 *     onCommentDeleted(commentId);
 *   }
 * };
 * ```
 */
export function useComment(): UseCommentResult {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  /**
   * Create a new comment
   */
  const create = async (
    tripId: string,
    data: CreateCommentInput
  ): Promise<Comment | null> => {
    setIsSubmitting(true);
    setError(null);

    try {
      const newComment = await createComment(tripId, data);
      return newComment;
    } catch (err: any) {
      const errorMessage = extractErrorMessage(err);
      setError(errorMessage);
      console.error('Error creating comment:', err);
      return null;
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Update an existing comment
   */
  const update = async (
    commentId: string,
    data: UpdateCommentInput
  ): Promise<Comment | null> => {
    setIsSubmitting(true);
    setError(null);

    try {
      const updatedComment = await updateComment(commentId, data);
      return updatedComment;
    } catch (err: any) {
      const errorMessage = extractErrorMessage(err);
      setError(errorMessage);
      console.error('Error updating comment:', err);
      return null;
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Delete a comment
   */
  const remove = async (commentId: string): Promise<boolean> => {
    setIsSubmitting(true);
    setError(null);

    try {
      await deleteComment(commentId);
      return true;
    } catch (err: any) {
      const errorMessage = extractErrorMessage(err);
      setError(errorMessage);
      console.error('Error deleting comment:', err);
      return false;
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    isSubmitting,
    error,
    create,
    update,
    remove,
    clearError,
  };
}

/**
 * Extract user-friendly error message from API error
 */
function extractErrorMessage(err: any): string {
  // Handle rate limit (429)
  if (err.response?.status === 429) {
    return (
      err.response?.data?.detail ||
      'Has alcanzado el límite de comentarios por hora. Espera un momento e intenta de nuevo.'
    );
  }

  // Handle forbidden (403)
  if (err.response?.status === 403) {
    return (
      err.response?.data?.detail ||
      'No tienes permiso para realizar esta acción.'
    );
  }

  // Handle validation errors (400)
  if (err.response?.status === 400) {
    return (
      err.response?.data?.detail ||
      'El contenido del comentario debe tener entre 1 y 500 caracteres.'
    );
  }

  // Handle not found (404)
  if (err.response?.status === 404) {
    return err.response?.data?.detail || 'El comentario o viaje no existe.';
  }

  // Generic error
  return err.response?.data?.detail || err.message || 'Error al procesar comentario';
}
