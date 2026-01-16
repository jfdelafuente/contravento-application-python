# Quick Start Guide: Social Links with Granular Privacy Control

**Feature**: 015-social-links-privacy
**For**: Developers implementing the Social Links feature
**Last Updated**: 2026-01-16

## Overview

This guide provides a step-by-step walkthrough for testing the Social Links feature with privacy control. Follow this guide to understand the complete testing workflow from basic link creation to advanced privacy filtering scenarios.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Completed 001-user-profiles feature (authentication system)
- ✅ Completed 011-follows feature (mutual follow relationship system)
- ✅ Python 3.12+ installed
- ✅ Poetry dependency manager
- ✅ PostgreSQL 15+ (production) or SQLite 3.40+ (development)
- ✅ Git repository cloned and on branch `015-social-links-privacy`
- ✅ Backend server running at `http://localhost:8000`

---

## Testing Scenarios

This guide covers 5 key testing scenarios from plan.md:

1. **Scenario 1**: Anonymous user visits profile → only sees PUBLIC links
2. **Scenario 2**: Authenticated user visits profile → sees PUBLIC + COMMUNITY
3. **Scenario 3**: Mutual follower visits profile → sees PUBLIC + COMMUNITY + MUTUAL_FOLLOWERS
4. **Scenario 4**: Owner edits links → changes privacy_level from PUBLIC to COMMUNITY
5. **Scenario 5**: XSS/Phishing attempt → URL with malicious content is rejected

---

## Setup: Create Test Users

### 1.1 Create Three Test Users

```bash
cd backend

# User A: Profile owner (juan_ciclista)
poetry run python scripts/create_verified_user.py \
  --username juan_ciclista \
  --email juan@example.com \
  --password "TestPass123!"

# User B: Authenticated user (no mutual follow)
poetry run python scripts/create_verified_user.py \
  --username maria_rider \
  --email maria@example.com \
  --password "TestPass123!"

# User C: Mutual follower
poetry run python scripts/create_verified_user.py \
  --username carlos_biker \
  --email carlos@example.com \
  --password "TestPass123!"
```

### 1.2 Establish Follow Relationships

```bash
# Get authentication tokens
export TOKEN_JUAN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@example.com","password":"TestPass123!"}' | jq -r '.data.access_token')

export TOKEN_MARIA=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"maria@example.com","password":"TestPass123!"}' | jq -r '.data.access_token')

export TOKEN_CARLOS=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"carlos@example.com","password":"TestPass123!"}' | jq -r '.data.access_token')

# Create mutual follow between Juan and Carlos
# Carlos follows Juan
curl -X POST http://localhost:8000/follows/juan_ciclista \
  -H "Authorization: Bearer $TOKEN_CARLOS"

# Juan follows Carlos back (now mutual)
curl -X POST http://localhost:8000/follows/carlos_biker \
  -H "Authorization: Bearer $TOKEN_JUAN"

# Maria follows Juan (but Juan doesn't follow back - unilateral)
curl -X POST http://localhost:8000/follows/juan_ciclista \
  -H "Authorization: Bearer $TOKEN_MARIA"
```

### 1.3 Create Social Links for Juan (Profile Owner)

```bash
# Link 1: Instagram - PUBLIC (visible to everyone)
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "INSTAGRAM",
    "url": "https://instagram.com/juan_ciclista",
    "privacy_level": "PUBLIC"
  }'

# Link 2: Strava - COMMUNITY (visible to authenticated users)
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "STRAVA",
    "url": "https://strava.com/athletes/123456",
    "privacy_level": "COMMUNITY"
  }'

# Link 3: Blog - MUTUAL_FOLLOWERS (visible only to mutual followers)
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "BLOG",
    "url": "https://juanciclista.substack.com",
    "privacy_level": "MUTUAL_FOLLOWERS"
  }'

# Link 4: Portfolio - HIDDEN (not visible to anyone except owner)
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "PORTFOLIO",
    "url": "https://juanciclista.com",
    "privacy_level": "HIDDEN"
  }'
```

---

## Scenario 1: Anonymous User Sees Only PUBLIC Links

**User Story**: Un visitante anónimo visita el perfil de Juan y solo debe ver enlaces con privacidad "Público".

**Expected Result**: Only Instagram link (PUBLIC) is visible.

### Test Command

```bash
# Anonymous request (no authentication)
curl -X GET http://localhost:8000/users/juan_ciclista/social-links
```

### Expected Response

```json
{
  "success": true,
  "data": [
    {
      "id": "link-1",
      "platform_type": "INSTAGRAM",
      "url": "https://instagram.com/juan_ciclista",
      "privacy_level": "PUBLIC"
    }
  ],
  "error": null
}
```

