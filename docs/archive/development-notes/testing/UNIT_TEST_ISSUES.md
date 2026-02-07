# Unit Test Failures - GitHub Issues Template

**Total Failures**: 63 failed tests + 24 errors = 87 issues
**Test Run Date**: 2026-01-21
**Priority**: HIGH - Blocking CI/CD pipeline

---

## Issue 1: Fix TripPhoto Model - thumbnail_url Property Has No Setter

**Labels**: `bug`, `priority: high`, `tests`, `models`

### Summary
4 unit tests failing due to `TripPhoto.thumbnail_url` being a read-only property without a setter.

### Category
Schema/Model Attribute Issues - **HIGH PRIORITY** (blocking 4+ tests)

### Affected Tests
- `tests/unit/test_trip_model.py::TestTripPhotoModel::test_create_trip_photo`
- `tests/unit/test_trip_model.py::TestTripPhotoModel::test_trip_photos_relationship`
- `tests/unit/test_trip_model.py::TestTripPhotoModel::test_photo_cascade_delete`
- `tests/unit/test_trip_model.py::TestTripCompleteRelationships::test_complete_trip_with_all_relationships`

### Root Cause
The `TripPhoto` model defines `thumbnail_url` as a `@property` with only a getter, but tests attempt to set it during object initialization:

```python
photo = TripPhoto(
    trip_id=trip.id,
    photo_url="https://example.com/photo.jpg",
    thumbnail_url="https://example.com/thumb.jpg",  # ❌ No setter!
    # ...
)
```

### Error Example
```
AttributeError: property 'thumbnail_url' of 'TripPhoto' object has no setter
```

### Proposed Fix
Two options:

**Option A** (Recommended): Make `thumbnail_url` a regular database column if it should be persisted independently:
```python
# In src/models/trip.py
class TripPhoto(Base):
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
```

**Option B**: Add a setter to the property if it's derived/computed:
```python
@thumbnail_url.setter
def thumbnail_url(self, value: Optional[str]) -> None:
    self._thumbnail_url = value
```

### Related Files
- `backend/src/models/trip.py` - TripPhoto model definition
- `backend/tests/unit/test_trip_model.py` - Failing tests

### Impact
**HIGH** - Blocks 4 model tests and may cause cascading failures in trip service tests.

---

## Issue 2: Fix Social Service - NOT NULL Constraint Failures on user_profiles.user_id

**Labels**: `bug`, `priority: high`, `tests`, `database`, `social`

### Summary
8 unit tests failing with `NOT NULL constraint failed: user_profiles.user_id` and `follows.id` errors.

### Category
Database Constraint Violations - **HIGH PRIORITY**

### Affected Tests
- `tests/unit/test_social_service.py::TestSocialServiceFollowUser::test_follow_user_creates_relationship`
- `tests/unit/test_social_service.py::TestSocialServiceUnfollowUser::test_unfollow_user_removes_relationship`
- `tests/unit/test_social_service.py::TestSocialServiceGetFollowers::test_get_followers_returns_paginated_list`
- `tests/unit/test_social_service.py::TestSocialServiceGetFollowing::test_get_following_returns_paginated_list`
- `tests/unit/test_social_service.py::TestSocialServiceGetFollowStatus::test_get_follow_status_returns_true_when_following`
- `tests/unit/test_social_service.py::TestDuplicateFollowPrevention::test_follow_user_prevents_duplicate`
- `tests/unit/test_social_service.py::TestCounterUpdateOnFollowUnfollow::test_counters_increment_on_follow`
- `tests/unit/test_social_service.py::TestCounterUpdateOnFollowUnfollow::test_counters_decrement_on_unfollow`

### Root Cause
When creating test users via fixtures, `UserProfile` objects are being created with `user_id=None` instead of linking to the parent `User.id`.

### Error Example
```
sqlite3.IntegrityError: NOT NULL constraint failed: user_profiles.user_id
[SQL: INSERT INTO user_profiles (id, user_id, full_name, bio, location, cycling_type, profile_photo_url, show_email, show_location, followers_count, following_count, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)]
[parameters: ('38fe7ffd-7a49-447f-9730-ad6392920c92', None, None, None, ...)]
                                                         ^^^^ NULL!
```

