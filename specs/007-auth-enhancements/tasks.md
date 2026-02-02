# Implementation Tasks: Better Auth Integration & Enhanced Authentication

**Feature Branch**: `007-auth-enhancements`
**Created**: 2026-01-13
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

**Task Organization**: 14 phases with 110 sequential tasks covering all 7 user stories (US1-US7).

---

## Phase 1: Setup & Environment Configuration (6 tasks)

- [X] T001 [P] [SETUP] Update backend/app/.env.example with EMAIL_* vars (SendGrid/AWS SES config keys)
- [X] T002 [P] [SETUP] Update backend/app/.env.example with REFRESH_TOKEN_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES=30, REFRESH_TOKEN_EXPIRE_DAYS=7
- [X] T003 [P] [SETUP] Update frontend/.env.local.example with NEXT_PUBLIC_COOKIE_DOMAIN, NEXT_PUBLIC_SECURE_COOKIES=true
- [X] T004 [P] [SETUP] Install python email dependencies in backend/requirements.txt: sendgrid==6.11.0, python-multipart==0.0.6
- [X] T005 [P] [SETUP] Install frontend cookie dependencies in frontend/package.json: js-cookie@^3.0.5, @types/js-cookie@^3.0.6
- [X] T006 [SETUP] Create backend/alembic/versions/002_add_auth_tables.py migration file (empty, will populate in Phase 2)

---

## Phase 2: Database Schema - New Tables & Models (8 tasks)

- [X] T007 [US5] Add email_verified: bool (default=False) field to User model in backend/app/models.py
- [X] T008 [US5] Add last_login: Optional[datetime] field to User model in backend/app/models.py with index=True
- [X] T009 [US1] Create Session model in backend/app/models.py with fields: id (UUID), user_id (FK), refresh_token_hash (str), expires_at (datetime), created_at (datetime), last_activity (datetime), ip_address (str, 45 chars), user_agent (text)
- [X] T010 [US1] Add indexes to Session model: user_id, expires_at in backend/app/models.py
- [X] T011 [US2] Create PasswordResetToken model in backend/app/models.py with fields: id (UUID), user_id (FK), token_hash (str), expires_at (datetime), created_at (datetime), used (bool, default=False)
- [X] T012 [US2] Add indexes to PasswordResetToken model: user_id, expires_at in backend/app/models.py
- [X] T013 [US3] Create EmailVerificationToken model in backend/app/models.py with fields: id (UUID), user_id (FK), token_hash (str), expires_at (datetime), created_at (datetime)
- [X] T014 [US3] Add indexes to EmailVerificationToken model: user_id, expires_at in backend/app/models.py
- [X] T015 [SETUP] Write Alembic migration in backend/alembic/versions/002_add_auth_tables.py: add email_verified, last_login to users; create sessions, password_reset_tokens, email_verification_tokens tables
- [X] T016 [SETUP] Test Alembic migration with `alembic upgrade head` on local database

---

## Phase 3: Backend Services - Email, Token, Rate Limiting (10 tasks)

- [X] T017 [P] [US2] Create backend/app/services/email.py with send_email() base function using SendGrid/AWS SES
- [X] T018 [P] [US2] Add send_password_reset_email(email: str, token: str) function in backend/app/services/email.py
- [X] T019 [P] [US3] Add send_verification_email(email: str, token: str) function in backend/app/services/email.py
- [X] T020 [P] [US7] Add send_email_changed_notification(old_email: str, new_email: str) function in backend/app/services/email.py
- [X] T021 [P] [US2] Create backend/app/services/token.py with generate_secure_token() using secrets.token_urlsafe(32)
- [X] T022 [P] [US2] Add hash_token(token: str) -> str function using bcrypt in backend/app/services/token.py
- [X] T023 [P] [US2] Add verify_token_hash(plain_token: str, hashed_token: str) -> bool function in backend/app/services/token.py
- [X] T024 [P] [US6] Create backend/app/services/rate_limiter.py with InMemoryRateLimiter class using dict storage
- [X] T025 [US6] Add check_rate_limit(key: str, max_attempts: int, window_seconds: int) -> bool method in rate_limiter.py
- [X] T026 [US6] Add get_retry_after(key: str) -> int method to return seconds until rate limit resets in rate_limiter.py

