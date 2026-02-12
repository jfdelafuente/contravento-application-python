import { api } from './api';
import { TripSummary, PublicTripSummary } from '../types/trip';

interface GetTripsParams {
  username: string;
  status?: 'draft' | 'published';
  limit?: number;
  offset?: number;
}

interface TripsApiResponse {
  success: boolean;
  data: {
    trips: TripSummary[];
    count: number;
    limit: number;
    offset: number;
  };
  error: null | any;
}

interface PublicTripsApiResponse {
  trips: PublicTripSummary[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  };
}

/**
 * Fetch user's trips
 * @param params - Query parameters (username, status, limit, offset)
 * @returns List of trips
 */
export const getUserTrips = async (params: GetTripsParams): Promise<TripSummary[]> => {
  const { username, status, limit, offset } = params;

  const queryParams = new URLSearchParams();
  if (status) queryParams.append('status', status);
  if (limit) queryParams.append('limit', limit.toString());
  if (offset) queryParams.append('offset', offset.toString());

  const url = `/users/${username}/trips${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  const response = await api.get<TripsApiResponse>(url);
  return response.data.data.trips;
};

/**
 * Fetch recent published trips for current user
 * Convenience function for dashboard recent trips
 * @param username - Current user's username
 * @param limit - Number of trips to fetch (default: 5)
 * @returns List of recent published trips
 */
export const getRecentTrips = async (username: string, limit: number = 5): Promise<TripSummary[]> => {
  return await getUserTrips({
    username,
    status: 'published',
    limit,
  });
};

/**
 * Fetch public trips feed (Feature 013)
 * No authentication required - fully public endpoint
 * @param page - Page number (1-indexed, default: 1)
 * @param limit - Items per page (default: 8, max: 50)
 * @returns Paginated list of published trips with public visibility
 */
export const getPublicTrips = async (page: number = 1, limit: number = 8): Promise<PublicTripsApiResponse> => {
  const queryParams = new URLSearchParams();
  queryParams.append('page', page.toString());
  queryParams.append('limit', limit.toString());

  const url = `/trips/public?${queryParams.toString()}`;
  const response = await api.get<PublicTripsApiResponse>(url);
  return response.data;
};