### Proposed Fix
Fix the user creation fixtures in `tests/conftest.py` or test setup to ensure `UserProfile.user_id` is properly set:

```python
# In test setup
user = User(username="testuser", email="test@example.com")
profile = UserProfile(user_id=user.id)  # ✅ Explicitly set user_id
user.profile = profile

# OR use relationship
user = User(username="testuser", email="test@example.com")
user.profile = UserProfile()  # ✅ SQLAlchemy auto-sets user_id via relationship
```

### Related Files
- `backend/tests/conftest.py` - Test fixtures for user creation
- `backend/tests/unit/test_social_service.py` - Failing tests
- `backend/src/models/user.py` - User and UserProfile models
- `backend/src/services/social_service.py` - SocialService implementation

### Impact
**HIGH** - Blocks all 8 social service tests. Critical for feature 004-social-connections.

---

## Issue 3: Fix Auth Service - RegisterResponse Missing Attributes

**Labels**: `bug`, `priority: high`, `tests`, `auth`, `schemas`

### Summary
3 auth service tests failing due to `RegisterResponse` schema issues.

### Category
Schema/Response Model Issues - **HIGH PRIORITY**

### Affected Tests
- `tests/unit/test_auth_service.py::TestAuthServiceRegister::test_register_creates_user_successfully`
- `tests/unit/test_auth_service.py::TestAuthServiceRegister::test_register_hashes_password`
- `tests/unit/test_auth_service.py::TestAuthServiceRegister::test_register_creates_verification_token`

### Root Cause
Tests expect `RegisterResponse` to have `id`, `is_active`, and other attributes that may be missing from the schema definition.

### Error Example
```python
tests\unit\test_auth_service.py:40: in test_register_creates_user_successfully
    assert result.is_active is True
    # AttributeError or assertion failure
```

### Proposed Fix
Update `RegisterResponse` schema in `src/schemas/auth.py` to include all expected fields:

```python
class RegisterResponse(BaseModel):
    id: UUID  # ✅ Add this
    username: str
    email: EmailStr
    is_active: bool = True  # ✅ Add this
    is_verified: bool = False
    created_at: datetime
    # ... other fields
```

### Related Files
- `backend/src/schemas/auth.py` - RegisterResponse schema definition
- `backend/tests/unit/test_auth_service.py` - Failing tests
- `backend/src/services/auth_service.py` - AuthService.register() method

### Impact
**HIGH** - Blocks 3 critical auth tests. Affects feature 001-user-profiles.

---

## Issue 4: Fix Validator Error Messages and Case Preservation

**Labels**: `bug`, `priority: medium`, `tests`, `validators`

### Summary
9 validator tests failing due to error message format mismatches and username case not being preserved.

### Category
Validation Logic - **MEDIUM PRIORITY**

### Affected Tests
- `tests/unit/test_validators.py::TestUsernameValidator::test_valid_usernames`
- `tests/unit/test_validators.py::TestUsernameValidator::test_username_too_short`
- `tests/unit/test_validators.py::TestUsernameValidator::test_username_invalid_characters`
- `tests/unit/test_validators.py::TestUsernameValidator::test_username_case_preserved`
- `tests/unit/test_validators.py::TestEmailValidator::test_invalid_email_format`
- `tests/unit/test_validators.py::TestEmailValidator::test_email_too_long`
- `tests/unit/test_validators.py::TestPasswordValidator::test_password_missing_special_character`
- `tests/unit/test_validators.py::TestBioValidator::test_valid_bios`
- `tests/unit/test_validators.py::TestCyclingTypeValidator::test_invalid_cycling_type`

### Root Cause Issues

**1. Username Case Not Preserved**:
```python
# Test expects: 'John_Doe_99'
# Validator returns: 'john_doe_99'
assert result == 'John_Doe_99'  # ❌ FAILS
```

**2. Error Message Format Mismatches**:
Tests expect specific Spanish error messages but validators raise different messages.

### Proposed Fix

**Fix 1**: Preserve username case in `validate_username()`:
```python
# In src/utils/validators.py
def validate_username(username: str) -> str:
    # Don't lowercase! Preserve original case
    username = username.strip()  # Only trim whitespace

    if not 3 <= len(username) <= 30:
        raise ValueError("El nombre de usuario debe tener entre 3 y 30 caracteres")

    if not re.match(r'^[a-zA-Z0-9_]+$', username):  # Allow uppercase
        raise ValueError("El nombre de usuario solo puede contener letras, números y guiones bajos")

    return username  # ✅ Return original case
```

