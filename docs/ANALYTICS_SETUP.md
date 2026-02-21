# Analytics Setup Guide - MedBillDozer

This guide explains how to set up Google Analytics 4 (GA4) for both the React frontend and Streamlit app in MedBillDozer.

## Overview

MedBillDozer uses **Google Analytics 4** with a privacy-focused configuration to track user journey events:
- Page views (navigation only)
- Login events (authentication method only - google/github)
- Logout events

**Privacy Protections:**
- ✅ IP addresses anonymized
- ✅ Advertising features disabled
- ✅ Google signals disabled
- ✅ NO Protected Health Information (PHI) tracked
- ✅ NO user personal information (email, name) tracked
- ✅ NO document data or medical information tracked

## Prerequisites

1. **Create a Google Analytics 4 Property:**
   - Go to [Google Analytics](https://analytics.google.com/)
   - Create a new GA4 property
   - Get your **Measurement ID** (format: `G-XXXXXXXXXX`)
   - Optionally enable **Debug View** for testing

## React Frontend Setup

### 1. Install Dependencies

The `react-ga4` package has already been installed:

```bash
cd frontend
npm install  # Will install react-ga4 from package.json
```

### 2. Configure Environment Variables

Create or update `frontend/.env.local`:

```bash
# Copy from example
cp .env.example .env.local

# Add your GA4 Measurement ID
echo "VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX" >> .env.local
```

Replace `G-XXXXXXXXXX` with your actual GA4 Measurement ID.

### 3. Verify Setup

Start the development server:

```bash
npm run dev
```

Open your browser's console and look for:
```
✅ GA4: Initialized with measurement ID: G-XXXXXXXXXX
📊 GA4: Page view tracked: /
```

### 4. Test Events

1. **Page Navigation:** Navigate between pages and check console for page view events
2. **Login:** Sign in with Google or GitHub, check for login event
3. **Logout:** Sign out, check for logout event
4. **GA4 DebugView:** View real-time events in GA4 Admin → DebugView

### React Implementation Details

**Files Modified:**
- `frontend/src/utils/analytics.ts` - GA4 utility with privacy configuration
- `frontend/src/App.tsx` - Initialize GA4 and track route changes
- `frontend/src/components/auth/LoginButton.tsx` - Track login events
- `frontend/src/components/auth/UserMenu.tsx` - Track logout events
- `frontend/.env.example` - Environment variable template

**Key Functions:**
```typescript
import { initGA, trackPageView, trackLogin, trackLogout } from './utils/analytics';

// Initialize on app mount
initGA();

// Track page view
trackPageView('/path');

// Track authentication
trackLogin('google');  // or 'github'
trackLogout();
```

## Streamlit App Setup

### 1. Configure Environment Variables

Set the GA4 measurement ID via environment variable:

```bash
# Option 1: Export environment variable
export GA4_MEASUREMENT_ID=G-XXXXXXXXXX

# Option 2: Add to .env file (if using python-dotenv)
echo "GA4_MEASUREMENT_ID=G-XXXXXXXXXX" >> .env
```

Or add to Streamlit secrets (`.streamlit/secrets.toml`):

```toml
GA4_MEASUREMENT_ID = "G-XXXXXXXXXX"
```

### 2. Verify Setup

Run the Streamlit app:

```bash
streamlit run <your_app.py>
```

Check the terminal output for:
```
✅ GA4: Streamlit analytics initialized with ID: G-XXXXXXXXXX
```

Check browser console for:
```
✅ GA4: Initialized with measurement ID: G-XXXXXXXXXX
📊 GA4: Page view tracked: /streamlit/home
```

### 3. Test Events

1. **Page Navigation:** Click between Home, Profile, and API pages
2. **Browser Network Tab:** Look for requests to `google-analytics.com/g/collect`
3. **GA4 DebugView:** View real-time events in GA4

### Streamlit Implementation Details

**Files Modified:**
- `src/medbilldozer/ui/analytics.py` - GA4 tracking module
- `src/medbilldozer/ui/page_router.py` - Track page navigation
- `src/medbilldozer/ui/bootstrap.py` - Initialize analytics on app start
- `config/constants.py` - GA4 configuration constant

**Key Functions:**
```python
from medbilldozer.ui.analytics import (
    initialize_ga4_for_streamlit,
    track_page_view,
    track_event
)

# Initialize once on app start (already done in bootstrap.py)
initialize_ga4_for_streamlit()

# Track page view
track_page_view('/streamlit/home', 'Home')

# Track custom event
track_event('navigation', category='user_action', label='button_click')
```

## Privacy Compliance

### What We Track ✅

- **Page Views:** Path only (e.g., `/`, `/login`, `/streamlit/home`)
- **Login Events:** Authentication method only (`google` or `github`)
- **Logout Events:** No parameters
- **Navigation:** High-level page transitions

### What We NEVER Track ❌

- ❌ User personal information (email, name, phone)
- ❌ Document names, contents, or metadata
- ❌ Medical data, diagnoses, or treatment information
- ❌ Financial amounts or billing data
- ❌ Analysis results or findings
- ❌ Any Protected Health Information (PHI)
- ❌ Query parameters (sanitized before tracking)

### Privacy Configuration

Both implementations use these GA4 settings:

```javascript
{
  'anonymize_ip': true,                        // Anonymize IP addresses
  'allow_ad_personalization_signals': false,   // Disable ad personalization
  'allow_google_signals': false,               // Disable Google signals
  'cookie_flags': 'SameSite=Strict;Secure'     // Secure cookies
}
```

## Troubleshooting

### No Events Appearing in GA4

1. **Check Measurement ID:** Verify it's correct and starts with `G-`
2. **Check Environment Variables:** Ensure they're set correctly
3. **Check Browser Console:** Look for GA4 initialization messages
4. **Use Debug Mode:** Enable GA4 DebugView for real-time event monitoring
5. **Wait for Data:** Standard GA4 reports can take 24-48 hours to populate

### Analytics Not Initializing

**React Frontend:**
```bash
# Check if environment variable is loaded
console.log(import.meta.env.VITE_GA4_MEASUREMENT_ID)

# Should output: G-XXXXXXXXXX
```

**Streamlit App:**
```python
import os
print(os.environ.get('GA4_MEASUREMENT_ID'))
# Should output: G-XXXXXXXXXX
```

### TypeScript Errors (React)

If you see TypeScript errors for `react-ga4`, ensure it's installed:

```bash
cd frontend
npm install react-ga4
```

## Viewing Analytics Data

### Real-Time Monitoring

1. Go to [Google Analytics](https://analytics.google.com/)
2. Select your property
3. Click **Reports** → **Realtime**
4. See live events as they happen

### Debug View

1. Go to **Admin** → **DebugView**
2. See detailed event information with parameters
3. Useful for development and testing

### Standard Reports

1. **Engagement** → **Pages and screens:** View page views
2. **Engagement** → **Events:** View all events (login, logout, etc.)
3. Custom reports can be created for specific metrics

## Production Deployment

### React Frontend (Vercel)

Add environment variable in Vercel dashboard:
- Variable: `VITE_GA4_MEASUREMENT_ID`
- Value: `G-XXXXXXXXXX`

### Backend API (Cloud Run)

Add secret in Google Secret Manager:
- Name: `GA4_MEASUREMENT_ID`
- Value: `G-XXXXXXXXXX`

Update Cloud Run service to use the secret.

### Streamlit App

Set environment variable in your deployment platform:
```bash
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
```

## Disabling Analytics

To disable analytics (e.g., for local development):

**React Frontend:**
```bash
# Remove or comment out in .env.local
# VITE_GA4_MEASUREMENT_ID=
```

**Streamlit App:**
```bash
# Remove or unset environment variable
unset GA4_MEASUREMENT_ID
```

Analytics will gracefully degrade - no errors will occur if the measurement ID is not set.

## HIPAA Compliance Notes

⚠️ **Important:** Google Analytics 4 does **NOT** provide Business Associate Agreements (BAAs) required for full HIPAA compliance.

This implementation is designed with privacy in mind:
- No PHI is transmitted
- Only high-level navigation events are tracked
- IP addresses are anonymized
- User identifiers are hashed or omitted

However, for strict HIPAA compliance, consider:
1. Self-hosted analytics (PostHog, Matomo)
2. Backend-only event logging to your Supabase database
3. Consulting with legal counsel on analytics requirements

## Additional Resources

- [Google Analytics 4 Documentation](https://support.google.com/analytics/answer/10089681)
- [react-ga4 Library](https://github.com/codler/react-ga4)
- [GA4 Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [Privacy-Focused Analytics Best Practices](https://support.google.com/analytics/answer/9019185)

## Support

For issues or questions about analytics setup:
- Check browser console for error messages
- Review GA4 DebugView for event details
- Verify environment variables are set correctly
- Consult this guide for privacy compliance

---

*Last Updated: February 19, 2026*
*Version: 0.3.0*
