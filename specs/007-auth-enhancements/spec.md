# Feature Specification: Better Auth Integration & Enhanced Authentication

**Feature Branch**: `007-auth-enhancements`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "Update/enhance existing authentication system with Better Auth framework, adding refresh tokens, password reset, email verification, session management, and improved security"

## Executive Summary

This specification outlines enhancements to the existing JWT-based authentication system by integrating Better Auth framework features and implementing missing critical authentication flows. The current system has basic login/register functionality with JWT tokens, but lacks refresh tokens, password reset, email verification, session management, and several security best practices outlined in the Better Auth specification.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Refresh Token Flow (Priority: P1)

Users can maintain authenticated sessions beyond the 30-minute access token expiration using secure refresh tokens, enabling seamless app usage without frequent re-logins.

**Why this priority**: Refresh tokens are CRITICAL for production applications. Without them, users are logged out every 30 minutes, creating terrible UX. This is the highest priority enhancement for authentication.

**Independent Test**: Can be fully tested by logging in, waiting for access token to expire (or manually invalidating), then making an API request that automatically uses refresh token to get new access token without re-login. Delivers persistent session value.

**Acceptance Scenarios**:

1. **Given** I log in successfully, **When** I receive authentication tokens, **Then** I receive both access_token (30min expiry) and refresh_token (7d expiry)
2. **Given** my access token expires, **When** I make an API request, **Then** the frontend automatically calls /api/auth/refresh with refresh token and gets new access token
3. **Given** I have a valid refresh token, **When** I call /api/auth/refresh, **Then** I receive new access_token and new refresh_token (token rotation)
4. **Given** my refresh token expires, **When** I attempt to refresh, **Then** I receive 401 Unauthorized and must log in again
5. **Given** I refresh my token, **When** token rotation occurs, **Then** old refresh token is invalidated (can't be reused)
6. **Given** I log out, **When** logout endpoint is called, **Then** refresh token is revoked/blacklisted in sessions table

---

### User Story 2 - Password Reset Flow (Priority: P1)

Users can securely reset forgotten passwords via email link with time-limited reset tokens, enabling account recovery without contacting support.

**Why this priority**: Password reset is ESSENTIAL for production applications. Users forget passwords frequently, and this is the primary self-service recovery method. Critical for reducing support burden and user frustration.

**Independent Test**: Can be fully tested by requesting password reset with email, receiving reset link via email, clicking link (or using reset token), submitting new password, and successfully logging in with new password. Delivers account recovery value.

**Acceptance Scenarios**:

1. **Given** I forgot my password, **When** I submit /api/auth/forgot-password with my email, **Then** I receive 200 OK and password reset email is sent (always returns success even if email doesn't exist - security)
2. **Given** I receive password reset email, **When** I click the reset link, **Then** I'm directed to password reset form with valid reset token
3. **Given** I have a valid reset token, **When** I submit /api/auth/reset-password with token and new password, **Then** my password is updated and old password no longer works
4. **Given** reset token was issued 2 hours ago, **When** I attempt to use it, **Then** I receive error "Reset token expired. Request a new one."
5. **Given** I use a reset token to change password, **When** I attempt to reuse the same token, **Then** I receive error "Reset token already used" (single-use tokens)
6. **Given** I request password reset 4 times in 1 hour, **When** rate limit is reached, **Then** I receive 429 Too Many Requests (3 attempts per hour per email)

---

### User Story 3 - Email Verification System (Priority: P2)

New users receive verification emails and must verify their email address before accessing certain features, reducing spam accounts and ensuring valid email addresses.

**Why this priority**: Email verification is IMPORTANT for production but not blocking MVP. It improves account quality and enables email-based features, but users can still access core functionality without it in MVP.

**Independent Test**: Can be fully tested by registering new account, receiving verification email, clicking verification link, and seeing account marked as verified. Delivers spam prevention and email validation value.

**Acceptance Scenarios**:

1. **Given** I register a new account, **When** registration completes, **Then** I receive verification email with verification link
2. **Given** I registered but haven't verified email, **When** I log in, **Then** I can access the app but see "Verify your email" banner
3. **Given** I click verification link in email, **When** /api/auth/verify-email is called with token, **Then** my email_verified flag is set to true
4. **Given** my email is not verified, **When** I attempt certain actions (future: team invites, password reset), **Then** I'm prompted to verify email first
5. **Given** verification token was sent 25 hours ago, **When** I attempt to use it, **Then** I receive error "Verification link expired. Resend verification email."
6. **Given** I didn't receive verification email, **When** I click "Resend verification email", **Then** new verification email is sent with fresh token

---

### User Story 4 - Session Management Dashboard (Priority: P3)

Users can view all active sessions (devices, locations, last activity) and revoke sessions remotely, enabling security monitoring and device management.

**Why this priority**: Session management is VALUABLE for security-conscious users and multi-device scenarios, but not critical for MVP. Nice-to-have feature for production.

**Independent Test**: Can be fully tested by logging in from 2 different devices, viewing session list showing both devices, revoking one session, and confirming that device is logged out. Delivers multi-device security value.

**Acceptance Scenarios**:

1. **Given** I'm logged in from multiple devices, **When** I view /api/auth/sessions, **Then** I see list of active sessions with device info, IP, and last activity
2. **Given** I see suspicious session, **When** I click "Revoke session", **Then** that session's refresh token is invalidated and device is logged out
3. **Given** I revoke a session, **When** that device attempts API request, **Then** it receives 401 Unauthorized and must log in again
4. **Given** I view my sessions, **When** I click "Revoke all other sessions", **Then** all sessions except current are revoked
5. **Given** session has been inactive for 30 days, **When** automatic cleanup runs, **Then** old session is automatically removed from sessions table

---

### User Story 5 - Secure Token Storage (HttpOnly Cookies) (Priority: P1)

Authentication tokens are stored in HttpOnly, Secure, SameSite cookies instead of localStorage, preventing XSS attacks from stealing tokens.

**Why this priority**: Cookie-based token storage is a CRITICAL security enhancement. localStorage is vulnerable to XSS attacks. HttpOnly cookies provide much better security. This is essential for production.

**Independent Test**: Can be fully tested by logging in, inspecting browser cookies (not localStorage), confirming access_token and refresh_token are in HttpOnly cookies, and verifying XSS scripts cannot read cookies. Delivers XSS protection value.

**Acceptance Scenarios**:

1. **Given** I log in successfully, **When** tokens are issued, **Then** access_token and refresh_token are set as HttpOnly, Secure, SameSite=Strict cookies (not localStorage)
2. **Given** tokens are in cookies, **When** I make API request, **Then** cookies are automatically sent via browser, no manual Authorization header needed
3. **Given** attacker injects XSS script, **When** script attempts to read cookies, **Then** HttpOnly attribute prevents access (cookies invisible to JavaScript)
4. **Given** I'm on HTTPS site, **When** cookies are set, **Then** Secure attribute ensures cookies only sent over HTTPS
5. **Given** I log out, **When** logout completes, **Then** cookies are cleared (deleted from browser)
6. **Given** I close browser and reopen, **When** refresh token cookie is valid, **Then** I remain logged in (persistent sessions)

---

### User Story 6 - Rate Limiting on Auth Endpoints (Priority: P2)

Authentication endpoints have rate limiting to prevent brute-force attacks, credential stuffing, and abuse.

**Why this priority**: Rate limiting is IMPORTANT for security in production but not blocking MVP. It prevents common attacks but core functionality works without it initially.

**Independent Test**: Can be fully tested by attempting 10 login requests in 30 seconds, receiving 429 Too Many Requests after 5th attempt, waiting 15 minutes, and successfully attempting login again. Delivers brute-force protection value.

**Acceptance Scenarios**:

1. **Given** I attempt login 6 times in 5 minutes, **When** rate limit is reached (5 per 15 min per IP), **Then** I receive 429 Too Many Requests
2. **Given** I'm rate limited on login, **When** I wait 15 minutes, **Then** rate limit resets and I can attempt login again
3. **Given** I attempt registration 4 times in 1 hour, **When** rate limit is reached (3 per hour per IP), **Then** I receive 429 Too Many Requests
4. **Given** I request password reset 4 times in 1 hour, **When** rate limit is reached (3 per hour per email), **Then** I receive 429 Too Many Requests
5. **Given** rate limit is reached, **When** error is returned, **Then** response includes Retry-After header with seconds until rate limit resets

---

### User Story 7 - User Profile Update (Priority: P3)

Authenticated users can update their profile information (name, email) with proper validation and re-authentication for sensitive changes.

**Why this priority**: Profile updates are USEFUL but not critical for MVP. Users can function with initial registration data. Nice-to-have for production.

**Independent Test**: Can be fully tested by logging in, updating name to "Jane Doe", receiving success response, and seeing updated name in profile and /api/auth/me response. Delivers profile management value.

**Acceptance Scenarios**:

1. **Given** I'm authenticated, **When** I PATCH /api/auth/profile with {"name": "Jane Doe"}, **Then** my name is updated and I receive 200 OK with updated user
2. **Given** I want to change email, **When** I submit new email, **Then** verification email is sent to new address (email not changed until verified)
3. **Given** I verify new email, **When** verification completes, **Then** email is updated and I receive confirmation
4. **Given** I'm not authenticated, **When** I attempt to update profile, **Then** I receive 401 Unauthorized
5. **Given** I submit invalid data (email format), **When** validation runs, **Then** I receive 422 Unprocessable Entity with validation errors

---

### Edge Cases

- **What happens when** user has 10+ active sessions (multiple devices, browsers)?
  - System allows unlimited sessions per user in MVP; sessions table handles large numbers efficiently; old sessions auto-expire after 7 days

- **What happens when** refresh token is used exactly at expiration timestamp (race condition)?
  - Token validation checks exp claim; if expired at time of check, returns 401; user must re-login; no grace period to avoid security issues

- **What happens when** user requests password reset but changes password via another reset link first?
  - All pending reset tokens for that user are invalidated when password changes; attempting to use old token returns "Invalid or expired token"

- **What happens when** user logs in from new device while at maximum session limit (future feature)?
  - In MVP, no session limit; future: oldest session is auto-revoked to make room for new session; user receives email notification

- **What happens when** attacker obtains refresh token from database dump?
  - Refresh tokens are hashed (bcrypt) in sessions table; attacker can't use them without plain token; plain tokens only stored in HttpOnly cookies (never logs, never responses except initial login)

- **What happens when** user's refresh token cookie is stolen via MITM (HTTP, not HTTPS)?
  - Secure cookie flag prevents transmission over HTTP; SameSite=Strict prevents CSRF; HTTPS enforced in production; if stolen, user can revoke session from session management dashboard

- **What happens when** password reset email doesn't arrive (spam folder, email service down)?
  - "Resend verification email" button available after 60 seconds; rate limited to 3 per hour; always returns success (even if email doesn't exist - security)

- **What happens when** user clicks expired password reset link?
  - Backend validates exp timestamp; if expired (>24hrs old), returns 400 Bad Request with "Reset token expired. Request a new password reset."; frontend redirects to forgot-password page

- **What happens when** two users attempt to register with same email simultaneously?
  - Database unique constraint on email column prevents duplicates; second request returns 400 Bad Request "Email already registered"; race condition handled at DB level

- **What happens when** user changes password while logged in on multiple devices?
  - All existing sessions remain valid (refresh tokens not invalidated by password change in MVP); future: option to "log out all other devices" after password change

## Requirements *(mandatory)*

### Functional Requirements

#### Refresh Token System (FR-AUTH-001 to FR-AUTH-015)

- **FR-AUTH-001**: System MUST issue both access_token (30min expiry) and refresh_token (7 day expiry) on successful login
- **FR-AUTH-002**: System MUST store refresh_token hash (bcrypt) in sessions table with user_id, expires_at, ip_address, user_agent
- **FR-AUTH-003**: System MUST provide /api/auth/refresh endpoint accepting refresh_token to issue new access_token + new refresh_token
- **FR-AUTH-004**: System MUST implement token rotation: old refresh_token is invalidated when new tokens are issued
- **FR-AUTH-005**: System MUST validate refresh_token signature, expiration, and existence in sessions table before issuing new tokens
- **FR-AUTH-006**: System MUST revoke refresh_token from sessions table on logout
- **FR-AUTH-007**: System MUST use HttpOnly, Secure, SameSite=Strict cookies for storing access_token and refresh_token (not localStorage)
- **FR-AUTH-008**: Frontend MUST automatically call /api/auth/refresh when access_token expires (401 interceptor)
- **FR-AUTH-009**: Frontend MUST retry failed request with new access_token after successful refresh
- **FR-AUTH-010**: System MUST return 401 Unauthorized if refresh_token is expired or revoked (require re-login)
- **FR-AUTH-011**: System MUST clean up expired sessions from sessions table (cron job or on-access cleanup)
- **FR-AUTH-012**: System MUST prevent refresh_token reuse: after refresh, old token becomes invalid immediately
- **FR-AUTH-013**: Sessions table MUST track: id, user_id, refresh_token_hash, expires_at, created_at, ip_address, user_agent
- **FR-AUTH-014**: System MUST create new session record on login, delete on logout
- **FR-AUTH-015**: System MUST support multiple concurrent sessions per user (different devices)

#### Password Reset Flow (FR-AUTH-016 to FR-AUTH-028)

- **FR-AUTH-016**: System MUST provide /api/auth/forgot-password endpoint accepting email
- **FR-AUTH-017**: System MUST generate secure random reset token (uuid4 or cryptographic random) on password reset request
- **FR-AUTH-018**: System MUST store reset_token hash (bcrypt) in password_reset_tokens table with user_id, expires_at (24 hours)
- **FR-AUTH-019**: System MUST send password reset email with reset link containing plain token
- **FR-AUTH-020**: System MUST always return 200 OK for forgot-password (security: don't reveal if email exists)
- **FR-AUTH-021**: System MUST provide /api/auth/reset-password endpoint accepting token and new_password
- **FR-AUTH-022**: System MUST validate reset token: signature valid, not expired (24hrs), not already used, user exists
- **FR-AUTH-023**: System MUST mark reset token as "used" after successful password change (single-use tokens)
- **FR-AUTH-024**: System MUST hash new password with bcrypt before updating user.hashed_password
- **FR-AUTH-025**: System MUST invalidate all pending reset tokens for user when password changes
- **FR-AUTH-026**: System MUST rate limit forgot-password: 3 requests per hour per email address
- **FR-AUTH-027**: Password reset tokens table MUST track: id, user_id, token_hash, expires_at, created_at, used (boolean)
- **FR-AUTH-028**: System MUST clean up expired/used reset tokens (older than 48 hours)

#### Email Verification System (FR-AUTH-029 to FR-AUTH-039)

- **FR-AUTH-029**: System MUST add email_verified boolean field to users table (default: false)
- **FR-AUTH-030**: System MUST send verification email with verification link on user registration
- **FR-AUTH-031**: System MUST generate secure verification token (uuid4) and store hash in email_verification_tokens table
- **FR-AUTH-032**: System MUST provide /api/auth/verify-email endpoint accepting verification token
- **FR-AUTH-033**: System MUST validate verification token: not expired (24hrs), user exists, not already verified
- **FR-AUTH-034**: System MUST set user.email_verified = true on successful verification
- **FR-AUTH-035**: System MUST delete verification token after successful verification
- **FR-AUTH-036**: System MUST provide /api/auth/resend-verification endpoint for users to request new verification email
- **FR-AUTH-037**: System MUST rate limit resend-verification: 3 requests per hour per user
- **FR-AUTH-038**: Frontend MUST display "Verify your email" banner for unverified users
- **FR-AUTH-039**: System MUST allow unverified users to access core app features (verification not blocking in MVP)

#### Session Management (FR-AUTH-040 to FR-AUTH-048)

- **FR-AUTH-040**: System MUST provide /api/auth/sessions endpoint to list all active sessions for authenticated user
- **FR-AUTH-041**: Sessions endpoint MUST return: session_id, created_at, last_activity, ip_address, user_agent, is_current
- **FR-AUTH-042**: System MUST provide /api/auth/sessions/{session_id} DELETE endpoint to revoke specific session
- **FR-AUTH-043**: Revoking session MUST delete session record from sessions table (invalidates refresh_token)
- **FR-AUTH-044**: System MUST provide /api/auth/sessions/revoke-all endpoint to revoke all sessions except current
- **FR-AUTH-045**: System MUST update session.last_activity timestamp on token refresh (track active sessions)
- **FR-AUTH-046**: System MUST automatically delete sessions inactive for 30+ days (cleanup job)
- **FR-AUTH-047**: Frontend MUST display session list with device icons, last activity relative time (e.g., "2 hours ago")
- **FR-AUTH-048**: Frontend MUST confirm before revoking sessions with "Are you sure?" dialog

#### Secure Token Storage (FR-AUTH-049 to FR-AUTH-056)

- **FR-AUTH-049**: System MUST set access_token and refresh_token as HttpOnly cookies (prevent JavaScript access)
- **FR-AUTH-050**: System MUST set Secure flag on cookies in production (HTTPS only)
- **FR-AUTH-051**: System MUST set SameSite=Strict on cookies (CSRF protection)
- **FR-AUTH-052**: System MUST set appropriate cookie paths: /api for backend cookies
- **FR-AUTH-053**: Backend MUST read tokens from cookies, not Authorization header (cookie-based auth)
- **FR-AUTH-054**: Frontend MUST NOT store tokens in localStorage or sessionStorage (use cookies exclusively)
- **FR-AUTH-055**: System MUST clear cookies on logout (set expiry to past date)
- **FR-AUTH-056**: Frontend MUST handle CORS with credentials: true (allow cookies in cross-origin requests)

#### Rate Limiting (FR-AUTH-057 to FR-AUTH-063)

- **FR-AUTH-057**: System MUST rate limit /api/auth/login: 5 attempts per 15 minutes per IP address
- **FR-AUTH-058**: System MUST rate limit /api/auth/register: 3 attempts per hour per IP address
- **FR-AUTH-059**: System MUST rate limit /api/auth/forgot-password: 3 attempts per hour per email address
- **FR-AUTH-060**: System MUST rate limit /api/auth/resend-verification: 3 attempts per hour per user
- **FR-AUTH-061**: System MUST return 429 Too Many Requests when rate limit exceeded
- **FR-AUTH-062**: System MUST include Retry-After header in 429 response (seconds until rate limit resets)
- **FR-AUTH-063**: Rate limiting MUST use in-memory cache (Redis recommended) or database tracking

#### Profile Management (FR-AUTH-064 to FR-AUTH-069)

- **FR-AUTH-064**: System MUST provide /api/auth/profile PATCH endpoint for authenticated users to update profile
- **FR-AUTH-065**: Profile updates MUST support: name (string, 2-100 chars)
- **FR-AUTH-066**: Email changes MUST require new email verification (send verification to new email, don't update until verified)
- **FR-AUTH-067**: System MUST validate profile data: name length, email format (422 on validation failure)
- **FR-AUTH-068**: System MUST update user.updated_at timestamp on profile changes
- **FR-AUTH-069**: System MUST return updated user object on successful profile update (200 OK)

### Key Entities

- **User** (existing, enhanced):
  - New Fields:
    - email_verified (boolean, default: false)
    - last_login (timestamp, nullable)
  - Existing Fields: id, email, hashed_password, name, created_at, updated_at

- **Session** (new table):
  - id (UUID, primary key)
  - user_id (UUID, foreign key to user.id, CASCADE delete)
  - refresh_token_hash (string, bcrypt hash of plain refresh token)
  - expires_at (timestamp, 7 days from creation)
  - created_at (timestamp, session creation time)
  - last_activity (timestamp, updated on token refresh)
  - ip_address (string, 45 chars for IPv6)
  - user_agent (text, browser/device info)
  - Indexes: user_id, expires_at

- **PasswordResetToken** (new table):
  - id (UUID, primary key)
  - user_id (UUID, foreign key to user.id, CASCADE delete)
  - token_hash (string, bcrypt hash of reset token)
  - expires_at (timestamp, 24 hours from creation)
  - created_at (timestamp)
  - used (boolean, default: false, single-use enforcement)
  - Indexes: user_id, expires_at

- **EmailVerificationToken** (new table):
  - id (UUID, primary key)
  - user_id (UUID, foreign key to user.id, CASCADE delete)
  - token_hash (string, bcrypt hash of verification token)
  - expires_at (timestamp, 24 hours from creation)
  - created_at (timestamp)
  - Indexes: user_id, expires_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-AUTH-001**: Refresh token flow works in 100% of test cases (access token expires, refresh succeeds, API request retries)
- **SC-AUTH-002**: Token rotation prevents refresh token reuse in 100% of cases (old token invalid after refresh)
- **SC-AUTH-003**: Password reset flow completes successfully in 95%+ of cases (email delivered, token valid, password updated)
- **SC-AUTH-004**: Reset tokens expire after 24 hours in 100% of validation tests
- **SC-AUTH-005**: Single-use reset tokens cannot be reused in 100% of security tests
- **SC-AUTH-006**: Email verification flow completes successfully in 90%+ of cases (email delivered, token valid, verified=true)
- **SC-AUTH-007**: HttpOnly cookies prevent XSS token theft in 100% of security tests (JavaScript cannot read cookies)
- **SC-AUTH-008**: Secure cookies only transmitted over HTTPS in 100% of production scenarios
- **SC-AUTH-009**: SameSite=Strict prevents CSRF attacks in 100% of security tests
- **SC-AUTH-010**: Rate limiting blocks brute-force attacks after configured threshold (5 login attempts in 15min)
- **SC-AUTH-011**: Rate limiting returns 429 with Retry-After header in 100% of exceeded limit cases
- **SC-AUTH-012**: Session management displays all active sessions with correct device/IP info in 100% of cases
- **SC-AUTH-013**: Revoking session invalidates refresh token and logs out device in 100% of cases
- **SC-AUTH-014**: Users remain logged in after browser close/reopen in 95%+ of cases (persistent cookies)
- **SC-AUTH-015**: Zero XSS vulnerabilities in token storage (cookies inaccessible to JavaScript)
- **SC-AUTH-016**: Zero refresh token leaks in logs, error messages, or API responses (except login response)
- **SC-AUTH-017**: Token refresh latency is <500ms at p95 (fast, seamless token renewal)
- **SC-AUTH-018**: Password reset emails arrive within 2 minutes in 95%+ of cases
- **SC-AUTH-019**: Verification emails arrive within 2 minutes in 95%+ of cases
- **SC-AUTH-020**: Test coverage for auth enhancements reaches 90%+ (unit + integration tests)

## Assumptions

1. **Email Service**: System has email service configured (SMTP, SendGrid, AWS SES) for password reset and verification emails.

2. **HTTPS in Production**: Production environment uses HTTPS for all requests (required for Secure cookie flag).

3. **Database Support**: Neon PostgreSQL database supports UUID, indexes, and foreign key CASCADE delete.

4. **Better Auth Library**: Better Auth NPM package is already installed in frontend (based on existing frontend/lib/auth-server.ts).

5. **Backward Compatibility**: Enhanced auth system maintains backward compatibility with existing users (existing JWT tokens continue to work during migration).

6. **Token Secrets**: BETTER_AUTH_SECRET environment variable is properly configured and matches between frontend and backend.

7. **Cookie Domain**: Frontend and backend are on same domain or proper CORS + credentials configuration allows cookies in cross-origin requests.

8. **Browser Support**: Modern evergreen browsers with full cookie support (HttpOnly, Secure, SameSite attributes).

9. **Session Limits**: No hard limit on sessions per user in MVP (unlimited devices); future version may add limits.

10. **Email Verification Optional**: Unverified users can access core features in MVP; verification is encouraged but not required for basic functionality.

11. **Migration Strategy**: Existing logged-in users will be migrated gracefully (first refresh creates session record; localStorage tokens still work during transition).

12. **Rate Limiting Storage**: In-memory rate limiting is acceptable for MVP; production should use Redis for distributed rate limiting.

## Dependencies

### External Dependencies

1. **Neon PostgreSQL**: Cloud database for new tables (sessions, password_reset_tokens, email_verification_tokens)
   - Risk: Schema migration complexity, downtime during deployment
   - Mitigation: Test migrations on staging, use zero-downtime migration tools (Alembic)

2. **Email Service** (SendGrid, AWS SES, SMTP):
   - Risk: Email delivery failures, spam filtering, service outages
   - Mitigation: Configure SPF/DKIM records, use reputable service, implement retry logic, queue emails

3. **Better Auth NPM Package**:
   - Risk: Library version compatibility, breaking changes
   - Mitigation: Pin to specific version, test thoroughly before upgrading

4. **Redis** (future, for rate limiting):
   - Risk: Additional infrastructure complexity
   - Mitigation: Use in-memory rate limiting in MVP, migrate to Redis for production

### Internal Dependencies

1. **Current Authentication System**: Existing JWT implementation must be enhanced, not replaced
   - Backend: backend/app/auth.py, backend/app/routers/auth.py
   - Frontend: frontend/lib/auth.ts, frontend/hooks/useAuth.ts

2. **Database Models**: User model must be extended with new fields
   - File: backend/app/models.py
   - New fields: email_verified, last_login

3. **Environment Configuration**: New environment variables required
   - Backend .env: EMAIL_SERVICE_*, BETTER_AUTH_JWT_SECRET (matches frontend)
   - Frontend .env.local: BETTER_AUTH_SECRET, NEXT_PUBLIC_BETTER_AUTH_URL

4. **API Client**: Frontend API client must handle cookie-based auth
   - File: frontend/lib/api.ts
   - Update: Remove Authorization header, add credentials: 'include', handle 401 refresh retry

5. **Constitution Compliance**: All enhancements must follow project constitution
   - Security-first architecture (JWT validation, ownership verification)
   - Type safety (TypeScript strict mode, Python type hints)
   - Agent-driven development (no manual coding)
   - Documentation (PHRs, ADRs for significant decisions)

### Technical Prerequisites

1. **Database Migrations**: Alembic configured for PostgreSQL schema changes
2. **Email Templates**: HTML email templates for password reset and verification emails
3. **Cookie Configuration**: CORS configured to allow credentials (cookies) in cross-origin requests
4. **Testing Setup**: Test fixtures for sessions, reset tokens, verification tokens
5. **Better Auth Integration**: Frontend Better Auth server (auth-server.ts) properly configured

## Out of Scope

The following are explicitly **not** included in this feature specification:

1. **OAuth/Social Login**: Google, GitHub, Microsoft sign-in (Better Auth supports this, but out of scope for MVP)
2. **Two-Factor Authentication (2FA)**: TOTP, SMS codes, authenticator apps
3. **Magic Link Login**: Passwordless email-based login
4. **Biometric Authentication**: Face ID, Touch ID, fingerprint
5. **Account Deletion**: Self-service account deletion flow
6. **Password Strength Meter**: Real-time password strength feedback during registration
7. **Login History**: Detailed audit log of all login attempts (successful and failed)
8. **Suspicious Activity Alerts**: Email notifications for unusual login locations or devices
9. **Session IP/Device Details API**: Geographic location lookup from IP, device fingerprinting
10. **Remember Me**: Extended refresh token expiry (30 days instead of 7 days) with checkbox
11. **Multi-Language Email Templates**: Password reset/verification emails only in English initially
12. **Admin Session Management**: Admins viewing/revoking other users' sessions
13. **SSO/SAML**: Enterprise single sign-on integration
14. **CAPTCHA**: Bot prevention on registration/login forms (may add later if spam becomes issue)
15. **Account Recovery Questions**: Security questions for password reset alternative
16. **Email Change Workflow**: Full workflow with old email confirmation before new email verification
17. **Password History**: Prevent reuse of last N passwords
18. **Forced Password Rotation**: Require password change every 90 days
19. **Account Lockout**: Temporary account suspension after X failed login attempts

---

**Next Steps**:
- Run `/sp.plan` to create architecture and design plan for auth enhancements
- Run `/sp.clarify` if any requirements need further clarification
- Proceed with `/sp.tasks` after plan approval to generate actionable implementation tasks

---

## Related Documents

- **Parent Feature**: `specs/001-todo-full-stack-app/spec.md` (Overall todo application architecture)
- **Constitution**: `.specify/memory/constitution.md` (Project governance and security standards)
- **Auth Skill**: `.claude/skills/auth.skill.md` (JWT validation, token management patterns)
- **API Skill**: `.claude/skills/api.skill.md` (Endpoint design, error handling, validation)
- **Database Skill**: `.claude/skills/database.skill.md` (Schema design, migrations, indexes)
- **Better Auth Documentation**: Provided authentication specification (reference document)
- **Current Backend Auth**: `backend/app/auth.py`, `backend/app/routers/auth.py`
- **Current Frontend Auth**: `frontend/lib/auth.ts`, `frontend/hooks/useAuth.ts`
- **Better Auth Integration**: `backend/app/better_auth_integration.py`, `frontend/lib/auth-server.ts`
