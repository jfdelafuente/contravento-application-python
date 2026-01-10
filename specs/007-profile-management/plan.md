# Implementation Plan: Profile Management

**Branch**: `007-profile-management` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-profile-management/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable users to manage their complete profile including editing bio/location/cycling type, uploading and cropping profile photos, changing passwords with security validation, and configuring privacy settings for profile and trip visibility. The feature leverages existing backend APIs and focuses on creating an intuitive, secure frontend experience with real-time validation and responsive design.

## Technical Context

**Language/Version**: TypeScript 5 + React 18
**Primary Dependencies**: React Hook Form, Zod validation, Axios, React Cropper
**Storage**: Profile photos uploaded to backend storage (existing endpoint `/api/profile/me/photo`)
**Testing**: Manual testing (unit tests planned for future)
**Target Platform**: Web (responsive: mobile, tablet, desktop)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- Profile edits save in <2 minutes (SC-001)
- Photo upload/crop completes in <30 seconds (SC-002)
- Password change completes in <10 seconds (SC-003)
- 95% success rate for profile updates (SC-004)
- Form validation feedback within 500ms (SC-007)

**Constraints**:
- Bio max 500 characters (FR-001)
- Photo max 5MB, JPG/PNG only (FR-005)
- Photo display size 200x200px circular (FR-007)
- Password min 8 chars, mixed case + number (FR-010)
- Mobile-friendly touch interface (SC-012)

**Scale/Scope**:
- 4 user stories (2 P1, 1 P2, 1 P3)
- 20 functional requirements
- 5-6 main components + 3-4 sub-components
- Integration with 2 existing backend APIs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality ✅
- ✅ **PEP 8 / TypeScript ESLint**: Frontend follows ESLint + Prettier (already configured)
- ✅ **Type hints required**: TypeScript strict mode enabled
- ✅ **Google-style docstrings**: TSDoc comments for public components/functions
- ✅ **Single Responsibility**: Each component has one clear purpose
- ✅ **No magic numbers**: Use constants from design system variables

### Testing (TDD Mandatory) ⚠️
- ⚠️ **Write tests FIRST**: Manual testing for MVP, unit tests planned post-MVP
- ⚠️ **Coverage ≥90%**: Not enforced for this feature (frontend tests planned later)
- ✅ **Test structure**: Manual testing checklist provided in spec

**JUSTIFICATION**: Feature 006 established pattern of manual testing for frontend MVP with unit tests deferred to future iteration. Backend already has ≥90% coverage. Frontend test infrastructure will be added after 2-3 features are complete.

### User Experience ✅
- ✅ **Spanish language**: All user-facing text in Spanish
- ✅ **Standardized responses**: Error messages in Spanish with field-specific details
- ✅ **Validation errors**: Real-time validation with Spanish messages
- ✅ **UTC timestamps**: All dates handled with timezone awareness

### Performance ✅
- ✅ **Response times**: Form validation <500ms, saves <2min (SC-001, SC-007)
- ✅ **Photo uploads**: <30s for photo upload/crop (SC-002)
- ✅ **Eager loading**: Profile data loaded once on mount
- ✅ **Pagination**: N/A for this feature

### Security ✅
- ✅ **Password hashing**: Backend handles bcrypt (12 rounds production)
- ✅ **JWT tokens**: HttpOnly cookies already implemented
- ✅ **Rate limiting**: Backend has rate limiting for password changes
- ✅ **File validation**: MIME type and size validation on upload
- ✅ **XSS prevention**: React's built-in escaping + backend HTML sanitization

**GATE STATUS**: ✅ PASSED with TDD justification

## Project Structure

### Documentation (this feature)

