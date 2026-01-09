import React, { useEffect, useState } from 'react';
import { Achievement } from '../../types/achievement';
import { getUserAchievements } from '../../services/achievementsService';
import { useAuth } from '../../contexts/AuthContext';
import AchievementCard from './AchievementCard';
import './AchievementsSection.css';

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

  const earnedCount = achievements.filter(a => a.is_earned).length;

  return (
    <section className="achievements-section" aria-labelledby="achievements-heading">
      <div className="achievements-section__header">
        <h2 id="achievements-heading" className="achievements-section__title">
          Logros Desbloqueados
        </h2>
        <span className="achievements-section__count">
          {earnedCount} de {achievements.length}
        </span>
      </div>

      {loading && (
        <div className="achievements-section__loading">
          <div className="spinner"></div>
          <p>Cargando logros...</p>
        </div>
      )}

      {error && (
        <div className="achievements-section__error">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && achievements.length === 0 && (
        <div className="achievements-section__empty">
          <p>No hay logros disponibles</p>
        </div>
      )}

      {!loading && !error && achievements.length > 0 && (
        <div className="achievements-section__grid">
          {achievements.map((achievement, index) => (
            <div
              key={achievement.achievement_id}
              style={{ animationDelay: `${index * 0.05}s` }}
              className="achievements-section__grid-item"
            >
              <AchievementCard achievement={achievement} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default AchievementsSection;
