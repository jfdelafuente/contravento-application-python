# Following Users - ContraVento

Learn how to connect with other cyclists by following their profiles and trips.

**Audience**: End-users, cyclists building community
**Difficulty**: 🟢 Basic

---

## Table of Contents

- [Overview](#overview)
- [How to Follow Users](#how-to-follow-users)
- [How to Unfollow Users](#how-to-unfollow-users)
- [Following List](#following-list)
- [Followers List](#followers-list)
- [Following Workflow](#following-workflow)
- [Privacy & Visibility](#privacy--visibility)
- [Troubleshooting](#troubleshooting)

---

## Overview

Following users on ContraVento allows you to:

- 🔔 **Stay updated** on their new trips and activities
- 👥 **Build connections** with cyclists who share your interests
- 🗺️ **Discover routes** in areas you want to explore
- 💬 **Engage** through comments and likes
- 📊 **Track** cycling community activity

**Key Features**:
- Follow/unfollow with one click
- See who you follow and who follows you
- No limit on number of follows
- Following is public (visible to all users)

---

## How to Follow Users

You can follow users from multiple locations on ContraVento.

### Option 1: From Profile Page

**Steps**:

```
1. Navigate to user's profile:
   - Click on username in trip card (public feed)
   - Click on username in comments
   - Visit /users/{username}

2. Click "Seguir" button (blue)

3. Button changes to "Siguiendo" (gray) immediately

4. Success toast appears: "Ahora sigues a {username}"
```

**Visual Feedback**:

```
Before (not following):
┌─────────────────────────────────┐
│  maria_garcia                   │
│  📍 Barcelona, España           │
│                                  │
│  [Seguir]                       │ ← Blue button
└─────────────────────────────────┘

After (following):
┌─────────────────────────────────┐
│  maria_garcia                   │
│  📍 Barcelona, España           │
│                                  │
│  [Siguiendo]                    │ ← Gray button
└─────────────────────────────────┘
```

---

### Option 2: From Trip Detail Page

**Steps**:

```
1. View trip from another user

2. Click username below trip title

3. Profile opens in overlay or new page

4. Click "Seguir" button

5. Following status updates immediately
```

---

### Option 3: From Public Feed

**Steps**:

```
1. Browse public feed

2. Find interesting trip

3. Click on author's username (below trip title)

4. Profile card appears

5. Click "Seguir" button
```

---

## How to Unfollow Users

Unfollowing removes the connection and stops updates.

### Steps

**From Profile Page**:

```
1. Navigate to user's profile

2. Click "Siguiendo" button (gray)

3. Confirmation dialog appears:
   ┌────────────────────────────────────┐
   │  ¿Dejar de seguir a maria_garcia?  │
   │                                     │
   │  [Cancelar]  [Dejar de seguir]     │
   └────────────────────────────────────┘

4. Click "Dejar de seguir" to confirm

5. Button changes back to "Seguir" (blue)

6. Success toast: "Has dejado de seguir a {username}"
```

**From Following List**:

```
1. Go to your profile

2. Click "Siguiendo" tab (shows who you follow)

3. Find user in list

4. Click "Siguiendo" button next to their name

5. Confirm unfollow in dialog

6. User removed from following list immediately
```

---

## Following List

The Following list shows all users you follow.

### Accessing Following List

**Steps**:

```
1. Go to your profile:
   - Click profile icon (top-right)
   - Or visit /users/{your-username}

2. Click "Siguiendo" tab

3. List displays all users you follow
```

**Following List Layout**:

```
┌────────────────────────────────────────────┐
│  Siguiendo (12)                             │
├────────────────────────────────────────────┤
│                                             │
│  👤 maria_garcia                            │
│     Barcelona, España • Gravel             │
│     [Siguiendo ▾]                           │
│                                             │
├────────────────────────────────────────────┤
│  👤 pepe_bikepacking                        │
│     Madrid, España • Bikepacking           │
│     [Siguiendo ▾]                           │
│                                             │
├────────────────────────────────────────────┤
│  👤 laura_mtb                               │
│     Sevilla, España • MTB                  │
│     [Siguiendo ▾]                           │
│                                             │
└────────────────────────────────────────────┘
```

**Information Displayed**:
- Username (clickable → profile)
- Location and cycling type
- "Siguiendo" button (click to unfollow)

---

### Following List Features

**Sorting**:
- Alphabetical by username (default)
- Most recent first (future feature)

**Search**:
- Filter following list by username (future feature)

**Pagination**:
- Shows 20 users per page
- "Cargar más" button for additional users

---

## Followers List

The Followers list shows users who follow you.

### Accessing Followers List

**Steps**:

```
1. Go to your profile

2. Click "Seguidores" tab

3. List displays all users who follow you
```

**Followers List Layout**:

```
┌────────────────────────────────────────────┐
│  Seguidores (28)                            │
├────────────────────────────────────────────┤
│                                             │
│  👤 carlos_road                             │
│     Valencia, España • Road                │
│     [Seguir]                                │ ← You don't follow back
│                                             │
├────────────────────────────────────────────┤
│  👤 ana_touring                             │
│     Bilbao, España • Touring               │
│     [Siguiendo ▾]                           │ ← Mutual following
│                                             │
├────────────────────────────────────────────┤
│  👤 javi_urban                              │
│     Zaragoza, España • Urban               │
│     [Seguir]                                │ ← You don't follow back
│                                             │
└────────────────────────────────────────────┘
```

**Mutual Following**:
- Users you follow back show "Siguiendo" button
- Users you don't follow back show "Seguir" button
- Click "Seguir" to follow them back

---

## Following Workflow

### New User Discovery

**How to Find Users to Follow**:

1. **Browse Public Feed**:
   - See trips from all users
   - Follow authors of interesting trips

2. **Search by Location**:
   - Filter users by city/country (future feature)
   - Follow local cyclists

3. **Search by Cycling Type**:
   - Filter users by gravel, road, MTB, etc. (future feature)
   - Follow cyclists with similar interests

4. **Check Comments**:
   - See who comments on your trips
   - Visit their profiles and follow

5. **Explore Followers**:
   - Check who follows you
   - Visit their profiles and follow back

---

### Following Notifications

**When Someone Follows You**:

```
Desktop notification (if enabled):
┌────────────────────────────────────┐
│  🔔 ContraVento                    │
│                                     │
│  maria_garcia te ha empezado a     │
│  seguir                             │
│                                     │
│  Hace 2 minutos                    │
└────────────────────────────────────┘

In-app notification (bell icon):
┌────────────────────────────────────┐
│  🔔 Notificaciones (3)             │
├────────────────────────────────────┤
│                                     │
│  👤 maria_garcia te sigue           │
│     Hace 2 minutos                 │
│                                     │
│  👤 pepe_bikepacking te sigue       │
│     Hace 1 hora                    │
│                                     │
│  👤 laura_mtb te sigue              │
│     Hace 3 horas                   │
│                                     │
└────────────────────────────────────┘
```

**Notification Actions**:
- Click notification → visit follower's profile
- Click "Seguir" to follow back
- Click "✕" to dismiss notification

---

### Following Best Practices

**Do**:
- ✅ Follow users whose trips inspire you
- ✅ Follow local cyclists to discover routes
- ✅ Follow back users who engage with your content
- ✅ Comment on trips from users you follow
- ✅ Like trips to show appreciation

**Don't**:
- ❌ Mass follow hundreds of users (spam-like behavior)
- ❌ Follow/unfollow repeatedly (considered rude)
- ❌ Follow users just to get followers back
- ❌ Expect instant follow-back (not required)

---

## Privacy & Visibility

### What Followers Can See

**Public Trips** (published):
- ✅ Trip title, description, photos
- ✅ GPX route and elevation profile
- ✅ Comments and likes
- ✅ Trip statistics

**Draft Trips** (unpublished):
- ❌ Not visible to followers
- ❌ Only you can see drafts

**Profile Information**:
- ✅ Username, profile photo, bio
- ✅ Location, cycling type
- ✅ Public trip count, distance, countries
- ✅ Following/followers lists

---

### Privacy Settings

**Following is Public**:
- Everyone can see who you follow
- Everyone can see who follows you
- No option to hide following/followers (by design)

**Why Public?**:
- Encourages community building
- Helps discover new users
- Standard social network behavior

**Future Features**:
- Private accounts (followers must be approved)
- Hide specific trips from followers
- Mute users without unfollowing

---

### Blocking Users (Future Feature)

**Planned Features**:
- Block users from following you
- Block users from commenting on your trips
- Hide your trips from blocked users
- Report users for spam or harassment

**Current Workaround**: Unfollow and avoid interaction.

---

## Troubleshooting

### "Already following" Error

**Cause**: You already follow this user

**Solution**:
- Refresh page (may be cache issue)
- Check "Siguiendo" tab to verify
- If button stuck, unfollow and re-follow

---

### Cannot Follow User

**Possible Causes**:

1. **Not logged in**:
   - Solution: Log in first

2. **User blocked you** (future feature):
   - Solution: Cannot follow blocked users

3. **Network error**:
   - Solution: Check internet connection, try again

4. **Server error**:
   - Solution: Wait 1 minute and retry

---

### Following Count Doesn't Update

**Cause**: Cache or sync issue

**Solution**:

1. **Hard refresh**:
   - Windows: Ctrl+Shift+R
   - Mac: Cmd+Shift+R

2. **Clear browser cache**:
   - Chrome: Settings → Privacy → Clear browsing data

3. **Wait 30 seconds**:
   - Following count updates asynchronously

---

### Follower Disappeared from List

**Possible Causes**:

1. **User unfollowed you**:
   - Normal behavior

2. **User deleted account**:
   - Removed from followers list

3. **User was banned**:
   - Removed from platform (rare)

---

### Cannot Unfollow User

**Cause**: Network error or server issue

**Solution**:

1. **Retry**:
   - Click "Siguiendo" button again
   - Confirm unfollow

2. **Hard refresh page**:
   - Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Try unfollowing again

3. **Contact support**:
   - Email: soporte@contravento.com
   - Include username you're trying to unfollow

---

### Following List Shows Deleted Users

**Cause**: User deleted account but not removed from list yet

**Solution**:
- System automatically removes deleted users within 24 hours
- If persists >24h, contact support

---

## Related Guides

- **[Public Feed](public-feed.md)** - Discover trips from users you follow
- **[Commenting](commenting.md)** - Engage with trips from followed users
- **[Editing Profile](../profile/editing-profile.md)** - Make your profile attractive to followers
- **[Getting Started](../getting-started.md)** - Platform basics

---

## Related Documentation

- **[API: Social Endpoints](../../api/endpoints/social.md)** - Follow API for developers
- **[Manual Testing: Social Testing](../../testing/manual-qa/social-testing.md)** - QA for follow feature
- **[Features: Social Network](../../features/social-network.md)** - Feature specification

---

**Last Updated**: 2026-02-07
**Difficulty**: 🟢 Basic
**Estimated Reading Time**: 7 minutes
