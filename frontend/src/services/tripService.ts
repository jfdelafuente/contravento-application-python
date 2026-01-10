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
  const response = await api.get<ApiResponse<Trip>>(`/trips/${tripId}`);
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
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const url = `/users/${username}/trips${queryParams.toString() ? `?${queryParams}` : ''}`;
  const response = await api.get<ApiResponse<TripListResponse>>(url);

  return {
    trips: response.data.data.trips,
    total: response.data.data.total,
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
  const response = await api.post<ApiResponse<{ trip: Trip }>>('/trips', tripData);
  return response.data.data.trip;
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
  const response = await api.put<ApiResponse<{ trip: Trip }>>(`/trips/${tripId}`, updates);
  return response.data.data.trip;
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
  const response = await api.post<ApiResponse<{ trip: Trip }>>(`/trips/${tripId}/publish`);
  return response.data.data.trip;
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
