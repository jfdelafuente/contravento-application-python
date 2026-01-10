/**
 * Step2StoryTags Component
 *
 * Second step of trip creation wizard - collects trip story and tags.
 * Fields: description (textarea), tags (autocomplete input, max 10)
 *
 * Used in:
 * - TripFormWizard (step 2/4)
 */

import React, { useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { TripCreateInput } from '../../../types/trip';
import './Step1BasicInfo.css'; // Shared styles

export const Step2StoryTags: React.FC = () => {
  const {
    register,
    formState: { errors },
    watch,
    setValue,
  } = useFormContext<TripCreateInput>();

  const description = watch('description') || '';
  const tags = watch('tags') || [];

  const [tagInput, setTagInput] = useState('');

  // Character count for description
  const descriptionLength = description.length;
  const isDescriptionWarning = descriptionLength > 40000;
  const isDescriptionError = descriptionLength > 50000;

  /**
   * Add tag to the list
   */
  const handleAddTag = () => {
    const trimmedTag = tagInput.trim();

    if (!trimmedTag) return;

    // Check if tag already exists (case-insensitive)
    const tagExists = tags.some(
      (t) => t.toLowerCase() === trimmedTag.toLowerCase()
    );

    if (tagExists) {
      // Show feedback that tag already exists
      return;
    }

    // Check max tags limit
    if (tags.length >= 10) {
      // Show feedback about limit
      return;
    }

    // Add tag
    setValue('tags', [...tags, trimmedTag], { shouldDirty: true });
    setTagInput('');
  };

  /**
   * Remove tag from the list
   */
  const handleRemoveTag = (index: number) => {
    const newTags = tags.filter((_, i) => i !== index);
    setValue('tags', newTags, { shouldDirty: true });
  };

  /**
   * Handle Enter key to add tag
   */
  const handleTagKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <div className="step2-story-tags">
      <div className="step2-story-tags__header">
        <h2 className="step2-story-tags__title">Historia y Etiquetas</h2>
        <p className="step2-story-tags__description">
          Comparte los detalles de tu aventura y añade etiquetas para que otros ciclistas puedan encontrar tu viaje.
        </p>
      </div>

      <div className="step2-story-tags__form">
        {/* Description Field (Required) - T082: Accessibility */}
        <div className="form-field">
          <label htmlFor="description" className="form-field__label">
            Descripción del viaje *
          </label>
          <textarea
            id="description"
            className={`form-field__textarea ${errors.description ? 'form-field__input--error' : ''}`}
            placeholder="Cuéntanos sobre tu viaje: ¿qué viste? ¿cómo fue el terreno? ¿qué desafíos encontraste? ¿qué recomendarías a otros ciclistas?"
            rows={10}
            aria-label="Descripción del viaje"
            aria-required="true"
            aria-invalid={!!errors.description}
            aria-describedby={errors.description ? 'description-error description-hint description-counter' : 'description-hint description-counter'}
            {...register('description', {
              required: 'La descripción es obligatoria',
              minLength: {
                value: 10,
                message: 'La descripción debe tener al menos 10 caracteres',
              },
              maxLength: {
                value: 50000,
                message: 'La descripción no puede exceder 50,000 caracteres',
              },
            })}
          />

          {/* Character Counter */}
          <div className="form-field__counter">
            <div>
              {errors.description && (
                <span id="description-error" className="form-field__error" role="alert">
                  {errors.description.message}
                </span>
              )}
              {!errors.description && descriptionLength < 50 && (
                <span id="description-hint" className="form-field__hint">
                  Mínimo 50 caracteres para publicar (puedes guardar como borrador con menos)
                </span>
              )}
            </div>
            <span
              id="description-counter"
              className={`form-field__counter-text ${
                isDescriptionError
                  ? 'form-field__counter-text--error'
                  : isDescriptionWarning
                  ? 'form-field__counter-text--warning'
                  : ''
              }`}
              aria-live="polite"
              aria-atomic="true"
            >
              {descriptionLength.toLocaleString()} / 50,000
            </span>
          </div>
        </div>

        {/* Tags Field (Optional) */}
        <div className="form-field">
          <label htmlFor="tag-input" className="form-field__label">
            Etiquetas (opcional, máximo 10)
          </label>

          {/* Tag Input - T082: Accessibility */}
          <div className="tag-input-wrapper">
            <input
              id="tag-input"
              type="text"
              className="form-field__input"
              placeholder="Escribe una etiqueta y presiona Enter"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagKeyDown}
              disabled={tags.length >= 10}
              aria-label="Agregar etiqueta al viaje"
              aria-required="false"
              aria-describedby="tag-hint tag-list"
              aria-invalid={false}
            />
            <button
              type="button"
              className="tag-add-button"
              onClick={handleAddTag}
              disabled={!tagInput.trim() || tags.length >= 10}
              aria-label="Añadir etiqueta a la lista"
            >
              Añadir
            </button>
          </div>

          {/* Tag List - T082: Accessibility */}
          {tags.length > 0 && (
            <div
              id="tag-list"
              className="tag-list"
              role="list"
              aria-label="Etiquetas del viaje"
            >
              {tags.map((tag, index) => (
                <div key={index} className="tag-chip" role="listitem">
                  <span className="tag-chip__text">{tag}</span>
                  <button
                    type="button"
                    className="tag-chip__remove"
                    onClick={() => handleRemoveTag(index)}
                    aria-label={`Eliminar etiqueta ${tag}`}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <span id="tag-hint" className="form-field__hint">
            Ejemplos: bikepacking, montaña, gravel, costa, vías verdes
            {tags.length > 0 && ` (${tags.length}/10 etiquetas)`}
          </span>
        </div>
      </div>

      <style>{`
        .tag-input-wrapper {
          display: flex;
          gap: 8px;
          align-items: stretch;
        }

        .tag-input-wrapper input {
          flex: 1;
          min-width: 0;
        }

        .tag-add-button {
          flex: 0 0 auto;
          width: 90px;
          padding: 12px 16px;
          font-size: 0.875rem;
          font-weight: 600;
          color: #ffffff;
          background-color: var(--primary-color, #2563eb);
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease-in-out;
          white-space: nowrap;
        }

        .tag-add-button:hover:not(:disabled) {
          background-color: var(--primary-dark, #1d4ed8);
        }

        .tag-add-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .tag-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 12px;
        }

        .tag-chip {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          background-color: #eff6ff;
          color: var(--primary-color, #2563eb);
          border: 1px solid #dbeafe;
          border-radius: 16px;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .tag-chip__text {
          line-height: 1;
        }

        .tag-chip__remove {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 18px;
          height: 18px;
          padding: 0;
          background-color: transparent;
          border: none;
          color: var(--primary-color, #2563eb);
          font-size: 1.25rem;
          line-height: 1;
          cursor: pointer;
          border-radius: 50%;
          transition: all 0.2s ease-in-out;
        }

        .tag-chip__remove:hover {
          background-color: var(--primary-color, #2563eb);
          color: #ffffff;
        }
      `}</style>
    </div>
  );
};
