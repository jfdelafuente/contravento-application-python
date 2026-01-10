# Manual Testing Checklist - Feature 007: Profile Management

**Feature Branch**: `007-profile-management`
**Test Date**: 2026-01-10
**Tester**: [Your Name]
**Environment**: Local Development (Frontend: localhost:3001, Backend: localhost:8000)

## Pre-Testing Setup

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3001
- [ ] Test user credentials available (username: testuser, password: TestPass123!)
- [ ] Admin user available if needed (username: admin, password: AdminPass123!)
- [ ] Browser DevTools open for monitoring network requests
- [ ] Clear browser cache and localStorage before testing

---

## User Story 1: Edit Basic Profile Information (Priority: P1)

### Test Setup
- [ ] Login with test user (testuser / TestPass123!)
- [ ] Navigate to profile page
- [ ] Click "Editar Perfil" button

### Scenario 1.1: Update Bio (200 characters)

**Steps**:
1. Locate the "Biografía" textarea field
2. Clear existing content
3. Enter a 200-character bio: "Soy un ciclista apasionado de Barcelona. Me encanta explorar nuevas rutas de montaña y compartir mis experiencias. Llevo 5 años practicando ciclismo y cada día descubro algo nuevo. ¡Siempre en busca de nuevas aventuras!"
4. Verify character counter shows "200 / 500"
5. Click "Guardar Cambios" button
6. Wait for success toast notification
7. Navigate to profile page (/profile/testuser)
8. Verify bio displays correctly

**Expected Results**:
- [ ] Bio saves successfully
- [ ] Success toast appears: "Perfil actualizado correctamente"
- [ ] Bio displays on profile page exactly as entered
- [ ] Character counter updates in real-time while typing

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 1.2: Update Cycling Type and Location

**Steps**:
1. On edit profile page, locate "Tipo de ciclismo" dropdown
2. Select "Mountain Bike" from dropdown
3. Locate "Ubicación" input field
4. Enter "Barcelona, España"
5. Click "Guardar Cambios"
6. Wait for success toast
7. Navigate to profile page
8. Verify cycling type shows "Mountain Bike"
9. Verify location shows "Barcelona, España"

**Expected Results**:
- [ ] Both fields save successfully
- [ ] Success toast appears
- [ ] Cycling type displays correctly on profile
- [ ] Location displays correctly on profile
- [ ] No validation errors

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 1.3: Unsaved Changes Warning

**Steps**:
1. On edit profile page, change bio to "Test changes without saving"
2. Do NOT click "Guardar Cambios"
3. Attempt to navigate away by clicking browser back button OR clicking another link
4. Observe if warning prompt appears

**Expected Results**:
- [ ] Browser shows confirmation dialog
- [ ] Dialog asks if user wants to discard changes
- [ ] If user clicks "Cancel", stays on edit page with changes intact
- [ ] If user clicks "OK", navigates away and discards changes

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 1.4: Validation Error - Bio Too Long

**Steps**:
1. On edit profile page, clear bio field
2. Enter a bio longer than 500 characters (copy 600 characters of text)
3. Attempt to save
4. Observe validation error

**Expected Results**:
- [ ] Form prevents submission
- [ ] Clear error message appears explaining bio must be ≤500 characters
- [ ] Character counter shows red when over limit
- [ ] Error message is in Spanish

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

## User Story 2: Upload and Manage Profile Photo (Priority: P1)

### Test Setup
- [ ] Prepare test images:
  - Valid JPG under 5MB (e.g., 2MB portrait photo)
  - Valid PNG under 5MB
  - Invalid large file over 5MB (e.g., 7MB image)
  - Invalid format (e.g., .gif or .bmp)
- [ ] Login as testuser
- [ ] Navigate to profile edit page

### Scenario 2.1: Upload Valid JPG and Crop

