/**
 * Step1BasicInfo Component
 *
 * First step of trip creation wizard - collects basic trip information.
 * Fields: title, start_date, end_date (optional), distance_km (optional), difficulty (optional)
 *
 * Used in:
 * - TripFormWizard (step 1/4)
 */

import React from 'react';
import { useFormContext } from 'react-hook-form';
import { TripCreateInput, DIFFICULTY_LABELS } from '../../../types/trip';
import './Step1BasicInfo.css';

export const Step1BasicInfo: React.FC = () => {
  const {
    register,
    formState: { errors },
    watch,
  } = useFormContext<TripCreateInput>();

  // Watch start_date to validate end_date
  const startDate = watch('start_date');

  return (
    <div className="step1-basic-info">
      <div className="step1-basic-info__header">
        <h2 className="step1-basic-info__title">Información Básica</h2>
        <p className="step1-basic-info__description">
          Cuéntanos sobre tu viaje en bicicleta. Los campos marcados con * son obligatorios.
        </p>
      </div>

      <div className="step1-basic-info__form">
        {/* Title Field (Required) - T082: Accessibility */}
        <div className="form-field">
          <label htmlFor="title" className="form-field__label">
            Título del viaje *
          </label>
          <input
            id="title"
            type="text"
            className={`form-field__input ${errors.title ? 'form-field__input--error' : ''}`}
            placeholder="Ej: Ruta Transpirenaica 2024"
            aria-label="Título del viaje"
            aria-required="true"
            aria-invalid={!!errors.title}
            aria-describedby={errors.title ? 'title-error title-hint' : 'title-hint'}
            {...register('title', {
              required: 'El título es obligatorio',
              minLength: {
                value: 3,
                message: 'El título debe tener al menos 3 caracteres',
              },
              maxLength: {
                value: 200,
                message: 'El título no puede exceder 200 caracteres',
              },
            })}
          />
          {errors.title && (
            <span id="title-error" className="form-field__error" role="alert">
              {errors.title.message}
            </span>
          )}
          <span id="title-hint" className="form-field__hint">
            Un título descriptivo ayudará a otros ciclistas a encontrar tu ruta
          </span>
        </div>

        {/* Date Fields Row */}
        <div className="form-field-row">
          {/* Start Date (Required) - T082: Accessibility */}
          <div className="form-field">
            <label htmlFor="start_date" className="form-field__label">
              Fecha de inicio *
            </label>
            <input
              id="start_date"
              type="date"
              className={`form-field__input ${errors.start_date ? 'form-field__input--error' : ''}`}
              aria-label="Fecha de inicio del viaje"
              aria-required="true"
              aria-invalid={!!errors.start_date}
              aria-describedby={errors.start_date ? 'start-date-error' : undefined}
              {...register('start_date', {
                required: 'La fecha de inicio es obligatoria',
              })}
            />
            {errors.start_date && (
              <span id="start-date-error" className="form-field__error" role="alert">
                {errors.start_date.message}
              </span>
            )}
          </div>

          {/* End Date (Optional) - T082: Accessibility */}
          <div className="form-field">
            <label htmlFor="end_date" className="form-field__label">
              Fecha de fin (opcional)
            </label>
            <input
              id="end_date"
              type="date"
              className={`form-field__input ${errors.end_date ? 'form-field__input--error' : ''}`}
              min={startDate || undefined}
              aria-label="Fecha de fin del viaje (opcional)"
              aria-required="false"
              aria-invalid={!!errors.end_date}
              aria-describedby={errors.end_date ? 'end-date-error end-date-hint' : 'end-date-hint'}
              {...register('end_date', {
                validate: (value) => {
                  if (!value) return true; // Optional field
                  if (!startDate) return 'Debes seleccionar una fecha de inicio primero';
                  if (value < startDate) return 'La fecha de fin debe ser posterior a la fecha de inicio';
                  return true;
                },
              })}
            />
            {errors.end_date && (
              <span id="end-date-error" className="form-field__error" role="alert">
                {errors.end_date.message}
              </span>
            )}
            <span id="end-date-hint" className="form-field__hint">
              Deja vacío si fue un viaje de un solo día
            </span>
          </div>
        </div>

        {/* Distance Field (Optional) - T082: Accessibility */}
        <div className="form-field">
          <label htmlFor="distance_km" className="form-field__label">
            Distancia (km, opcional)
          </label>
          <input
            id="distance_km"
            type="number"
            step="0.1"
            min="0.1"
            max="10000"
            className={`form-field__input ${errors.distance_km ? 'form-field__input--error' : ''}`}
            placeholder="Ej: 125.5"
            aria-label="Distancia del viaje en kilómetros (opcional)"
            aria-required="false"
            aria-invalid={!!errors.distance_km}
            aria-describedby={errors.distance_km ? 'distance-error distance-hint' : 'distance-hint'}
            {...register('distance_km', {
              valueAsNumber: true,
              min: {
                value: 0.1,
                message: 'La distancia debe ser al menos 0.1 km',
              },
              max: {
                value: 10000,
                message: 'La distancia no puede exceder 10,000 km',
              },
            })}
          />
          {errors.distance_km && (
            <span id="distance-error" className="form-field__error" role="alert">
              {errors.distance_km.message}
            </span>
          )}
          <span id="distance-hint" className="form-field__hint">
            Distancia total recorrida en kilómetros
          </span>
        </div>

        {/* Difficulty Field (Optional) - T082: Accessibility */}
        <div className="form-field">
          <label htmlFor="difficulty" className="form-field__label">
            Dificultad (opcional)
          </label>
          <select
            id="difficulty"
            className={`form-field__select ${errors.difficulty ? 'form-field__input--error' : ''}`}
            aria-label="Dificultad del viaje (opcional)"
            aria-required="false"
            aria-invalid={!!errors.difficulty}
            aria-describedby={errors.difficulty ? 'difficulty-error difficulty-hint' : 'difficulty-hint'}
            {...register('difficulty')}
          >
            <option value="">-- Selecciona la dificultad --</option>
            <option value="easy">{DIFFICULTY_LABELS.easy}</option>
            <option value="moderate">{DIFFICULTY_LABELS.moderate}</option>
            <option value="difficult">{DIFFICULTY_LABELS.difficult}</option>
            <option value="extreme">{DIFFICULTY_LABELS.extreme}</option>
          </select>
          {errors.difficulty && (
            <span id="difficulty-error" className="form-field__error" role="alert">
              {errors.difficulty.message}
            </span>
          )}
          <span id="difficulty-hint" className="form-field__hint">
            Califica la dificultad técnica y física del viaje
          </span>
        </div>
      </div>
    </div>
  );
};
