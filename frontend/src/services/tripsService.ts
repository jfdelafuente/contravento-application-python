import { api } from './api';
import { TripSummary } from '../types/trip';

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
