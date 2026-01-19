/**
 * CommentItem Component - Display individual comment (Feature 004 - US3: Comentarios)
 *
 * Features:
 * - Show comment content (sanitized HTML)
 * - Display author info (username, photo, full name)
 * - Show "editado" marker if is_edited=true
 * - Edit/Delete actions (author-only)
 * - Timestamps (created_at, updated_at)
 * - Delete confirmation modal
 *
 * Related tasks: T103
 */

import React, { useState } from 'react';
import { Comment } from '../../services/commentService';
import { useAuth } from '../../hooks/useAuth';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface CommentItemProps {
  comment: Comment;
  onEdit?: (comment: Comment) => void;
  onDelete?: (commentId: string) => void;
}

export const CommentItem: React.FC<CommentItemProps> = ({
  comment,
  onEdit,
  onDelete,
}) => {
  const { user } = useAuth();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const isAuthor = user && comment.user_id === user.user_id;

  const handleEdit = () => {
    if (onEdit) {
      onEdit(comment);
    }
  };

  const handleDelete = () => {
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    if (onDelete) {
      onDelete(comment.id);
    }
    setShowDeleteConfirm(false);
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  const formatTimestamp = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return formatDistanceToNow(date, { addSuffix: true, locale: es });
    } catch {
      return isoString;
    }
  };

  const getProfilePhotoUrl = (url: string | null | undefined): string => {
    if (!url) {
      return '/images/placeholders/profile-placeholder.jpg';
    }
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`;
  };

  return (
    <>
      <article className="comment-item">
        <div className="comment-item-header">
          <div className="comment-item-author">
            <img
              src={getProfilePhotoUrl(comment.author?.profile_photo_url)}
              alt={comment.author?.username || 'Usuario'}
              className="comment-item-avatar"
            />
            <div className="comment-item-author-info">
              <span className="comment-item-author-name">
                {comment.author?.full_name || comment.author?.username || 'Usuario'}
              </span>
              <span className="comment-item-author-username">
                @{comment.author?.username || 'unknown'}
              </span>
            </div>
          </div>

          {isAuthor && (
            <div className="comment-item-actions">
              <button
                onClick={handleEdit}
                className="comment-item-action-edit"
                aria-label="Editar comentario"
                title="Editar"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </button>
              <button
                onClick={handleDelete}
                className="comment-item-action-delete"
                aria-label="Eliminar comentario"
                title="Eliminar"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>

        <div className="comment-item-content">
          <div dangerouslySetInnerHTML={{ __html: comment.content }} />
        </div>

        <div className="comment-item-footer">
          <time className="comment-item-timestamp" dateTime={comment.created_at}>
            {formatTimestamp(comment.created_at)}
          </time>
          {comment.is_edited && (
            <span className="comment-item-edited" title="Este comentario ha sido editado">
              · editado
            </span>
          )}
        </div>
      </article>

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="delete-confirm-overlay" onClick={cancelDelete}>
          <div className="delete-confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="delete-confirm-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h3 className="delete-confirm-title">¿Eliminar comentario?</h3>
            <p className="delete-confirm-message">
              Esta acción es permanente y no se puede deshacer.
            </p>
            <div className="delete-confirm-actions">
              <button onClick={cancelDelete} className="delete-confirm-cancel">
                Cancelar
              </button>
              <button onClick={confirmDelete} className="delete-confirm-delete">
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
