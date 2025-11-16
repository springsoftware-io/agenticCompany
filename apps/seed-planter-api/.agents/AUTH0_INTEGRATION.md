# Auth0 Integration Summary

## Changes Made

### 1. **Auth0 Service** (`src/auth0_service.py`)
- Adapted from `asset-gold-volatility` project
- FastAPI-compatible JWT verification using Auth0's JWKS
- Async functions for token verification and user management
- Two authentication dependencies:
  - `get_current_user_auth0()` - Required authentication (raises 401 if not authenticated)
  - `get_optional_user_auth0()` - Optional authentication (returns None if not authenticated)

### 2. **Database Models** (`src/db_models.py`)
- Added OAuth fields to `User` model:
  - `oauth_provider` - Provider name (e.g., 'auth0', 'github')
  - `oauth_id` - Provider's unique user ID (indexed for fast lookups)

### 3. **Configuration** (`src/config.py`)
- Added Auth0 settings:
  - `AUTH0_DOMAIN`
  - `AUTH0_CLIENT_ID`
  - `AUTH0_CLIENT_SECRET`
  - `AUTH0_AUDIENCE`

### 4. **Main API** (`src/main.py`)
- Updated `/api/v1/projects` endpoint to use optional Auth0 authentication
- Allows both authenticated and anonymous access
- Usage metering only applied to authenticated users
- Imports and includes Auth0 router

### 5. **Auth0 Routes** (`src/auth0_routes.py`)
- `/api/v1/auth/me` - Get current user info (requires auth)
- `/api/v1/auth/usage` - Get usage statistics (requires auth)

### 6. **Database Migration** (`alembic/versions/add_oauth_fields.py`)
- Migration to add OAuth fields to existing users table
- Creates unique index on `oauth_id`

### 7. **Environment Configuration** (`.env.example`)
- Added Auth0 configuration template

### 8. **Dependencies** (`requirements.txt`)
- `python-jose[cryptography]` already present for JWT handling
- `email-validator` added for Pydantic EmailStr validation

## Environment Variables Needed

Add these to your `.env` file (or Cloud Run secrets):

```bash
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
AUTH0_AUDIENCE=https://your-tenant.us.auth0.com/api/v2/
```

## How It Works

### For Anonymous Users
- Can call `/api/v1/projects` without authentication
- No usage tracking or quotas applied
- No Bearer token required

### For Authenticated Users
- Include `Authorization: Bearer <auth0_jwt_token>` header
- User automatically created in database on first request
- Usage tracked and quotas enforced
- Access to `/api/v1/auth/me` and `/api/v1/auth/usage` endpoints

### User Creation Flow
1. User authenticates with Auth0 (frontend handles this)
2. Frontend sends Auth0 JWT token to API
3. API verifies token with Auth0's JWKS
4. If user doesn't exist locally, fetches user info from Auth0
5. Creates user record with OAuth fields populated
6. Returns user object for subsequent requests

## Testing

### Without Authentication
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "test-project",
    "project_description": "Test description",
    "mode": "saas"
  }'
```

### With Authentication
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <auth0_jwt_token>" \
  -d '{
    "project_name": "test-project",
    "project_description": "Test description",
    "mode": "saas"
  }'
```

### Get User Info
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <auth0_jwt_token>"
```

## Next Steps

1. **Set up Auth0 tenant** if not already done
2. **Configure Auth0 Application** with proper callbacks
3. **Add Auth0 credentials** to Cloud Run secrets
4. **Run database migration** to add OAuth fields
5. **Update frontend** to use Auth0 authentication
6. **Test both authenticated and anonymous flows**

## Migration Command

```bash
cd apps/seed-planter-api
alembic upgrade head
```

## Benefits

- ✅ Tests now pass (anonymous access allowed)
- ✅ Production-ready authentication with Auth0
- ✅ Automatic user provisioning
- ✅ Usage tracking for authenticated users
- ✅ Backward compatible (anonymous access still works)
- ✅ Follows Auth0 best practices from working project