**Steps**:
1. Click on profile photo placeholder or existing photo
2. Click "Cambiar Foto" or similar button
3. Select valid JPG file (under 5MB)
4. Wait for crop modal to appear
5. Verify image loads in crop interface
6. Adjust crop area by dragging corners
7. Adjust zoom slider if available
8. Click "Guardar" button in crop modal
9. Wait for upload progress (if shown)
10. Wait for success toast
11. Verify photo updates immediately on edit page
12. Navigate to profile page and verify photo displays

**Expected Results**:
- [ ] Crop modal opens immediately after file selection
- [ ] Image displays correctly in crop interface
- [ ] Crop controls (drag, zoom) work smoothly
- [ ] "Guardar" and "Cancelar" buttons are visible at bottom
- [ ] Upload progress indicator appears (if upload takes >1s)
- [ ] Success toast: "Foto actualizada correctamente"
- [ ] Photo displays in circular format (200x200px)
- [ ] Photo appears on profile page within 5 seconds

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 2.2: Replace Existing Photo

**Steps**:
1. With existing profile photo visible on edit page
2. Click on photo to change it
3. Upload a different image
4. Complete crop process
5. Save new photo
6. Verify old photo is replaced

**Expected Results**:
- [ ] No confirmation dialog needed (implicit replacement)
- [ ] Old photo disappears
- [ ] New photo displays immediately
- [ ] Backend deletes old photo file (verify in storage directory if possible)

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 2.3: Remove Profile Photo

**Steps**:
1. With existing profile photo on edit page
2. Click "Eliminar Foto" or trash icon button
3. Confirm removal if prompted
4. Wait for success toast
5. Verify default avatar appears
6. Navigate to profile page and verify default avatar

**Expected Results**:
- [ ] Photo removal succeeds
- [ ] Default avatar/placeholder appears
- [ ] Success toast appears
- [ ] Profile page shows default avatar

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 2.4: Upload Invalid File

**Test 2.4a - File Too Large**:
1. Attempt to upload image over 5MB
2. Observe error message

**Expected Results**:
- [ ] Upload rejected
- [ ] Clear error message: "La imagen debe ser menor a 5MB" or similar
- [ ] No crash or freeze

**Test 2.4b - Invalid Format**:
1. Attempt to upload .gif or .bmp file
2. Observe error message

**Expected Results**:
- [ ] Upload rejected
- [ ] Clear error message: "Solo se permiten archivos JPG o PNG" or similar
- [ ] File picker may filter to show only JPG/PNG

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

## User Story 3: Change Password (Priority: P2)

### Test Setup
- [ ] Login as testuser (current password: TestPass123!)
- [ ] Navigate to profile edit page
- [ ] Locate "Cambiar Contraseña" section

### Scenario 3.1: Successful Password Change

**Steps**:
1. Enter current password: "TestPass123!"
2. Enter new password: "NewPass456!"
3. Enter confirm password: "NewPass456!"
4. Click "Cambiar Contraseña" button
5. Wait for success toast
6. Logout
7. Login with new password "NewPass456!"
8. Verify login succeeds
9. **IMPORTANT**: Change password back to "TestPass123!" for other tests

**Expected Results**:
- [ ] Password updates successfully
- [ ] Success toast: "Contraseña actualizada correctamente"
- [ ] User remains logged in after change
- [ ] New password works for login
- [ ] Confirmation email sent (check backend logs or email service)

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 3.2: Incorrect Current Password

**Steps**:
1. Enter incorrect current password: "WrongPass123!"
2. Enter new password: "NewPass456!"
3. Enter confirm password: "NewPass456!"
4. Click "Cambiar Contraseña"
5. Observe error

**Expected Results**:
- [ ] Password change fails
- [ ] Error message: "La contraseña actual es incorrecta" or similar
- [ ] Password not updated
- [ ] Form remains populated (except password fields cleared for security)

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 3.3: Password Validation - Requirements Not Met

**Test 3.3a - Too Short**:
1. Enter current password correctly
2. Enter new password: "Short1" (only 6 characters)
3. Observe validation error

