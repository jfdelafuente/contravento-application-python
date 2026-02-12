# Authentication Endpoints

API endpoints for user authentication and authorization.

**OpenAPI Contract**: [auth.yaml](../contracts/auth.yaml)

---

## Table of Contents

- [POST /auth/register](#post-authregister)
- [POST /auth/login](#post-authlogin)
- [POST /auth/refresh](#post-authrefresh)
- [POST /auth/logout](#post-authlogout)
- [POST /auth/verify-email](#post-authverify-email)
- [POST /auth/forgot-password](#post-authforgot-password)
- [POST /auth/reset-password](#post-authreset-password)

---

## POST /auth/register

Register a new user account.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "cycling_type": "road",
  "location": "Madrid, España"
}
```

**Response (201 Created)**:
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

**Validation**:
- Username: 3-30 chars, alphanumeric + underscore
- Email: Valid format, unique
- Password: ≥8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char

**Errors**:
- `400` - Email already exists, weak password
- `422` - Invalid request body

---

## POST /auth/login

Authenticate user and receive JWT tokens.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "error": null
}
```

**Token Lifetimes**:
- Access token: 15 minutes
- Refresh token: 30 days

**Rate Limiting**:
- Max 5 failed attempts per email
- 15-minute lockout after 5 failures

**Errors**:
- `401` - Invalid credentials
- `403` - Account not verified
- `429` - Rate limit exceeded

---

## POST /auth/refresh

Obtain new access token using refresh token.

**Authentication**: Bearer token (refresh token)

**Request Headers**:
```
Authorization: Bearer {refresh_token}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "error": null
}
```

**Notes**:
- Old refresh token is invalidated
- Token rotation prevents replay attacks

**Errors**:
- `401` - Invalid or expired refresh token
- `403` - Refresh token revoked

---

## POST /auth/logout

End user session and invalidate refresh token.

**Authentication**: Bearer token (access token)

**Request Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Sesión cerrada correctamente"
  },
  "error": null
}
```

**Notes**:
- Refresh token added to revocation list
- Access token remains valid until expiration (max 15 min)

**Errors**:
- `401` - Invalid or missing access token

---

## POST /auth/verify-email

Verify user email address using verification token.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "token": "verification-token-from-email"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Email verificado correctamente",
    "is_verified": true
  },
  "error": null
}
```

**Errors**:
- `400` - Invalid or expired verification token
- `404` - User not found

---

## POST /auth/forgot-password

Request password reset email.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Si el email existe, recibirás instrucciones para restablecer tu contraseña"
  },
  "error": null
}
```

**Notes**:
- Always returns 200 OK (prevents email enumeration)
- Reset token valid for 1 hour

---

## POST /auth/reset-password

Reset password using reset token from email.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Contraseña restablecida correctamente"
  },
  "error": null
}
```

**Errors**:
- `400` - Invalid or expired reset token
- `400` - Weak password (validation failure)

---

## Related Documentation

- **[Authentication Guide](../authentication.md)** - JWT token flow and best practices
- **[OpenAPI Contract](../contracts/auth.yaml)** - Full auth API schema
- **[Manual Testing](../testing/manual-testing.md)** - curl examples
- **[Postman Guide](../testing/postman-guide.md)** - Postman collection

---

**Last Updated**: 2026-02-06
**API Version**: 1.0.0
