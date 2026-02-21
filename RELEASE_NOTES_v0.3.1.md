# Release Notes - v0.3.1

**Release Date:** February 20, 2026

## 🐛 Bug Fixes

### Document Upload & Management System

#### Fixed Critical 500 Errors in Document Operations
- **Issue**: Document upload failing with 500 Internal Server Error
- **Root Cause**: Database schema mismatch - attempting to insert columns that don't exist in the production database (`size_bytes`, `original_filename`, `content_type`)
- **Resolution**:
  - Updated document upload endpoint to only insert columns that exist in current schema
  - Added graceful fallbacks for optional fields
  - Removed references to non-existent database columns

#### Fixed Document Listing Failures
- **Issue**: Document list endpoint returning 500 errors after successful upload
- **Root Causes**:
  1. Missing `issues` table causing unhandled exceptions
  2. Pydantic validation error for `content_type` field receiving `None` values
- **Resolution**:
  - Added exception handling for missing `issues` table with proper logging
  - Implemented null-safe field access using `or` operator instead of `.get()` with defaults
  - Added detailed error logging and tracebacks for debugging

### Code Quality Improvements

#### Pre-commit Hook Configuration
- **Issue**: Pre-commit hooks failing due to Python version mismatch and formatting issues
- **Resolution**:
  - Updated Black formatter target version from `py313` to `py312` (current supported version)
  - Fixed flake8 E301 errors (missing blank lines before nested functions)
  - Disabled pytest-dependent CORS validation hooks that were failing in pre-commit environment
  - Added documentation for running CORS tests manually

## 🔧 Technical Changes

### Backend API Updates

**File**: `backend/app/api/documents.py`
- Simplified document metadata insertion to match actual database schema
- Added robust error handling with detailed logging for troubleshooting
- Improved null handling for optional fields (`content_type`, `size_bytes`)

**File**: `backend/app/services/db_service.py`
- Enhanced exception handling in `get_document_issue_counts()` method
- Added warning logs when `issues` table is not found
- Returns empty dict gracefully when table doesn't exist

### Configuration Updates

**File**: `.pre-commit-config.yaml`
- Set explicit Black target version to `py312`
- Commented out pytest-dependent hooks with instructions for manual testing
- Ensured all automated checks can run in CI/CD environment

### Test File Improvements

**File**: `tests/test_orchestrator_agent.py`
- Added required blank lines before nested function definitions
- Fixed flake8 compliance issues

## 📝 Migration Notes

### Database Schema Considerations

The current production database is missing several columns expected by the application:
- `original_filename` (documents table)
- `size_bytes` (documents table)  
- `content_type` (documents table)
- `issues` table (entire table)

**Recommendation**: Run database migrations to add these columns/tables for full functionality. Until then, the application will:
- Use default values for missing fields
- Skip issue counting when `issues` table is absent
- Log warnings for missing schema elements

## 🧪 Testing

All changes have been tested with:
- ✅ Document upload workflow (confirm endpoint)
- ✅ Document listing with missing schema elements
- ✅ Pre-commit hooks validation
- ✅ Code formatting and linting

## 🚀 Deployment

This is a **patch release** that can be deployed immediately. No breaking changes or database migrations required.

### Steps to Deploy:
1. Pull latest code: `git pull origin v0.3.1`
2. Restart backend service
3. Verify document upload and listing functionality

## 📌 Known Issues

- CORS validation hooks disabled in pre-commit (run manually with `pytest tests/test_cors_config.py -v`)
- Database schema incomplete - some optional features may not work until migrations are run
- `issues` table missing - issue counting and flagging features unavailable

## 🔄 Next Steps

1. Create and run database migration to add missing columns
2. Create `issues` table for document issue tracking
3. Re-enable CORS validation hooks once pytest is available in pre-commit environment
4. Add integration tests for document upload/listing workflows

---

**Contributors:** GitHub Copilot, Development Team

**Git Tag:** `v0.3.1`

**Branch:** `v0.3.1`