---

## Phase 4: Backend Auth Core - Refresh Tokens & Cookies (9 tasks)

- [X] T027 [US1] Add create_refresh_token(data: dict, expires_delta: timedelta) -> str function in backend/app/auth.py
- [X] T028 [US1] Add decode_refresh_token(token: str) -> dict function with signature + expiration validation in backend/app/auth.py
- [X] T029 [US5] Add set_auth_cookies(response: Response, access_token: str, refresh_token: str) function in backend/app/auth.py with HttpOnly, Secure, SameSite=Strict flags
- [X] T030 [US5] Add clear_auth_cookies(response: Response) function to delete access_token and refresh_token cookies in backend/app/auth.py
- [X] T031 [US5] Add get_token_from_cookie(request: Request, cookie_name: str) -> str function in backend/app/auth.py
- [X] T032 [US1] Update backend/app/dependencies.py: modify get_current_user() to extract token from cookies instead of Authorization header
- [X] T033 [US6] Add get_rate_limiter() dependency returning InMemoryRateLimiter instance in backend/app/dependencies.py
- [X] T034 [US6] Add check_rate_limit_dependency(limiter: RateLimiter, request: Request, key_prefix: str, max_attempts: int, window: int) in backend/app/dependencies.py
- [X] T035 [US1] Create backend/app/schemas.py entries: RefreshTokenRequest, RefreshTokenResponse, SessionPublic, PasswordResetRequest, PasswordResetConfirm, EmailVerificationRequest, ProfileUpdateRequest

---

## Phase 5: Backend Endpoints - US1 Refresh Token & US5 Cookies (7 tasks)

- [ ] T036 [US1] Update POST /api/auth/login in backend/app/routers/auth.py: create Session record, set access_token + refresh_token in cookies (not in response body), update user.last_login
- [ ] T037 [US1] Create POST /api/auth/refresh endpoint in backend/app/routers/auth.py: validate refresh_token from cookie, check session exists, issue new tokens with rotation (invalidate old refresh_token)
- [ ] T038 [US1] Update POST /api/auth/logout in backend/app/routers/auth.py: delete Session record, clear cookies
- [ ] T039 [US1] Add POST /api/auth/logout-all endpoint in backend/app/routers/auth.py to revoke all sessions for current user (delete all Session records)
- [ ] T040 [US5] Update backend/app/main.py CORS config: add credentials=True, allow_credentials=True for cookie support
- [ ] T041 [US5] Add response.set_cookie() calls in login endpoint using set_auth_cookies() function
- [ ] T042 [US5] Add response.delete_cookie() calls in logout endpoint using clear_auth_cookies() function

---

## Phase 6: Backend Endpoints - US2 Password Reset & US3 Email Verification (10 tasks)

