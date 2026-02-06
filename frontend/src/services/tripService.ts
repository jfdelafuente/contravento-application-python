/**
 * Trip Service
 *
 * API service for managing trips in the Travel Diary feature.
 * Based on backend API contracts from Feature 002 (Travel Diary Backend).
 */

import { api } from './api';
import {
  Trip,
  TripListItem,
  TripListResponse,
  TripCreateInput,
  TripUpdateInput,
  Tag,
  PublicTripListResponse,
} from '../types/trip';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Parameters for getUserTrips
 */
interface GetUserTripsParams {
  tag?: string;
  status?: 'draft' | 'published';
  visibility?: 'public' | 'private';
  sort_by?: string;
  limit?: number;
  offset?: number;
}

/**
 * Standard API response wrapper
 */
interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: null | {
    code: string;
    message: string;
    field?: string;
  };
}

// ============================================================================
// Public Feed Operations (Feature 013)
// ============================================================================

/**
 * Get public trips feed (T025)
 *
 * Fetches paginated list of published trips from public profiles.
 * No authentication required - fully public endpoint.
 *
 * @param page - Page number (1-indexed, default 1)
 * @param limit - Items per page (1-50, default 20)
 * @returns PublicTripListResponse with trips and pagination metadata
 *
 * @example
 * const response = await getPublicTrips(1, 20);
 * console.log(`Showing ${response.trips.length} of ${response.pagination.total} trips`);
 */
export const getPublicTrips = async (
  page: number = 1,
  limit?: number
): Promise<PublicTripListResponse> => {
  const params: { page: number; limit?: number } = { page };
  if (limit !== undefined) {
    params.limit = limit;
  }

  const response = await api.get<PublicTripListResponse>('/trips/public', {
    params,
  });
  return response.data;
};

// ============================================================================
// Trip CRUD Operations
// ============================================================================

/**
 * Get trip by ID
 *
 * @param tripId - UUID of the trip
 * @returns Trip with full details (photos, tags, locations)
 *
 * @throws 404 if trip not found
 * @throws 403 if trying to view someone else's draft
 *
 * @example
 * const trip = await getTripById('550e8400-e29b-41d4-a716-446655440000');
 */
export const getTripById = async (tripId: string): Promise<Trip> => {
  const response = await api.get<ApiResponse<Trip>>(`/trips/${tripId}`, {
    timeout: 60000, // 60 seconds for trips with large GPX files and many trackpoints (aligned with backend)
  });
  return response.data.data;
};

/**
 * Get user's trips with filters and pagination
 *
 * @param username - Username of the profile owner
 * @param params - Optional query parameters (tag, status, limit, offset)
 * @returns Paginated trip list response
 *
 * @throws 404 if user not found
 *
 * @example
 * // Get all published trips
 * const data = await getUserTrips('maria_garcia', { status: 'published', limit: 12 });
 *
 * // Filter by tag
 * const data = await getUserTrips('maria_garcia', { tag: 'bikepacking' });
 *
 * // Get drafts (owner only)
 * const data = await getUserTrips('maria_garcia', { status: 'draft' });
 */
export const getUserTrips = async (
  username: string,
  params?: GetUserTripsParams
): Promise<TripListResponse> => {
  const queryParams = new URLSearchParams();
  if (params?.tag) queryParams.append('tag', params.tag);
  if (params?.status) queryParams.append('status', params.status);
  if (params?.visibility) queryParams.append('visibility', params.visibility);
  if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const url = `/users/${username}/trips${queryParams.toString() ? `?${queryParams}` : ''}`;
  const response = await api.get<ApiResponse<any>>(url);

  // Backend returns 'count', but frontend type expects 'total'
  return {
    trips: response.data.data.trips,
    total: response.data.data.count || response.data.data.total || 0,
    limit: response.data.data.limit,
    offset: response.data.data.offset,
  };
};

/**
 * Create new trip (defaults to draft status)
 *
 * @param tripData - Trip creation data
 * @returns Created trip with assigned trip_id
 *
 * @throws 400 if validation fails
 * @throws 401 if not authenticated
 *
 * @example
 * const newTrip = await createTrip({
 *   title: 'Vía Verde del Aceite',
 *   description: '<p>Ruta espectacular...</p>',
 *   start_date: '2024-05-15',
 *   end_date: '2024-05-17',
 *   distance_km: 127.3,
 *   difficulty: 'moderate',
 *   locations: [{ name: 'Baeza', country: 'España' }],
 *   tags: ['vías verdes', 'andalucía'],
 * });
 */