**Fix 2**: Update error messages to match test expectations (review each validator).

### Related Files
- `backend/src/utils/validators.py` - All validator functions
- `backend/tests/unit/test_validators.py` - Failing tests

### Impact
**MEDIUM** - Blocks 9 validator tests. Important for data integrity but not blocking critical features.

---

## Issue 5: Fix Trip Service - TripPhoto Attribute Errors (id, total_photos)

**Labels**: `bug`, `priority: high`, `tests`, `trips`, `photos`

### Summary
17 trip service tests failing due to `TripPhoto` object missing `id` attribute and `UserStats` attribute name mismatch.

### Category
Schema/Model Attribute Issues - **HIGH PRIORITY**

### Affected Tests
- `tests/unit/test_trip_service.py::TestTripServiceCreateTrip::test_create_trip_sanitizes_html`
- `tests/unit/test_trip_service.py::TestTripServicePhotoUpload::test_upload_photo_sets_correct_order`
- `tests/unit/test_trip_service.py::TestTripServicePhotoUpload::test_upload_photo_exceeds_max_limit`
- `tests/unit/test_trip_service.py::TestTripServicePhotoUpload::test_upload_photo_updates_stats_on_published_trip`
- `tests/unit/test_trip_service.py::TestTripServicePhotoDelete::test_delete_photo_success`
- `tests/unit/test_trip_service.py::TestTripServicePhotoDelete::test_delete_photo_reorders_remaining_photos`
- `tests/unit/test_trip_service.py::TestTripServicePhotoDelete::test_delete_photo_unauthorized`
- `tests/unit/test_trip_service.py::TestTripServicePhotoDelete::test_delete_photo_updates_stats_on_published_trip`
- `tests/unit/test_trip_service.py::TestTripServicePhotoReorder::test_reorder_photos_success`
- `tests/unit/test_trip_service.py::TestTripServicePhotoReorder::test_reorder_photos_invalid_photo_ids`
- `tests/unit/test_trip_service.py::TestTripServicePhotoReorder::test_reorder_photos_missing_photo_ids`
- `tests/unit/test_trip_service.py::TestTripServicePhotoReorder::test_reorder_photos_unauthorized`
- `tests/unit/test_trip_service.py::TestTripServiceTagLimit::test_create_trip_with_max_tags`
- `tests/unit/test_trip_service.py::TestTripServiceTagLimit::test_create_trip_exceeds_max_tags`
- `tests/unit/test_trip_service.py::TestTripServiceTagLimit::test_update_trip_exceeds_max_tags`
- `tests/unit/test_trip_service.py::TestTripServiceTagLimit::test_get_all_tags_returns_all`
- `tests/unit/test_trip_service.py::TestTripServiceUpdateTrip::test_update_trip_not_found`

### Root Cause Issues

**1. TripPhoto Missing `id` Attribute**:
```python
AttributeError: 'TripPhoto' object has no attribute 'id'
```
The model uses `photo_id` (UUID) but tests/service expect `id`.

**2. UserStats Attribute Mismatch**:
Tests expect `total_trip_photos` but model has `total_photos`.

### Proposed Fix

**Fix 1**: Standardize on `photo_id` (recommended) or add an alias:
```python
# Option A: Update all references to use photo_id
# In src/services/trip_service.py
photo.photo_id  # ✅ Use photo_id consistently

# Option B: Add hybrid property for backward compatibility
class TripPhoto(Base):
    @property
    def id(self) -> UUID:
        return self.photo_id
```

**Fix 2**: Rename `UserStats.total_photos` to `total_trip_photos`:
```python
# In src/models/user.py
class UserStats(Base):
    total_trip_photos: Mapped[int] = mapped_column(Integer, default=0)
    # OR keep as total_photos if that's the correct name
```

### Related Files
- `backend/src/models/trip.py` - TripPhoto model
- `backend/src/models/user.py` - UserStats model
- `backend/src/services/trip_service.py` - TripService methods
- `backend/tests/unit/test_trip_service.py` - Failing tests

### Impact
**HIGH** - Blocks 17 trip service tests. Critical for feature 002-travel-diary.

