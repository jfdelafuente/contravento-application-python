/**
 * POI Service
 *
 * API service for managing Points of Interest (POIs) on trip routes.
 * Feature 003 - User Story 4: Points of Interest along routes.
 */

import { api } from './api';
import {
  POI,
  POICreateInput,
  POIUpdateInput,
  POIReorderInput as _POIReorderInput,
  POIListResponse,
  POIType,
} from '../types/poi';

// ============================================================================
// POI CRUD Operations
// ============================================================================

/**
 * Create a new POI for a trip
 *
 * FR-029: Users can add POIs to published trips
 * SC-029: Maximum 20 POIs per trip
 *
 * @param tripId - Parent trip ID
 * @param data - POI creation data
 * @returns Created POI
 * @throws Error if trip not published, max 20 POIs exceeded, or user not owner
 */
export async function createPOI(
  tripId: string,
  data: POICreateInput
): Promise<POI> {
  const response = await api.post<POI>(`/trips/${tripId}/pois`, data);
  return response.data;
}

/**
 * Get all POIs for a trip, optionally filtered by type
 *
 * SC-030: POIs can be filtered by type
 *
 * @param tripId - Trip ID
 * @param poiType - Optional type filter (viewpoint, town, water, etc.)
 * @returns List of POIs ordered by sequence
 */
export async function getTripPOIs(
  tripId: string,
  poiType?: POIType
): Promise<POIListResponse> {
  const params = poiType ? { poi_type: poiType } : {};
  const response = await api.get<POIListResponse>(`/trips/${tripId}/pois`, {
    params,
  });
  return response.data;
}

/**
 * Get a single POI by ID
 *
 * SC-031: Clicking POI shows popup with name, description, photo, distance
 *
 * @param poiId - POI ID
 * @returns POI details
 * @throws Error if POI not found
 */
export async function getPOI(poiId: string): Promise<POI> {
  const response = await api.get<POI>(`/pois/${poiId}`);
  return response.data;
}

/**
 * Update an existing POI
 *
 * Only trip owner can update.
 *
 * @param poiId - POI ID
 * @param data - POI update data (only provided fields will be updated)
 * @returns Updated POI
 * @throws Error if POI not found or user not owner
 */
export async function updatePOI(
  poiId: string,
  data: POIUpdateInput
): Promise<POI> {
  const response = await api.put<POI>(`/pois/${poiId}`, data);
  return response.data;
}

/**
 * Delete a POI
 *
 * Only trip owner can delete.
 *
 * @param poiId - POI ID
 * @throws Error if POI not found or user not owner
 */
export async function deletePOI(poiId: string): Promise<void> {
  await api.delete(`/pois/${poiId}`);
}

/**
 * Reorder POIs for a trip
 *
 * FR-029: Users can reorder POIs without affecting GPX route
 *
 * @param tripId - Trip ID
 * @param poiIds - Ordered list of POI IDs (must include all trip POIs)
 * @returns Reordered POI list
 * @throws Error if POI list doesn't match trip POIs or user not owner
 */
export async function reorderPOIs(
  tripId: string,
  poiIds: string[]
): Promise<POIListResponse> {
  const response = await api.post<POIListResponse>(
    `/trips/${tripId}/pois/reorder`,
    { poi_ids: poiIds }
  );
  return response.data;
}

/**
 * Upload a photo to a POI
 *
 * FR-010 (Feature 017): POIs can have photos (max 5MB)
 *
 * @param poiId - POI ID
 * @param photo - Photo file (JPEG, PNG, WebP, max 5MB)
 * @returns Updated POI with photo_url
 * @throws Error if file too large, invalid format, or user not owner
 */
export async function uploadPOIPhoto(
  poiId: string,
  photo: File
): Promise<POI> {
  // Client-side validation
  const MAX_SIZE_MB = 5;
  const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

  if (photo.size > MAX_SIZE_BYTES) {
    throw new Error(`La foto excede el tamaño máximo de ${MAX_SIZE_MB}MB`);
  }

  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
  if (!allowedTypes.includes(photo.type)) {
    throw new Error('Solo se permiten archivos JPEG, PNG y WebP');
  }

  // Create FormData for multipart/form-data request
  const formData = new FormData();
  formData.append('photo', photo);

  const response = await api.post<{ success: boolean; data: POI; error: null }>(
    `/pois/${poiId}/photo`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data.data;
}
