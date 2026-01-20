/**
 * CommentList Component - Display paginated list of comments (Feature 004 - US3: Comentarios)
 *
 * Features:
 * - List all comments chronologically (oldest first - FR-018)
 * - Pagination with "Load More" button
 * - Empty state when no comments
 * - Loading skeletons
 * - Integrate with CommentForm and CommentItem
 *
 * Related tasks: T102
 */

import React, { useState, useCallback } from 'react';
import { useComments } from '../../hooks/useComments';
import { useComment } from '../../hooks/useComment';
import { useAuth } from '../../contexts/AuthContext';
import { Comment } from '../../services/commentService';
import { CommentForm } from './CommentForm';
import { CommentItem } from './CommentItem';
import './CommentList.css';

interface CommentListProps {
  tripId: string;
  tripOwnerId?: string; // ID of the trip owner (for moderation capabilities)
}

export const CommentList: React.FC<CommentListProps> = ({ tripId, tripOwnerId }) => {
  const { user } = useAuth();
  const { comments, total, isLoading, error, refetch, loadMore, hasMore } =
    useComments(tripId);
  const { remove } = useComment();

  const [editingComment, setEditingComment] = useState<Comment | null>(null);

  const handleCommentCreated = useCallback(
    (_newComment: Comment) => {
      refetch(); // Refresh the comments list
    },
    [refetch]
  );

  const handleCommentUpdated = useCallback(
    (_updatedComment: Comment) => {
      setEditingComment(null);
      refetch(); // Refresh to show updated comment
    },
    [refetch]
  );

  const handleEdit = useCallback((comment: Comment) => {
    setEditingComment(comment);
    // Scroll to form at bottom
    setTimeout(() => {
      const formElement = document.querySelector('.comment-list-form');
      if (formElement) {
        formElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
  }, []);

  const handleDelete = useCallback(
    async (commentId: string) => {
      const success = await remove(commentId);
      if (success) {
        refetch(); // Refresh after deletion
      }
    },
    [remove, refetch]
  );

  const handleCancelEdit = useCallback(() => {
    setEditingComment(null);
  }, []);

  if (error) {
    return (
      <div className="comment-list-error" role="alert">
        <p>Error al cargar comentarios: {error}</p>
        <button onClick={() => refetch()} className="comment-list-retry">
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="comment-list">
      <div className="comment-list-header">
        <h3 className="comment-list-title">
          Comentarios ({total})
        </h3>
      </div>

      {/* Comments List */}
      {isLoading && comments.length === 0 ? (
        <div className="comment-list-loading">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="comment-item-skeleton">
              <div className="comment-item-skeleton-header">
                <div className="comment-item-skeleton-avatar" />
                <div className="comment-item-skeleton-author">
                  <div className="comment-item-skeleton-name" />
                  <div className="comment-item-skeleton-username" />
                </div>
              </div>
              <div className="comment-item-skeleton-content" />
              <div className="comment-item-skeleton-footer" />
            </div>
          ))}
        </div>
      ) : comments.length === 0 ? (
        <div className="comment-list-empty">
          <p>Todavía no hay comentarios en este viaje.</p>
          <p className="comment-list-empty-hint">¡Sé el primero en comentar!</p>
        </div>
      ) : (
        <>
          <div className="comment-list-items">
            {comments.map((comment) => (
              <CommentItem
                key={comment.id}
                comment={comment}
                tripOwnerId={tripOwnerId}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div className="comment-list-load-more">
              <button
                onClick={loadMore}
                disabled={isLoading}
                className="comment-list-load-more-button"
              >
                {isLoading ? 'Cargando...' : 'Cargar más comentarios'}
              </button>
            </div>
          )}
        </>
      )}

      {/* Comment Form - Only for authenticated users */}
      {user ? (
        <div className="comment-list-form">
          <CommentForm
            tripId={tripId}
            editingComment={editingComment}
            onCommentCreated={handleCommentCreated}
            onCommentUpdated={handleCommentUpdated}
            onCancel={handleCancelEdit}
          />
        </div>
      ) : (
        <div className="comment-list-login-prompt">
          <p>
            <a href="/login">Inicia sesión</a> para escribir un comentario
          </p>
        </div>
      )}
    </div>
  );
};