---

## Issue 6: Fix TripResponse Schema - Missing 'author' Field

**Labels**: `bug`, `priority: high`, `tests`, `trips`, `schemas`

### Summary
2 trip schema tests failing due to `TripResponse` requiring an `author` field that isn't being provided.

### Category
Schema/Response Model Issues - **HIGH PRIORITY**

### Affected Tests
- `tests/unit/test_trip_schemas.py::TestTripResponse::test_trip_response_structure`
- `tests/unit/test_trip_schemas.py::TestTripResponse::test_trip_response_with_nested_data`

### Root Cause
`TripResponse` schema has `author` as a required field, but test data doesn't include it.

### Error Example
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for TripResponse
  author
    Field required [type=missing, input_value={...}, input_type=dict]
```

### Proposed Fix

**Option A**: Make `author` optional in schema if it's not always available:
```python
# In src/schemas/trip.py
class TripResponse(BaseModel):
    author: Optional[UserBasicInfo] = None  # ✅ Make optional
```

**Option B**: Ensure tests provide author data:
```python
# In tests/unit/test_trip_schemas.py
trip_data = {
    "trip_id": str(uuid4()),
    "title": "Test Trip",
    "author": {  # ✅ Add author
        "user_id": str(uuid4()),
        "username": "testuser"
    },
    # ... other fields
}
```

### Related Files
- `backend/src/schemas/trip.py` - TripResponse schema
- `backend/tests/unit/test_trip_schemas.py` - Failing tests

### Impact
**HIGH** - Blocks 2 schema validation tests. May affect API responses.

---

## Issue 7: Fix JWT Token Tests - Expiration Validation Failures

**Labels**: `bug`, `priority: medium`, `tests`, `security`, `auth`

### Summary
3 JWT token tests failing in security utils.

### Category
Security/Authentication - **MEDIUM PRIORITY**

### Affected Tests
- `tests/unit/test_security_utils.py::TestJWTTokens::test_create_access_token_default_expiration`
- `tests/unit/test_security_utils.py::TestJWTTokens::test_create_access_token_custom_expiration`
- `tests/unit/test_security_utils.py::TestJWTTokens::test_create_refresh_token_default_expiration`

### Root Cause
Token expiration tests may be failing due to:
1. Timing issues (millisecond precision)
2. Missing/incorrect `SECRET_KEY` in test environment
3. Token payload structure changes

### Proposed Fix
Needs investigation. Check:
1. Test environment has `SECRET_KEY` set
2. Token creation uses correct expiration delta
3. Tests use appropriate time comparison (allow 1-2 second tolerance)

```python
# Example fix for timing tolerance
import pytest
from datetime import datetime, timedelta

def test_token_expiration():
    token = create_access_token(user_id="123")
    decoded = decode_token(token)

    expected_exp = datetime.utcnow() + timedelta(minutes=15)
    actual_exp = datetime.fromtimestamp(decoded['exp'])

    # Allow 2-second tolerance
    assert abs((expected_exp - actual_exp).total_seconds()) < 2
```

### Related Files
- `backend/src/utils/security.py` - JWT token functions
- `backend/tests/unit/test_security_utils.py` - Failing tests

### Impact
**MEDIUM** - Blocks 3 security tests. Important but not blocking core functionality.

---

## Issue 8: Fix File Storage Validators - MIME Type and Size Validation

**Labels**: `bug`, `priority: medium`, `tests`, `file-upload`, `validation`

### Summary
9 file storage validation tests failing due to return value and error message mismatches.

### Category
File Upload Validation - **MEDIUM PRIORITY**

### Affected Tests
- `tests/unit/test_file_storage.py::TestPhotoMimeTypeValidation::test_validate_jpeg_photo`
- `tests/unit/test_file_storage.py::TestPhotoMimeTypeValidation::test_validate_png_photo`
- `tests/unit/test_file_storage.py::TestPhotoMimeTypeValidation::test_validate_webp_photo`
- `tests/unit/test_file_storage.py::TestPhotoMimeTypeValidation::test_reject_text_file`
- `tests/unit/test_file_storage.py::TestPhotoMimeTypeValidation::test_reject_svg`
- `tests/unit/test_file_storage.py::TestPhotoMimeTypeValidation::test_reject_gif`
- `tests/unit/test_file_storage.py::TestPhotoSizeLimitValidation::test_validate_photo_under_5mb`
- `tests/unit/test_file_storage.py::TestPhotoSizeLimitValidation::test_validate_photo_exactly_5mb`
- `tests/unit/test_file_storage.py::TestPhotoFilenameGeneration::test_filename_is_filesystem_safe`

### Root Cause
Validation functions returning `None` instead of `True`, or error messages not matching test expectations.

### Proposed Fix
Update validation functions in `src/utils/file_storage.py`:

```python
# Example fix
def validate_photo_mime_type(mime_type: str) -> bool:
    if mime_type not in ALLOWED_PHOTO_MIME_TYPES:
        raise ValueError(f"Tipo de archivo no permitido: {mime_type}")
    return True  # ✅ Return True, not None
