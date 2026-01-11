/**
 * LocationInput Component
 *
 * Input component for trip locations with optional GPS coordinates.
 * Allows users to add location name, latitude, and longitude.
 *
 * Features:
 * - Location name (required)
 * - GPS coordinates (optional)
 * - Real-time validation
 * - Spanish error messages
 * - Remove location button
 *
 * Used in:
 * - Step1BasicInfo (trip creation/editing)
 */

import React from 'react';
import './LocationInput.css';

export interface LocationInputData {
  name: string;
  latitude: number | null;
  longitude: number | null;
}

export interface LocationValidationErrors {
  name?: string;
  latitude?: string;
  longitude?: string;
}

export interface LocationInputProps {
  location: LocationInputData;
  index: number;
  onChange: (index: number, field: string, value: string | number | null) => void;
  onRemove: (index: number) => void;
  errors?: LocationValidationErrors;
  showRemove?: boolean;
}

export const LocationInput: React.FC<LocationInputProps> = ({
  location,
  index,
  onChange,
  onRemove,
  errors,
  showRemove = true,
}) => {
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(index, 'name', e.target.value);
  };

  const handleLatitudeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onChange(index, 'latitude', value === '' ? null : parseFloat(value));
  };

  const handleLongitudeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onChange(index, 'longitude', value === '' ? null : parseFloat(value));
  };

  const handleRemoveClick = () => {
    onRemove(index);
  };

  const hasError = errors && (errors.name || errors.latitude || errors.longitude);

  return (
    <div className={`location-input ${hasError ? 'location-input--error' : ''}`}>
      <div className="location-input__header">
        <h4 className="location-input__title">Ubicación {index + 1}</h4>
        {showRemove && (
          <button
            type="button"
            className="location-input__remove-btn"
            onClick={handleRemoveClick}
            aria-label={`Eliminar ubicación ${index + 1}`}
          >
            ✕ Eliminar
          </button>
        )}
      </div>

      {/* Location Name (Required) */}
      <div className="location-input__field">
        <label htmlFor={`location-name-${index}`} className="location-input__label">
          Nombre de la ubicación *
        </label>
        <input
          id={`location-name-${index}`}
          type="text"
          className={`location-input__input ${errors?.name ? 'location-input__input--error' : ''}`}
          placeholder="Ej: Madrid, Pirineos, Camino de Santiago"
          value={location.name}
          onChange={handleNameChange}
          required
          aria-label={`Nombre de la ubicación ${index + 1}`}
          aria-required="true"
          aria-invalid={!!errors?.name}
          aria-describedby={errors?.name ? `location-name-error-${index}` : undefined}
        />
        {errors?.name && (
          <span id={`location-name-error-${index}`} className="location-input__error" role="alert">
            {errors.name}
          </span>
        )}
      </div>

      {/* GPS Coordinates (Optional) */}
      <div className="location-input__coordinates">
        <p className="location-input__coordinates-label">
          Coordenadas GPS (opcional)
        </p>
        <p className="location-input__coordinates-hint">
          Añade coordenadas para visualizar la ubicación en el mapa
        </p>

        <div className="location-input__coordinates-row">
          {/* Latitude */}
          <div className="location-input__field">
            <label htmlFor={`location-latitude-${index}`} className="location-input__label">
              Latitud
            </label>
            <input
              id={`location-latitude-${index}`}
              type="number"
              step="0.000001"
              min="-90"
              max="90"
              className={`location-input__input location-input__input--number ${
                errors?.latitude ? 'location-input__input--error' : ''
              }`}
              placeholder="Ej: 40.416775"
              value={location.latitude ?? ''}
              onChange={handleLatitudeChange}
              aria-label={`Latitud de la ubicación ${index + 1}`}
              aria-invalid={!!errors?.latitude}
              aria-describedby={errors?.latitude ? `location-latitude-error-${index}` : `location-latitude-hint-${index}`}
            />
            {errors?.latitude ? (
              <span id={`location-latitude-error-${index}`} className="location-input__error" role="alert">
                {errors.latitude}
              </span>
            ) : (
              <span id={`location-latitude-hint-${index}`} className="location-input__hint">
                -90 a 90 grados
              </span>
            )}
          </div>

          {/* Longitude */}
          <div className="location-input__field">
            <label htmlFor={`location-longitude-${index}`} className="location-input__label">
              Longitud
            </label>
            <input
              id={`location-longitude-${index}`}
              type="number"
              step="0.000001"
              min="-180"
              max="180"
              className={`location-input__input location-input__input--number ${
                errors?.longitude ? 'location-input__input--error' : ''
              }`}
              placeholder="Ej: -3.703790"
              value={location.longitude ?? ''}
              onChange={handleLongitudeChange}
              aria-label={`Longitud de la ubicación ${index + 1}`}
              aria-invalid={!!errors?.longitude}
              aria-describedby={errors?.longitude ? `location-longitude-error-${index}` : `location-longitude-hint-${index}`}
            />
            {errors?.longitude ? (
              <span id={`location-longitude-error-${index}`} className="location-input__error" role="alert">
                {errors.longitude}
              </span>
            ) : (
              <span id={`location-longitude-hint-${index}`} className="location-input__hint">
                -180 a 180 grados
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