**Expected Results**:
- [ ] Real-time validation error appears
- [ ] Error: "La contraseña debe tener al menos 8 caracteres"
- [ ] Submit button disabled or form prevents submission

**Test 3.3b - No Uppercase**:
1. Enter new password: "lowercase123"
2. Observe validation error

**Expected Results**:
- [ ] Error: "Debe contener al menos una mayúscula"

**Test 3.3c - No Lowercase**:
1. Enter new password: "UPPERCASE123"
2. Observe validation error

**Expected Results**:
- [ ] Error: "Debe contener al menos una minúscula"

**Test 3.3d - No Number**:
1. Enter new password: "NoNumbers"
2. Observe validation error

**Expected Results**:
- [ ] Error: "Debe contener al menos un número"

**Test 3.3e - Passwords Don't Match**:
1. Enter new password: "NewPass456!"
2. Enter confirm: "NewPass789!"
3. Observe validation error

**Expected Results**:
- [ ] Error: "Las contraseñas no coinciden"

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 3.4: Password Strength Indicator

**Steps**:
1. Focus on new password field
2. Type progressively: "a" → "ab" → "ab1" → "Ab1" → "Ab12345"
3. Observe strength indicator changes

**Expected Results**:
- [ ] Strength indicator appears when typing
- [ ] Shows "weak", "medium", or "strong" based on password
- [ ] Updates in real-time as user types
- [ ] Visual indicator (color or progress bar)

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

## User Story 4: Configure Account Privacy Settings (Priority: P3)

### Test Setup
- [ ] Login as testuser
- [ ] Navigate to profile edit page
- [ ] Locate "Privacidad" or "Configuración de Privacidad" section

### Scenario 4.1: Toggle Private Profile

**Steps**:
1. Locate "Perfil Privado" toggle switch
2. Note current state (ON or OFF)
3. Click toggle to switch state
4. Click "Guardar Cambios"
5. Wait for success toast
6. Open incognito browser window
7. Navigate to testuser's profile (without login)
8. Verify visibility matches privacy setting

**Expected Results**:
- [ ] Toggle switches smoothly
- [ ] Setting saves successfully
- [ ] Success toast appears
- [ ] If private: logged-out users cannot see profile details (only username)
- [ ] If public: logged-out users can see full profile
- [ ] Changes take effect immediately (no logout required)

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 4.2: Private Profile - Search Visibility

**Steps**:
1. Set profile to private and save
2. Login as different user (admin / AdminPass123!)
3. Search for "testuser"
4. Observe search results

**Expected Results**:
- [ ] Username "testuser" appears in search
- [ ] Profile photo/avatar visible
- [ ] Bio and other details hidden or show "Private Profile" message
- [ ] "Seguir" or "Follow" button available

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 4.3: Trip Visibility Settings

**Steps**:
1. Locate "Visibilidad de Viajes" dropdown
2. Select "Solo Seguidores" (Followers Only)
3. Save changes
4. Verify setting persists after page reload
5. Login as different user (if possible)
6. Navigate to testuser's trips
7. Verify trips visibility matches setting

**Expected Results**:
- [ ] Dropdown has options: "Público", "Solo Seguidores", "Privado"
- [ ] Selected option saves successfully
- [ ] Trips visibility changes accordingly:
  - **Público**: Everyone can see trips
  - **Solo Seguidores**: Only followers see trips
  - **Privado**: Only user sees own trips

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Scenario 4.4: Privacy Changes Take Effect Immediately

**Steps**:
1. Set profile to public, save
2. Open profile in incognito window (should be visible)
3. Without closing incognito window, switch profile to private and save
4. Refresh incognito window
5. Verify profile now private

**Expected Results**:
- [ ] Changes apply immediately
- [ ] No logout required
- [ ] Refresh shows updated privacy state

**Actual Results**: ________________________________

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

## Edge Cases & Performance Testing

### Edge Case 1: Large Image Upload (10MB+)

**Steps**:
1. Attempt to upload 10MB image
2. Observe behavior