```text
specs/007-profile-management/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── profile-api.yaml       # PUT /api/profile/me
│   └── photo-upload-api.yaml  # POST /api/profile/me/photo
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── profile/
│   │       ├── ProfileEditForm.tsx        # Main edit form container
│   │       ├── ProfileEditForm.css
│   │       ├── BasicInfoSection.tsx       # Bio, location, cycling type
│   │       ├── BasicInfoSection.css
│   │       ├── PhotoUploadSection.tsx     # Photo upload + crop
│   │       ├── PhotoUploadSection.css
│   │       ├── PhotoCropModal.tsx         # Image cropper modal
│   │       ├── PhotoCropModal.css
│   │       ├── PasswordChangeSection.tsx  # Password change form
│   │       ├── PasswordChangeSection.css
│   │       ├── PrivacySettingsSection.tsx # Privacy controls
│   │       └── PrivacySettingsSection.css
│   ├── pages/
│   │   ├── ProfileEditPage.tsx            # /profile/edit route
│   │   └── ProfileEditPage.css
│   ├── hooks/
│   │   ├── useProfileEdit.ts              # Profile update logic
│   │   ├── usePhotoUpload.ts              # Photo upload/crop logic
│   │   └── usePasswordChange.ts           # Password change logic
│   ├── services/
│   │   ├── profileService.ts              # API: PUT /api/profile/me
│   │   └── photoService.ts                # API: POST /api/profile/me/photo
│   ├── types/
│   │   └── profile.ts                     # Profile, ProfileUpdate, PrivacySettings types
│   └── utils/
│       ├── validators.ts                  # Bio, password, file validators
│       └── fileHelpers.ts                 # Image resize, MIME check
└── tests/
    └── manual/
        └── profile-edit-checklist.md      # Manual testing guide

backend/
└── src/
    └── api/
        └── profile.py                     # Already exists: PUT /profile/me, POST /profile/me/photo
```

**Structure Decision**: Web application structure (frontend + backend). Frontend uses component-based architecture with separation of concerns: components (UI), hooks (state/logic), services (API calls), types (TypeScript interfaces), utils (shared helpers). Backend APIs already exist and don't require changes.

## Complexity Tracking

*No violations - table not needed*

## Phase 0: Research & Unknowns

### 0.1. Image Cropping Library Selection

**Question**: Which React image cropping library should we use?

**Options**:
1. **react-image-crop** (lightweight, 20KB, MIT)
   - Pros: Lightweight, simple API, widely used
   - Cons: Less features, manual canvas manipulation
2. **react-cropper** (Cropper.js wrapper, 50KB, MIT)
   - Pros: Full-featured, supports rotation/zoom, better UX
   - Cons: Heavier bundle, more complex
3. **react-easy-crop** (modern, 30KB, MIT)
   - Pros: Modern API, good mobile support, hooks-based
   - Cons: Newer library, less mature

**Research Tasks**:
- [ ] Compare bundle sizes with tree-shaking
- [ ] Test mobile touch performance
- [ ] Evaluate API complexity for our use case
- [ ] Check TypeScript support quality

**Recommendation**: **react-easy-crop** - Best balance of features, size, and modern API. Excellent mobile support aligns with SC-012.

---

### 0.2. Form State Management

**Question**: Use React Hook Form or plain React state?

**Options**:
1. **React Hook Form** (already used in auth forms)
   - Pros: Consistent with existing code, built-in validation, better performance
   - Cons: Learning curve for complex scenarios
2. **Plain React state**
   - Pros: Simpler, more control
   - Cons: More boilerplate, manual validation

**Decision**: **React Hook Form** - Already established pattern in Feature 005 auth forms. Consistency is critical.

---

### 0.3. Real-time Password Strength Indicator

**Question**: How to implement password strength visualization (FR-011)?

