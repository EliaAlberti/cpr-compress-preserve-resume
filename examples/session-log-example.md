# Session Log: 2026-03-05 14:20 - api-auth-refactor

## Quick Reference (for AI scanning)
**Confidence keywords:** auth, JWT, refresh-tokens, middleware, session-management, Redis, bcrypt, login-flow, rate-limiting, security
**Projects:** my-saas-app
**Outcome:** Replaced cookie-based auth with JWT + refresh tokens, added rate limiting to login endpoint, all tests passing

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| JWT + refresh tokens over session cookies | Stateless auth scales better for our API-first architecture |
| Store refresh tokens in Redis (not DB) | Fast lookup + built-in TTL expiry, DB stays clean |
| 15min access token / 7d refresh token | Balance between security and UX, since users don't re-login often |
| Rate limit login to 5 attempts/min per IP | Prevent brute force without affecting normal usage |

## Key Learnings

- `jsonwebtoken` library's `verify()` is synchronous and blocks the event loop for large payloads. Use `verifyAsync` wrapper instead
- Redis `EX` flag on `SET` is cleaner than separate `EXPIRE` calls for refresh token storage
- Middleware order matters: rate limiter must come BEFORE auth middleware, not after

## Solutions & Fixes

- **Login race condition:** Two simultaneous refresh requests could both succeed and create duplicate sessions. Fixed with Redis `SETNX` (set-if-not-exists) for refresh token rotation
- **Token size bloat:** Initial JWT payload included full user profile (2KB). Reduced to `{id, role, org}` (120 bytes), profile fetched on demand

## Files Modified
- `src/middleware/auth.ts`: Replaced session lookup with JWT verification
- `src/routes/auth/login.ts`: New JWT issuance + refresh token flow
- `src/routes/auth/refresh.ts`: New endpoint for token refresh
- `src/lib/redis.ts`: Added refresh token storage helpers
- `src/middleware/rateLimit.ts`: New rate limiting middleware
- `tests/auth.test.ts`: Updated all auth tests for JWT flow
- `.env.example`: Added JWT_SECRET, REFRESH_TOKEN_TTL, REDIS_URL

## Pending Tasks
- [ ] Add refresh token rotation (invalidate old token on use)
- [ ] Set up token blacklist for logout
- [ ] Load test the new auth flow under 1000 concurrent users

## Errors & Workarounds
- **`TokenExpiredError` not caught properly:** Express error handler wasn't matching the error type. Fix: Added specific catch for `jsonwebtoken` error types in error middleware
- **Redis connection drops in test:** CI Redis container wasn't ready. Fix: Added retry logic with 3s timeout in test setup

## Key Exchanges
- Discussed whether to use asymmetric (RS256) vs symmetric (HS256) JWT signing, went with HS256 for simplicity since we're not sharing tokens across services
- User clarified that mobile app will also use this auth flow, so refresh tokens are essential (mobile users shouldn't re-login)

## Custom Notes
The client wants a "remember me" checkbox that extends refresh token to 30 days. Implement after the base flow is stable.

---

## Quick Resume Context
Replaced cookie-based auth with JWT + refresh tokens in my-saas-app. Core flow is working and tested. Still need to implement token rotation on refresh, token blacklist for logout, and load testing. Redis is used for refresh token storage with TTL. Rate limiting is in place on the login endpoint.

---

## Raw Session Log

{Appended by scripts/dump_transcript.py: every user message and assistant reply, verbatim, for searchability. Filename for this example: CC-Session-Logs/2026-03-05-14_20-api-auth-refactor.md}
