/**
 * TripSortDropdown Component
 *
 * Dropdown for selecting trip sort order (most recent, distance, popularity, etc.).
 * Updates sort selection and triggers filter updates.
 *
 * Used in:
 * - TripsListPage (alongside search and filters)
 */

import React from 'react';
import { TRIP_SORT_OPTIONS } from '../../types/sort';
import './TripSortDropdown.css';

interface TripSortDropdownProps {
  /** Currently selected sort option value */
  value: string;
  /** Handler for sort selection changes */
  onChange: (value: string) => void;
  /** Whether dropdown is disabled */
  disabled?: boolean;
}

export const TripSortDropdown: React.FC<TripSortDropdownProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className="trip-sort-dropdown">
      <label htmlFor="trip-sort" className="trip-sort-dropdown__label">
        Ordenar por:
      </label>
      <div className="trip-sort-dropdown__wrapper">
        <svg
          className="trip-sort-dropdown__icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
          />
        </svg>
        <select
          id="trip-sort"
          className="trip-sort-dropdown__select"
          value={value}
          onChange={handleChange}
          disabled={disabled}
          aria-label="Seleccionar orden de viajes"
        >
          {TRIP_SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <svg
          className="trip-sort-dropdown__chevron"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </div>
  );
};
