# CORS Configuration Changes

## Summary

This document describes the CORS (Cross-Origin Resource Sharing) configuration changes made to fix inconsistencies and improve security in the medbilldozer application.

## Problem Statement

The previous CORS configuration had several issues:
1. **Hardcoded origins**: Origins were hardcoded in `config.py` rather than being environment-driven
2. **Overly permissive**: Used `allow_methods=["*"]` and `allow_headers=["*"]`
3. **No preflight caching**: Missing `max_age` parameter for OPTIONS requests
4. **No environment awareness**: Same origins used for all environments (local, staging, production)
5. **No single source of truth**: Origins scattered across multiple configuration files

## Changes Made

### 1. Modified Files

#### [backend/app/core/config.py](backend/app/config.py)

**Added:**
- `environment: str` - Deployment environment (local, development, staging, production)
- `frontend_url: Optional[str]` - Primary frontend URL to always allow
- `backend_cors_origins: List[str]` - Additional CORS origins from environment variable
- `all_cors_origins` property - Returns environment-specific list of allowed origins

**Details:**
The `all_cors_origins` property provides a single source of truth for CORS origins:
- **local/development**: Allows `localhost` and `127.0.0.1` on ports 3000, 5173, 8000
- **staging**: Allows `https://staging.medbilldozer.com`
- **production**: Allows `https://medbilldozer.com` and `https://www.medbilldozer.com`
- Always includes `FRONTEND_URL` if set
- Merges additional origins from `BACKEND_CORS_ORIGINS` environment variable

**Legacy:**
- Kept `allowed_origins` field for backwards compatibility (marked as deprecated)

#### [backend/app/main.py](backend/app/main.py)

**Changed CORS middleware from:**
```python
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)
```

**To:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Correlation-ID"],
    max_age=600,
)
```

**Improvements:**
- Uses environment-aware `settings.all_cors_origins`
- Explicitly lists allowed HTTP methods (more secure)
- Explicitly lists allowed headers (more secure)
- Added `max_age=600` (10 minutes) for preflight caching
- Exposes both `X-Request-ID` and `X-Correlation-ID` headers

#### [.env.example](.env.example)

**Added variables:**
```bash
ENVIRONMENT=local
FRONTEND_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=[]
```

#### [backend/.env.example](backend/.env.example)

**Replaced:**
```bash
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://your-frontend.vercel.app
```

**With:**
```bash
ENVIRONMENT=local
FRONTEND_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=[]
```

#### [backend/.env.cloudrun](backend/.env.cloudrun)

**Updated for production:**
```bash
ENVIRONMENT=production
FRONTEND_URL=https://medbilldozer.vercel.app
BACKEND_CORS_ORIGINS=[]
```

### 2. Files Checked (No Changes Needed)

- ✅ [backend/app/middleware/logging_middleware.py](backend/app/middleware/logging_middleware.py) - No CORS handling
- ✅ [frontend/src/services/api.ts](frontend/src/services/api.ts) - Already compatible with `withCredentials: true`
- ✅ No nginx configs found that might add conflicting CORS headers

## Configuration Guide

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `local` | Deployment environment: `local`, `development`, `staging`, or `production` |
| `FRONTEND_URL` | No | None | Primary frontend URL to allow (e.g., `https://medbilldozer.vercel.app`) |
| `BACKEND_CORS_ORIGINS` | No | `[]` | JSON array of additional origins (e.g., `["https://custom.com"]`) |

### Configuration by Environment

#### Local Development
```bash
ENVIRONMENT=local
# Automatically allows:
# - http://localhost:3000, http://localhost:5173, http://localhost:8000
# - http://127.0.0.1:3000, http://127.0.0.1:5173, http://127.0.0.1:8000
```

#### Staging
```bash
ENVIRONMENT=staging
FRONTEND_URL=https://staging-frontend.vercel.app
# Automatically allows:
# - https://staging.medbilldozer.com
# - https://staging-frontend.vercel.app (from FRONTEND_URL)
```

#### Production
```bash
ENVIRONMENT=production
FRONTEND_URL=https://medbilldozer.vercel.app
# Automatically allows:
# - https://medbilldozer.com
# - https://www.medbilldozer.com
# - https://medbilldozer.vercel.app (from FRONTEND_URL)
```

### Adding Custom Origins

To allow additional origins beyond the defaults:

```bash
BACKEND_CORS_ORIGINS=["https://custom-domain.com","https://another-domain.com"]
```

**Important:** Must be a valid JSON array of strings.

## Security Improvements

1. ✅ **No wildcard origins with credentials**: Never uses `allow_origins=["*"]` with `allow_credentials=True`
2. ✅ **Explicit methods**: Only allows necessary HTTP methods
3. ✅ **Explicit headers**: Only allows necessary headers
4. ✅ **Preflight caching**: Reduces OPTIONS requests with `max_age=600`
5. ✅ **Environment-specific**: Different origins for different environments
6. ✅ **Single source of truth**: All CORS logic in one property method

## Testing

### Test CORS Configuration

1. **Check allowed origins:**
   ```python
   from app.config import settings
   print(settings.all_cors_origins)
   ```

2. **Test preflight request:**
   ```bash
   curl -X OPTIONS http://localhost:8080/api/auth/login \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Authorization, Content-Type" \
     -v
   ```

   Should return:
   - `Access-Control-Allow-Origin: http://localhost:3000`
   - `Access-Control-Allow-Credentials: true`
   - `Access-Control-Max-Age: 600`

3. **Test actual request:**
   ```bash
   curl -X POST http://localhost:8080/api/auth/login \
     -H "Origin: http://localhost:3000" \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test"}' \
     -v
   ```

### Common Issues

**Issue: CORS error "Origin not allowed"**
- Check that `ENVIRONMENT` is set correctly
- Verify `FRONTEND_URL` matches your frontend's actual URL
- Check for typos in `BACKEND_CORS_ORIGINS` JSON

**Issue: "Credentials not allowed with wildcard origin"**
- Should not occur with new configuration
- If it does, check for conflicting CORS middleware or nginx config

**Issue: Preflight requests failing**
- Ensure backend is running and accessible
- Check that `OPTIONS` is in `allow_methods`
- Verify `Access-Control-Request-Headers` are in `allow_headers`

## Migration Notes

### From Old Configuration

If upgrading from the old hardcoded `ALLOWED_ORIGINS`:

1. Set `ENVIRONMENT` variable in your deployment
2. Set `FRONTEND_URL` to your deployed frontend URL
3. Remove `ALLOWED_ORIGINS` from environment (it's deprecated)
4. Restart the backend service

### Backwards Compatibility

The old `allowed_origins` field is still present in `config.py` but is no longer used by the CORS middleware. It will be removed in a future version.

## References

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CORS Specification](https://fetch.spec.whatwg.org/#http-cors-protocol)

## Author

Fixed by Claude Code Agent on 2026-02-19
