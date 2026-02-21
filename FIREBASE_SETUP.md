# Firebase Domain Authorization Setup

## Issue
Your Vercel deployments need to be added to Firebase's authorized domains list to enable Google OAuth authentication.

## Domains to Add

Add these domains to Firebase:
1. `frontend-five-umber-24.vercel.app` (Production/Aliased)
2. `frontend-eopdl2k8d-john-shultzs-projects.vercel.app` (Deployment-specific)

## Steps to Add Authorized Domains

### Method 1: Firebase Console (Recommended)

1. **Open Firebase Console**
   - Visit: https://console.firebase.google.com/project/medbilldozer/authentication/settings
   - Or navigate to: Firebase Console → medbilldozer → Authentication → Settings → Authorized domains

2. **Add Domain**
   - Click "Add domain" button
   - Enter: `frontend-five-umber-24.vercel.app`
   - Click "Add"

3. **Add Second Domain**
   - Click "Add domain" again
   - Enter: `frontend-eopdl2k8d-john-shultzs-projects.vercel.app`
   - Click "Add"

4. **Verify**
   - You should now see both domains in the authorized domains list
   - They should appear alongside any existing domains like `localhost` and `medbilldozer.firebaseapp.com`

### Method 2: Using Firebase API (Advanced)

If you prefer to use the API, you can use the Firebase Management API:

```bash
# Get current authorized domains
curl -X GET \
  "https://identitytoolkit.googleapis.com/v1/projects/medbilldozer/config" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)"

# Add domains via API (requires proper authentication)
```

## After Adding Domains

1. **Test Authentication**
   - Visit your production URL: https://frontend-five-umber-24.vercel.app
   - Try logging in with Google
   - You should no longer see the "unauthorized domain" error

2. **Verify Console Messages**
   - Open browser DevTools (F12)
   - Check for these confirmations:
     - ✅ No "auth/unauthorized-domain" errors
     - ✅ GA4 measurement ID detected
     - ✅ Firebase authentication working

## Troubleshooting

### Still seeing unauthorized domain error?
- Clear browser cache and cookies
- Try in incognito/private browsing mode
- Wait 1-2 minutes for Firebase to propagate the changes
- Verify the exact domain name matches (no typos, no http/https prefix)

### GA4 Analytics not working?
- Check that `VITE_FIREBASE_MEASUREMENT_ID` is set in Vercel environment variables
- Verify the build logs show the environment variables are being used
- Check browser console for any GA4 initialization errors

## Current Environment Variables in Vercel

All Firebase environment variables have been configured:
- ✅ VITE_API_BASE_URL
- ✅ VITE_FIREBASE_API_KEY
- ✅ VITE_FIREBASE_AUTH_DOMAIN
- ✅ VITE_FIREBASE_PROJECT_ID
- ✅ VITE_FIREBASE_STORAGE_BUCKET
- ✅ VITE_FIREBASE_MESSAGING_SENDER_ID
- ✅ VITE_FIREBASE_APP_ID
- ✅ VITE_FIREBASE_MEASUREMENT_ID
- ✅ VITE_INVITE_CODES

## Quick Links

- Firebase Console: https://console.firebase.google.com/project/medbilldozer/authentication/settings
- Vercel Dashboard: https://vercel.com/john-shultzs-projects/frontend
- Production URL: https://frontend-five-umber-24.vercel.app
- Deployment URL: https://frontend-eopdl2k8d-john-shultzs-projects.vercel.app
