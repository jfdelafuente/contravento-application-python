/**
 * CommentForm Component - Create/Edit comment form (Feature 004 - US3: Comentarios)
 *
 * Features:
 * - Create new comments (1-500 chars)
 * - Edit existing comments (author-only)
 * - Character counter with validation
 * - Rate limiting feedback (10 comments/hour)
 * - Spanish labels and error messages
 *
 * Related tasks: T101
 */

import React, { useState, useEffect } from 'react';
import { useComment } from '../../hooks/useComment';
import { Comment } from '../../services/commentService';

interface CommentFormProps {
  tripId: string;
  editingComment?: Comment | null;
  onCommentCreated?: (comment: Comment) => void;
  onCommentUpdated?: (comment: Comment) => void;
  onCancel?: () => void;
}

export const CommentForm: React.FC<CommentFormProps> = ({
  tripId,
  editingComment,
  onCommentCreated,
  onCommentUpdated,
  onCancel,
}) => {
  const { create, update, isSubmitting, error, clearError } = useComment();
  const [content, setContent] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const isEditMode = !!editingComment;
  const maxLength = 500;
  const remainingChars = maxLength - content.length;

  // Load editing comment content
  useEffect(() => {
    if (editingComment) {
      setContent(editingComment.content);
    }
  }, [editingComment]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);

    // Validate content
    const trimmed = content.trim();
    if (!trimmed) {
      setLocalError('El comentario no puede estar vacío');
      return;
    }

    if (trimmed.length > maxLength) {
      setLocalError(`El comentario debe tener máximo ${maxLength} caracteres`);
      return;
    }

    if (isEditMode && editingComment) {
      // Update existing comment
      const updated = await update(editingComment.id, { content: trimmed });
      if (updated && onCommentUpdated) {
        onCommentUpdated(updated);
        setContent('');
      }
    } else {
      // Create new comment
      const newComment = await create(tripId, { content: trimmed });
      if (newComment && onCommentCreated) {
        onCommentCreated(newComment);
        setContent('');
      }
    }
  };

  const handleCancel = () => {
    setContent('');
    clearError();
    setLocalError(null);
    if (onCancel) {
      onCancel();
    }
  };

  const displayError = error || localError;

  return (
    <form onSubmit={handleSubmit} className="comment-form">
      <div className="comment-form-field">
        <label htmlFor="comment-content" className="comment-form-label">
          {isEditMode ? 'Editar comentario' : 'Escribe un comentario'}
        </label>
        <textarea
          id="comment-content"
          className="comment-form-textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Comparte tu opinión sobre este viaje..."
          rows={3}
          maxLength={maxLength}
          disabled={isSubmitting}
          aria-describedby={displayError ? 'comment-error' : undefined}
          aria-invalid={!!displayError}
        />
        <div className="comment-form-footer">
          <span
            className={`comment-form-counter ${
              remainingChars < 50 ? 'comment-form-counter-warning' : ''
            }`}
          >
            {remainingChars} caracteres restantes
          </span>
        </div>
      </div>

      {displayError && (
        <div id="comment-error" className="comment-form-error" role="alert">
          {displayError}
        </div>
      )}

      <div className="comment-form-actions">
        {isEditMode && (
          <button
            type="button"
            onClick={handleCancel}
            className="comment-form-cancel"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
        )}
        <button
          type="submit"
          className="comment-form-submit"
          disabled={isSubmitting || !content.trim()}
        >
          {isSubmitting
            ? 'Enviando...'
            : isEditMode
            ? 'Guardar cambios'
            : 'Publicar comentario'}
        </button>
      </div>
    </form>
  );
};
