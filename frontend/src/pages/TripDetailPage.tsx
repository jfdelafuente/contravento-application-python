/**
 * TripDetailPage Component
 *
 * Full trip detail page with hero image, photo gallery, map, and metadata.
 * Includes owner-only action buttons (Edit, Delete, Publish).
 *
 * Route: /trips/:tripId
 */

import React, { useState, useEffect, lazy, Suspense } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { TripGallery } from '../components/trips/TripGallery';
import { LocationConfirmModal } from '../components/trips/LocationConfirmModal';
import { LikeButton } from '../components/likes/LikeButton';
import { LikesListModal } from '../components/likes/LikesListModal';
import { FollowButton } from '../components/social/FollowButton';
import { CommentList } from '../components/comments/CommentList';
import { GPXUploader } from '../components/trips/GPXUploader';
import { GPXStats } from '../components/trips/GPXStats';
import { getTripById, deleteTrip, publishTrip, updateTrip } from '../services/tripService';
import { useReverseGeocode } from '../hooks/useReverseGeocode';
import { useGPXTrack } from '../hooks/useGPXTrack';
import type { LocationSelection } from '../types/geocoding';
import type { LocationInput } from '../types/trip';
import {
  getDifficultyLabel,
  getDifficultyClass,
  formatDateRange,
  formatDistance,
  getStatusLabel,
  getStatusClass,
  getPhotoUrl,
} from '../utils/tripHelpers';
import { Trip } from '../types/trip';
import toast from 'react-hot-toast';
import './TripDetailPage.css';

// Lazy load TripMap (only loads if trip has locations)
const TripMap = lazy(() =>
  import('../components/trips/TripMap').then((module) => ({ default: module.TripMap }))
);

