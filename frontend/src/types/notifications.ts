/**
 * Notifications TypeScript Interfaces
 * Feature: 015-dashboard-redesign
 *
 * Interfaces para notificaciones y alertas del dashboard.
 * Fuente: GET /api/v1/dashboard/notifications
 */

export type NotificationType =
  | 'like'
  | 'comment'
  | 'new_follower'
  | 'challenge_completed'
  | 'achievement_unlocked'
  | 'security_alert';

export type NotificationPriority = 'low' | 'medium' | 'high';

export interface Notification {
  notification_id: string;
  type: NotificationType;
  priority: NotificationPriority;
  title: string;
  message: string;
  icon_url: string | null;

  // Metadata
  created_at: string; // ISO 8601
  is_read: boolean;
  read_at: string | null;

  // Action link (optional)
  action_url: string | null; // e.g., "/trips/trip_123", "/profile/user_456"
  action_text: string | null; // e.g., "Ver viaje", "Ver perfil"

  // Actor (who triggered the notification)
  actor_user_id: string | null;
  actor_username: string | null;
  actor_photo_url: string | null;
}

export interface NotificationsResponse {
  notifications: Notification[];
  total_unread: number;
  total_count: number;
}
