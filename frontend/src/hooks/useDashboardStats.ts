/**
 * useDashboardStats Hook
 * Feature: 015-dashboard-redesign - User Story 1
 *
 * Hook para obtener las estadísticas personales del usuario desde el dashboard.
 * Maneja estados de carga, error y datos.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getDashboardStats } from '../services/dashboardService';
import type { DashboardStats } from '../types/dashboard';

export interface UseDashboardStatsResult {
  /** Estadísticas del usuario (null mientras carga o si hay error) */
  stats: DashboardStats | null;

  /** true durante la carga inicial o recarga */
  isLoading: boolean;

  /** Mensaje de error (null si no hay error) */
  error: string | null;

  /** Función para recargar las estadísticas manualmente */
  refetch: () => void;
}

/**
 * Obtiene las estadísticas del dashboard del usuario autenticado
 *
 * @returns UseDashboardStatsResult con stats, isLoading, error, refetch
 *
 * @example
 * ```tsx
 * function StatsOverview() {
 *   const { stats, isLoading, error, refetch } = useDashboardStats();
 *
 *   if (isLoading) return <SkeletonLoader variant="card" count={3} />;
 *   if (error) return <ErrorMessage message={error} onRetry={refetch} />;
 *
 *   return (
 *     <div>
 *       <p>Viajes: {stats.total_trips}</p>
 *       <p>Distancia: {stats.total_distance_km} km</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function useDashboardStats(): UseDashboardStatsResult {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    // Si no hay usuario autenticado, no hacer la petición
    if (!user?.username) {
      setIsLoading(false);
      setError('Usuario no autenticado');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const data = await getDashboardStats(user.username);
      setStats(data);
    } catch (err: any) {
      // Extraer mensaje de error del backend (estructura estándar)
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        'Error al cargar las estadísticas del dashboard';

      setError(errorMessage);
      setStats(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch automático al montar el componente o cuando cambia el usuario
  useEffect(() => {
    fetchStats();
  }, [user?.username]);

  // Función de refetch para reintentar manualmente
  const refetch = () => {
    fetchStats();
  };

  return {
    stats,
    isLoading,
    error,
    refetch,
  };
}
