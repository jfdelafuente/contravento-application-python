import { api } from './api';
import { Achievement } from '../types/achievement';

interface EarnedAchievement {
  code: string;
  name: string;
  description: string;
  badge_icon: string;
  requirement_type: string;
  requirement_value: number;
  awarded_at: string;
}

interface AllAchievementsDefinition {
  code: string;
  name: string;
  description: string;
  badge_icon: string;
  requirement_type: string;
  requirement_value?: number;
}

interface UserAchievementsResponse {
  success: boolean;
  data: {
    achievements: EarnedAchievement[];
    total_count: number;
  };
  error: null | any;
}

interface AllAchievementsResponse {
  success: boolean;
  data: {
    achievements: AllAchievementsDefinition[];
  };
  error: null | any;
}

/**
 * Fetch all achievements and mark which ones the user has earned
 * @param username - Username to fetch achievements for
 * @returns Array of all achievements with is_earned flag
 */
export const getUserAchievements = async (username: string): Promise<Achievement[]> => {
  // Fetch both all achievements and user's earned achievements in parallel
  const [allAchievementsRes, earnedAchievementsRes] = await Promise.all([
    api.get<AllAchievementsResponse>('/achievements'),
    api.get<UserAchievementsResponse>(`/users/${username}/achievements`),
  ]);

  const allAchievements = allAchievementsRes.data.data.achievements;
  const earnedAchievements = earnedAchievementsRes.data.data.achievements;

  // Create a map of earned achievements by code
  const earnedMap = new Map(
    earnedAchievements.map(a => [a.code, a.awarded_at])
  );

  // Helper to map requirement_type to category
  const mapCategory = (requirementType: string): Achievement['category'] => {
    const categoryMap: Record<string, Achievement['category']> = {
      'distance': 'distance',
      'trips': 'trips',
      'followers': 'social',
      'photos': 'photos',
      'countries': 'special',
    };
    return categoryMap[requirementType] || 'special';
  };

  // Map all achievements and mark which ones are earned
  const achievementsWithStatus = allAchievements.map(achievement => ({
    achievement_id: achievement.code, // Use code as ID since achievement_id not returned
    code: achievement.code,
    name: achievement.name,
    description: achievement.description,
    badge_icon: achievement.badge_icon,
    category: mapCategory(achievement.requirement_type),
    requirement_value: achievement.requirement_value,
    is_earned: earnedMap.has(achievement.code),
    earned_at: earnedMap.get(achievement.code) || null,
    progress: undefined, // TODO: Calculate progress based on user stats
  }));

  // Sort: earned achievements first, then locked achievements
  return achievementsWithStatus.sort((a, b) => {
    if (a.is_earned && !b.is_earned) return -1;
    if (!a.is_earned && b.is_earned) return 1;
    return 0;
  });
};
