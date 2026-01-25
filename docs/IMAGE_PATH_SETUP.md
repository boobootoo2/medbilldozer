# Image Path Configuration

## Overview

The medBillDozer application now supports dynamic image path resolution that automatically switches between local file paths and GitHub CDN URLs based on the deployment environment.

## How It Works

### Local Development
When running on:
- `localhost`
- `127.0.0.1`
- Any IP address (e.g., `192.168.1.100`, `10.0.0.5`)

Images are served from: `app/static/images/...`

### Production Deployment
When running on any other domain (e.g., `myapp.streamlit.app`), images are served from:
```
https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/images/...
```

## Implementation

### Python Files

#### Utility Module: `_modules/utils/image_paths.py`

Core functions:
- `is_local_environment()` - Detects if running locally
- `get_image_url(path)` - Returns appropriate URL for any image
- `get_avatar_url(filename)` - Helper for avatar images
- `get_transparent_avatar_url(filename)` - Helper for transparent avatars

**Usage Example:**
```python
from _modules.utils.image_paths import get_avatar_url

# Automatically returns correct path based on environment
avatar_url = get_avatar_url("billie__eyes_open__ready.png")
# Local: "app/static/images/avatars/billie__eyes_open__ready.png"
# Prod: "https://raw.githubusercontent.com/.../images/avatars/billie__eyes_open__ready.png"
```

#### Updated Files:
1. **`_modules/ui/ui.py`**
   - Updated `render_header()` to use `get_image_url()` for logo
   - Imports: `from _modules.utils.image_paths import get_image_url`

2. **`_modules/ui/doc_assistant.py`**
   - Updated avatar rendering to use `get_avatar_url()`
   - Dynamically generates image URLs for all avatar states
   - Imports: `from _modules.utils.image_paths import get_avatar_url`

### Static HTML Files

All HTML files now include JavaScript to detect environment and set image sources dynamically.

#### Updated Files:

1. **`static/bulldozer_animation.html`**
   - JavaScript function `getImageBasePath()` detects hostname
   - Dynamically sets all image `src` attributes on page load
   - Images initially have empty `src=""` attributes

2. **`static/billdozer_animation.html`**
   - Same dynamic image loading approach
   - Supports iframe embedding with proper path resolution

3. **`static/avatar_prototype.html`**
   - Updates avatar images dynamically
   - Uses same hostname detection logic

**JavaScript Implementation:**
```javascript
function getImageBasePath() {
    const hostname = window.location.hostname;
    const isLocal = hostname === 'localhost' ||
                   hostname === '127.0.0.1' ||
                   /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(hostname);

    if (isLocal) {
        return 'app/static/images/avatars/transparent';
    } else {
        return 'https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/images/avatars/transparent';
    }
}
```

## Environment Detection Logic

### Python Detection
Checks environment variables:
- `HOSTNAME`
- `STREAMLIT_SERVER_ADDRESS`
- `SERVER_ADDRESS`

Uses regex pattern to identify IP addresses: `\b(?:\d{1,3}\.){3}\d{1,3}\b`

### JavaScript Detection
Checks `window.location.hostname` against:
- Exact match: `localhost`, `127.0.0.1`
- Regex pattern for any IP address

## GitHub CDN URL Structure

Base URL:
```
https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/
```

**Examples:**
- Avatar: `https://raw.githubusercontent.com/.../images/avatars/billie__eyes_open__ready.png`
- Transparent: `https://raw.githubusercontent.com/.../images/avatars/transparent/billy__eyes_closed__billdozer_down.png`
- Logo: `https://raw.githubusercontent.com/.../images/medBillDozer-logo-transparent.png`

## Testing

Test file: `tests/test_image_paths.py`

**Test Coverage:**
- ✅ Local environment detection (localhost, 127.0.0.1, IP addresses)
- ✅ Production environment detection
- ✅ URL generation for local paths
- ✅ URL generation for CDN paths
- ✅ Path prefix handling (static/, app/static/)
- ✅ Avatar helper functions
- ✅ Edge cases (leading/trailing slashes)

Run tests:
```bash
pytest tests/test_image_paths.py -v
```

## Benefits

1. **Zero Configuration** - Automatically adapts to environment
2. **Development Friendly** - Local files load faster during development
3. **Production Ready** - CDN ensures images work on any deployment
4. **Maintainable** - Single source of truth for path logic
5. **Testable** - Comprehensive test coverage

## Migration Notes

### Before:
```python
# Hardcoded local path
logo_path = Path("static/images/medBillDozer-logo-transparent.png")
```

### After:
```python
from _modules.utils.image_paths import get_image_url

# Dynamic path based on environment
logo_url = get_image_url("images/medBillDozer-logo-transparent.png")
```

### HTML Before:
```html
<img src="app/static/images/avatars/transparent/billie.png">
```

### HTML After:
```html
<!-- Empty src, set by JavaScript -->
<img src="" alt="Billie">

<script>
const basePath = getImageBasePath();
document.querySelector('img').src = `${basePath}/billie.png`;
</script>
```

## Troubleshooting

### Images Not Loading Locally
- Check that files exist in `static/images/` directory
- Verify Streamlit is serving static files correctly
- Check browser console for 404 errors

### Images Not Loading in Production
- Verify GitHub repository is public
- Check CDN URL is accessible: `https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/images/...`
- Ensure images are committed to `main` branch
- Check browser console for CORS errors

### Wrong Environment Detected
- Check environment variables: `echo $HOSTNAME`
- Review detection logic in `is_local_environment()`
- Add debug logging to see which environment is detected

## Future Enhancements

Potential improvements:
- Support for multiple branches/environments (dev, staging, prod)
- Image optimization and lazy loading
- Fallback images if CDN fails
- Configurable CDN base URL via environment variable
- Image caching strategies