- [ ] T043 [US2] Create POST /api/auth/forgot-password endpoint in backend/app/routers/auth.py: generate token, save PasswordResetToken, send email, always return 200 OK
- [ ] T044 [US2] Add rate limiting to forgot-password endpoint: 3 attempts per hour per email using check_rate_limit_dependency
- [ ] T045 [US2] Create POST /api/auth/reset-password endpoint in backend/app/routers/auth.py: validate token, check not expired (<24hrs), check not used, update user.hashed_password, mark token as used
- [ ] T046 [US2] Add invalidate_all_reset_tokens(user_id: UUID) function to mark all pending reset tokens as used when password changes
- [ ] T047 [US3] Update POST /api/auth/register in backend/app/routers/auth.py: create EmailVerificationToken, send verification email after user creation
- [ ] T048 [US3] Create POST /api/auth/verify-email endpoint in backend/app/routers/auth.py: validate token, check not expired (<24hrs), set user.email_verified=True, delete token
- [ ] T049 [US3] Create POST /api/auth/resend-verification endpoint in backend/app/routers/auth.py: check user not already verified, generate new token, send email
- [ ] T050 [US3] Add rate limiting to resend-verification endpoint: 3 attempts per hour per user_id using check_rate_limit_dependency
- [ ] T051 [US6] Add rate limiting to POST /api/auth/login: 5 attempts per 15 minutes per IP address using check_rate_limit_dependency
- [ ] T052 [US6] Add rate limiting to POST /api/auth/register: 3 attempts per hour per IP address using check_rate_limit_dependency

---

## Phase 7: Backend Endpoints - US4 Session Management & US7 Profile (6 tasks)

- [ ] T053 [US4] Create GET /api/auth/sessions endpoint in backend/app/routers/auth.py: return all active sessions for current_user with device info, IP, last_activity
- [ ] T054 [US4] Add is_current: bool field to session response based on comparing refresh_token from request cookie
- [ ] T055 [US4] Create DELETE /api/auth/sessions/{session_id} endpoint in backend/app/routers/auth.py: verify ownership (session.user_id == current_user_id), delete session
- [ ] T056 [US4] Create DELETE /api/auth/sessions/revoke-all endpoint in backend/app/routers/auth.py: delete all sessions except current (identified by refresh_token)
- [ ] T057 [US7] Create PATCH /api/auth/profile endpoint in backend/app/routers/auth.py: validate ProfileUpdateRequest, update user.name, return updated UserPublic
- [ ] T058 [US7] Add email change workflow in profile endpoint: if new email provided, create EmailVerificationToken for new email, send verification, don't update email until verified

---

## Phase 8: Backend Email Templates & Cleanup Jobs (5 tasks)

- [ ] T059 [P] [US2] Create backend/templates/emails/password_reset.html: HTML email template with reset link ({{reset_url}}, {{user_name}}, {{expiry_hours}})
- [ ] T060 [P] [US3] Create backend/templates/emails/email_verification.html: HTML email template with verification link ({{verify_url}}, {{user_name}})
- [ ] T061 [P] [US7] Create backend/templates/emails/email_changed.html: notification email for successful email change
- [ ] T062 [US1] Add cleanup_expired_sessions() function in backend/app/services/token.py: delete Session records where expires_at < now() or last_activity < 30 days ago
- [ ] T063 [US2] Add cleanup_expired_reset_tokens() function in backend/app/services/token.py: delete PasswordResetToken records where created_at < 48 hours ago

---

## Phase 9: Frontend - Cookie Handling & Refresh Interceptor (12 tasks)

- [ ] T064 [P] [US5] Create frontend/lib/cookies.ts with getCookie(name: string), setCookie(name, value, options), removeCookie(name) using js-cookie
- [ ] T065 [US5] Update frontend/lib/api.ts: remove Authorization header logic, add credentials: 'include' to all fetch() calls for cookie transmission
- [ ] T066 [US1] Add automatic refresh interceptor in frontend/lib/api.ts: on 401 response, call POST /api/auth/refresh, retry original request once
- [ ] T067 [US1] Add refreshAccessToken() function in frontend/lib/api.ts: POST to /api/auth/refresh with credentials, return success/failure
- [ ] T068 [US5] Update frontend/hooks/useAuth.ts: remove setToken/removeToken calls (cookies managed by backend), update login/logout to rely on cookies
- [ ] T069 [US5] Update frontend/lib/auth.ts: remove getToken/setToken/removeToken functions (deprecated with cookie auth), keep only isTokenExpired for local checks
- [ ] T070 [US1] Add useEffect in frontend/hooks/useAuth.ts to check session validity on mount: call /api/auth/me to verify cookie session
- [ ] T071 [US4] Create frontend/hooks/useSessions.ts with fetchSessions(), revokeSession(id), revokeAllSessions() using api.get/delete
- [ ] T072 [US2] Add forgotPassword(email: string) method to frontend/hooks/useAuth.ts: POST /api/auth/forgot-password
- [ ] T073 [US2] Add resetPassword(token: string, newPassword: string) method to frontend/hooks/useAuth.ts: POST /api/auth/reset-password
- [ ] T074 [US3] Add verifyEmail(token: string) method to frontend/hooks/useAuth.ts: POST /api/auth/verify-email
- [ ] T075 [US3] Add resendVerification() method to frontend/hooks/useAuth.ts: POST /api/auth/resend-verification

