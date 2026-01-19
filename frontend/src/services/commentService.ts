/**
 * Comment Service - API calls for trip comments (Feature 004 - US3: Comentarios)
 *
 * Endpoints:
 * - POST /trips/{trip_id}/comments - Create comment
 * - GET /trips/{trip_id}/comments - Get trip comments (paginated)
 * - PUT /comments/{comment_id} - Update comment
 * - DELETE /comments/{comment_id} - Delete comment
 *
 * Related tasks: T098
 */

import { api } from './api';

/**
 * Minimal user details for comment author
 */
export interface CommentAuthor {
  user_id: string;
  username: string;
  full_name: string | null;
  profile_photo_url: string | null;
}

/**
 * Comment response from API
 */
export interface Comment {
  id: string;
  user_id: string;
  trip_id: string;
  content: string;
  created_at: string;
  updated_at: string | null;
  is_edited: boolean;
  author?: CommentAuthor;
}

/**
 * Paginated comments list response
 */
export interface CommentsListResponse {
  items: Comment[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Create comment input
 */
export interface CreateCommentInput {
  content: string;
}

/**
 * Update comment input
 */
export interface UpdateCommentInput {
  content: string;
}

/**
 * Create a new comment on a trip
 *
 * @param tripId - Trip ID to comment on
 * @param data - Comment content
 * @returns Created comment
 *
 * @throws {Error} 400 - Validation error (empty content, >500 chars)
 * @throws {Error} 401 - Unauthorized (no auth token)
 * @throws {Error} 404 - Trip not found
 * @throws {Error} 429 - Rate limit exceeded (10 comments/hour)
 */
export async function createComment(
  tripId: string,
  data: CreateCommentInput
): Promise<Comment> {
  const response = await api.post<Comment>(`/trips/${tripId}/comments`, data);
  return response.data;
}

/**
 * Get all comments for a trip (paginated)
 *
 * @param tripId - Trip ID to get comments for
 * @param limit - Max comments to return (default: 50, max: 50)
 * @param offset - Number of comments to skip (default: 0)
 * @returns Paginated list of comments
 *
 * @throws {Error} 404 - Trip not found
 */
export async function getTripComments(
  tripId: string,
  limit: number = 50,
  offset: number = 0
): Promise<CommentsListResponse> {
  const response = await api.get<CommentsListResponse>(`/trips/${tripId}/comments`, {
    params: { limit, offset },
  });
  return response.data;
}

/**
 * Update a comment (author-only)
 *
 * @param commentId - Comment ID to update
 * @param data - Updated comment content
 * @returns Updated comment with is_edited=true
 *
 * @throws {Error} 400 - Validation error (empty content, >500 chars)
 * @throws {Error} 401 - Unauthorized (no auth token)
 * @throws {Error} 403 - Forbidden (not comment author)
 * @throws {Error} 404 - Comment not found
 */
export async function updateComment(
  commentId: string,
  data: UpdateCommentInput
): Promise<Comment> {
  const response = await api.put<Comment>(`/comments/${commentId}`, data);
  return response.data;
}

/**
 * Delete a comment (author or trip owner)
 *
 * @param commentId - Comment ID to delete
 *
 * @throws {Error} 401 - Unauthorized (no auth token)
 * @throws {Error} 403 - Forbidden (not author or trip owner)
 * @throws {Error} 404 - Comment not found
 */
export async function deleteComment(commentId: string): Promise<void> {
  await api.delete(`/comments/${commentId}`);
}
