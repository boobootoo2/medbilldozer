/**
 * Firebase configuration and initialization
 */
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, GithubAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);

// Initialize Auth
export const auth = getAuth(app);

// Configure reCAPTCHA settings to prevent autocomplete warnings
if (typeof window !== 'undefined') {
  // Set reCAPTCHA language and size
  (window as any).recaptchaOptions = {
    useRecaptchaNet: true,
    badge: 'bottomright'
  };

  // Disable autocomplete warnings by setting the reCAPTCHA verifier to use invisible mode
  auth.settings.appVerificationDisabledForTesting = false;
}

// Auth providers
export const googleProvider = new GoogleAuthProvider();
export const githubProvider = new GithubAuthProvider();