export const createTrip = async (tripData: TripCreateInput): Promise<Trip> => {
  const response = await api.post<ApiResponse<Trip>>('/trips', tripData);
  return response.data.data;
};

/**
 * Update existing trip (partial updates supported)
 *
 * @param tripId - UUID of the trip to update
 * @param updates - Fields to update (all optional)
 * @returns Updated trip
 *
 * @throws 403 if not the owner
 * @throws 404 if trip not found
 * @throws 409 if concurrent edit detected
 *
 * @example
 * // Update title and distance
 * const updated = await updateTrip('550e8400...', {
 *   title: 'Vía Verde del Aceite - ACTUALIZADO',
 *   distance_km: 130.5,
 *   client_updated_at: trip.updated_at, // For optimistic locking
 * });
 */
export const updateTrip = async (
  tripId: string,
  updates: TripUpdateInput
): Promise<Trip> => {
  const response = await api.put<ApiResponse<Trip>>(`/trips/${tripId}`, updates);
  return response.data.data;
};

/**
 * Delete trip permanently
 *
 * Deletes trip and all associated data (photos, tags, locations).
 *
 * @param tripId - UUID of the trip to delete
 *
 * @throws 403 if not the owner
 * @throws 404 if trip not found
 *
 * @example
 * await deleteTrip('550e8400-e29b-41d4-a716-446655440000');
 * navigate('/profile');
 */
export const deleteTrip = async (tripId: string): Promise<void> => {
  await api.delete(`/trips/${tripId}`);
};

/**
 * Publish draft trip
 *
 * Changes status from 'draft' to 'published'.
 * Enforces publish requirements (description >= 50 chars).
 *
 * @param tripId - UUID of the trip to publish
 * @returns Published trip with updated status and published_at timestamp
 *
 * @throws 400 if validation fails (e.g., description too short)
 * @throws 403 if not the owner
 * @throws 409 if trip already published
 *
 * @example
 * try {
 *   const published = await publishTrip('550e8400...');
 *   toast.success('Viaje publicado correctamente');
 * } catch (error) {
 *   // Handle validation errors (description < 50 chars, etc.)
 * }
 */
export const publishTrip = async (tripId: string): Promise<Trip> => {
  const response = await api.post<ApiResponse<Trip>>(`/trips/${tripId}/publish`);
  return response.data.data;
};

// ============================================================================
// Tag Operations
// ============================================================================

/**
 * Get all tags ordered by popularity
 *
 * Public endpoint (no authentication required).
 *
 * @returns List of tags ordered by usage_count (descending)
 *
 * @example
 * const tags = await getAllTags();
 * // [
 * //   { tag_id: '...', name: 'Vías Verdes', normalized: 'vias verdes', usage_count: 125 },
 * //   { tag_id: '...', name: 'Bikepacking', normalized: 'bikepacking', usage_count: 98 },
 * // ]
 */
export const getAllTags = async (): Promise<Tag[]> => {
  const response = await api.get<ApiResponse<{ tags: Tag[]; count: number }>>('/tags');
  return response.data.data.tags;
};

// ============================================================================
// Convenience Functions
// ============================================================================

/**
 * Get recent published trips for a user
 *
 * Convenience function for dashboard/profile recent trips section.
 *
 * @param username - Username to fetch trips for
 * @param limit - Number of trips to fetch (default: 5)
 * @returns List of recent published trips
 *
 * @example
 * const recentTrips = await getRecentTrips('maria_garcia', 5);
 */
export const getRecentTrips = async (
  username: string,
  limit: number = 5
): Promise<TripListItem[]> => {
  const data = await getUserTrips(username, {
    status: 'published',
    limit,
    offset: 0,
  });

  return data.trips;
};

/**
 * Check if user can edit trip
 *
 * @param trip - Trip to check
 * @param currentUserId - Current user's ID
 * @returns True if user is the trip owner
 *
 * @example
 * if (canEditTrip(trip, currentUser.user_id)) {
 *   return <EditButton />;
 * }
 */
export const canEditTrip = (trip: Trip, currentUserId: string): boolean => {
  return trip.user_id === currentUserId;
};