---

## Phase 10: Frontend UI Components - Auth Pages (12 tasks)

- [ ] T076 [P] [US2] Create frontend/components/features/auth/ForgotPasswordForm.tsx: email input, submit button, success message
- [ ] T077 [P] [US2] Create frontend/app/[locale]/(auth)/forgot-password/page.tsx: render ForgotPasswordForm, handle submission with forgotPassword()
- [ ] T078 [P] [US2] Create frontend/components/features/auth/ResetPasswordForm.tsx: new password + confirm password inputs, token from URL, submit button
- [ ] T079 [P] [US2] Create frontend/app/[locale]/(auth)/reset-password/page.tsx: extract token from query params, render ResetPasswordForm, handle resetPassword()
- [ ] T080 [P] [US3] Create frontend/components/features/auth/EmailVerificationBanner.tsx: banner showing "Verify your email" with resend button
- [ ] T081 [P] [US3] Create frontend/app/[locale]/(auth)/verify-email/page.tsx: extract token from query, call verifyEmail() on mount, show success/error
- [ ] T082 [P] [US3] Create frontend/components/features/auth/ResendVerificationButton.tsx: button with 60-second cooldown after resend
- [ ] T083 [US3] Add EmailVerificationBanner to frontend/app/[locale]/layout.tsx: conditionally show if user.email_verified === false
- [ ] T084 [P] [US4] Create frontend/components/features/sessions/SessionCard.tsx: display session device, IP, last activity, revoke button
- [ ] T085 [P] [US4] Create frontend/components/features/sessions/SessionList.tsx: map sessions to SessionCard, handle revoke actions
- [ ] T086 [P] [US4] Create frontend/app/[locale]/(dashboard)/sessions/page.tsx: render SessionList, fetch sessions on mount with useSessions()
- [ ] T087 [US7] Create frontend/components/features/profile/ProfileUpdateForm.tsx: name input, email input, submit button, display updated user data

---

## Phase 11: Frontend i18n - Urdu Translations (5 tasks)

- [ ] T088 [P] [US2] Add password reset translations to frontend/messages/en.json: "forgotPassword", "resetPassword", "resetEmailSent", "resetSuccess"
- [ ] T089 [P] [US2] Add password reset translations to frontend/messages/ur.json: Urdu equivalents for password reset flow
- [ ] T090 [P] [US3] Add email verification translations to frontend/messages/en.json: "verifyEmail", "verificationSent", "verificationSuccess", "resendVerification"
- [ ] T091 [P] [US3] Add email verification translations to frontend/messages/ur.json: Urdu equivalents for email verification
- [ ] T092 [P] [US4] Add session management translations to frontend/messages/en.json and ur.json: "sessions", "activeDevices", "revokeSession", "revokeAll"

---

## Phase 12: Backend Tests - Unit & Integration (8 tasks)

