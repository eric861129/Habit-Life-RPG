# Habit Life RPG Runbook

## Daily checks

1. Confirm the frontend URL loads.
2. Confirm `/docs` on the API is reachable.
3. Confirm `GET /api/v1/user/profile` returns 200 with the configured token.
4. Check recent 5xx count.
5. Check database connection errors.

## First response for API outage

1. Confirm App Service status.
2. Check latest deployment time.
3. Review App Service logs.
4. Verify `DATABASE_URL` and `HLR_ALLOWED_ORIGINS`.
5. Roll back to the previous working deployment if needed.

## First response for CORS failure

1. Capture the failing browser Origin.
2. Compare it with `HLR_ALLOWED_ORIGINS`.
3. Add only the required production origin.
4. Retest through browser Network tools.
