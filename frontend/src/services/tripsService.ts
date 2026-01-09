import { api } from './api';
import { TripSummary } from '../types/trip';

interface GetTripsParams {
  username: string;
  status?: 'DRAFT' | 'PUBLISHED';
  limit?: number;
  offset?: number;
}

interface GetTripsResponse {
  trips: TripSummary[];
  total: number;
}

/**
 * Fetch user's trips
 * @param params - Query parameters (username, status, limit, offset)
 * @returns List of trips and total count
 */
export const getUserTrips = async (params: GetTripsParams): Promise<GetTripsResponse> => {
  const { username, status, limit, offset } = params;

  const queryParams = new URLSearchParams();
  if (status) queryParams.append('status', status);
  if (limit) queryParams.append('limit', limit.toString());
  if (offset) queryParams.append('offset', offset.toString());

  const url = `/users/${username}/trips${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  const response = await api.get<GetTripsResponse>(url);
  return response.data;
};

/**
 * Fetch recent published trips for current user
 * Convenience function for dashboard recent trips
 * @param username - Current user's username
 * @param limit - Number of trips to fetch (default: 5)
 * @returns List of recent published trips
 */
export const getRecentTrips = async (username: string, limit: number = 5): Promise<TripSummary[]> => {
  const response = await getUserTrips({
    username,
    status: 'PUBLISHED',
    limit,
  });
  return response.trips;
};