**Validation**:
- ✅ Only 1 link returned (Instagram)
- ✅ STRAVA (COMMUNITY), BLOG (MUTUAL_FOLLOWERS), PORTFOLIO (HIDDEN) are NOT visible
- ✅ No authentication error (public endpoint)

---

## Scenario 2: Authenticated User Sees PUBLIC + COMMUNITY

**User Story**: María (usuario autenticado pero sin seguimiento mutuo) visita el perfil de Juan y debe ver enlaces públicos y comunitarios.

**Expected Result**: Instagram (PUBLIC) + Strava (COMMUNITY) visible.

### Test Command

```bash
# Authenticated request as Maria (no mutual follow)
curl -X GET http://localhost:8000/users/juan_ciclista/social-links \
  -H "Authorization: Bearer $TOKEN_MARIA"
```

### Expected Response

```json
{
  "success": true,
  "data": [
    {
      "id": "link-1",
      "platform_type": "INSTAGRAM",
      "url": "https://instagram.com/juan_ciclista",
      "privacy_level": "PUBLIC"
    },
    {
      "id": "link-2",
      "platform_type": "STRAVA",
      "url": "https://strava.com/athletes/123456",
      "privacy_level": "COMMUNITY"
    }
  ],
  "error": null
}
```

**Validation**:
- ✅ 2 links returned (Instagram + Strava)
- ✅ BLOG (MUTUAL_FOLLOWERS) NOT visible (María is not mutual follower)
- ✅ PORTFOLIO (HIDDEN) NOT visible
- ✅ Authentication successful (Bearer token accepted)

---

## Scenario 3: Mutual Follower Sees PUBLIC + COMMUNITY + MUTUAL_FOLLOWERS

**User Story**: Carlos (seguidor mutuo de Juan) visita el perfil de Juan y debe ver todos los enlaces excepto ocultos.

**Expected Result**: Instagram (PUBLIC) + Strava (COMMUNITY) + Blog (MUTUAL_FOLLOWERS) visible.

### Test Command

```bash
# Authenticated request as Carlos (mutual follower)
curl -X GET http://localhost:8000/users/juan_ciclista/social-links \
  -H "Authorization: Bearer $TOKEN_CARLOS"
```

### Expected Response

```json
{
  "success": true,
  "data": [
    {
      "id": "link-1",
      "platform_type": "INSTAGRAM",
      "url": "https://instagram.com/juan_ciclista",
      "privacy_level": "PUBLIC"
    },
    {
      "id": "link-2",
      "platform_type": "STRAVA",
      "url": "https://strava.com/athletes/123456",
      "privacy_level": "COMMUNITY"
    },
    {
      "id": "link-3",
      "platform_type": "BLOG",
      "url": "https://juanciclista.substack.com",
      "privacy_level": "MUTUAL_FOLLOWERS"
    }
  ],
  "error": null
}
```

**Validation**:
- ✅ 3 links returned (Instagram + Strava + Blog)
- ✅ BLOG (MUTUAL_FOLLOWERS) IS visible (Carlos and Juan follow each other)
- ✅ PORTFOLIO (HIDDEN) still NOT visible (hidden from everyone except owner)
- ✅ Mutual follow relationship correctly detected

---

## Scenario 4: Owner Edits Privacy Level

**User Story**: Juan cambia la privacidad de Instagram de "Público" a "Solo Comunidad" y verifica que usuarios anónimos ya no lo vean.

**Expected Result**: Instagram link privacy updated, no longer visible to anonymous users.

### Test Commands

```bash
# Step 1: Get link ID for Instagram
LINK_ID=$(curl -X GET http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" | jq -r '.data[] | select(.platform_type=="INSTAGRAM") | .id')

# Step 2: Update privacy level to COMMUNITY
curl -X PUT http://localhost:8000/social-links/$LINK_ID \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_level": "COMMUNITY"
  }'

# Step 3: Verify anonymous user no longer sees Instagram
curl -X GET http://localhost:8000/users/juan_ciclista/social-links
```

### Expected Response (After Update)

```json
{
  "success": true,
  "data": [],
  "error": null
}
```

**Validation**:
- ✅ Update successful (status 200)
- ✅ Instagram link privacy changed from PUBLIC to COMMUNITY
- ✅ Anonymous users now see ZERO links (no PUBLIC links remain)
- ✅ Authenticated users still see Instagram + Strava (both COMMUNITY)

### Restore Original State