export const TripDetailPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [trip, setTrip] = useState<Trip | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Geocoding state (Feature 010)
  const [isMapEditMode, setIsMapEditMode] = useState(false);
  const [pendingLocation, setPendingLocation] = useState<LocationSelection | null>(null);
  const { geocode } = useReverseGeocode();

  // GPX track hook (Feature 003: GPS Routes - User Story 2)
  const { track: gpxTrack } = useGPXTrack(trip?.gpx_file?.gpx_file_id);

  // Likes list modal state (Feature 004 - US2)
  const [showLikesModal, setShowLikesModal] = useState(false);

  // Fetch trip details (extracted for reuse)
  const fetchTrip = async () => {
      if (!tripId) {
        setError('ID de viaje no válido');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const tripData = await getTripById(tripId);
        setTrip(tripData);
      } catch (err: any) {
        console.error('Error fetching trip:', err);
        console.error('Error details:', {
          status: err.response?.status,
          data: err.response?.data,
          message: err.message,
        });

        // Note: 401 errors are now handled by axios interceptor (api.ts)
        // which will retry without auth for public endpoints or redirect to login for protected ones

        const errorMessage =
          err.response?.status === 404
            ? 'Viaje no encontrado'
            : err.response?.status === 403
            ? 'No tienes permiso para ver este viaje'
            : err.response?.status === 401
            ? 'No tienes permiso para ver este viaje'
            : 'Error al cargar el viaje. Intenta nuevamente.';

        setError(errorMessage);

        toast.error(errorMessage, {
          duration: 5000,
          position: 'top-center',
        });
      } finally {
        setIsLoading(false);
      }
  };

  // Fetch trip on mount and when tripId changes
  useEffect(() => {
    fetchTrip();
  }, [tripId]);

  // Check if current user is the trip owner
  const isOwner = !!(user && trip && user.user_id === trip.user_id);

  // Auto-refresh: Passive polling to detect GPX completed in background (Layer 3c)
  // If user is owner and trip has no GPX, check every 5s if GPX appeared
  // This handles cases where upload showed timeout error but processing completed
  useEffect(() => {
    if (!trip?.gpx_file && isOwner) {
      console.log('[Auto-refresh] Starting passive polling for GPX completion...');

      const interval = setInterval(async () => {
        try {
          const updatedTrip = await getTripById(tripId!);

          if (updatedTrip.gpx_file) {
            console.log('[Auto-refresh] GPX detected! Refreshing trip data...');
            setTrip(updatedTrip);

            toast.success('Ruta GPS cargada correctamente', {
              duration: 4000,
              position: 'top-center',
            });

            clearInterval(interval);
          }
        } catch (error) {
          // Ignore errors in background polling (don't disturb user)
          console.warn('[Auto-refresh] Polling error (ignored):', error);
        }
      }, 5000); // Check every 5 seconds

      // Stop polling after 60 seconds (prevent infinite polling)
      const timeout = setTimeout(() => {
        console.log('[Auto-refresh] Stopping passive polling after 60s');
        clearInterval(interval);
      }, 60000);

      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }
  }, [trip?.gpx_file, isOwner, tripId]);

  // Handle trip deletion - Phase 8: Show confirmation dialog
  const handleDelete = () => {
    if (!trip || !isOwner) return;
    setShowDeleteConfirm(true);
  };

  // Confirm deletion after dialog confirmation
  const confirmDelete = async () => {
    if (!trip) return;

    setShowDeleteConfirm(false);
    setIsDeleting(true);

    try {
      await deleteTrip(trip.trip_id);

      toast.success('Viaje eliminado correctamente', {
        duration: 3000,
        position: 'top-center',
      });

      navigate('/trips');
    } catch (err: any) {
      console.error('Error deleting trip:', err);

      // Handle specific error cases
      const errorMessage =
        err.response?.status === 404
          ? 'Viaje no encontrado'
          : err.response?.status === 403
          ? 'No tienes permiso para eliminar este viaje'
          : err.response?.data?.error?.message || 'Error al eliminar el viaje. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  // Cancel deletion
  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  // Handle trip publishing
  const handlePublish = async () => {
    if (!trip || !isOwner || trip.status !== 'draft') return;

    // Validate publish requirements
    if (trip.description.length < 50) {
      toast.error('La descripción debe tener al menos 50 caracteres para publicar', {
        duration: 5000,
        position: 'top-center',
      });
      return;
    }

    setIsPublishing(true);

    try {
      await publishTrip(trip.trip_id);

      // Refetch complete trip data instead of using partial response from publish endpoint
      await fetchTrip();

      toast.success('Viaje publicado correctamente', {
        duration: 3000,
        position: 'top-center',
      });
    } catch (err: any) {
      console.error('Error publishing trip:', err);

      const errorMessage =
        err.response?.data?.error?.message || 'Error al publicar el viaje. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsPublishing(false);
    }
  };

  // Handle map click for adding locations (Feature 010)
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

  // Confirm and add/update location to trip (Feature 010)
  const handleConfirmLocation = async (name: string, lat: number, lng: number) => {
    if (!trip) return;

    const locationIdToUpdate = pendingLocation?.locationId;
    const isUpdatingExisting = !!locationIdToUpdate;

    setPendingLocation(null);
    setIsMapEditMode(false);

    try {
      const currentLocations = trip.locations || [];

      let updatedLocations: LocationInput[];

      if (isUpdatingExisting) {
        // Update existing location coordinates and name
        updatedLocations = currentLocations.map((loc) => {
          if (loc.location_id === locationIdToUpdate) {
            return {
              name,
              latitude: lat,
              longitude: lng,
            };
          }
          return {
            name: loc.name,
            latitude: loc.latitude,
            longitude: loc.longitude,
          };
        });
      } else {
        // Add new location at the end
        const newLocation: LocationInput = {
          name,
          latitude: lat,
          longitude: lng,
        };

        updatedLocations = [
          ...currentLocations.map((loc) => ({
            name: loc.name,
            latitude: loc.latitude,
            longitude: loc.longitude,
          })),
          newLocation,
        ];
      }

      // Update trip with locations array
      const updatedTrip = await updateTrip(trip.trip_id, {
        locations: updatedLocations,
      });

      // Update local state with new trip data
      setTrip(updatedTrip);

      const successMessage = isUpdatingExisting
        ? `Ubicación "${name}" actualizada correctamente`
        : `Ubicación "${name}" agregada al viaje`;

      toast.success(successMessage, {
        duration: 3000,
        position: 'top-center',
      });
    } catch (err: any) {
      console.error('Error saving location to trip:', err);

      const errorMessage =
        err.response?.data?.error?.message || 'Error al guardar ubicación. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
      });
    }
  };

  // Cancel location addition (Feature 010)
  const handleCancelLocation = () => {
    setPendingLocation(null);
  };

  // Handle marker drag for updating location coordinates (Feature 010 - User Story 2)
  const handleMarkerDrag = async (locationId: string, newLat: number, newLng: number) => {
    setPendingLocation({
      latitude: newLat,
      longitude: newLng,
      suggestedName: '',
      fullAddress: '',
      isLoading: true,
      hasError: false,
      locationId, // Store the location ID to update the correct location
    });

    try {
      const { name, fullAddress } = await geocode(newLat, newLng);
      setPendingLocation({
        latitude: newLat,
        longitude: newLng,
        suggestedName: name,
        fullAddress,
        isLoading: false,
        hasError: false,
        locationId,
      });
    } catch (err: any) {
      console.error('Error geocoding dragged location:', err);
      setPendingLocation({
        latitude: newLat,
        longitude: newLng,
        suggestedName: '',
        fullAddress: '',
        isLoading: false,
        hasError: true,
        errorMessage: err.message || 'Error al obtener el nombre del lugar',
        locationId,
      });
    }
  };

  // Toggle map edit mode (Feature 010)
  const handleToggleMapEdit = () => {
    setIsMapEditMode(!isMapEditMode);
    if (isMapEditMode) {
      // Exiting edit mode - cancel any pending location
      setPendingLocation(null);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="trip-detail-page trip-detail-page--loading">
        <div className="trip-detail-page__skeleton">
          <div className="trip-detail-page__skeleton-hero" />
          <div className="trip-detail-page__skeleton-content">
            <div className="trip-detail-page__skeleton-title" />
            <div className="trip-detail-page__skeleton-meta" />
            <div className="trip-detail-page__skeleton-description" />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !trip) {
    return (
      <div className="trip-detail-page trip-detail-page--error">
        <div className="trip-detail-page__error">
          <div className="trip-detail-page__error-icon">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h1 className="trip-detail-page__error-title">{error || 'Viaje no encontrado'}</h1>
          <Link to={user ? "/trips" : "/"} className="trip-detail-page__error-button">
            {user ? "Volver a Mis Viajes" : "Volver al Feed Público"}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="trip-detail-page">
      {/* Hero Section */}
      <div className="trip-detail-page__hero">
        {trip.photos && trip.photos.length > 0 ? (
          <img
            src={getPhotoUrl(trip.photos[0].photo_url) || ''}
            alt={trip.title}
            className="trip-detail-page__hero-image"
          />
        ) : (
          <div className="trip-detail-page__hero-placeholder">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Status Badge (T039: owner-only for drafts) */}
        {trip.status === 'draft' && isOwner && (
          <div className={`trip-detail-page__status-badge ${getStatusClass(trip.status)}`}>
            {getStatusLabel(trip.status)}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="trip-detail-page__content">
        {/* Header with Actions (T039: owner-only action buttons) */}
        <div className="trip-detail-page__header">
          <div className="trip-detail-page__header-content">
            <h1 className="trip-detail-page__title">{trip.title}</h1>

            {/* Metadata */}
            <div className="trip-detail-page__meta">
              {/* Date */}
              <div className="trip-detail-page__meta-item">
                <svg
                  className="trip-detail-page__meta-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span className="trip-detail-page__meta-text">
                  {formatDateRange(trip.start_date, trip.end_date)}
                </span>
              </div>

              {/* Distance */}
              {trip.distance_km !== null && (
                <div className="trip-detail-page__meta-item">
                  <svg
                    className="trip-detail-page__meta-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                    />
                  </svg>
                  <span className="trip-detail-page__meta-text">
                    {formatDistance(trip.distance_km)}
                  </span>
                </div>
              )}

              {/* Difficulty */}
              {trip.difficulty && (
                <div
                  className={`trip-detail-page__difficulty ${getDifficultyClass(trip.difficulty)}`}
                >
                  {getDifficultyLabel(trip.difficulty)}
                </div>
              )}

              {/* Like Button (Feature 004 - US2) */}
              {!isOwner && trip.status === 'published' && (
                <div className="trip-detail-page__meta-item">
                  <LikeButton
                    tripId={trip.trip_id}
                    initialLiked={trip.is_liked || false}
                    initialCount={trip.like_count || 0}
                    size="medium"
                    showCount={true}
                    onCountClick={trip.like_count && trip.like_count > 0 ? () => setShowLikesModal(true) : undefined}
                  />
                </div>
              )}

              {/* Like Count (owner-only - TC-US2-005) */}
              {isOwner && trip.status === 'published' && (
                <div
                  className={`trip-detail-page__meta-item trip-detail-page__like-count-readonly ${
                    trip.like_count && trip.like_count > 0 ? 'trip-detail-page__like-count-clickable' : ''
                  }`}
                  onClick={trip.like_count && trip.like_count > 0 ? () => setShowLikesModal(true) : undefined}
                  role={trip.like_count && trip.like_count > 0 ? 'button' : undefined}
                  tabIndex={trip.like_count && trip.like_count > 0 ? 0 : undefined}
                  title={trip.like_count && trip.like_count > 0 ? 'Ver usuarios que dieron like' : undefined}
                >
                  <svg
                    className="trip-detail-page__meta-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                  </svg>
                  <span className="trip-detail-page__meta-text">
                    {trip.like_count || 0} {trip.like_count === 1 ? 'like' : 'likes'}
                  </span>
                </div>
              )}

              {/* Author (Feature 004) - Right-aligned */}
              {trip.author && (
                <div className="trip-detail-page__author">
                  <Link to={`/users/${trip.author.username}`} className="trip-detail-page__author-link">
                    {trip.author.profile_photo_url ? (
                      <img
                        src={getPhotoUrl(trip.author.profile_photo_url)}
                        alt={trip.author.username}
                        className="trip-detail-page__author-avatar"
                      />
                    ) : (
                      <div className="trip-detail-page__author-avatar trip-detail-page__author-avatar--placeholder">
                        {trip.author.username.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div className="trip-detail-page__author-info">
                      <span className="trip-detail-page__author-username">{trip.author.username}</span>
                      {trip.author.full_name && (
                        <span className="trip-detail-page__author-fullname">{trip.author.full_name}</span>
                      )}
                    </div>
                  </Link>
                  {!isOwner && (
                    <FollowButton
                      username={trip.author.username}
                      initialFollowing={trip.author.is_following || false}
                      size="small"
                      variant="secondary"
                    />
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Owner-only action buttons (T039) */}
          {isOwner && (
            <div className="trip-detail-page__actions">
              {/* Publish button (only for drafts) */}
              {trip.status === 'draft' && (
                <button
                  className="trip-detail-page__action-button trip-detail-page__action-button--publish"
                  onClick={handlePublish}
                  disabled={isPublishing}
                >
                  {isPublishing ? 'Publicando...' : 'Publicar'}
                </button>
              )}

              {/* Edit locations button (Feature 010) */}
              <button
                className={`trip-detail-page__action-button ${
                  isMapEditMode
                    ? 'trip-detail-page__action-button--cancel'
                    : 'trip-detail-page__action-button--edit'
                }`}
                onClick={handleToggleMapEdit}
              >
                {isMapEditMode ? 'Cancelar edición' : 'Editar ubicaciones'}
              </button>

              {/* Edit button - Phase 7 */}
              <Link
                to={`/trips/${trip.trip_id}/edit`}
                className="trip-detail-page__action-button trip-detail-page__action-button--edit"
              >
                Editar
              </Link>

              {/* Delete button */}
              <button
                className="trip-detail-page__action-button trip-detail-page__action-button--delete"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          )}
        </div>

        {/* Description */}
        <section className="trip-detail-page__section">
          <h2 className="trip-detail-page__section-title">Descripción</h2>
          <div
            className="trip-detail-page__description"
            dangerouslySetInnerHTML={{ __html: trip.description }}
          />
        </section>

        {/* Tags */}
        {trip.tags && trip.tags.length > 0 && (
          <section className="trip-detail-page__section">
            <h2 className="trip-detail-page__section-title">Etiquetas</h2>
            <div className="trip-detail-page__tags">
              {trip.tags.map((tag) => (
                <Link
                  key={tag.tag_id}
                  to={`/trips?tag=${encodeURIComponent(tag.name)}`}
                  className="trip-detail-page__tag"
                >
                  {tag.name}
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Photo Gallery */}
        {trip.photos && trip.photos.length > 0 && (
          <section className="trip-detail-page__section">
            <h2 className="trip-detail-page__section-title">Galería de Fotos</h2>
            <TripGallery photos={trip.photos} tripTitle={trip.title} />
          </section>
        )}

        {/* GPX Section (Feature 003 - GPS Routes Interactive) */}
        {trip.gpx_file && (
          <section className="trip-detail-page__section">
            <h2 className="trip-detail-page__section-title">Ruta GPS</h2>
            <GPXStats
              metadata={trip.gpx_file}
              gpxFileId={trip.gpx_file.gpx_file_id}
              isOwner={isOwner}
            />
          </section>
        )}

        {/* GPX Uploader (owner-only, if no GPX exists) */}
        {isOwner && !trip.gpx_file && (
          <section className="trip-detail-page__section">
            <h2 className="trip-detail-page__section-title">Subir Archivo GPX</h2>
            <GPXUploader
              tripId={trip.trip_id}
              onUploadComplete={() => {
                toast.success('Archivo GPX procesado correctamente', {
                  duration: 3000,
                  position: 'top-center',
                });
                fetchTrip(); // Refetch trip to show GPX data
              }}
            />
          </section>
        )}

        {/* Map Section - TripMap shows locations list + map (or just list if no GPS) */}
        {/* Show map if there are locations OR if there's a GPX file (Feature 003) */}
        {/* Use trip.gpx_file (metadata) instead of gpxTrack (hook result) to avoid loading state issues */}
        {((trip.locations && trip.locations.length > 0) || trip.gpx_file) && (
          <section className="trip-detail-page__section">
            <Suspense
              fallback={
                <div className="trip-detail-page__map-loading">Cargando ubicaciones...</div>
              }
            >
              <TripMap
                locations={trip.locations || []}
                tripTitle={trip.title}
                isEditMode={isMapEditMode}
                onMapClick={handleMapClick}
                onMarkerDrag={handleMarkerDrag}
                hasGPX={!!trip.gpx_file}
                gpxTrackPoints={gpxTrack?.trackpoints}
                gpxStartPoint={gpxTrack?.start_point}
                gpxEndPoint={gpxTrack?.end_point}
              />
            </Suspense>
          </section>
        )}

        {/* Comments Section (Feature 004 - US3) */}
        {trip.status === 'published' && (
          <section className="trip-detail-page__section">
            <CommentList tripId={trip.trip_id} tripOwnerId={trip.user_id} />
          </section>
        )}

        {/* Back to list button */}
        <div className="trip-detail-page__footer">
          <Link to={user ? "/trips" : "/"} className="trip-detail-page__back-button">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            {user ? "Volver a Mis Viajes" : "Volver al Feed Público"}
          </Link>
        </div>
      </div>

      {/* Delete Confirmation Dialog - Phase 8 */}
      {showDeleteConfirm && (
        <div className="trip-detail-page__delete-dialog-overlay" onClick={cancelDelete}>
          <div
            className="trip-detail-page__delete-dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="trip-detail-page__delete-dialog-icon">
              <svg
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h3 className="trip-detail-page__delete-dialog-title">
              ¿Eliminar viaje?
            </h3>
            <p className="trip-detail-page__delete-dialog-text">
              ¿Estás seguro de que quieres eliminar este viaje? Esta acción es permanente y
              eliminará el viaje junto con todas sus fotos. No se puede deshacer.
            </p>
            <div className="trip-detail-page__delete-dialog-actions">
              <button
                type="button"
                className="trip-detail-page__delete-dialog-button trip-detail-page__delete-dialog-button--cancel"
                onClick={cancelDelete}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="trip-detail-page__delete-dialog-button trip-detail-page__delete-dialog-button--confirm"
                onClick={confirmDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Location Confirmation Modal (Feature 010) */}
      <LocationConfirmModal
        location={pendingLocation}
        onConfirm={handleConfirmLocation}
        onCancel={handleCancelLocation}
      />

      {/* Likes List Modal (Feature 004 - US2, TC-US2-008) */}
      {trip && (
        <LikesListModal
          tripId={trip.trip_id}
          tripTitle={trip.title}
          isOpen={showLikesModal}
          onClose={() => setShowLikesModal(false)}
        />
      )}
    </div>
  );
};
