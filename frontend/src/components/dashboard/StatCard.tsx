/**
 * StatCard Component
 * Feature: 015-dashboard-redesign - User Story 1
 *
 * Componente reutilizable para mostrar una estadística individual del dashboard.
 * Usa Tailwind CSS para estilos.
 */

import React from 'react';
import { cn } from '../../lib/cn';

export interface StatCardProps {
  /** Etiqueta descriptiva de la estadística */
  label: string;

  /** Valor numérico a mostrar */
  value: number | string;

  /** Icono SVG o emoji para la estadística */
  icon?: React.ReactNode;

  /** Unidad de medida (opcional, ej: "km", "pueblos") */
  unit?: string;

  /** Color del borde superior (verde/azul/amarillo/etc) */
  accentColor?: 'primary' | 'success' | 'info' | 'warning';

  /** Clases adicionales para personalización */
  className?: string;
}

/**
 * Tarjeta para mostrar una estadística individual con icono, valor y etiqueta
 *
 * @example
 * ```tsx
 * <StatCard
 *   label="Viajes Realizados"
 *   value={42}
 *   icon={<TripIcon />}
 *   accentColor="primary"
 * />
 *
 * <StatCard
 *   label="Distancia Total"
 *   value={3547.5}
 *   unit="km"
 *   accentColor="success"
 * />
 * ```
 */
export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon,
  unit,
  accentColor = 'primary',
  className,
}) => {
  // Colores modernos con gradientes sutiles y fondos de color
  const colorSchemes = {
    primary: {
      bg: 'bg-gradient-to-br from-green-50 to-emerald-50',
      iconBg: 'bg-green-100',
      iconText: 'text-green-700',
      ring: 'ring-green-500/20',
      value: 'text-green-900',
    },
    success: {
      bg: 'bg-gradient-to-br from-emerald-50 to-teal-50',
      iconBg: 'bg-emerald-100',
      iconText: 'text-emerald-700',
      ring: 'ring-emerald-500/20',
      value: 'text-emerald-900',
    },
    info: {
      bg: 'bg-gradient-to-br from-blue-50 to-cyan-50',
      iconBg: 'bg-blue-100',
      iconText: 'text-blue-700',
      ring: 'ring-blue-500/20',
      value: 'text-blue-900',
    },
    warning: {
      bg: 'bg-gradient-to-br from-amber-50 to-yellow-50',
      iconBg: 'bg-amber-100',
      iconText: 'text-amber-700',
      ring: 'ring-amber-500/20',
      value: 'text-amber-900',
    },
  };

  const colors = colorSchemes[accentColor];

  return (
    <div
      className={cn(
        // Card base con gradiente de fondo
        'relative overflow-hidden rounded-xl p-4 sm:p-5 lg:p-6',
        colors.bg,

        // Borde sutil con ring
        'ring-1 ring-inset',
        colors.ring,

        // Efectos de hover modernos
        'transition-all duration-300 ease-in-out',
        'hover:shadow-lg hover:shadow-black/5',
        'hover:-translate-y-1',
        'hover:ring-2',

        // Custom classes
        className
      )}
    >
      {/* Patrón de fondo decorativo sutil */}
      <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.5))] opacity-20" aria-hidden="true" />

      <div className="relative flex flex-col">
        {/* Header: Icon + Label (horizontal) */}
        <div className="flex items-center gap-2 sm:gap-3 mb-4">
          {/* Icon Badge */}
          {icon && (
            <div
              className={cn(
                'flex-shrink-0 flex items-center justify-center',
                'w-10 h-10 sm:w-12 sm:h-12 rounded-lg',
                colors.iconBg,
                colors.iconText,
                'text-xl sm:text-2xl',
                'shadow-sm'
              )}
              aria-hidden="true"
            >
              {icon}
            </div>
          )}

          {/* Label */}
          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm font-medium text-gray-600 leading-tight">
              {label}
            </p>
          </div>
        </div>

        {/* Value + Unit (centrado) */}
        <div className="flex items-baseline justify-center gap-1.5 flex-wrap">
          <span className={cn(
            'text-2xl sm:text-3xl font-bold tracking-tight',
            colors.value
          )}>
            {typeof value === 'number' ? value.toLocaleString('es-ES') : value}
          </span>
          {unit && (
            <span className="text-base sm:text-lg font-medium text-gray-500 whitespace-nowrap">
              {unit}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
