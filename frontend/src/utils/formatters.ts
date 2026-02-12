/**
 * Format large numbers with commas (Spanish locale)
 * @param value - Number to format
 * @returns Formatted string (e.g., 1234 -> "1.234")
 */
export const formatStatNumber = (value: number): string => {
  return new Intl.NumberFormat('es-ES').format(value);
};

/**
 * Format distance with units
 * @param km - Distance in kilometers
 * @returns Formatted distance string (e.g., 1234 -> "1.234 km", 1500 -> "1.5 mil km")
 */
export const formatDistance = (km: number): string => {
  if (km >= 1000) {
    return `${(km / 1000).toFixed(1)} mil km`;
  }
  return `${formatStatNumber(Math.round(km))} km`;
};

/**
 * Format countries list for display
 * @param countries - Array of country names
 * @returns Formatted string (e.g., ["España", "Francia"] -> "España, Francia")
 */
export const formatCountries = (countries: string[]): string => {
  if (countries.length === 0) return 'Ninguno';
  if (countries.length <= 3) return countries.join(', ');
  return `${countries.slice(0, 3).join(', ')} +${countries.length - 3}`;
};

/**
 * Format relative time (e.g., "hace 2 horas", "hace 3 días")
 * @param timestamp - ISO timestamp string
 * @returns Formatted relative time string
 */
export const formatRelativeTime = (timestamp: string): string => {
  const now = new Date();
  const date = new Date(timestamp);
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  // Less than 1 minute
  if (diffInSeconds < 60) {
    return 'hace un momento';
  }

  // Less than 1 hour
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return diffInMinutes === 1 ? 'hace 1 minuto' : `hace ${diffInMinutes} minutos`;
  }

  // Less than 1 day
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return diffInHours === 1 ? 'hace 1 hora' : `hace ${diffInHours} horas`;
  }

  // Less than 1 week
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return diffInDays === 1 ? 'hace 1 día' : `hace ${diffInDays} días`;
  }

  // Less than 1 month
  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return diffInWeeks === 1 ? 'hace 1 semana' : `hace ${diffInWeeks} semanas`;
  }

  // Less than 1 year
  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return diffInMonths === 1 ? 'hace 1 mes' : `hace ${diffInMonths} meses`;
  }

  // 1 year or more
  const diffInYears = Math.floor(diffInDays / 365);
  return diffInYears === 1 ? 'hace 1 año' : `hace ${diffInYears} años`;
};

/**
 * Get time of day greeting (Buenos días, Buenas tardes, Buenas noches)
 * @returns Contextual greeting based on current time
 */
export const getTimeOfDayGreeting = (): string => {
  const hour = new Date().getHours();

  if (hour >= 6 && hour < 12) {
    return 'Buenos días';
  } else if (hour >= 12 && hour < 20) {
    return 'Buenas tardes';
  } else {
    return 'Buenas noches';
  }
};

/**
 * Format date to Spanish locale (e.g., "15 de enero de 2024")
 * @param dateString - ISO date string
 * @returns Formatted date string
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(date);
};

/**
 * Format date to short format (e.g., "15/01/2024")
 * @param dateString - ISO date string
 * @returns Formatted short date string
 */
export const formatShortDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-ES').format(date);
};
