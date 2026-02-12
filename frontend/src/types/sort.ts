/**
 * Sort Options for Trips
 *
 * Defines available sorting methods for trip lists.
 */

export type SortField = 'date' | 'distance' | 'popularity';
export type SortOrder = 'asc' | 'desc';

export interface SortOption {
  /** Unique identifier for the sort option */
  value: string;
  /** Display label in Spanish */
  label: string;
  /** Field to sort by */
  field: SortField;
  /** Sort order (ascending/descending) */
  order: SortOrder;
  /** Icon for the option (optional) */
  icon?: string;
}

/**
 * Available sort options for trips
 */
export const TRIP_SORT_OPTIONS: SortOption[] = [
  {
    value: 'date-desc',
    label: 'Más recientes primero',
    field: 'date',
    order: 'desc',
    icon: '📅',
  },
  {
    value: 'date-asc',
    label: 'Más antiguos primero',
    field: 'date',
    order: 'asc',
    icon: '📆',
  },
  {
    value: 'distance-desc',
    label: 'Mayor distancia',
    field: 'distance',
    order: 'desc',
    icon: '🚴‍♂️',
  },
  {
    value: 'distance-asc',
    label: 'Menor distancia',
    field: 'distance',
    order: 'asc',
    icon: '🚴',
  },
  {
    value: 'popularity-desc',
    label: 'Más populares',
    field: 'popularity',
    order: 'desc',
    icon: '⭐',
  },
];

/**
 * Default sort option (most recent first)
 */
export const DEFAULT_SORT_OPTION = TRIP_SORT_OPTIONS[0];
