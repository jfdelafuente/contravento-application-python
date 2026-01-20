/**
 * StatsOverview Component
 * Feature: 015-dashboard-redesign - User Story 1
 *
 * Componente principal para mostrar las estadísticas personales del usuario.
 * Incluye:
 * - Responsive grid layout (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
 * - Skeleton loading state
 * - Error handling con retry button
 * - Mensajes motivacionales para usuarios nuevos (cero estadísticas)
 */

import React from 'react';
import { useDashboardStats } from '../../hooks/useDashboardStats';
import StatCard from './StatCard';
import SkeletonLoader from '../common/SkeletonLoader';
import { cn } from '../../lib/cn';

export interface StatsOverviewProps {
  /** Clases adicionales para el contenedor */
  className?: string;
}

/**
 * Vista general de estadísticas del usuario con grid responsivo
 *
 * @example
 * ```tsx
 * <StatsOverview />
 * ```
 */
export const StatsOverview: React.FC<StatsOverviewProps> = ({ className }) => {
  const { stats, isLoading, error, refetch } = useDashboardStats();

  // Loading state - Skeleton loaders
  if (isLoading) {
    return (
      <div
        className={cn(
          'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
          className
        )}
        aria-busy="true"
        aria-live="polite"
      >
        <SkeletonLoader variant="card" height="150px" count={6} />
      </div>
    );
  }

  // Error state - Error message con retry button
  if (error) {
    return (
      <div
        className={cn(
          'bg-red-50 border border-red-200 rounded-lg p-6 text-center',
          className
        )}
        role="alert"
        aria-live="assertive"
      >
        <div className="text-red-600 mb-4">
          <svg
            className="w-12 h-12 mx-auto mb-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <p className="text-lg font-semibold mb-2">Error al cargar estadísticas</p>
          <p className="text-sm text-red-700">{error}</p>
        </div>

        <button
          onClick={refetch}
          className={cn(
            'px-6 py-2 bg-red-600 text-white rounded-lg',
            'hover:bg-red-700 transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2'
          )}
          aria-label="Reintentar carga de estadísticas"
        >
          Reintentar
        </button>
      </div>
    );
  }

  // No stats (usuario nuevo) - Mensaje motivacional
  if (!stats) {
    return (
      <div
        className={cn(
          'bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-8 text-center',
          className
        )}
      >
        <div className="text-6xl mb-4" aria-hidden="true">
          🚴
        </div>
        <h3 className="text-2xl font-bold text-gray-800 mb-2">
          ¡Bienvenido a ContraVento!
        </h3>
        <p className="text-gray-600 mb-4">
          Aún no has registrado ningún viaje. Empieza a documentar tus aventuras
          ciclistas y descubre pueblos, comercios locales y rutas increíbles.
        </p>
        <a
          href="/trips/new"
          className={cn(
            'inline-block px-6 py-3 bg-[#6B8E23] text-white rounded-lg font-semibold',
            'hover:bg-[#556B1A] transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-[#6B8E23] focus:ring-offset-2'
          )}
        >
          Registrar mi primer viaje
        </a>
      </div>
    );
  }

  // Success state - Stats grid
  const isNewUser = stats.total_trips === 0;

  return (
    <div className={cn('space-y-6', className)}>
      {/* Motivational message for users with zero trips */}
      {isNewUser && (
        <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <span className="text-2xl" aria-hidden="true">💡</span>
            <p className="text-amber-900 text-sm leading-relaxed flex-1">
              <strong className="font-semibold">Consejo:</strong> Registra tu primer viaje para empezar a
              acumular estadísticas y descubrir rutas sugeridas personalizadas.
            </p>
          </div>
        </div>
      )}

      {/* Stats Grid - Responsive (1 col mobile, 2 cols tablet, 3 cols desktop) */}
      <div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6"
        role="region"
        aria-label="Estadísticas personales del ciclista"
      >
        {/* Viajes Realizados */}
        <StatCard
          label="Viajes Realizados"
          value={stats.total_trips}
          icon="🚴"
          accentColor="primary"
        />

        {/* Distancia Total */}
        <StatCard
          label="Distancia Total"
          value={stats.total_distance_km.toFixed(1)}
          unit="km"
          icon="📏"
          accentColor="success"
        />

        {/* Pueblos Visitados */}
        <StatCard
          label="Pueblos Visitados"
          value={stats.towns_visited}
          icon="🏘️"
          accentColor="info"
        />

        {/* Países Visitados */}
        <StatCard
          label="Países Visitados"
          value={stats.countries_visited}
          icon="🌍"
          accentColor="warning"
        />

        {/* Fotos Compartidas */}
        <StatCard
          label="Fotos Compartidas"
          value={stats.total_photos}
          icon="📷"
          accentColor="primary"
        />

        {/* Impacto Económico Local */}
        <StatCard
          label="Impacto Económico Local"
          value={
            stats.local_economic_impact_euros
              ? `${stats.local_economic_impact_euros.toFixed(2)}€`
              : 'N/A'
          }
          icon="💶"
          accentColor="success"
        />

        {/* Seguidores */}
        <StatCard
          label="Seguidores"
          value={stats.followers_count}
          icon="👥"
          accentColor="info"
        />

        {/* Siguiendo */}
        <StatCard
          label="Siguiendo"
          value={stats.following_count}
          icon="🤝"
          accentColor="warning"
        />

        {/* Logros Desbloqueados */}
        <StatCard
          label="Logros Desbloqueados"
          value={`${stats.achievements_unlocked}/${stats.achievements_total}`}
          icon="🏆"
          accentColor="primary"
        />
      </div>

      {/* Last updated timestamp */}
      <p className="text-xs text-gray-500 text-right mt-4">
        Última actualización:{' '}
        {new Date(stats.last_updated).toLocaleString('es-ES', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })}
      </p>
    </div>
  );
};

export default StatsOverview;