```bash
# Restore Instagram to PUBLIC for other tests
curl -X PUT http://localhost:8000/social-links/$LINK_ID \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_level": "PUBLIC"
  }'
```

---

## Scenario 5: XSS/Phishing Attempt Blocked

**User Story**: Un atacante intenta crear enlaces maliciosos con scripts XSS o dominios de phishing, y el sistema debe rechazarlos.

**Expected Result**: All malicious URLs rejected with validation errors.

### Test 5.1: JavaScript XSS Attempt

```bash
# Attempt to inject JavaScript
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "CUSTOM_1",
    "url": "javascript:alert(\"XSS\")",
    "privacy_level": "PUBLIC"
  }'
```

**Expected Response**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "URL inválida. Verifica el formato (debe comenzar con https://)",
    "field": "url"
  }
}
```

**Validation**:
- ✅ Request rejected with 400 status
- ✅ Error message in Spanish
- ✅ javascript: scheme blocked by validators library

### Test 5.2: Invalid Domain for Instagram

```bash
# Attempt to use wrong domain for Instagram
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "INSTAGRAM",
    "url": "https://evil-site.com/fake-profile",
    "privacy_level": "PUBLIC"
  }'
```

**Expected Response**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dominio no permitido para Instagram. Usa un enlace válido de instagram.com",
    "field": "url"
  }
}
```

**Validation**:
- ✅ Request rejected with 400 status
- ✅ Domain allowlist enforced for Instagram
- ✅ Phishing attempt prevented

### Test 5.3: Data URI Scheme

```bash
# Attempt to use data: scheme
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "CUSTOM_1",
    "url": "data:text/html,<script>alert(\"XSS\")</script>",
    "privacy_level": "PUBLIC"
  }'
```

**Expected Response**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "URL inválida. Verifica el formato (debe comenzar con https://)",
    "field": "url"
  }
}
```

**Validation**:
- ✅ Request rejected with 400 status
- ✅ data: scheme blocked
- ✅ XSS vector prevented

### Test 5.4: URL Too Long (>2000 chars)

```bash
# Attempt to create URL exceeding maximum length
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d "{
    \"platform_type\": \"PORTFOLIO\",
    \"url\": \"https://example.com/$(printf 'a%.0s' {1..2000})\",
    \"privacy_level\": \"PUBLIC\"
  }"
```

**Expected Response**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La URL no puede exceder 2000 caracteres",
    "field": "url"
  }
}
```

**Validation**:
- ✅ Request rejected with 400 status
- ✅ URL length limit enforced (≤2000 chars)

---

## Additional Test Cases

### Test 6: Duplicate Platform Prevention

```bash
# Attempt to create second Instagram link (already exists)
curl -X POST http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_type": "INSTAGRAM",
    "url": "https://instagram.com/another_account",
    "privacy_level": "PUBLIC"
  }'
```

**Expected Response**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "DUPLICATE_PLATFORM",
    "message": "Ya tienes un enlace de Instagram configurado. Edítalo o elimínalo primero"
  }
}
```

**Validation**:
- ✅ Request rejected with 400 status
- ✅ Duplicate prevention enforced (max 1 link per platform per user)

### Test 7: Owner Sees All Links (Including HIDDEN)

```bash
# Juan requests his own links
curl -X GET http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN"
```

**Expected Response**:

```json
{
  "success": true,
  "data": [
    {
      "id": "link-1",
      "platform_type": "INSTAGRAM",
      "url": "https://instagram.com/juan_ciclista",
      "privacy_level": "PUBLIC",
      "created_at": "2026-01-16T10:00:00Z",
      "updated_at": "2026-01-16T10:00:00Z"
    },
    {
      "id": "link-2",
      "platform_type": "STRAVA",
      "url": "https://strava.com/athletes/123456",
      "privacy_level": "COMMUNITY",
      "created_at": "2026-01-16T10:05:00Z",
      "updated_at": "2026-01-16T10:05:00Z"
    },
    {
      "id": "link-3",
      "platform_type": "BLOG",
      "url": "https://juanciclista.substack.com",
      "privacy_level": "MUTUAL_FOLLOWERS",
      "created_at": "2026-01-16T10:10:00Z",
      "updated_at": "2026-01-16T10:10:00Z"
    },
    {
      "id": "link-4",
      "platform_type": "PORTFOLIO",
      "url": "https://juanciclista.com",
      "privacy_level": "HIDDEN",
      "created_at": "2026-01-16T10:15:00Z",
      "updated_at": "2026-01-16T10:15:00Z"
    }
  ],
  "error": null
}
```

**Validation**:
- ✅ 4 links returned (all links including HIDDEN)
- ✅ Timestamps included for edit mode
- ✅ Owner bypass works correctly

### Test 8: Delete Social Link

```bash
# Delete Portfolio link (HIDDEN)
PORTFOLIO_ID=$(curl -X GET http://localhost:8000/social-links \
  -H "Authorization: Bearer $TOKEN_JUAN" | jq -r '.data[] | select(.platform_type=="PORTFOLIO") | .id')

