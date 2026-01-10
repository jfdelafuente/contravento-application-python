/**
 * TripFilters Component
 *
 * Filter panel for trips list with search input, tag chips, and status toggle.
 * Updates in real-time as user types or clicks filter options.
 *
 * Used in:
 * - TripsListPage (top section above trip grid)
 */

import React from 'react';
import { Tag } from '../../types/trip';
import './TripFilters.css';

interface TripFiltersProps {
  /** Current search query */
  searchQuery: string;
  /** Handler for search input changes */
  onSearchChange: (query: string) => void;

  /** Currently selected tag (null if none selected) */
  selectedTag: string | null;
  /** Handler for tag selection/deselection */
  onTagSelect: (tagName: string | null) => void;

  /** Available tags for filtering */
  availableTags: Tag[];

  /** Currently selected status filter (null shows both, 'draft' or 'published') */
  selectedStatus: 'draft' | 'published' | null;
  /** Handler for status filter changes */
  onStatusChange: (status: 'draft' | 'published' | null) => void;

  /** Whether to show status filter (only shown for own trips) */
  showStatusFilter?: boolean;

  /** Whether filters are loading */
  isLoading?: boolean;
}

export const TripFilters: React.FC<TripFiltersProps> = ({
  searchQuery,
  onSearchChange,
  selectedTag,
  onTagSelect,
  availableTags,
  selectedStatus,
  onStatusChange,
  showStatusFilter = false,
  isLoading = false,
}) => {
  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(e.target.value);
  };

  // Handle tag chip click
  const handleTagClick = (tagName: string) => {
    // If clicking the already-selected tag, deselect it
    if (selectedTag === tagName) {
      onTagSelect(null);
    } else {
      onTagSelect(tagName);
    }
  };

  // Handle clear all filters
  const handleClearFilters = () => {
    onSearchChange('');
    onTagSelect(null);
    onStatusChange(null);
  };

  // Check if any filters are active
  const hasActiveFilters = searchQuery || selectedTag || selectedStatus;

  return (
    <div className="trip-filters">
      {/* Search Input */}
      <div className="trip-filters__search-section">
        <div className="trip-filters__search-wrapper">
          <svg
            className="trip-filters__search-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            className="trip-filters__search-input"
            placeholder="Buscar viajes..."
            value={searchQuery}
            onChange={handleSearchChange}
            disabled={isLoading}
          />
          {searchQuery && (
            <button
              className="trip-filters__search-clear"
              onClick={() => onSearchChange('')}
              aria-label="Limpiar búsqueda"
            >
              <svg
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>

        {/* Clear all filters button */}
        {hasActiveFilters && (
          <button className="trip-filters__clear-all" onClick={handleClearFilters}>
            Limpiar filtros
          </button>
        )}
      </div>

      {/* Status Filter (only shown if showStatusFilter=true) */}
      {showStatusFilter && (
        <div className="trip-filters__status-section">
          <span className="trip-filters__label">Estado:</span>
          <div className="trip-filters__status-buttons">
            <button
              className={`trip-filters__status-button ${
                selectedStatus === null ? 'trip-filters__status-button--active' : ''
              }`}
              onClick={() => onStatusChange(null)}
              disabled={isLoading}
            >
              Todos
            </button>
            <button
              className={`trip-filters__status-button ${
                selectedStatus === 'published' ? 'trip-filters__status-button--active' : ''
              }`}
              onClick={() => onStatusChange('published')}
              disabled={isLoading}
            >
              Publicados
            </button>
            <button
              className={`trip-filters__status-button ${
                selectedStatus === 'draft' ? 'trip-filters__status-button--active' : ''
              }`}
              onClick={() => onStatusChange('draft')}
              disabled={isLoading}
            >
              Borradores
            </button>
          </div>
        </div>
      )}

      {/* Tag Filter */}
      <div className="trip-filters__tags-section">
        <span className="trip-filters__label">Etiquetas:</span>

        {isLoading ? (
          <div className="trip-filters__tags-loading">
            <div className="trip-filters__tag-skeleton" />
            <div className="trip-filters__tag-skeleton" />
            <div className="trip-filters__tag-skeleton" />
          </div>
        ) : availableTags.length > 0 ? (
          <div className="trip-filters__tags">
            {availableTags.slice(0, 12).map((tag) => (
              <button
                key={tag.tag_id}
                className={`trip-filters__tag ${
                  selectedTag === tag.name ? 'trip-filters__tag--active' : ''
                }`}
                onClick={() => handleTagClick(tag.name)}
                disabled={isLoading}
              >
                {tag.name}
                <span className="trip-filters__tag-count">({tag.usage_count})</span>
              </button>
            ))}
          </div>
        ) : (
          <p className="trip-filters__no-tags">No hay etiquetas disponibles</p>
        )}
      </div>

      {/* Active filters summary */}
      {hasActiveFilters && (
        <div className="trip-filters__active-summary">
          <span className="trip-filters__active-label">Filtros activos:</span>
          {searchQuery && (
            <span className="trip-filters__active-chip">
              Búsqueda: "{searchQuery}"
              <button
                className="trip-filters__active-chip-remove"
                onClick={() => onSearchChange('')}
                aria-label="Eliminar filtro de búsqueda"
              >
                ×
              </button>
            </span>
          )}
          {selectedTag && (
            <span className="trip-filters__active-chip">
              Etiqueta: {selectedTag}
              <button
                className="trip-filters__active-chip-remove"
                onClick={() => onTagSelect(null)}
                aria-label="Eliminar filtro de etiqueta"
              >
                ×
              </button>
            </span>
          )}
          {selectedStatus && (
            <span className="trip-filters__active-chip">
              Estado: {selectedStatus === 'draft' ? 'Borradores' : 'Publicados'}
              <button
                className="trip-filters__active-chip-remove"
                onClick={() => onStatusChange(null)}
                aria-label="Eliminar filtro de estado"
              >
                ×
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
};
