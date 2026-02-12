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

interface StatusCounts {
  all: number;
  published: number;
  draft: number;
}

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

  /** Currently selected visibility filter (null shows both, 'public' or 'private') */
  selectedVisibility: 'public' | 'private' | null;
  /** Handler for visibility filter changes */
  onVisibilityChange: (visibility: 'public' | 'private' | null) => void;

  /** Whether to show status filter (only shown for own trips) */
  showStatusFilter?: boolean;

  /** Trip counts by status (for status filter buttons) */
  statusCounts?: StatusCounts;

  /** Whether status counts are loading */
  countsLoading?: boolean;

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
  selectedVisibility,
  onVisibilityChange,
  showStatusFilter = false,
  statusCounts,
  countsLoading = false,
  isLoading = false,
}) => {
  // State for showing all tags or just first 8 (2 rows × 4 columns)
  const [showAllTags, setShowAllTags] = React.useState(false);

  // State for collapsing/expanding filters section
  const [isExpanded, setIsExpanded] = React.useState(false);

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
    onVisibilityChange(null);
  };

  // Check if any filters are active
  const hasActiveFilters = searchQuery || selectedTag || selectedStatus || selectedVisibility;

  // Count active filters (excluding search)
  const activeFilterCount = (selectedTag ? 1 : 0) + (selectedStatus ? 1 : 0) + (selectedVisibility ? 1 : 0);

  // Toggle filters expand/collapse
  const toggleFilters = () => setIsExpanded(!isExpanded);

  return (
    <div className="trip-filters">
      {/* Top bar: Search + Filters toggle button */}
      <div className="trip-filters__top-bar">
        {/* Search Input */}
        <div className="trip-filters__search-wrapper">
          <svg
            className="trip-filters__search-icon"
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
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            id="trip-search"
            className="trip-filters__search-input"
            placeholder="Buscar viajes..."
            value={searchQuery}
            onChange={handleSearchChange}
            disabled={isLoading}
            aria-label="Buscar viajes por título o descripción"
          />
          {searchQuery && (
            <button
              type="button"
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

        {/* Filters toggle button */}
        <button
          className={`trip-filters__toggle ${isExpanded ? 'trip-filters__toggle--active' : ''}`}
          onClick={toggleFilters}
          aria-expanded={isExpanded}
          aria-label={isExpanded ? 'Ocultar filtros' : 'Mostrar filtros'}
        >
          <svg
            className="trip-filters__toggle-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          </svg>
          <span>Filtros</span>
          {activeFilterCount > 0 && (
            <span className="trip-filters__toggle-badge">{activeFilterCount}</span>
          )}
          <svg
            className={`trip-filters__toggle-chevron ${isExpanded ? 'trip-filters__toggle-chevron--up' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {/* Clear all filters button (only if filters active) */}
        {hasActiveFilters && (
          <button className="trip-filters__clear-all" onClick={handleClearFilters}>
            Limpiar filtros
          </button>
        )}
      </div>

      {/* Collapsible filters section */}
      <div className={`trip-filters__collapsible ${isExpanded ? 'trip-filters__collapsible--expanded' : ''}`}>
        <div>
          {/* Status and Visibility Filters Row */}
          <div className="trip-filters__row">
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
                    {statusCounts && !countsLoading && (
                      <span className="trip-filters__status-count">({statusCounts.all})</span>
                    )}
                  </button>
                  <button
                    className={`trip-filters__status-button ${
                      selectedStatus === 'published' ? 'trip-filters__status-button--active' : ''
                    }`}
                    onClick={() => onStatusChange('published')}
                    disabled={isLoading}
                  >
                    Publicados
                    {statusCounts && !countsLoading && (
                      <span className="trip-filters__status-count">({statusCounts.published})</span>
                    )}
                  </button>
                  <button
                    className={`trip-filters__status-button ${
                      selectedStatus === 'draft' ? 'trip-filters__status-button--active' : ''
                    }`}
                    onClick={() => onStatusChange('draft')}
                    disabled={isLoading}
                  >
                    Borradores
                    {statusCounts && !countsLoading && (
                      <span className="trip-filters__status-count">({statusCounts.draft})</span>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Visibility Filter */}
            <div className="trip-filters__status-section">
              <span className="trip-filters__label">Visibilidad:</span>
              <div className="trip-filters__status-buttons">
                <button
                  className={`trip-filters__status-button ${
                    selectedVisibility === null ? 'trip-filters__status-button--active' : ''
                  }`}
                  onClick={() => onVisibilityChange(null)}
                  disabled={isLoading}
                >
                  Todos
                </button>
                <button
                  className={`trip-filters__status-button ${
                    selectedVisibility === 'public' ? 'trip-filters__status-button--active' : ''
                  }`}
                  onClick={() => onVisibilityChange('public')}
                  disabled={isLoading}
                >
                  Públicos
                </button>
                <button
                  className={`trip-filters__status-button ${
                    selectedVisibility === 'private' ? 'trip-filters__status-button--active' : ''
                  }`}
                  onClick={() => onVisibilityChange('private')}
                  disabled={isLoading}
                >
                  Privados
                </button>
              </div>
            </div>
          </div>

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
          <>
            <div className="trip-filters__tags">
              {(showAllTags ? availableTags : availableTags.slice(0, 8)).map((tag) => (
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

            {/* Show "Ver más/menos" button if there are more than 8 tags */}
            {availableTags.length > 8 && (
              <button
                className="trip-filters__show-more-tags"
                onClick={() => setShowAllTags(!showAllTags)}
              >
                {showAllTags
                  ? 'Ver menos'
                  : `+${availableTags.length - 8} más`
                }
              </button>
            )}
          </>
          ) : (
            <p className="trip-filters__no-tags">No hay etiquetas disponibles</p>
          )}
        </div>
      </div>
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
          {selectedVisibility && (
            <span className="trip-filters__active-chip">
              Visibilidad: {selectedVisibility === 'public' ? 'Públicos' : 'Privados'}
              <button
                className="trip-filters__active-chip-remove"
                onClick={() => onVisibilityChange(null)}
                aria-label="Eliminar filtro de visibilidad"
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
