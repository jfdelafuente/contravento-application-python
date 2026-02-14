import React, { memo, useEffect, useState } from 'react';
import { Achievement } from '../../types/achievement';
import { getUserAchievements } from '../../services/achievementsService';
import { useAuth } from '../../contexts/AuthContext';
import AchievementCard from './AchievementCard';
import './AchievementsSection.css';

/**
 * Performance: rerender-memo - Prevents re-renders when parent re-renders
 * Performance: rendering-conditional-render - Early returns for loading/error/empty states
 */

/**
 * AchievementsSection component - Display user achievements with icons and descriptions
 * Shows earned achievements and progress on locked achievements
 */
const AchievementsSection: React.FC = () => {
  const { user } = useAuth();
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAchievements = async () => {
      if (!user?.username) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await getUserAchievements(user.username);
        setAchievements(data);
      } catch (err: any) {
        console.error('Error fetching achievements:', err);
        setError(err.response?.data?.message || 'Error al cargar logros');
        setAchievements([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAchievements();
  }, [user?.username]);

  // TODO: Use earnedCount for stats display
  // const earnedCount = achievements.filter(a => a.is_earned).length;

  // Performance: rendering-conditional-render - Early return for loading state
  if (loading) {
    return (
      <section className="achievements-section" aria-labelledby="achievements-heading">
        <h2 id="achievements-heading" className="achievements-section__title">
          Hitos
        </h2>
        <div className="achievements-section__loading">
          <div className="spinner"></div>
        </div>
      </section>
    );
  }

  // Performance: rendering-conditional-render - Early return for error state
  if (error) {
    return (
      <section className="achievements-section" aria-labelledby="achievements-heading">
        <h2 id="achievements-heading" className="achievements-section__title">
          Hitos
        </h2>
        <div className="achievements-section__error">
          <p>{error}</p>
        </div>
      </section>
    );
  }

  // Performance: rendering-conditional-render - Early return for empty state
  if (achievements.length === 0) {
    return (
      <section className="achievements-section" aria-labelledby="achievements-heading">
        <h2 id="achievements-heading" className="achievements-section__title">
          Hitos
        </h2>
        <div className="achievements-section__empty">
          <p>No hay logros disponibles</p>
        </div>
      </section>
    );
  }

  // Main render - only when we have achievements
  return (
    <section className="achievements-section" aria-labelledby="achievements-heading">
      <h2 id="achievements-heading" className="achievements-section__title">
        Hitos
      </h2>
      <div className="achievements-section__grid">
        {achievements.slice(0, 4).map((achievement, index) => (
          <div
            key={achievement.achievement_id}
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <AchievementCard achievement={achievement} />
          </div>
        ))}
      </div>
    </section>
  );
};

// Performance: rerender-memo - Add display name for better debugging
AchievementsSection.displayName = 'AchievementsSection';

export default memo(AchievementsSection);
