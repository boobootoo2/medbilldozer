# MedBillDozer Frontend

Modern React + TypeScript frontend for MedBillDozer medical billing analysis.

## Features

- **Firebase Authentication** - Google/GitHub OAuth login
- **Document Upload** - Drag-and-drop with direct GCS uploads
- **Real-time Analysis** - Poll for analysis results with MedGemma
- **Responsive UI** - Tailwind CSS with mobile-first design
- **Type-Safe** - Full TypeScript coverage

## Tech Stack

- **React 18** - Component-based UI
- **TypeScript** - Type safety
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Firebase Auth** - OAuth 2.0 authentication
- **Axios** - HTTP client with interceptors
- **Zustand** - Lightweight state management
- **React Router** - Client-side routing
- **React Dropzone** - File upload UI

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local` with your credentials:

```bash
# Backend API
VITE_API_BASE_URL=http://localhost:8080

# Firebase Configuration
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### 3. Run Development Server

```bash
npm run dev
```

App will be available at: http://localhost:5173

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginButton.tsx       # OAuth login UI
│   │   │   ├── ProtectedRoute.tsx    # Route guard
│   │   │   └── UserMenu.tsx          # User menu dropdown
│   │   ├── documents/
│   │   │   ├── DocumentUpload.tsx    # Drag-drop upload
│   │   │   └── DocumentList.tsx      # Document list with selection
│   │   └── analysis/
│   │       ├── AnalysisDashboard.tsx # Main results view
│   │       ├── IssueCard.tsx         # Issue display
│   │       └── SavingsCalculator.tsx # Savings summary
│   ├── pages/
│   │   └── HomePage.tsx              # Main dashboard
│   ├── hooks/
│   │   └── useAuth.ts                # Firebase Auth hook
│   ├── services/
│   │   ├── api.ts                    # Axios instance
│   │   ├── documents.service.ts      # Document API
│   │   └── analysis.service.ts       # Analysis API
│   ├── stores/
│   │   └── authStore.ts              # Auth state (Zustand)
│   ├── types/
│   │   └── index.ts                  # TypeScript types
│   ├── lib/
│   │   └── firebase.ts               # Firebase config
│   ├── App.tsx                       # Root component
│   ├── main.tsx                      # Entry point
│   └── index.css                     # Global styles
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## Key Components

### Authentication Flow

```typescript
// useAuth.ts - Firebase Auth integration
const { user, loginWithGoogle, logout, isAuthenticated } = useAuth();

// Automatic token exchange with backend
// Stores JWT in localStorage and httpOnly cookie
```

### Document Upload Flow

```typescript
// 1. Get signed URL from backend
const { upload_url, document_id } = await getUploadUrl(file.name, file.type);

// 2. Upload directly to GCS
await fetch(upload_url, { method: 'PUT', body: file });

// 3. Confirm with backend
await confirmUpload(document_id, gcs_path, file.size);
```

### Analysis Polling

```typescript
// Poll for analysis completion
await analysisService.pollAnalysis(analysisId, (analysis) => {
  setAnalysis(analysis); // Update UI on each poll
});
```

## API Integration

All API calls go through `services/api.ts` with automatic:
- JWT token attachment
- Token refresh on 401
- Error handling

Example:
```typescript
import api from './services/api';

// Automatically includes Authorization header
const response = await api.post('/api/analyze', { document_ids });
```

## Deployment

### Option 1: Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
```

### Option 2: Google Cloud Run

```bash
# Build Docker image
docker build -t gcr.io/PROJECT_ID/medbilldozer-frontend .

# Push to GCR
docker push gcr.io/PROJECT_ID/medbilldozer-frontend

# Deploy to Cloud Run
gcloud run deploy medbilldozer-frontend \
  --image gcr.io/PROJECT_ID/medbilldozer-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Production Build

```bash
npm run build
# Output in dist/
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `https://api.medbilldozer.com` |
| `VITE_FIREBASE_API_KEY` | Firebase API key | `AIza...` |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase auth domain | `project.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | Firebase project ID | `medbilldozer` |
| `VITE_FIREBASE_STORAGE_BUCKET` | Firebase storage | `project.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase sender | `123456789` |
| `VITE_FIREBASE_APP_ID` | Firebase app ID | `1:123:web:abc` |

## Features Overview

### 1. Authentication
- Google OAuth login
- GitHub OAuth login
- Automatic JWT token management
- Persistent sessions

### 2. Document Management
- Drag-and-drop upload
- Direct upload to GCS (no backend bottleneck)
- Document type classification
- Download with signed URLs
- Delete documents

### 3. Analysis
- Trigger MedGemma analysis
- Real-time polling for results
- Savings calculator
- Issue cards with evidence
- Cross-document coverage matrix

### 4. UI/UX
- Responsive design (mobile, tablet, desktop)
- Loading states
- Error handling
- Toast notifications
- Accessible (keyboard navigation)

## Development

### Run in Development Mode

```bash
npm run dev
```

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

### Type Checking

```bash
tsc --noEmit
```

### Linting

```bash
npm run lint
```

## Troubleshooting

### Backend Connection Issues
- Verify `VITE_API_BASE_URL` is correct
- Check CORS configuration in backend
- Ensure backend is running

### Firebase Auth Issues
- Verify Firebase credentials in `.env.local`
- Check Firebase Console for enabled providers
- Ensure authorized domains include localhost:5173

### Upload Issues
- Check GCS CORS configuration
- Verify signed URLs are not expired
- Check browser console for errors

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome)

## Performance

- Initial load: < 2s
- Time to Interactive: < 3s
- Bundle size: ~200KB gzipped
- Lighthouse score: 90+ (Performance, Accessibility, Best Practices)

## Security

- httpOnly cookies for refresh tokens
- JWT access tokens in memory only
- HTTPS required in production
- Input sanitization
- XSS protection

## License

Proprietary - MedBillDozer
