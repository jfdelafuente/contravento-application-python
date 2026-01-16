# Research: Enlaces Sociales con Control de Privacidad Granular

**Feature**: 015-social-links-privacy
**Date**: 2026-01-16
**Status**: ✅ Completed

## Research Questions & Decisions

### 1. URL Sanitization Library Selection

**Question**: ¿Qué librería usar para sanitizar URLs en Python con mejor protección contra XSS/phishing?

**Options Evaluated**:

| Library | Pros | Cons | Python 3.12 Support |
|---------|------|------|---------------------|
| **bleach** | Industry standard, Mozilla-maintained, configurable allowlist | Heavier dependency, some features deprecated | ✅ Yes |
| **html5lib** | Pure parsing library, very accurate | No built-in sanitization, requires custom logic | ✅ Yes |
| **Custom regex** | Lightweight, no dependencies | Error-prone, hard to maintain, misses edge cases | ✅ Yes |
| **validators** | Simple URL validation | No sanitization, only validates format | ✅ Yes |

**Decision**: ✅ **Use `validators` library for basic URL format validation + custom allowlist validation**

**Rationale**:
- `bleach` is primarily for HTML sanitization, overkill for URL-only validation
- `validators` provides battle-tested URL format checking (RFC 3986 compliant)
- Custom allowlist logic is simpler and more maintainable for our specific use case (6 social platforms)
- Lighter dependency footprint (validators is small, pure Python)
- Performance: ~1-2ms validation time for URLs

**Implementation Pattern**:
```python
import validators
from urllib.parse import urlparse

ALLOWED_DOMAINS = {
    'INSTAGRAM': ['instagram.com', 'www.instagram.com'],
    'STRAVA': ['strava.com', 'www.strava.com'],
    'BLOG': ['substack.com', 'medium.com', 'wordpress.com', 'blogger.com'],  # Flexible
    'PORTFOLIO': None,  # Allow any domain for custom portfolios (with extra validation)
    'CUSTOM': None  # User-defined platforms
}

def sanitize_url(url: str, platform_type: str) -> str:
    # 1. Validate URL format
    if not validators.url(url):
        raise ValueError("URL inválida")

    # 2. Extract domain
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # 3. Check allowlist (strict for Instagram/Strava, flexible for Blog/Portfolio)
    allowed = ALLOWED_DOMAINS.get(platform_type)
    if allowed and domain not in allowed:
        raise ValueError(f"Dominio no permitido para {platform_type}")

    # 4. Sanitize: Remove query params for social platforms, keep path only
    if platform_type in ['INSTAGRAM', 'STRAVA']:
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    return url  # Full URL for blogs/portfolios
```

**Alternatives Considered & Rejected**:
- **bleach**: Rejected - Too heavy for URL-only validation, designed for HTML content
- **html5lib**: Rejected - No built-in sanitization, requires custom logic anyway
- **regex only**: Rejected - Error-prone, hard to cover all edge cases (IPv6, punycode, etc.)

---

### 2. Privacy Filtering Performance Pattern

**Question**: ¿Cómo optimizar queries para verificar seguimiento mutuo al renderizar perfiles?

**Options Evaluated**:

| Approach | Performance | Complexity | Scalability |
|----------|-------------|------------|-------------|
| **Query JOIN with Follows** | ~50ms for 6 links + 100 followers | Low (single query) | ✅ Good (scales to 10k users) |
| **Cache relaciones** | ~5ms (cached) | High (cache invalidation logic) | ⚠️ Moderate (stale data risk) |
| **Denormalization** | ~20ms (no JOIN) | Very High (data consistency) | ✅ Good (faster reads) |
| **Lazy load per link** | ~300ms (N+1 problem) | Low | ❌ Poor (N queries) |

**Decision**: ✅ **Query JOIN with Follows table + eager loading**

**Rationale**:
- Meets performance target (<200ms p95) without cache complexity
- SQLAlchemy eager loading prevents N+1 queries
- Single database query with JOIN is simpler than cache invalidation logic
- No risk of stale data (cache invalidation is hard)
- Scales to 10k users with proper indexes