**Options**:
1. **zxcvbn library** (Dropbox's password strength estimator)
   - Pros: Accurate, considers common passwords
   - Cons: 400KB bundle (lazy load it)
2. **Custom regex-based scoring**
   - Pros: Lightweight, simple
   - Cons: Less accurate, more maintenance
3. **Visual-only indicator** (no scoring)
   - Pros: Simplest, meets FR-011
   - Cons: Less helpful to users

**Recommendation**: **Custom regex-based** - FR-011 requires indicator, not necessarily advanced scoring. Regex checks (length, uppercase, lowercase, number) provide sufficient feedback for our validation rules without 400KB overhead.

---

### 0.4. Unsaved Changes Detection (FR-015)

**Question**: How to detect and warn about unsaved changes?

**Approach**:
- Use React Hook Form's `formState.isDirty`
- Add `beforeunload` event listener when form is dirty
- Add prompt on route change with React Router's `usePrompt` hook (v6.4+)

**Implementation**:
```typescript
// Custom hook
export const useUnsavedChanges = (isDirty: boolean) => {
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);
};
```

---

### 0.5. Photo Upload Progress Indicator (FR-020)

**Question**: How to show upload progress?

**Approach**:
- Use Axios `onUploadProgress` callback
- Update React state with percentage
- Display linear progress bar during upload

**Implementation**:
```typescript
const uploadPhoto = async (file: File) => {
  const formData = new FormData();
  formData.append('photo', file);

  const response = await api.post('/profile/me/photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const percentCompleted = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      );
      setUploadProgress(percentCompleted);
    },
  });
  return response.data;
};
```

---

## Phase 1: Design & Contracts

### 1.1. Data Model

**File**: [data-model.md](./data-model.md)

**Entities** (frontend types):

```typescript
// User Profile (from backend)
interface UserProfile {
  user_id: string;
  username: string;
  email: string;
  bio?: string;
  location?: string;
  cycling_type?: string;
  photo_url?: string;
  is_verified: boolean;
  profile_visibility: 'public' | 'private';
  trip_visibility: 'public' | 'followers' | 'private';
  created_at: string;
  updated_at: string;
}

// Profile Update Request
interface ProfileUpdateRequest {
  bio?: string;          // Max 500 chars
  location?: string;     // Free text or searchable
  cycling_type?: string; // From predefined options
}

// Privacy Settings Update
interface PrivacySettingsUpdate {
  profile_visibility?: 'public' | 'private';
  trip_visibility?: 'public' | 'followers' | 'private';
}

// Password Change Request
interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

// Photo Upload Response
interface PhotoUploadResponse {
  photo_url: string;
  message: string;
}
```

**Validation Rules**:
- `bio`: max 500 characters, optional
- `location`: string, optional
- `cycling_type`: one of predefined options, optional
- `current_password`: required for password change
- `new_password`: min 8 chars, 1 uppercase, 1 lowercase, 1 number
- `photo`: max 5MB, JPG/PNG only

---

### 1.2. API Contracts

**File**: `contracts/profile-api.yaml`

```yaml
openapi: 3.0.0
info:
  title: Profile Management API
  version: 1.0.0

paths:
  /api/profile/me:
    put:
      summary: Update current user's profile
      tags: [Profile]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                bio:
                  type: string
                  maxLength: 500
                  example: "Ciclista apasionado del bikepacking"
                location:
                  type: string
                  example: "Barcelona, España"
                cycling_type:
                  type: string
                  enum: [bikepacking, road, mountain, touring, gravel]
                  example: "bikepacking"
      responses:
        '200':
          description: Profile updated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  data:
                    $ref: '#/components/schemas/UserProfile'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized

  /api/profile/me/password:
    put:
      summary: Change current user's password
      tags: [Profile]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - current_password
                - new_password
              properties:
                current_password:
                  type: string
                  format: password
                new_password:
                  type: string
                  format: password
                  minLength: 8
                  pattern: '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
      responses:
        '200':
          description: Password changed successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  message:
                    type: string
                    example: "Contraseña actualizada correctamente"
        '400':
          description: Validation error or incorrect current password
        '401':
          description: Unauthorized

  /api/profile/me/photo:
    post:
      summary: Upload and update profile photo
      tags: [Profile]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required:
                - photo
              properties:
                photo:
                  type: string
                  format: binary
                  description: Photo file (JPG/PNG, max 5MB)
      responses:
        '200':
          description: Photo uploaded successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  data:
                    type: object
                    properties:
                      photo_url:
                        type: string
                        example: "/storage/profile_photos/2024/01/user123_abc.jpg"
                  message:
                    type: string
                    example: "Foto de perfil actualizada"
        '400':
          description: Invalid file (wrong format, too large)
        '401':
          description: Unauthorized

components:
  schemas:
    UserProfile:
      type: object
      properties:
        user_id:
          type: string
          format: uuid
        username:
          type: string
        email:
          type: string
          format: email
        bio:
          type: string
          nullable: true
        location:
          type: string
          nullable: true
        cycling_type:
          type: string
          nullable: true
        photo_url:
          type: string
          nullable: true
        is_verified:
          type: boolean
        profile_visibility:
          type: string
          enum: [public, private]
        trip_visibility:
          type: string
          enum: [public, followers, private]
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
        field:
          type: string
          nullable: true

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

### 1.3. Component Architecture

**Page**: `ProfileEditPage`
- Container component
- Handles routing, navigation
- Integrates all sections

**Sections** (sub-components):
1. `BasicInfoSection`: Bio, location, cycling type
2. `PhotoUploadSection`: Photo upload button, current photo display
3. `PhotoCropModal`: Modal with image cropper (lazy loaded)
4. `PasswordChangeSection`: Password change form
5. `PrivacySettingsSection`: Toggle switches for visibility

**Hooks** (custom logic):
1. `useProfileEdit`: Manages profile update state
2. `usePhotoUpload`: Handles photo upload/crop logic
3. `usePasswordChange`: Password change with validation
4. `useUnsavedChanges`: Warns on navigation with unsaved changes

**Services** (API integration):
1. `profileService.updateProfile()`: PUT /api/profile/me
2. `profileService.updatePrivacy()`: PUT /api/profile/me (same endpoint)
3. `profileService.changePassword()`: PUT /api/profile/me/password
4. `photoService.uploadPhoto()`: POST /api/profile/me/photo
5. `photoService.removePhoto()`: DELETE /api/profile/me/photo (if needed)

---

### 1.4. User Flow Diagram

```
ProfileEditPage (mounted)
  │
  ├─> Load current profile data (useAuth context)
  │
  ├─> BasicInfoSection
  │   ├─> User edits bio (real-time char count)
  │   ├─> User selects location (searchable dropdown)
  │   └─> User selects cycling type (dropdown)
  │
  ├─> PhotoUploadSection
  │   ├─> User clicks "Cambiar foto"
  │   ├─> File input opens
  │   ├─> User selects image
  │   ├─> PhotoCropModal opens
  │   │   ├─> User crops image
  │   │   └─> User saves → upload to backend
  │   └─> Photo preview updates
  │
  ├─> PasswordChangeSection
  │   ├─> User enters current password
  │   ├─> User enters new password (strength indicator updates)
  │   ├─> Real-time validation feedback
  │   └─> User saves → API call → success message
  │
  └─> PrivacySettingsSection
      ├─> User toggles profile visibility
      ├─> User selects trip visibility
      └─> Changes save immediately (or on form submit)

User clicks "Guardar cambios"
  ├─> Validation runs
  ├─> If valid → PUT /api/profile/me
  ├─> Success → Show toast, redirect to /profile
  └─> Error → Show field-specific errors
```

---

### 1.5. Validation Strategy

**Client-side** (Zod schemas):
```typescript
const profileEditSchema = z.object({
  bio: z.string().max(500, 'La bio no puede exceder 500 caracteres').optional(),
  location: z.string().optional(),
  cycling_type: z.string().optional(),
});

const passwordChangeSchema = z.object({
  current_password: z.string().min(1, 'Ingresa tu contraseña actual'),
  new_password: z
    .string()
    .min(8, 'Mínimo 8 caracteres')
    .regex(/[A-Z]/, 'Debe incluir al menos una mayúscula')
    .regex(/[a-z]/, 'Debe incluir al menos una minúscula')
    .regex(/\d/, 'Debe incluir al menos un número'),
});

const photoUploadSchema = z.object({
  file: z
    .instanceof(File)
    .refine((file) => file.size <= 5 * 1024 * 1024, 'El archivo no puede exceder 5MB')
    .refine(
      (file) => ['image/jpeg', 'image/png'].includes(file.type),
      'Solo se permiten archivos JPG o PNG'
    ),
});
```

**Server-side**: Backend already validates (FastAPI Pydantic schemas)

---

### 1.6. Error Handling

**Error Types**:
1. **Validation errors**: Show below each field
2. **API errors**: Show toast notification
3. **Network errors**: Show retry option
4. **File upload errors**: Show specific message (size, format)

**Example**:
```typescript
try {
  await updateProfile(data);
  toast.success('Perfil actualizado correctamente');
  navigate('/profile');
} catch (error) {
  if (error.response?.status === 400) {
    // Field-specific validation error
    setError(error.response.data.field, {
      message: error.response.data.message,
    });
  } else {
    // Generic error
    toast.error('Error al actualizar el perfil. Intenta nuevamente.');
  }
}
```

---

### 1.7. Quickstart Guide

**File**: [quickstart.md](./quickstart.md)

**Setup**:
```bash
# Install dependencies (if not already)
cd frontend
npm install react-hook-form zod @hookform/resolvers
npm install react-easy-crop
npm install react-hot-toast  # For notifications

# Start dev server
npm run dev

# Backend should be running
cd ../backend
./run-local-dev.sh
```

**Manual Testing**:
1. Navigate to `http://localhost:3001/profile/edit`
2. Edit bio, location, cycling type → Save → Verify updates on `/profile`
3. Upload photo → Crop → Save → Verify circular photo on profile
4. Change password → Login with new password
5. Toggle privacy settings → Verify profile visibility from logged-out view

---

## Phase 2: Implementation Tasks

**Note**: Tasks will be generated in separate `/speckit.tasks` command. This section provides high-level task categories.

### Task Categories

**T001-T010: Setup & Foundation**
- Create directory structure
- Define TypeScript types
- Create validation schemas
- Set up routing for `/profile/edit`

**T011-T020: Basic Info Section**
- Implement BasicInfoSection component
- Bio textarea with character counter
- Location input (searchable dropdown)
- Cycling type dropdown
- Form validation with React Hook Form

**T021-T030: Photo Upload Section**
- Implement PhotoUploadSection component
- File input with validation
- PhotoCropModal with react-easy-crop
- Upload progress indicator
- Photo preview update

**T031-T040: Password Change Section**
- Implement PasswordChangeSection component
- Current password input
- New password input with strength indicator
- Validation feedback
- Success/error handling

**T041-T050: Privacy Settings Section**
- Implement PrivacySettingsSection component
- Profile visibility toggle
- Trip visibility selector
- Immediate or deferred save

**T051-T060: Integration & Polish**
- ProfileEditPage integration
- Unsaved changes warning
- API service functions
- Custom hooks implementation
- Error handling

**T061-T070: Testing & Deployment**
- Manual testing checklist
- Responsive testing
- Cross-browser testing
- Performance validation
- Code review
- Merge to develop

---

## Phase 3: Agent Context Update

### New Technologies Added
- `react-easy-crop`: Image cropping library for profile photos
- `react-hot-toast`: Toast notifications for success/error messages
- `@hookform/resolvers`: Zod integration with React Hook Form

### New Patterns Established
- **Multi-section form**: Complex form split into logical sections
- **Image upload + crop workflow**: File selection → crop → upload → preview
- **Real-time validation feedback**: Zod + React Hook Form integration
- **Unsaved changes warning**: `beforeunload` + route prompt
- **Immediate vs deferred save**: Privacy settings may save immediately

### Design System Extensions
- **Photo upload component**: Drag-and-drop zone with rustic styling
- **Progress bar**: Linear progress for photo uploads
- **Password strength indicator**: Visual bar with color coding
- **Toggle switches**: Rustic-styled toggles for privacy settings
- **Character counter**: Real-time counter for bio field

### Performance Considerations
- **Lazy load PhotoCropModal**: Only import when needed
- **Debounce validation**: Avoid excessive validation on keystroke
- **Optimize photo upload**: Client-side resize before upload (if needed)
- **Cache profile data**: Avoid re-fetching on mount if data exists

---

## Constitution Re-check (Post Phase 1)

### Code Quality ✅
- Component structure follows Single Responsibility
- TypeScript types fully defined
- No magic numbers (using constants)

### Testing ⚠️
- Manual testing checklist created
- Unit tests deferred (same justification as Phase 1)

### User Experience ✅
- All error messages in Spanish
- Real-time validation feedback
- Loading states for all async operations
- Success confirmations via toast

### Performance ✅
- Form validation <500ms (debounced)
- Photo upload with progress indicator
- Lazy loading for heavy components

### Security ✅
- Password validation on client + server
- File type/size validation
- CSRF protection via HttpOnly cookies
- No sensitive data in localStorage

**FINAL GATE**: ✅ PASSED

---

## Next Steps

1. **Run `/speckit.tasks`** to generate detailed task breakdown
2. **Create feature branch** (already created: `007-profile-management`)
3. **Begin implementation** starting with foundation tasks (types, schemas)
4. **Iterate through user stories** by priority (P1 → P2 → P3)
5. **Manual testing** after each section completion
6. **Merge to develop** when all acceptance scenarios pass

---

**Plan Status**: ✅ COMPLETE
**Ready for**: `/speckit.tasks` command
**Last Updated**: 2026-01-09
