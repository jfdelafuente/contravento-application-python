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
import { useAuth } from '../../contexts/AuthContext';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getPhotoUrl } from '../../utils/tripHelpers';
import './CommentItem.css';

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

  return (
    <>
      <article className="comment-item">
        <div className="comment-item-header">
          <div className="comment-item-author">
            {comment.author?.profile_photo_url ? (
              <img
                src={getPhotoUrl(comment.author.profile_photo_url)}
                alt={comment.author?.username || 'Usuario'}
                className="comment-item-avatar"
              />
            ) : (
              <div className="comment-item-avatar comment-item-avatar--placeholder">
                {(comment.author?.username || 'U').charAt(0).toUpperCase()}
              </div>
            )}
            <div className="comment-item-author-info">
              <span className="comment-item-author-name">
                {comment.author?.full_name || comment.author?.username || 'Usuario'}
              </span>
              <span className="comment-item-author-username">
                @{comment.author?.username || 'unknown'}
              </span>
            </div>
          </div>

        </div>

        <div className="comment-item-content" dangerouslySetInnerHTML={{ __html: comment.content }} />

        <div className="comment-item-footer">
          <time className="comment-item-timestamp" dateTime={comment.created_at}>
            {formatTimestamp(comment.created_at)}
            {comment.is_edited && (
              <span className="comment-item-edited-marker"> · editado</span>
            )}
          </time>

          {isAuthor && (
            <div className="comment-item-actions">
              <button
                onClick={handleEdit}
                className="comment-item-action-button comment-item-action-button--edit"
                aria-label="Editar comentario"
              >
                Editar
              </button>
              <button
                onClick={handleDelete}
                className="comment-item-action-button comment-item-action-button--delete"
                aria-label="Eliminar comentario"
              >
                Eliminar
              </button>
            </div>
          )}
        </div>
      </article>

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="comment-item-delete-dialog-overlay" onClick={cancelDelete}>
          <div className="comment-item-delete-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="comment-item-delete-dialog-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h3 className="comment-item-delete-dialog-title">¿Eliminar comentario?</h3>
            <p className="comment-item-delete-dialog-text">
              Esta acción es permanente y no se puede deshacer.
            </p>
            <div className="comment-item-delete-dialog-actions">
              <button onClick={cancelDelete} className="comment-item-delete-dialog-button comment-item-delete-dialog-button--cancel">
                Cancelar
              </button>
              <button onClick={confirmDelete} className="comment-item-delete-dialog-button comment-item-delete-dialog-button--confirm">
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
