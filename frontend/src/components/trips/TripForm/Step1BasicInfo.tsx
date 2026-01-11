/**
 * Step1BasicInfo Component
 *
 * First step of trip creation wizard - collects basic trip information.
 * Fields: title, start_date, end_date (optional), distance_km (optional), difficulty (optional), locations (with GPS)
 *
 * Used in:
 * - TripFormWizard (step 1/4)
 */

import React, { useState, lazy, Suspense } from 'react';
import { useFormContext } from 'react-hook-form';
import { TripCreateInput, DIFFICULTY_LABELS } from '../../../types/trip';
import { LocationInput, LocationInputData, LocationValidationErrors } from './LocationInput';
import { LocationConfirmModal } from '../LocationConfirmModal';
import { useReverseGeocode } from '../../../hooks/useReverseGeocode';
import type { LocationSelection } from '../../../types/geocoding';
import toast from 'react-hot-toast';
import './Step1BasicInfo.css';

// Lazy load TripMap
const TripMap = lazy(() =>
  import('../TripMap').then((module) => ({ default: module.TripMap }))
);

export const Step1BasicInfo: React.FC = () => {
  const {
    register,
    formState: { errors },
    watch,
    setValue,
    getValues,
  } = useFormContext<TripCreateInput>();

  // Watch start_date to validate end_date
  const startDate = watch('start_date');

  // Locations state management
  const [locations, setLocations] = useState<LocationInputData[]>(() => {
    const existingLocations = getValues('locations');
    return existingLocations && existingLocations.length > 0
      ? existingLocations.map((loc) => ({
          name: loc.name,
          latitude: loc.latitude ?? null,
          longitude: loc.longitude ?? null,
        }))
      : [{ name: '', latitude: null, longitude: null }];
  });

  const [locationErrors, setLocationErrors] = useState<Record<number, LocationValidationErrors>>({});

  // Geocoding state (Feature 010)
  const [showMapPicker, setShowMapPicker] = useState(false);
  const [pendingLocation, setPendingLocation] = useState<LocationSelection | null>(null);
  const { geocode } = useReverseGeocode();

  // Update form value when locations change
  React.useEffect(() => {
    setValue('locations', locations);
  }, [locations, setValue]);

  const handleLocationChange = (index: number, field: string, value: string | number | null) => {
    setLocations((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });

    // Clear error for this field
    setLocationErrors((prev) => {
      const updated = { ...prev };
      if (updated[index]) {
        delete updated[index][field as keyof LocationValidationErrors];
        if (Object.keys(updated[index]).length === 0) {
          delete updated[index];
        }
      }
      return updated;
    });
  };

  // Validate locations before allowing next step
  const validateLocations = (): boolean => {
    const errors: Record<number, LocationValidationErrors> = {};
    let hasErrors = false;

    locations.forEach((location, index) => {
      // Validate location name
      if (!location.name || location.name.trim() === '') {
        if (!errors[index]) errors[index] = {};
        errors[index].name = 'El nombre de la ubicación es obligatorio';
        hasErrors = true;
      }

      // Validate partial coordinates (both or none)
      const hasLatitude = location.latitude !== null && location.latitude !== undefined && location.latitude !== '';
      const hasLongitude = location.longitude !== null && location.longitude !== undefined && location.longitude !== '';

      if (hasLatitude && !hasLongitude) {
        if (!errors[index]) errors[index] = {};
        errors[index].longitude = 'Debes proporcionar la longitud si ingresas latitud';
        hasErrors = true;
      }

      if (!hasLatitude && hasLongitude) {
        if (!errors[index]) errors[index] = {};
        errors[index].latitude = 'Debes proporcionar la latitud si ingresas longitud';
        hasErrors = true;
      }

      // Validate coordinate ranges
      if (hasLatitude) {
        const lat = Number(location.latitude);
        if (isNaN(lat) || lat < -90 || lat > 90) {
          if (!errors[index]) errors[index] = {};
          errors[index].latitude = 'La latitud debe estar entre -90 y 90 grados';
          hasErrors = true;
        }
      }

      if (hasLongitude) {
        const lon = Number(location.longitude);
        if (isNaN(lon) || lon < -180 || lon > 180) {
          if (!errors[index]) errors[index] = {};
          errors[index].longitude = 'La longitud debe estar entre -180 y 180 grados';
          hasErrors = true;
        }
      }
    });

    setLocationErrors(errors);
    return !hasErrors;
  };

  // Expose validation function to parent (TripFormWizard)
  React.useEffect(() => {
    // Store validation function in window for TripFormWizard to call
    (window as any).__validateStep1Locations = validateLocations;
    return () => {
      delete (window as any).__validateStep1Locations;
    };
  }, [locations]);

  const handleAddLocation = () => {
    if (locations.length >= 50) {
      alert('Máximo 50 ubicaciones permitidas');
      return;
    }
    setLocations((prev) => [...prev, { name: '', latitude: null, longitude: null }]);
  };

  const handleRemoveLocation = (index: number) => {
    if (locations.length === 1) {
      alert('Debe haber al menos una ubicación');
      return;
    }
    setLocations((prev) => prev.filter((_, i) => i !== index));
    setLocationErrors((prev) => {
      const updated = { ...prev };
      delete updated[index];
      // Re-index errors after removal
      const reindexed: Record<number, LocationValidationErrors> = {};
      Object.keys(updated).forEach((key) => {
        const oldIndex = parseInt(key);
        const newIndex = oldIndex > index ? oldIndex - 1 : oldIndex;
        reindexed[newIndex] = updated[oldIndex];
      });
      return reindexed;
    });
  };

  // Geocoding handlers (Feature 010)
  const handleMapClick = async (lat: number, lng: number) => {
    setPendingLocation({
      latitude: lat,
      longitude: lng,
      suggestedName: '',
      fullAddress: '',
      isLoading: true,
      hasError: false,
    });

    try {
      const { name, fullAddress } = await geocode(lat, lng);
      setPendingLocation({
        latitude: lat,
        longitude: lng,
        suggestedName: name,
        fullAddress,
        isLoading: false,
        hasError: false,
      });
    } catch (err: any) {
      console.error('Error geocoding location:', err);
      setPendingLocation({
        latitude: lat,
        longitude: lng,
        suggestedName: '',
        fullAddress: '',
        isLoading: false,
        hasError: true,
        errorMessage: err.message || 'Error al obtener el nombre del lugar',
      });
    }
  };

  const handleConfirmLocation = (name: string, lat: number, lng: number) => {
    if (locations.length >= 50) {
      toast.error('Máximo 50 ubicaciones permitidas');
      setPendingLocation(null);
      setShowMapPicker(false);
      return;
    }

    // Add new location to the list
    setLocations((prev) => [
      ...prev,
      {
        name,
        latitude: lat,
        longitude: lng,
      },
    ]);

    setPendingLocation(null);
    setShowMapPicker(false);

    toast.success(`Ubicación "${name}" añadida`, {
      duration: 3000,
      position: 'top-center',
    });
  };

  const handleCancelLocation = () => {
    setPendingLocation(null);
  };

  const handleToggleMapPicker = () => {
    setShowMapPicker(!showMapPicker);
    if (showMapPicker) {
      setPendingLocation(null);
    }
  };

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
            <option value="very_difficult">{DIFFICULTY_LABELS.very_difficult}</option>
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

        {/* Locations Section with GPS Coordinates */}
        <div className="form-section">
          <div className="form-section__header">
            <h3 className="form-section__title">Ubicaciones del Viaje</h3>
            <p className="form-section__description">
              Añade las ubicaciones de tu ruta. Las coordenadas GPS son opcionales y permiten visualizar la ruta en el mapa.
            </p>
          </div>

          <div className="locations-container">
            {locations.map((location, index) => (
              <LocationInput
                key={index}
                location={location}
                index={index}
                onChange={handleLocationChange}
                onRemove={handleRemoveLocation}
                errors={locationErrors[index]}
                showRemove={locations.length > 1}
              />
            ))}
          </div>

          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="add-location-btn"
              onClick={handleAddLocation}
              disabled={locations.length >= 50}
              aria-label="Añadir otra ubicación"
            >
              + Añadir Ubicación
            </button>

            <button
              type="button"
              className="add-location-btn add-location-btn--map"
              onClick={handleToggleMapPicker}
              disabled={locations.length >= 50}
              aria-label="Añadir ubicación desde mapa"
              style={{
                background: showMapPicker ? '#ef4444' : '#10b981',
                borderColor: showMapPicker ? '#dc2626' : '#059669',
              }}
            >
              {showMapPicker ? (
                <>
                  <svg
                    width="16"
                    height="16"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    style={{ display: 'inline', marginRight: '0.5rem' }}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  Cerrar Mapa
                </>
              ) : (
                <>
                  <svg
                    width="16"
                    height="16"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    style={{ display: 'inline', marginRight: '0.5rem' }}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                  Añadir desde Mapa
                </>
              )}
            </button>
          </div>

          {locations.length >= 50 && (
            <span className="form-field__hint" style={{ color: '#dc3545' }}>
              Máximo 50 ubicaciones alcanzado
            </span>
          )}

          {/* Map Picker (Feature 010) */}
          {showMapPicker && (
            <div style={{ marginTop: '1.5rem' }}>
              <p className="form-field__hint" style={{ marginBottom: '1rem' }}>
                Haz click en el mapa para seleccionar una ubicación. Se obtendrá automáticamente el nombre del lugar.
              </p>
              <Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Cargando mapa...</div>}>
                <TripMap
                  locations={locations.filter((loc) => loc.latitude !== null && loc.longitude !== null).map((loc, idx) => ({
                    location_id: `temp-${idx}`,
                    name: loc.name,
                    latitude: loc.latitude,
                    longitude: loc.longitude,
                    sequence: idx,
                  }))}
                  tripTitle="Selecciona ubicación"
                  isEditMode={true}
                  onMapClick={handleMapClick}
                />
              </Suspense>
            </div>
          )}
        </div>

        {/* Location Confirmation Modal (Feature 010) */}
        <LocationConfirmModal
          location={pendingLocation}
          onConfirm={handleConfirmLocation}
          onCancel={handleCancelLocation}
        />
      </div>
    </div>
  );
};