/**
 * Check if trip can be published
 *
 * @param trip - Trip to check
 * @returns True if trip meets publish requirements
 *
 * @example
 * <Button
 *   disabled={!canPublishTripData(trip)}
 *   onClick={() => publishTrip(trip.trip_id)}
 * >
 *   Publicar
 * </Button>
 */
export const canPublishTripData = (trip: Trip): boolean => {
  return trip.status === 'draft' && trip.description.length >= 50;
};

// ============================================================================
// GPS Trip Creation Wizard (Feature 017)
// ============================================================================

/**
 * Create trip with GPX file in atomic transaction (T073)
 *
 * Creates a trip and uploads GPX file in a single atomic operation.
 * If any step fails, the entire operation is rolled back.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 6 (US6 - Publish Trip)
 * Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml
 *
 * @param gpxFile - GPX file to upload (max 10MB)
 * @param tripDetails - Trip metadata (title, description, dates, privacy)
 * @returns Created trip with GPX metadata
 *
 * @throws 400 if validation fails (title too long, description too short, invalid GPX)
 * @throws 413 if GPX file exceeds 10MB size limit
 * @throws 401 if not authenticated
 *
 * @example
 * const formData = {
 *   title: 'Ruta Bikepacking Pirineos',
 *   description: 'Descripción detallada con más de 50 caracteres...',
 *   start_date: '2024-06-01',
 *   end_date: '2024-06-05',
 *   privacy: 'public',
 * };
 *
 * const trip = await createTripWithGPX(gpxFile, formData);
 * console.log(`Trip created: ${trip.trip_id} with ${trip.gpx_file.total_distance_km} km`);
 */
export const createTripWithGPX = async (
  gpxFile: File,
  tripDetails: {
    title: string;
    description: string;
    start_date: string;
    end_date?: string;
    privacy: 'public' | 'private';
  }
): Promise<Trip> => {
  const formData = new FormData();

  // Add GPX file
  formData.append('gpx_file', gpxFile);

  // Add trip details
  formData.append('title', tripDetails.title);
  formData.append('description', tripDetails.description);
  formData.append('start_date', tripDetails.start_date);
  if (tripDetails.end_date) {
    formData.append('end_date', tripDetails.end_date);
  }
  formData.append('privacy', tripDetails.privacy);

  const response = await api.post<ApiResponse<Trip>>('/trips/gpx-wizard', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 60 seconds for large GPX files
  });

  return response.data.data;
};

// ============================================================================
// Photo Management Operations
// ============================================================================

/**
 * Upload photo to trip
 *
 * @param tripId - UUID of the trip
 * @param file - Photo file to upload (JPG/PNG/WEBP, max 10MB)
 * @returns Uploaded photo data
 *
 * @throws 400 if validation fails
 * @throws 403 if not the trip owner
 * @throws 413 if file exceeds size limit
 *
 * @example
 * const photo = await uploadTripPhoto(tripId, file);
 */
export const uploadTripPhoto = async (
  tripId: string,
  file: File
): Promise<import('../types/trip').TripPhoto> => {
  const formData = new FormData();
  formData.append('photo', file);

  const response = await api.post<ApiResponse<import('../types/trip').TripPhoto>>(
    `/trips/${tripId}/photos`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data.data;
};

/**
 * Delete photo from trip
 *
 * @param tripId - UUID of the trip
 * @param photoId - UUID of the photo to delete
 *
 * @throws 403 if not the trip owner
 * @throws 404 if photo not found
 *
 * @example
 * await deleteTripPhoto(tripId, photoId);
 */
export const deleteTripPhoto = async (tripId: string, photoId: string): Promise<void> => {
  await api.delete(`/trips/${tripId}/photos/${photoId}`);
};

/**
 * Reorder trip photos
 *
 * @param tripId - UUID of the trip
 * @param photoIds - Array of photo IDs in desired order
 *
 * @throws 403 if not the trip owner
 * @throws 400 if photo IDs don't match trip's photos
 *
 * @example
 * await reorderTripPhotos(tripId, [photo1.photo_id, photo2.photo_id, photo3.photo_id]);
 */
export const reorderTripPhotos = async (tripId: string, photoIds: string[]): Promise<void> => {
  await api.put(`/trips/${tripId}/photos/reorder`, { photo_order: photoIds });
};