```

### Related Files
- `backend/src/utils/file_storage.py` - Validation functions
- `backend/tests/unit/test_file_storage.py` - Failing tests

### Impact
**MEDIUM** - Blocks 9 file upload tests. Important for photo upload feature.

---

## Issue 9: Fix Trip Visibility/Privacy Filtering Logic

**Labels**: `bug`, `priority: high`, `tests`, `trips`, `privacy`

### Summary
4 tests failing in public trip service due to incorrect privacy/visibility filtering.

### Category
Business Logic - **HIGH PRIORITY**

### Affected Tests
- `tests/unit/test_trip_service_public.py::test_get_public_trips_filters_by_privacy`
- `tests/unit/test_trip_service_public.py::test_get_public_trips_excludes_private_profiles`
- `tests/unit/test_trip_service_public.py::test_count_public_trips`
- `tests/unit/test_trip_service_public.py::test_get_public_trips_profile_visibility_transition`

### Root Cause
Public trips query not correctly filtering by:
1. Trip privacy status (PUBLIC vs PRIVATE)
2. User profile visibility (public vs private profiles)

### Error Example
```python
# Test expects only 1 public trip, but service returns 2
assert 2 == 1  # ❌ FAILS
```

### Proposed Fix
Review and fix the query logic in `get_public_trips()`:

```python
# In src/services/trip_service.py
async def get_public_trips(...):
    query = (
        select(Trip)
        .join(User)
        .join(UserProfile)
        .where(
            Trip.privacy == TripPrivacy.PUBLIC,  # ✅ Only public trips
            UserProfile.is_public == True,  # ✅ Only public profiles
            Trip.status == TripStatus.PUBLISHED  # ✅ Only published
        )
    )
```

### Related Files
- `backend/src/services/trip_service.py` - get_public_trips() method
- `backend/tests/unit/test_trip_service_public.py` - Failing tests
- `backend/src/models/trip.py` - TripPrivacy enum
- `backend/src/models/user.py` - UserProfile.is_public field

### Impact
**HIGH** - Blocks 4 privacy tests. Critical security/privacy feature.

---

## Issue 10: Fix Profile Service Validation Logic

**Labels**: `bug`, `priority: medium`, `tests`, `profile`, `validation`

### Summary
2 profile service tests failing due to validation not being enforced correctly.

### Category
Validation Logic - **MEDIUM PRIORITY**

### Affected Tests
- `tests/unit/test_profile_service.py::TestProfileServiceUpdateProfile::test_update_profile_validates_bio_length`
- `tests/unit/test_profile_service.py::TestProfileServiceUpdateProfile::test_update_profile_validates_cycling_type`

### Root Cause
ProfileService.update_profile() not properly validating bio length or cycling_type before saving.

### Proposed Fix
Ensure ProfileService validates input using Pydantic schemas:

```python
# In src/services/profile_service.py
async def update_profile(user_id: UUID, data: ProfileUpdateInput):
    # ✅ Pydantic validates automatically
    # But ensure validators are called
    if data.bio and len(data.bio) > 500:
        raise ValueError("La biografía no puede exceder 500 caracteres")

    if data.cycling_type:
        validate_cycling_type_async(data.cycling_type)  # ✅ Validate

    # ... update logic