curl -X DELETE http://localhost:8000/social-links/$PORTFOLIO_ID \
  -H "Authorization: Bearer $TOKEN_JUAN"
```

**Expected Response**:

```json
{
  "success": true,
  "data": {
    "message": "Enlace social eliminado exitosamente"
  },
  "error": null
}
```

**Validation**:
- ✅ Link deleted successfully
- ✅ Subsequent GET requests no longer include Portfolio link
- ✅ User can now create a new Portfolio link (uniqueness constraint freed)

---

## Performance Validation

### Test 9: Profile Load Performance (<200ms p95)

```bash
# Measure response time for profile with 6 links + privacy filtering
time curl -X GET http://localhost:8000/users/juan_ciclista/social-links \
  -H "Authorization: Bearer $TOKEN_CARLOS"
```

**Expected Result**:
- ✅ Response time < 200ms (p95 target from SC-008)
- ✅ Query includes mutual follow check without N+1 problem

**Performance Profiling** (Backend):

```python
# In backend/src/services/social_link_service.py
import time

start = time.time()
links = await get_visible_links(db, profile_user_id, viewer_user_id)
elapsed = (time.time() - start) * 1000
print(f"Privacy filtering query: {elapsed:.2f}ms")
```

---

## Cleanup

```bash
# Optional: Remove test data
curl -X DELETE http://localhost:8000/users/juan_ciclista \
  -H "Authorization: Bearer $TOKEN_JUAN"

curl -X DELETE http://localhost:8000/users/maria_rider \
  -H "Authorization: Bearer $TOKEN_MARIA"

curl -X DELETE http://localhost:8000/users/carlos_biker \
  -H "Authorization: Bearer $TOKEN_CARLOS"
```

---

## Success Criteria Checklist

After running all scenarios, verify:

- ✅ **SC-001**: Users can add social link in <30 seconds
- ✅ **SC-002**: 95% of valid URLs save successfully on first attempt
- ✅ **SC-003**: 100% of malicious URLs rejected/sanitized
- ✅ **SC-004**: Privacy indicators visible without documentation (UI test)
- ✅ **SC-005**: Privacy changes update in <1 second
- ✅ **SC-006**: 100% of XSS attempts prevented
- ✅ **SC-007**: MUTUAL_FOLLOWERS links only visible to mutual followers (100% accuracy)
- ✅ **SC-008**: Profile load time <50ms increase with 6 links

---

## Troubleshooting

### Issue: "User not found" error

**Solution**: Verify users were created successfully:

```bash
poetry run python -c "
from src.database import AsyncSessionLocal
from src.models.user import User
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute('SELECT username FROM users')
        print('Users:', [row[0] for row in result])

asyncio.run(check())
"
```

### Issue: Mutual follow not working

**Solution**: Verify bidirectional relationship:

```bash
curl -X GET http://localhost:8000/users/juan_ciclista/followers \
  -H "Authorization: Bearer $TOKEN_JUAN"

curl -X GET http://localhost:8000/users/juan_ciclista/following \
  -H "Authorization: Bearer $TOKEN_JUAN"
```

Both Carlos should appear in followers AND Juan should be following Carlos back.

### Issue: XSS validation not triggering

**Solution**: Verify `validators` library installed:

```bash
poetry show | grep validators
# Should show: validators 0.22.0
```

---

## Next Steps

After manual testing:

1. **Automated Tests**: Run pytest suite for unit/integration tests
   ```bash
   poetry run pytest tests/unit/test_social_link_service.py -v
   poetry run pytest tests/integration/test_social_links_api.py -v
   ```

2. **Contract Tests**: Validate OpenAPI schema compliance
   ```bash
   poetry run pytest tests/contract/test_social_links_contract.py -v
   ```

3. **Frontend Integration**: Test UI components with privacy indicators
   - SocialLinksDisplay component (icon rendering)
   - SocialLinksEditor component (dropdown for privacy levels)
   - PrivacyIndicator component (tooltips)

4. **E2E Tests**: Run Playwright tests for full user flows
   ```bash
   cd frontend
   npm run test:e2e -- social-links.spec.ts
   ```

---

**Quick Start Status**: ✅ READY FOR TESTING
**Last Updated**: 2026-01-16
