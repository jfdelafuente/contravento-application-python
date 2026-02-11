/**
 * TripsListPage Component
 *
 * Main page for browsing trips with filters, search, and pagination.
 * Displays trips in a responsive grid with TripCard components.
 *
 * Route: /trips
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import HeaderQuickActions from '../components/dashboard/HeaderQuickActions';
import { TripCard } from '../components/trips/TripCard';
import { TripFilters } from '../components/trips/TripFilters';
import { TripSortDropdown } from '../components/trips/TripSortDropdown';
import { useTripList } from '../hooks/useTripList';
import { useTripFilters } from '../hooks/useTripFilters';
import { useTripStatusCounts } from '../hooks/useTripStatusCounts';
import { getAllTags } from '../services/tripService';
import { Tag } from '../types/trip';
import './TripsListPage.css';
import './DashboardPage.css'; // For dashboard-header styles

export const TripsListPage: React.FC = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [tagsLoading, setTagsLoading] = useState(true);

  // Get username from URL query parameter, or use logged-in user's username
  const targetUsername = searchParams.get('user') || user?.username || '';

  // Show status filter only when user is viewing their own trips
  const isViewingOwnTrips = user && targetUsername === user.username;
  const showStatusFilter = Boolean(isViewingOwnTrips);

  // Filter state management
  const {
    searchQuery,
    debouncedSearchQuery,
    setSearchQuery,
    selectedTag,
    setSelectedTag,
    selectedStatus,
    setSelectedStatus,
    selectedVisibility,
    setSelectedVisibility,
    sortBy,
    setSortBy,
    offset,
    nextPage,
    previousPage,
    goToPage,
    limit,
  } = useTripFilters({
    initialLimit: 12,
  });

  // Fetch trips based on current filters (use debounced search for API calls)
  const {
    trips,
    total,
    isLoading,
    currentPage,
    totalPages,
  } = useTripList({
    username: targetUsername,
    searchQuery: debouncedSearchQuery, // Use debounced version for API
    selectedTag,
    selectedStatus: isViewingOwnTrips ? selectedStatus : null, // Only apply status filter for own trips
    selectedVisibility: isViewingOwnTrips ? selectedVisibility : null, // Only apply visibility filter for own trips
    sortBy,
    limit,
    offset,
  });

  // Fetch available tags on mount
  useEffect(() => {
    const fetchTags = async () => {
      setTagsLoading(true);
      try {
        const tags = await getAllTags();
        setAvailableTags(tags);
      } catch (error) {
        console.error('Error fetching tags:', error);
      } finally {
        setTagsLoading(false);
      }
    };

    fetchTags();
  }, []);

  // Reset pagination when changing users
  useEffect(() => {
    goToPage(1);
  }, [targetUsername, goToPage]);

  // Clear status and visibility filters when viewing other users' trips
  useEffect(() => {
    if (!isViewingOwnTrips) {
      if (selectedStatus) setSelectedStatus(null);
      if (selectedVisibility) setSelectedVisibility(null);
    }
  }, [isViewingOwnTrips, selectedStatus, selectedVisibility, setSelectedStatus, setSelectedVisibility]);

  // Get status counts for filter buttons (only when viewing own trips)
  const { allCount, publishedCount, draftCount, isLoading: countsLoading } = useTripStatusCounts({
    username: targetUsername,
    enabled: showStatusFilter,
  });

  return (
    <div className="trips-list-page">
      {/* Header with UserMenu */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-header__logo">
            <svg
              className="dashboard-header__logo-icon"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM12 6C9.79 6 8 7.79 8 10H10C10 8.9 10.9 8 12 8C13.1 8 14 8.9 14 10C14 12 11 11.75 11 15H13C13 12.75 16 12.5 16 10C16 7.79 14.21 6 12 6Z"
                fill="currentColor"
              />
            </svg>
            <span>ContraVento</span>
          </h1>

          {/* Quick Actions - Brújula de Cabecera */}
          <HeaderQuickActions />

          <UserMenu />
        </div>
      </header>

      {/* Page Title */}
      <div className="trips-list-page__header">
        <div className="trips-list-page__header-content">
          <h1 className="trips-list-page__title">
            {isViewingOwnTrips
              ? 'Mis Viajes'
              : targetUsername
                ? `Viajes de @${targetUsername}`
                : 'Viajes'
            }
          </h1>
          <p className="trips-list-page__subtitle">
            {isViewingOwnTrips
              ? 'Explora, organiza y comparte tus aventuras en bicicleta'
              : targetUsername
                ? `Explora las aventuras en bicicleta de @${targetUsername}`
                : 'Explora viajes de la comunidad'
            }
          </p>
        </div>

        {/* Phase 5: Create Trip button will be enabled when TripCreatePage is implemented */}
        {/* {user && (
          <Link to="/trips/new" className="trips-list-page__create-button">
            <svg
              className="trips-list-page__create-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Crear Viaje
          </Link>
        )} */}
      </div>

      {/* Filters - only shown when viewing own trips */}
      {isViewingOwnTrips && (
        <TripFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedTag={selectedTag}
          onTagSelect={setSelectedTag}
          availableTags={availableTags}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
          selectedVisibility={selectedVisibility}
          onVisibilityChange={setSelectedVisibility}
          showStatusFilter={showStatusFilter}
          isLoading={tagsLoading}
          statusCounts={{ all: allCount, published: publishedCount, draft: draftCount }}
          countsLoading={countsLoading}
        />
      )}

      {/* Results Summary with Sort Dropdown */}
      {!isLoading && (
        <div className="trips-list-page__results-summary">
          <p className="trips-list-page__results-text">
            {total === 0 ? (
              'No se encontraron viajes'
            ) : total === 1 ? (
              '1 viaje encontrado'
            ) : (
              `${total ?? 0} viajes encontrados`
            )}
          </p>
          {trips.length > 0 && (
            <TripSortDropdown
              value={sortBy}
              onChange={setSortBy}
              disabled={isLoading}
            />
          )}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="trips-list-page__grid">
          {Array.from({ length: 12 }).map((_, index) => (
            <div key={index} className="trip-card-skeleton">
              <div className="trip-card-skeleton__thumbnail" />
              <div className="trip-card-skeleton__content">
                <div className="trip-card-skeleton__title" />
                <div className="trip-card-skeleton__meta" />
                <div className="trip-card-skeleton__tags">
                  <div className="trip-card-skeleton__tag" />
                  <div className="trip-card-skeleton__tag" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Trips Grid */}
      {!isLoading && trips.length > 0 && (
        <div className="trips-list-page__grid">
          {trips.map((trip) => (
            <TripCard key={trip.trip_id} trip={trip} showStatus={showStatusFilter} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && trips.length === 0 && (
        <div className="trips-list-page__empty-state">
          <div className="trips-list-page__empty-illustration">
            <svg
              className="trips-list-page__empty-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
          </div>

          <h2 className="trips-list-page__empty-title">No se encontraron viajes</h2>

          {searchQuery || selectedTag || selectedStatus ? (
            <p className="trips-list-page__empty-description">
              Intenta ajustar los filtros para encontrar lo que buscas
            </p>
          ) : (
            <>
              <p className="trips-list-page__empty-description">
                Aún no tienes viajes registrados. La función de crear viajes estará disponible próximamente.
              </p>
              {/* Phase 5: Enable when TripCreatePage is implemented */}
              {/* {user && (
                <Link to="/trips/new" className="trips-list-page__empty-button">
                  Crear Primer Viaje
                </Link>
              )} */}
            </>
          )}
        </div>
      )}

      {/* Pagination */}
      {!isLoading && trips.length > 0 && totalPages > 1 && (
        <div className="trips-list-page__pagination">
          <button
            className="trips-list-page__pagination-button"
            onClick={previousPage}
            disabled={currentPage === 1}
            aria-label="Página anterior"
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
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Anterior
          </button>

          <div className="trips-list-page__pagination-info">
            <span className="trips-list-page__pagination-text">
              Página {currentPage} de {totalPages}
            </span>

            {/* Page numbers (show first, current-1, current, current+1, last) */}
            <div className="trips-list-page__pagination-numbers">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter((page) => {
                  // Show first, last, and pages around current
                  if (page === 1 || page === totalPages) return true;
                  if (page >= currentPage - 1 && page <= currentPage + 1) return true;
                  return false;
                })
                .map((page, index, array) => {
                  // Add ellipsis between non-consecutive pages
                  const showEllipsis =
                    index > 0 && array[index - 1] !== page - 1;

                  return (
                    <React.Fragment key={page}>
                      {showEllipsis && (
                        <span className="trips-list-page__pagination-ellipsis">
                          ...
                        </span>
                      )}
                      <button
                        className={`trips-list-page__pagination-number ${
                          page === currentPage
                            ? 'trips-list-page__pagination-number--active'
                            : ''
                        }`}
                        onClick={() => goToPage(page)}
                      >
                        {page}
                      </button>
                    </React.Fragment>
                  );
                })}
            </div>
          </div>

          <button
            className="trips-list-page__pagination-button"
            onClick={nextPage}
            disabled={currentPage === totalPages}
            aria-label="Página siguiente"
          >
            Siguiente
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
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};
