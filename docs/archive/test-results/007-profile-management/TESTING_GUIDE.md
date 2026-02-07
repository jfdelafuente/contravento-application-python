# Quick Testing Guide - Feature 007: Profile Management

## Overview

This guide helps you quickly test the Profile Management feature. For detailed test cases, see [MANUAL_TESTING.md](./MANUAL_TESTING.md).

---

## Setup (5 minutes)

### 1. Start Servers

**Backend**:
```bash
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd frontend
npm run dev
# Should start on http://localhost:3001
```

### 2. Test Credentials

- **Test User**: `testuser` / `TestPass123!`
- **Admin User**: `admin` / `AdminPass123!`

### 3. Prepare Test Files

Download or create:
- ✅ Valid JPG image (2-3MB) for photo upload
- ✅ Valid PNG image (2-3MB) for photo upload
- ❌ Large image (7MB+) to test size limit
- ❌ Invalid format (GIF or BMP) to test format validation

---

## Quick Smoke Test (10 minutes)

This covers the most critical paths to verify basic functionality works.

### ✅ Test 1: Login & Navigation (2 min)
1. Open http://localhost:3001
2. Login as `testuser` / `TestPass123!`
3. Navigate to profile page
4. Click "Editar Perfil" button
5. **Expected**: Edit page loads with all sections visible

---

### ✅ Test 2: Edit Bio & Save (2 min)
1. On edit profile page, find "Biografía" field
2. Clear existing content
3. Type: "Soy un ciclista de Barcelona apasionado por las rutas de montaña"
4. Watch character counter update
5. Click "Guardar Cambios"
6. **Expected**:
   - ✅ Success toast appears
   - ✅ Character counter shows correct count
   - ✅ Navigate to profile and bio displays correctly

---

### ✅ Test 3: Upload Profile Photo (3 min)
1. Click on profile photo area
2. Select "Cambiar Foto"
3. Upload valid JPG image (under 5MB)
4. **Expected**: Crop modal opens
5. Adjust crop area by dragging
6. Adjust zoom slider
7. Click "Guardar" button
8. **Expected**:
   - ✅ Upload progress shows (if >1s)
   - ✅ Success toast appears
   - ✅ Photo displays immediately in circular format
   - ✅ Navigate to profile and photo is visible

---

### ✅ Test 4: Change Password (2 min)
1. Scroll to "Cambiar Contraseña" section
2. Enter current password: `TestPass123!`
3. Enter new password: `NewPass456!`
4. Confirm new password: `NewPass456!`
5. Click "Cambiar Contraseña"
6. **Expected**: Success toast appears
7. Logout and login with new password
8. **Expected**: Login succeeds
9. **IMPORTANT**: Change password back to `TestPass123!`

---

### ✅ Test 5: Privacy Toggle (1 min)
1. Find "Perfil Privado" toggle
2. Click to enable private profile
3. Click "Guardar Cambios"
4. **Expected**: Success toast appears
5. Open incognito window
6. Navigate to http://localhost:3001/profile/testuser (without login)
7. **Expected**: Profile details hidden or "Private Profile" message

---

## Critical Error Checks (5 minutes)

Test that validations work correctly.

### ❌ Test 6: Validation Errors

**6a. Bio Too Long**:
- Enter 600 characters in bio field
- **Expected**: Error message, cannot save

**6b. Password Too Short**:
- Try new password: `Short1`
- **Expected**: Validation error about 8 character minimum

**6c. Photo Too Large**:
- Upload 7MB+ image
- **Expected**: Error message about 5MB limit

**6d. Invalid Photo Format**:
- Upload .gif or .bmp file
- **Expected**: Rejection with format error

---

## Browser Console Check

Open DevTools (F12) and check:

- ✅ No console errors (red messages)
- ✅ Network requests return 200/201 status (not 401, 404, 500)
- ✅ No CORS errors

---

## Common Issues & Solutions

### Issue: "401 Unauthorized" errors
**Solution**:
- Check access_token in localStorage
- Try logout and login again
- Verify backend is running on port 8000

### Issue: Photo upload fails silently
**Solution**:
- Check if Toaster component is mounted in App.tsx
- Verify backend endpoint: POST /users/{username}/profile/photo
- Check file size is under 5MB

### Issue: Form doesn't save
**Solution**:
- Check browser console for errors
- Verify backend is running
- Check network tab for failed requests

### Issue: "Guardar" button not visible in crop modal
**Solution**:
- Scroll down in modal
- Check if modal height is 300px (not 400px)
- Verify buttons have flex-shrink: 0 in CSS

---

## Success Criteria Checklist

After testing, verify these performance targets:

- [ ] **SC-001**: Profile edit completes in <2 minutes
- [ ] **SC-002**: Photo upload and crop in <30 seconds
- [ ] **SC-003**: Password change in <10 seconds
- [ ] **SC-007**: Validation feedback appears in <500ms
- [ ] **SC-008**: Unsaved changes warning works 100% of time
- [ ] **SC-010**: Page loads in <2 seconds

---

## Test Report Template

After testing, record results:

```
FEATURE 007 - PROFILE MANAGEMENT TEST REPORT
Date: ___________
Tester: ___________

SMOKE TESTS:
✅ / ❌  Test 1: Login & Navigation
✅ / ❌  Test 2: Edit Bio & Save
✅ / ❌  Test 3: Upload Profile Photo
✅ / ❌  Test 4: Change Password
✅ / ❌  Test 5: Privacy Toggle

VALIDATION TESTS:
✅ / ❌  Test 6a: Bio Too Long
✅ / ❌  Test 6b: Password Too Short
✅ / ❌  Test 6c: Photo Too Large
✅ / ❌  Test 6d: Invalid Photo Format

CRITICAL ISSUES FOUND:
1. ________________________________
2. ________________________________
3. ________________________________

OVERALL STATUS:
⬜ Ready for Production
⬜ Minor Issues (fix before deploy)
⬜ Major Issues (needs rework)
```

---

## Next Steps

1. Complete smoke tests (10 min)
2. Complete error validation tests (5 min)
3. If all pass → Run full test suite in [MANUAL_TESTING.md](./MANUAL_TESTING.md)
4. If issues found → Document and fix
5. Repeat until all tests pass

For detailed test scenarios and edge cases, see [MANUAL_TESTING.md](./MANUAL_TESTING.md).