```

### Related Files
- `backend/src/services/profile_service.py` - ProfileService.update_profile()
- `backend/src/schemas/profile.py` - ProfileUpdateInput schema
- `backend/tests/unit/test_profile_service.py` - Failing tests

### Impact
**MEDIUM** - Blocks 2 profile validation tests. Important for data integrity.

---

## Issue 11: Fix Like Service - Draft Trip Validation

**Labels**: `bug`, `priority: low`, `tests`, `likes`, `validation`

### Summary
1 like service test failing - should prevent liking draft trips.

### Category
Business Logic Validation - **LOW PRIORITY**

### Affected Tests
- `tests/unit/test_like_service.py::TestLikeTrip::test_like_draft_trip_fails`

### Root Cause
LikeService.like_trip() not checking if trip status is PUBLISHED before allowing like.

### Proposed Fix
Add status validation in like_trip():

```python
# In src/services/like_service.py
async def like_trip(user_id: UUID, trip_id: UUID):
    trip = await get_trip_by_id(trip_id)

    if trip.status != TripStatus.PUBLISHED:  # ✅ Check status
        raise ValueError("No se pueden dar 'me gusta' a viajes no publicados")

    # ... like logic
```

### Related Files
- `backend/src/services/like_service.py` - like_trip() method
- `backend/tests/unit/test_like_service.py` - Failing test

### Impact
**LOW** - Blocks 1 validation test. Minor business rule enforcement.

---

## Issue 12: Fix UserStats - Country Code to Name Conversion

**Labels**: `bug`, `priority: low`, `tests`, `stats`

### Summary
1 stats service test failing - country code not being converted to name correctly.

### Category
Data Transformation - **LOW PRIORITY**

### Affected Tests
- `tests/unit/test_stats_service.py::TestStatsServiceGetUserStats::test_get_user_stats_converts_country_codes_to_names`

### Root Cause
Test expects `CountryInfo` object to have `'code' in obj` work as a dict check, but it's a dataclass/Pydantic model.

### Error Example
```python
assert 'code' in CountryInfo(code='ES', name='España')  # ❌ FAILS
# Should be: assert hasattr(country_info, 'code')
```

### Proposed Fix
Either:
1. Fix the test to use proper attribute checking
2. Make CountryInfo behave like a dict (add `__contains__`)

```python
# Fix test
def test_country_conversion():
    stats = await get_user_stats(user_id)
    country = stats.countries[0]

    assert hasattr(country, 'code')  # ✅ Correct
    assert country.code == 'ES'
```

### Related Files
- `backend/src/services/stats_service.py` - get_user_stats() method
- `backend/src/schemas/stats.py` - CountryInfo schema
- `backend/tests/unit/test_stats_service.py` - Failing test

### Impact
**LOW** - Blocks 1 stats test. Minor schema/test issue.

---

## Summary by Priority

### HIGH Priority (44 tests) - Fix ASAP
1. ✅ **Issue 1**: TripPhoto thumbnail_url property (4 tests)
2. ✅ **Issue 2**: Social Service NULL constraints (8 tests)
3. ✅ **Issue 3**: RegisterResponse missing attributes (3 tests)
4. ✅ **Issue 5**: TripPhoto id/total_photos attributes (17 tests)
5. ✅ **Issue 6**: TripResponse missing author field (2 tests)
6. ✅ **Issue 9**: Trip visibility/privacy filtering (4 tests)

**Subtotal**: 38 tests

### MEDIUM Priority (23 tests) - Fix Next
7. ✅ **Issue 4**: Validator error messages/case preservation (9 tests)
8. ✅ **Issue 7**: JWT token expiration tests (3 tests)
9. ✅ **Issue 8**: File storage MIME/size validation (9 tests)
10. ✅ **Issue 10**: Profile service validation (2 tests)

**Subtotal**: 23 tests

### LOW Priority (3 tests) - Fix Last
11. ✅ **Issue 11**: Like draft trip validation (1 test)
12. ✅ **Issue 12**: Country code conversion (1 test)

**Subtotal**: 2 tests

---

## Total: 63 Failed Tests Categorized

**Next Steps**:
1. Create GitHub issues from this document (manually or via gh CLI)
2. Start fixing HIGH priority issues first
3. Re-run tests after each fix to verify progress
4. Update CI/CD pipeline once all tests pass

---

**Generated**: 2026-01-21
**Test Results**: `backend/test_results.txt`
**Command**: `poetry run pytest tests/unit/ -v --tb=short`