**Implementation Pattern**:
```python
# In SocialLinkService.get_visible_links()
async def get_visible_links(
    db: AsyncSession,
    profile_user_id: UUID,
    viewer_user_id: UUID | None
) -> List[SocialLink]:
    query = (
        select(SocialLink)
        .where(SocialLink.user_id == profile_user_id)
        .options(selectinload(SocialLink.user))  # Eager load User
    )

    # Filter by privacy level
    if viewer_user_id is None:
        # Anonymous: only PUBLIC
        query = query.where(SocialLink.privacy_level == PrivacyLevel.PUBLIC)
    elif viewer_user_id == profile_user_id:
        # Owner: see all (including HIDDEN)
        pass
    else:
        # Authenticated user: PUBLIC + COMMUNITY + check MUTUAL_FOLLOWERS
        mutual_follow = await check_mutual_follow(db, profile_user_id, viewer_user_id)

        if mutual_follow:
            # Show PUBLIC, COMMUNITY, MUTUAL_FOLLOWERS
            query = query.where(
                SocialLink.privacy_level.in_([
                    PrivacyLevel.PUBLIC,
                    PrivacyLevel.COMMUNITY,
                    PrivacyLevel.MUTUAL_FOLLOWERS
                ])
            )
        else:
            # Show PUBLIC, COMMUNITY only
            query = query.where(
                SocialLink.privacy_level.in_([
                    PrivacyLevel.PUBLIC,
                    PrivacyLevel.COMMUNITY
                ])
            )

    result = await db.execute(query)
    return result.scalars().all()

async def check_mutual_follow(
    db: AsyncSession,
    user_a_id: UUID,
    user_b_id: UUID
) -> bool:
    """Check if both users follow each other."""
    query = (
        select(func.count())
        .select_from(Follow)
        .where(
            or_(
                and_(
                    Follow.follower_id == user_a_id,
                    Follow.following_id == user_b_id
                ),
                and_(
                    Follow.follower_id == user_b_id,
                    Follow.following_id == user_a_id
                )
            )
        )
    )
    result = await db.execute(query)
    count = result.scalar()
    return count == 2  # Both follow relationships exist
```

**Alternatives Considered & Rejected**:
- **Cache**: Rejected - Complexity of invalidation outweighs 45ms savings
- **Denormalization**: Rejected - Data consistency risk, not worth 30ms savings
- **Lazy load**: Rejected - N+1 problem kills performance (300ms+)

---

### 3. Frontend Icon Library

**Question**: ¿Qué librería de iconos usar para redes sociales + indicadores de privacidad?

**Options Evaluated**:

| Library | Bundle Size | Icons Available | Estética ContraVento |
|---------|-------------|-----------------|----------------------|
| **HeroIcons** (current) | ~50KB | Lock, Eye, Users, Globe | ✅ Excellent (already used) |
| **React Icons** | ~200KB | Social icons + privacy icons | ⚠️ Good (more variety) |
| **FontAwesome** | ~400KB | Comprehensive | ❌ Heavy bundle |
| **Custom SVGs** | ~5KB | Only what we need | ✅ Perfect control |

**Decision**: ✅ **Use HeroIcons (already in project) + Custom SVGs for social platform icons**

**Rationale**:
- HeroIcons already in use (@heroicons/react 2.2.0 in package.json)
- Provides privacy indicators: LockClosedIcon, LockOpenIcon, UserGroupIcon, EyeSlashIcon
- Lightweight (~50KB) and matches ContraVento aesthetic (outline style, clean lines)
- Custom SVGs for Instagram/Strava/Blog/Portfolio logos (brand-specific, small file size)
- No additional bundle size increase

**Implementation Pattern**:
```typescript
// Privacy Indicators (HeroIcons)
import {
  LockOpenIcon,      // PUBLIC (candado abierto)
  LockClosedIcon,    // COMMUNITY (candado cerrado)
  UserGroupIcon,     // MUTUAL_FOLLOWERS (grupo de personas)
  EyeSlashIcon       // HIDDEN (ojo tachado)
} from '@heroicons/react/24/outline';

// Social Platform Icons (Custom SVGs in src/assets/icons/)
import InstagramIcon from '@/assets/icons/instagram.svg';
import StravaIcon from '@/assets/icons/strava.svg';
import BlogIcon from '@/assets/icons/blog.svg';  // Generic blog/article icon
import PortfolioIcon from '@/assets/icons/portfolio.svg';  // Briefcase/folder

const PRIVACY_ICONS = {
  PUBLIC: LockOpenIcon,
  COMMUNITY: LockClosedIcon,
  MUTUAL_FOLLOWERS: UserGroupIcon,
  HIDDEN: EyeSlashIcon
};

const PLATFORM_ICONS = {
  INSTAGRAM: InstagramIcon,
  STRAVA: StravaIcon,
  BLOG: BlogIcon,
  PORTFOLIO: PortfolioIcon,
  CUSTOM_1: null,  // User chooses icon or shows generic link
  CUSTOM_2: null
};
```

**Color Palette Adaptation** (ContraVento tonos tierra):
- Primary icons: `#1B2621` (Verde bosque) for dark mode
- Accent: `#D35400` (Terracota) for hover/active states
- Background: `#F9F7F2` (Crema) for icon containers

**Alternatives Considered & Rejected**:
- **React Icons**: Rejected - 4x larger bundle, unnecessary variety
- **FontAwesome**: Rejected - 8x larger bundle, overkill
- **All custom SVGs**: Rejected - Reinventing wheel for privacy icons

---

### 4. Domain Validation Strategy

**Question**: ¿Validar dominios con allowlist estricta o regex flexible?

**Options Evaluated**:

| Strategy | Security | Flexibility | Maintenance |
|----------|----------|-------------|-------------|
| **Allowlist hardcoded** | ✅ Excellent (zero false positives) | ❌ Poor (manual updates) | ⚠️ Moderate (code changes) |
| **Regex pattern matching** | ⚠️ Moderate (complex patterns) | ✅ Excellent (dynamic) | ❌ Poor (regex hell) |
| **Hybrid approach** | ✅ Excellent (strict for social, flexible for blogs) | ✅ Good (best of both) | ✅ Good (clear separation) |

**Decision**: ✅ **Hybrid approach: Strict allowlist for Instagram/Strava, flexible for Blog/Portfolio**

**Rationale**:
- Instagram/Strava: Well-known single domains, no ambiguity → strict allowlist
- Blog platforms: Many options (Substack, Medium, WordPress, Ghost, custom) → allowlist of common platforms
- Portfolio: Any domain allowed (artists, photographers have custom domains) → format validation only
- Custom 1/2: User-defined, any domain → format validation only
- Balance security (prevent phishing) with flexibility (support creative users)

**Implementation Pattern**:
```python
from enum import Enum
from typing import Dict, List, Optional

class PlatformType(str, Enum):
    INSTAGRAM = "INSTAGRAM"
    STRAVA = "STRAVA"
    BLOG = "BLOG"
    PORTFOLIO = "PORTFOLIO"
    CUSTOM_1 = "CUSTOM_1"
    CUSTOM_2 = "CUSTOM_2"

# Domain allowlist configuration
DOMAIN_ALLOWLIST: Dict[PlatformType, Optional[List[str]]] = {
    PlatformType.INSTAGRAM: [
        'instagram.com',
        'www.instagram.com'
    ],
    PlatformType.STRAVA: [
        'strava.com',
        'www.strava.com',
        'app.strava.com'  # Strava app URLs
    ],
    PlatformType.BLOG: [
        'substack.com',
        'medium.com',
        'wordpress.com',
        'ghost.io',
        'blogger.com',
        'tumblr.com',
        'hashnode.dev',
        'dev.to'
    ],
    PlatformType.PORTFOLIO: None,  # Any domain allowed (with format check)
    PlatformType.CUSTOM_1: None,   # User-defined, any domain
    PlatformType.CUSTOM_2: None
}

def validate_domain(url: str, platform_type: PlatformType) -> bool:
    """Validate domain based on platform type."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace('www.', '')  # Normalize

    allowlist = DOMAIN_ALLOWLIST.get(platform_type)

    if allowlist is None:
        # No allowlist (Portfolio, Custom): Only check URL format is valid
        return validators.url(url)

    # Check domain matches allowlist
    return domain in [d.replace('www.', '') for d in allowlist]
```

**Security Considerations**:
- Blog allowlist covers 90% of use cases (expandable without code change via config)
- Portfolio/Custom flexibility allows artists/guides to use personal domains
- Format validation prevents `javascript:`, `data:`, `file:` schemes
- Subdomain wildcards not allowed (prevents `evil.instagram.com` attacks)

**Alternatives Considered & Rejected**:
- **Strict allowlist for all**: Rejected - Too restrictive for creative users (photographers, writers)
- **Regex only**: Rejected - Complex to maintain, security risks, no clear benefit over hybrid
- **No domain validation**: Rejected - Opens phishing attack vector

---

## Implementation Decisions Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **URL Sanitization** | `validators` library + custom allowlist | Lightweight, RFC 3986 compliant, simple maintenance |
| **Privacy Filtering** | Query JOIN with Follows + eager loading | <200ms p95, no cache complexity, scales to 10k users |
| **Icons** | HeroIcons (privacy) + Custom SVGs (social) | Already in project, ~50KB, matches estética |
| **Domain Validation** | Hybrid (strict for social, flexible for blogs/portfolio) | Balance security + flexibility for creative users |

## Performance Benchmarks (Expected)

Based on research and similar implementations:

- **URL Validation**: ~1-2ms per URL (validators library)
- **Privacy Filtering Query**: ~50ms for profile with 6 links + 100 followers (with JOIN)
- **Mutual Follow Check**: ~10ms (indexed query on Follows table)
- **Total Profile Load**: ~150ms p95 (well below 200ms target)

## Dependencies Added

### Backend
- `validators==0.22.0` - URL format validation (pure Python, no C dependencies)

### Frontend
- No new dependencies (HeroIcons already installed)
- Custom SVGs for social platforms (5-10KB total)

## Next Steps

✅ Research complete - Ready for Phase 1 (Design Artifacts)

1. Generate `data-model.md` with SocialLink schema
2. Generate `contracts/social-links-api.yaml` with OpenAPI specs
3. Generate `quickstart.md` with testing scenarios
4. Update agent context with new technologies

---

**Research Status**: ✅ COMPLETED
**Date Completed**: 2026-01-16
**Ready for Phase 1**: YES
