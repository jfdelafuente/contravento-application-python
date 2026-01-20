/**
 * Application Constants
 * Feature: 015-dashboard-redesign
 *
 * Constantes globales para la aplicación, incluyendo breakpoints responsivos.
 */

// ============================================================================
// Responsive Breakpoints (Media Queries)
// ============================================================================

/**
 * Breakpoints para diseño responsivo (mobile-first approach)
 *
 * Uso:
 * - MOBILE: 320px+ (base, smartphone pequeño)
 * - TABLET: 768px+ (tablet portrait, iPad)
 * - DESKTOP: 1024px+ (desktop, laptop)
 */
export const BREAKPOINTS = {
  /** Smartphone pequeño (base styles, mobile-first) */
  MOBILE: 320,

  /** Tablet portrait (iPad, Android tablets) */
  TABLET: 768,

  /** Desktop/Laptop (pantalla completa) */
  DESKTOP: 1024,
} as const;

/**
 * Media queries para uso en JavaScript (window.matchMedia)
 *
 * @example
 * ```typescript
 * const isTablet = window.matchMedia(MEDIA_QUERIES.TABLET).matches;
 * ```
 */
export const MEDIA_QUERIES = {
  /** Mobile: 320px - 767px */
  MOBILE: `(max-width: ${BREAKPOINTS.TABLET - 1}px)`,

  /** Tablet: 768px - 1023px */
  TABLET: `(min-width: ${BREAKPOINTS.TABLET}px) and (max-width: ${BREAKPOINTS.DESKTOP - 1}px)`,

  /** Desktop: 1024px+ */
  DESKTOP: `(min-width: ${BREAKPOINTS.DESKTOP}px)`,

  /** Tablet and above (768px+) */
  TABLET_UP: `(min-width: ${BREAKPOINTS.TABLET}px)`,

  /** Desktop and above (1024px+) */
  DESKTOP_UP: `(min-width: ${BREAKPOINTS.DESKTOP}px)`,
} as const;

// ============================================================================
// Dashboard Constants
// ============================================================================

/**
 * Límites de paginación para el dashboard
 */
export const DASHBOARD_LIMITS = {
  /** Items por página en feed de actividad */
  FEED_PAGE_SIZE: 50,

  /** Máximo de rutas sugeridas a mostrar */
  SUGGESTED_ROUTES_MAX: 5,

  /** Máximo de notificaciones a mostrar en el panel */
  NOTIFICATIONS_MAX: 20,

  /** Resultados máximos en búsqueda global */
  SEARCH_RESULTS_MAX: 10,
} as const;

/**
 * Tiempos de debounce (milisegundos)
 */
export const DEBOUNCE_DELAYS = {
  /** Búsqueda global (evita llamadas excesivas al tipear) */
  SEARCH: 300,

  /** Auto-save de formularios */
  AUTO_SAVE: 1000,

  /** Redimensionamiento de ventana */
  WINDOW_RESIZE: 150,
} as const;

/**
 * Z-index layers (definidos también en Tailwind @theme)
 */
export const Z_INDEX = {
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
} as const;
