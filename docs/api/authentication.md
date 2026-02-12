# Authentication - ContraVento API

Comprehensive guide to JWT-based authentication in ContraVento.

## Table of Contents

- [Overview](#overview)
- [JWT Token Flow](#jwt-token-flow)
- [Authentication Endpoints](#authentication-endpoints)
- [Using Access Tokens](#using-access-tokens)
- [Token Refresh](#token-refresh)
- [Security Best Practices](#security-best-practices)
- [Error Handling](#error-handling)

---

## Overview

ContraVento uses **JWT (JSON Web Tokens)** for authentication with a dual-token system:

- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (30 days), used to obtain new access tokens

**Why dual tokens?**
- Access tokens expire quickly for security (reduced risk if stolen)
- Refresh tokens allow seamless re-authentication without re-login
- Refresh tokens can be revoked server-side (logout, security breach)

---

## JWT Token Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User Login                                                │
├──────────────────────────────────────────────────────────────┤
│ POST /auth/login                                             │
│ { "email": "user@example.com", "password": "..." }           │
│                                                              │
│ Response:                                                    │
│ {                                                            │
│   "access_token": "eyJ...",  ← Use for API requests         │
│   "refresh_token": "eyJ...", ← Store for renewal            │
│   "expires_in": 900          ← 15 minutes                   │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. Authenticated API Requests                                │
├──────────────────────────────────────────────────────────────┤
│ GET /trips                                                   │
│ Authorization: Bearer {access_token}                         │
│                                                              │
│ ✅ Valid token → 200 OK with data                            │
│ ❌ Expired token → 401 Unauthorized                          │
└──────────────────────────────────────────────────────────────┘
                        ↓ (when access token expires)
┌──────────────────────────────────────────────────────────────┐
│ 3. Token Refresh (automatic or manual)                      │
├──────────────────────────────────────────────────────────────┤
│ POST /auth/refresh                                           │
│ Authorization: Bearer {refresh_token}                        │
│                                                              │
│ Response:                                                    │
│ {                                                            │
│   "access_token": "eyJ...",  ← New access token             │
│   "refresh_token": "eyJ...", ← New refresh token            │
│   "expires_in": 900                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. Logout                                                    │
├──────────────────────────────────────────────────────────────┤
│ POST /auth/logout                                            │
│ Authorization: Bearer {access_token}                         │
│                                                              │
│ ✅ Refresh token invalidated server-side                     │
│ ✅ Client clears tokens from storage                         │
└──────────────────────────────────────────────────────────────┘
```

---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "cycling_type": "road",
  "location": "Madrid, España"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "john@example.com",
    "is_verified": false,
    "created_at": "2024-06-01T12:00:00Z"
  },
  "error": null
}
```

**Validation Requirements:**
- **Username**: 3-30 chars, alphanumeric + underscore
- **Email**: Valid email format, unique
- **Password**: ≥8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
- **Cycling Type**: One of: road, mountain, gravel, bikepacking, touring, commuting, BMX, track

**Errors:**
- `400` - Validation error (email already exists, weak password)
- `422` - Invalid request body

---

### POST /auth/login

Authenticate and receive JWT tokens.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "error": null
}
```

**JWT Claims** (decoded access token):
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",  // user_id
  "type": "access",
  "iat": 1704070800,   // Issued at (Unix timestamp)
  "exp": 1704071700    // Expires at (Unix timestamp, 15 min later)
}
```

**Errors:**
- `401` - Invalid credentials
- `403` - Account not verified (email verification required)
- `429` - Rate limit exceeded (5 attempts, 15 min lockout)

**Rate Limiting:**
- Max 5 failed login attempts per email
- 15-minute lockout after 5 failures
- Counter resets on successful login

---

### POST /auth/refresh

Obtain new access and refresh tokens using a valid refresh token.

**Request Headers:**
```
Authorization: Bearer {refresh_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",  // New access token
    "refresh_token": "eyJ...", // New refresh token (old one invalidated)
    "token_type": "bearer",
    "expires_in": 900
  },
  "error": null
}
```

**JWT Claims** (decoded refresh token):
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",  // user_id
  "type": "refresh",
  "iat": 1704070800,
  "exp": 1706662800    // Expires in 30 days
}
```

**Errors:**
- `401` - Invalid or expired refresh token
- `403` - Refresh token revoked (logout, security breach)

**Security Notes:**
- Old refresh token is invalidated after successful refresh
- Refresh token rotation prevents token replay attacks
- Server maintains a revocation list for logged-out tokens

---

### POST /auth/logout

Invalidate refresh token and end session.

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Sesión cerrada correctamente"
  },
  "error": null
}
```

**What happens on logout:**
1. Server adds refresh token to revocation list
2. Client clears tokens from storage (localStorage, cookies)
3. Access token remains valid until expiration (15 min max)
4. Subsequent refresh attempts with old token fail with 403

**Errors:**
- `401` - Invalid or missing access token

---

## Using Access Tokens

### In HTTP Requests

**Header Format:**
```
Authorization: Bearer {access_token}
```

**Example (curl):**
```bash
curl -X GET "http://localhost:8000/trips" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example (JavaScript/Axios):**
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Set authorization header globally
api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

// Or per-request
const response = await api.get('/trips', {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});
```

---

### Token Storage

**Frontend (Web):**
```javascript
// Store tokens securely
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
localStorage.setItem('token_expires_at', Date.now() + data.expires_in * 1000);

// Retrieve tokens
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

// Clear tokens on logout
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('token_expires_at');
```

**Alternative (HttpOnly Cookies):**
```javascript
// Server sets cookie (more secure, XSS-proof)
// Set-Cookie: access_token={token}; HttpOnly; Secure; SameSite=Strict
// Browser automatically includes cookie in requests
```

**Mobile (React Native):**
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Store tokens
await AsyncStorage.setItem('@access_token', data.access_token);
await AsyncStorage.setItem('@refresh_token', data.refresh_token);

// Retrieve tokens
const accessToken = await AsyncStorage.getItem('@access_token');
```

---

## Token Refresh

### Manual Refresh

```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');

  const response = await fetch('http://localhost:8000/auth/refresh', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${refreshToken}`,
    },
  });

  const data = await response.json();

  if (data.success) {
    localStorage.setItem('access_token', data.data.access_token);
    localStorage.setItem('refresh_token', data.data.refresh_token);
    localStorage.setItem('token_expires_at', Date.now() + data.data.expires_in * 1000);
  } else {
    // Refresh failed - redirect to login
    window.location.href = '/login';
  }
}
```

### Automatic Refresh with Axios Interceptor

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Request interceptor: Add access token
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Retry with refreshed token on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt token refresh
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:8000/auth/refresh',
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          }
        );

        const { access_token, refresh_token } = response.data.data;

        // Update stored tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

## Security Best Practices

### Password Requirements

**Enforced by backend:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

**Hashing:**
- Bcrypt with 12 rounds (production)
- Bcrypt with 4 rounds (tests only - faster)

**Example validation:**
```python
# Backend (src/utils/validators.py)
def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe tener al menos una mayúscula")
    if not re.search(r"[a-z]", password):
        raise ValueError("La contraseña debe tener al menos una minúscula")
    if not re.search(r"[0-9]", password):
        raise ValueError("La contraseña debe tener al menos un número")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
        raise ValueError("La contraseña debe tener al menos un carácter especial")
```

---

### Token Security

**Access Token Best Practices:**
- Short expiration (15 minutes)
- Never store in URL query params (visible in logs)
- Use HTTPS only in production
- Include minimal claims (user_id, type, exp)

**Refresh Token Best Practices:**
- Long expiration (30 days) but revocable
- Store in HttpOnly cookies (preferred) or secure storage
- Rotate on each refresh (invalidate old token)
- Maintain server-side revocation list

**Transmission:**
- Always use `Authorization: Bearer` header
- Never pass tokens in URL query parameters
- Never log tokens server-side (redact in logs)

---

### CORS Configuration

**Allowed Origins** (production):
```python
# backend/src/config.py
CORS_ORIGINS = [
    "https://contravento.com",
    "https://www.contravento.com",
    "https://app.contravento.com",
]
```

**Allowed Origins** (development):
```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative frontend
]
```

**Credentials:**
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Error Handling

### Error Response Format

All authentication errors return a standardized JSON response:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensaje descriptivo en español",
    "field": "email"  // Optional: field that caused error
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Message | Cause |
|-------------|------------|---------|-------|
| 400 | `VALIDATION_ERROR` | "El email ya está registrado" | Duplicate email |
| 400 | `VALIDATION_ERROR` | "La contraseña no cumple los requisitos" | Weak password |
| 401 | `UNAUTHORIZED` | "Credenciales inválidas" | Wrong email/password |
| 401 | `UNAUTHORIZED` | "Token inválido o expirado" | Expired access token |
| 403 | `FORBIDDEN` | "Cuenta no verificada" | Email not verified |
| 403 | `FORBIDDEN` | "Refresh token revocado" | Token revoked (logout) |
| 429 | `RATE_LIMIT_EXCEEDED` | "Demasiados intentos de login. Intenta de nuevo en 15 minutos." | Rate limit hit |

### Example Error Handling (Frontend)

```javascript
try {
  const response = await api.post('/auth/login', {
    email: 'test@example.com',
    password: 'WrongPassword123!',
  });
} catch (error) {
  if (error.response?.status === 401) {
    // Invalid credentials
    alert(error.response.data.error.message);
  } else if (error.response?.status === 429) {
    // Rate limit exceeded
    alert('Demasiados intentos. Espera 15 minutos.');
  } else {
    // Generic error
    alert('Error al iniciar sesión. Intenta de nuevo.');
  }
}
```

---

## Related Documentation

- **[API Overview](README.md)** - API documentation hub
- **[Endpoint Reference: Auth](endpoints/auth.md)** - Detailed auth endpoint specs
- **[OpenAPI Contract: Auth](contracts/auth.yaml)** - Auth API schema
- **[Manual Testing](testing/manual-testing.md)** - curl command examples
- **[Postman Guide](testing/postman-guide.md)** - Postman/Insomnia setup

---

**Last Updated**: 2026-02-06
**API Version**: 1.0.0
**Security**: JWT with dual-token system (access + refresh)
