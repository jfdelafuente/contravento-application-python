/**
 * Achievement data from backend API
 */
export interface Achievement {
  achievement_id: string;
  code: string;
  name: string;
  description: string;
  badge_icon: string; // Emoji from database (e.g., "🚴", "🏆", "🌍")
  category: 'distance' | 'trips' | 'social' | 'photos' | 'special';
  requirement_value?: number;
  is_earned: boolean;
  earned_at?: string | null;
  progress?: number; // 0-100 percentage
}

/**
 * Grouped achievements by category for display
 */
export interface AchievementsByCategory {
  distance: Achievement[];
  trips: Achievement[];
  social: Achievement[];
  photos: Achievement[];
  special: Achievement[];
}