**Expected Results**:
- [ ] Upload rejected before processing
- [ ] Clear error message about 5MB limit
- [ ] No browser freeze or crash

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Edge Case 2: Concurrent Edits (Multiple Tabs)

**Steps**:
1. Open profile edit in Tab 1
2. Open profile edit in Tab 2
3. In Tab 1: Change bio to "Version 1" and save
4. In Tab 2: Change bio to "Version 2" and save
5. Refresh both tabs and check which version persisted

**Expected Results**:
- [ ] Last save wins (Version 2)
- [ ] No data corruption
- [ ] Ideally: Warning about concurrent edits or optimistic locking

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Edge Case 3: Session Expiry During Edit

**Steps**:
1. Start editing profile
2. Wait for access token to expire (15 minutes)
3. Attempt to save changes
4. Observe refresh token behavior

**Expected Results**:
- [ ] Refresh token automatically renews access token
- [ ] Save succeeds without user intervention
- [ ] No data loss

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Edge Case 4: Special Characters in Bio

**Steps**:
1. Enter bio with emojis, special characters: "🚴 ¡Hola! Ciclismo 100% 🌄 #MTB @testuser"
2. Save and verify

**Expected Results**:
- [ ] All characters save correctly
- [ ] Emojis display properly
- [ ] No encoding issues

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Edge Case 5: Slow Network - Photo Upload

**Steps**:
1. Open browser DevTools → Network tab
2. Throttle connection to "Slow 3G"
3. Upload 4MB photo
4. Observe progress indicator

**Expected Results**:
- [ ] Upload progress bar shows incremental progress
- [ ] Upload completes successfully (may take 30-60 seconds)
- [ ] No timeout errors
- [ ] User can cancel upload mid-progress

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

### Edge Case 6: Backend API Unavailable

**Steps**:
1. Stop backend server
2. Attempt to save profile changes
3. Observe error handling

**Expected Results**:
- [ ] Clear error message: "Error de conexión. Intenta nuevamente."
- [ ] No crash or silent failure
- [ ] Form data preserved so user can retry

**Status**: ⬜ Pass  ⬜ Fail  ⬜ Blocked

---

## Success Criteria Verification

### SC-001: Profile Edit Speed (<2 minutes)

**Test**: Time how long it takes to complete bio, location, cycling type edit and save.

- [ ] Completed in under 2 minutes

---

### SC-002: Photo Upload Speed (<30 seconds)

**Test**: Time photo upload and crop on average network (no throttling).

- [ ] Completed in under 30 seconds

---

### SC-003: Password Change Speed (<10 seconds)

**Test**: Time password change from click to success toast.

- [ ] Completed in under 10 seconds

---

### SC-007: Form Validation Speed (<500ms)

**Test**: Use DevTools Performance tab to measure validation feedback delay.

- [ ] Validation feedback appears within 500ms

---

### SC-008: Unsaved Changes Warning (100%)

**Test**: Attempt navigation with unsaved changes 5 times.

- [ ] Warning appears 5/5 times (100%)

---

### SC-010: Page Load Speed (<2 seconds)

**Test**: Measure profile edit page load time with DevTools Network tab.

- [ ] Page fully loads in under 2 seconds

---

### SC-012: Mobile Touch-Friendly Interface

**Test**: Open on mobile device or Chrome DevTools mobile emulation.

- [ ] All buttons tappable (min 44x44px)
- [ ] Forms usable on small screens
- [ ] Photo crop works with touch gestures

---

## Summary & Sign-Off

**Total Tests Executed**: ______
**Tests Passed**: ______
**Tests Failed**: ______
**Tests Blocked**: ______

**Pass Rate**: ______%

**Critical Issues Found**:
1. ________________________________
2. ________________________________
3. ________________________________

**Recommendations**:
- ________________________________
- ________________________________

**Tester Signature**: ________________  **Date**: ________

**Status**: ⬜ Ready for Production  ⬜ Needs Fixes  ⬜ Major Issues
