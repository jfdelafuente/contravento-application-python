/**
 * AdvancedStats Component (Feature 003 - User Story 5)
 *
 * Displays advanced route statistics calculated from GPX files with timestamps.
 *
 * Features:
 * - Speed metrics (average, maximum)
 * - Time analysis (total time, moving time)
 * - Gradient metrics (average, maximum)
 * - Top climbs table
 *
 * Only displayed if GPX file has timestamps and statistics are available.
 */

import React from 'react';
import { RouteStatistics } from '../../types/gpx';
import './AdvancedStats.css';

interface AdvancedStatsProps {
  /** Route statistics data */
  statistics: RouteStatistics;
}

/**
 * Format time in minutes to human-readable format (e.g., "2h 15min")
 */
const formatTime = (minutes: number | null): string => {
  if (minutes === null || minutes === 0) return 'N/A';

  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);

  if (hours === 0) {
    return `${mins}min`;
  }

  return `${hours}h ${mins}min`;
};

/**
 * Format gradient percentage with sign and color coding
 */
const formatGradient = (gradient: number | null): string => {
  if (gradient === null) return 'N/A';

  const sign = gradient > 0 ? '+' : '';
  return `${sign}${gradient.toFixed(1)}%`;
};

export const AdvancedStats: React.FC<AdvancedStatsProps> = ({ statistics }) => {
  return (
    <div className="advanced-stats">
      <div className="advanced-stats__header">
        <h3 className="advanced-stats__title">Estadísticas Avanzadas</h3>
        <p className="advanced-stats__subtitle">Basado en timestamps del archivo GPX</p>
      </div>

      <div className="advanced-stats__grid">
        {/* Speed Metrics */}
        <div className="advanced-stats__section">
          <h4 className="advanced-stats__section-title">
            <svg
              className="advanced-stats__icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
            Velocidad
          </h4>
          <div className="advanced-stats__metrics">
            <div className="advanced-stats__metric">
              <span className="advanced-stats__metric-label">Promedio</span>
              <span className="advanced-stats__metric-value">
                {statistics.avg_speed_kmh !== null
                  ? `${statistics.avg_speed_kmh.toFixed(1)} km/h`
                  : 'N/A'}
              </span>
            </div>
            <div className="advanced-stats__metric">
              <span className="advanced-stats__metric-label">Máxima</span>
              <span className="advanced-stats__metric-value advanced-stats__metric-value--highlight">
                {statistics.max_speed_kmh !== null
                  ? `${statistics.max_speed_kmh.toFixed(1)} km/h`
                  : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Time Metrics */}
        <div className="advanced-stats__section">
          <h4 className="advanced-stats__section-title">
            <svg
              className="advanced-stats__icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Tiempo
          </h4>
          <div className="advanced-stats__metrics">
            <div className="advanced-stats__metric">
              <span className="advanced-stats__metric-label">Total</span>
              <span className="advanced-stats__metric-value">
                {formatTime(statistics.total_time_minutes)}
              </span>
            </div>
            <div className="advanced-stats__metric">
              <span className="advanced-stats__metric-label">En movimiento</span>
              <span className="advanced-stats__metric-value">
                {formatTime(statistics.moving_time_minutes)}
              </span>
            </div>
          </div>
        </div>

        {/* Gradient Metrics */}
        <div className="advanced-stats__section">
          <h4 className="advanced-stats__section-title">
            <svg
              className="advanced-stats__icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
            Pendiente
          </h4>
          <div className="advanced-stats__metrics">
            <div className="advanced-stats__metric">
              <span className="advanced-stats__metric-label">Promedio</span>
              <span className="advanced-stats__metric-value">
                {formatGradient(statistics.avg_gradient)}
              </span>
            </div>
            <div className="advanced-stats__metric">
              <span className="advanced-stats__metric-label">Máxima</span>
              <span
                className={`advanced-stats__metric-value ${
                  statistics.max_gradient && statistics.max_gradient > 10
                    ? 'advanced-stats__metric-value--steep'
                    : ''
                }`}
              >
                {formatGradient(statistics.max_gradient)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Gradient Distribution Chart (FR-032) */}
      {statistics.gradient_distribution && (
        <div className="advanced-stats__gradient">
          <h4 className="advanced-stats__section-title">
            <svg
              className="advanced-stats__icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            Distribución de Pendientes
          </h4>
          <div className="advanced-stats__gradient-chart">
            {/* Llano (0-3%) */}
            <div className="advanced-stats__gradient-bar">
              <div className="advanced-stats__gradient-label">
                <span className="advanced-stats__gradient-name">Llano (0-3%)</span>
                <span className="advanced-stats__gradient-value">
                  {statistics.gradient_distribution.llano.distance_km.toFixed(1)} km (
                  {statistics.gradient_distribution.llano.percentage.toFixed(1)}%)
                </span>
              </div>
              <div className="advanced-stats__gradient-bar-bg">
                <div
                  className="advanced-stats__gradient-bar-fill advanced-stats__gradient-bar-fill--llano"
                  style={{ width: `${statistics.gradient_distribution.llano.percentage}%` }}
                />
              </div>
            </div>

            {/* Moderado (3-6%) */}
            <div className="advanced-stats__gradient-bar">
              <div className="advanced-stats__gradient-label">
                <span className="advanced-stats__gradient-name">Moderado (3-6%)</span>
                <span className="advanced-stats__gradient-value">
                  {statistics.gradient_distribution.moderado.distance_km.toFixed(1)} km (
                  {statistics.gradient_distribution.moderado.percentage.toFixed(1)}%)
                </span>
              </div>
              <div className="advanced-stats__gradient-bar-bg">
                <div
                  className="advanced-stats__gradient-bar-fill advanced-stats__gradient-bar-fill--moderado"
                  style={{ width: `${statistics.gradient_distribution.moderado.percentage}%` }}
                />
              </div>
            </div>

            {/* Empinado (6-10%) */}
            <div className="advanced-stats__gradient-bar">
              <div className="advanced-stats__gradient-label">
                <span className="advanced-stats__gradient-name">Empinado (6-10%)</span>
                <span className="advanced-stats__gradient-value">
                  {statistics.gradient_distribution.empinado.distance_km.toFixed(1)} km (
                  {statistics.gradient_distribution.empinado.percentage.toFixed(1)}%)
                </span>
              </div>
              <div className="advanced-stats__gradient-bar-bg">
                <div
                  className="advanced-stats__gradient-bar-fill advanced-stats__gradient-bar-fill--empinado"
                  style={{ width: `${statistics.gradient_distribution.empinado.percentage}%` }}
                />
              </div>
            </div>

            {/* Muy empinado (>10%) */}
            <div className="advanced-stats__gradient-bar">
              <div className="advanced-stats__gradient-label">
                <span className="advanced-stats__gradient-name">Muy empinado (&gt;10%)</span>
                <span className="advanced-stats__gradient-value">
                  {statistics.gradient_distribution.muy_empinado.distance_km.toFixed(1)} km (
                  {statistics.gradient_distribution.muy_empinado.percentage.toFixed(1)}%)
                </span>
              </div>
              <div className="advanced-stats__gradient-bar-bg">
                <div
                  className="advanced-stats__gradient-bar-fill advanced-stats__gradient-bar-fill--muy-empinado"
                  style={{ width: `${statistics.gradient_distribution.muy_empinado.percentage}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Climbs Table */}
      {statistics.top_climbs && statistics.top_climbs.length > 0 && (
        <div className="advanced-stats__climbs">
          <h4 className="advanced-stats__section-title">
            <svg
              className="advanced-stats__icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 3l3.057-3L12 2.557 16.943 0 20 3v18l-3.057 3L12 21.443 7.057 24 4 21V3z"
              />
            </svg>
            Top Subidas
          </h4>
          <div className="advanced-stats__climbs-table">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Inicio</th>
                  <th>Fin</th>
                  <th>Desnivel</th>
                  <th>Pendiente</th>
                </tr>
              </thead>
              <tbody>
                {statistics.top_climbs.map((climb, index) => (
                  <tr key={index}>
                    <td className="advanced-stats__climbs-rank">{index + 1}</td>
                    <td>{climb.start_km.toFixed(1)} km</td>
                    <td>{climb.end_km.toFixed(1)} km</td>
                    <td className="advanced-stats__climbs-elevation">
                      {climb.elevation_gain_m.toFixed(0)}m
                    </td>
                    <td
                      className={`advanced-stats__climbs-gradient ${
                        climb.avg_gradient > 10
                          ? 'advanced-stats__climbs-gradient--steep'
                          : climb.avg_gradient > 6
                          ? 'advanced-stats__climbs-gradient--moderate'
                          : ''
                      }`}
                    >
                      {formatGradient(climb.avg_gradient)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Info Footer */}
      <div className="advanced-stats__footer">
        <svg
          className="advanced-stats__footer-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="advanced-stats__footer-text">
          Las estadísticas se calculan automáticamente cuando el archivo GPX incluye timestamps.
          Las paradas se detectan cuando la velocidad es inferior a 3 km/h.
        </p>
      </div>
    </div>
  );
};