- [ ] T093 [P] [US1] Create backend/tests/test_refresh_token.py: test token rotation, expiration validation, session creation/deletion
- [ ] T094 [P] [US2] Create backend/tests/test_password_reset.py: test forgot-password flow, reset token expiration, single-use enforcement, rate limiting
- [ ] T095 [P] [US3] Create backend/tests/test_email_verification.py: test verification flow, token expiration, resend logic
- [ ] T096 [P] [US4] Create backend/tests/test_sessions.py: test session CRUD, ownership verification, revoke-all logic
- [ ] T097 [P] [US5] Create backend/tests/test_cookies.py: test cookie setting/clearing, HttpOnly/Secure/SameSite flags
- [ ] T098 [P] [US6] Create backend/tests/test_rate_limiting.py: test rate limit enforcement, Retry-After header, limit reset
- [ ] T099 [P] [US7] Create backend/tests/test_profile_update.py: test name update, email change workflow, validation
- [ ] T100 [SETUP] Update backend/tests/conftest.py: add fixtures for sessions, reset tokens, verification tokens, rate limiter

---

## Phase 13: Frontend Tests - Components & Hooks (6 tasks)

- [ ] T101 [P] [US2] Create frontend/__tests__/components/ForgotPasswordForm.test.tsx: test form submission, error handling
- [ ] T102 [P] [US2] Create frontend/__tests__/components/ResetPasswordForm.test.tsx: test password validation, token handling
- [ ] T103 [P] [US3] Create frontend/__tests__/components/EmailVerificationBanner.test.tsx: test banner display, resend cooldown
- [ ] T104 [P] [US4] Create frontend/__tests__/components/SessionList.test.tsx: test session rendering, revoke actions
- [ ] T105 [P] [US1] Create frontend/__tests__/hooks/useAuth.test.tsx: test refresh logic, cookie-based auth
- [ ] T106 [P] [US4] Create frontend/__tests__/hooks/useSessions.test.tsx: test fetch/revoke session operations

---

## Phase 14: Documentation & Polish (4 tasks)

- [ ] T107 [P] [SETUP] Create specs/007-auth-enhancements/quickstart.md: developer setup guide with environment variables, migration steps
- [ ] T108 [P] [SETUP] Update backend/README.md: document new auth endpoints, cookie configuration, rate limiting
- [ ] T109 [P] [SETUP] Update frontend/README.md: document cookie-based auth, refresh flow, new auth pages
- [ ] T110 [SETUP] Create specs/007-auth-enhancements/testing.md: manual testing checklist for all 7 user stories with acceptance scenarios

---

## Task Execution Notes

**Dependencies**:
- T015-T016 (migration) blocks all database-dependent tasks (T036-T058)
- T017-T026 (services) blocks all endpoint tasks (T043-T058)
- T027-T035 (auth core) blocks frontend integration (T064-T087)
- T064-T075 (frontend lib) blocks UI components (T076-T087)

**Parallelization Strategy**:
- Phase 1 (T001-T006): All parallelizable
- Phase 2 (T007-T016): T007-T014 parallelizable, T015-T016 sequential
- Phase 3 (T017-T026): Email/token/rate limiter services parallelizable
- Phase 8 (T059-T063): Email templates parallelizable
- Phase 11 (T088-T092): All translations parallelizable
- Phase 12 (T093-T100): All tests parallelizable
- Phase 13 (T101-T106): All tests parallelizable
- Phase 14 (T107-T110): All documentation parallelizable

**Critical Path**:
T001-T006 (setup) → T015-T016 (migration) → T027-T035 (auth core) → T036-T042 (refresh/cookies) → T064-T070 (frontend integration) → T076-T087 (UI components) → T100 (test all flows)

**Testing Requirements**:
- Each user story has dedicated test file covering all acceptance scenarios
- Backend: pytest with fixtures for auth tokens, sessions, rate limiting
- Frontend: Jest + React Testing Library for component and hook tests
- Manual testing checklist (T110) covers all 7 user stories end-to-end

**Total**: 110 tasks across 14 phases covering all 7 user stories (US1-US7) with comprehensive backend, frontend, testing, and documentation work.
