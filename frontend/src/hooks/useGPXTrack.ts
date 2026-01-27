/**
 * useGPXTrack Hook
 *
 * Custom hook for fetching GPX track data (simplified trackpoints for map rendering).
 * Feature 003 - GPS Routes Interactive (User Story 2)
 */

import { useEffect, useState } from 'react';
import { getGPXTrack, TrackDataResponse } from '../services/gpxService';

interface UseGPXTrackReturn {
  /** Track data with simplified trackpoints */
  track: TrackDataResponse | null;

  /** Loading state */
  isLoading: boolean;

  /** Error message (Spanish) */
  error: string | null;

  /** Refetch track data */
  refetch: () => Promise<void>;
}

/**
 * Fetch GPX track data for map visualization
 *
 * @param gpxFileId - GPX file identifier (null to skip fetching)
 * @returns Track data, loading state, and error
 *
 * @example
 * ```typescript
 * const { track, isLoading, error } = useGPXTrack(trip.gpx_file?.gpx_file_id);
 *
 * if (isLoading) return <Spinner />;
 * if (error) return <Error message={error} />;
 * if (track) return <TripMap trackPoints={track.trackpoints} />;
 * ```
 */
export const useGPXTrack = (gpxFileId: string | null | undefined): UseGPXTrackReturn => {
  const [track, setTrack] = useState<TrackDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrack = async () => {
    if (!gpxFileId) {
      setTrack(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const trackData = await getGPXTrack(gpxFileId);
      setTrack(trackData);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message || 'Error al cargar datos de la ruta GPS';
      setError(errorMessage);
      setTrack(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrack();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gpxFileId]);

  return {
    track,
    isLoading,
    error,
    refetch: fetchTrack,
  };
};
