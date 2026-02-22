import { initializeApp } from 'firebase/app';

// Dynamically determine auth domain based on current hostname
const getAuthDomain = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;

        // Local development
        if (hostname === 'localhost') {
            return 'localhost';
        }

        // Vercel deployments - use the actual deployment URL
        if (hostname.includes('vercel.app')) {
            return hostname;
        }

        // Production or other domains
        return 'medbilldozer.firebaseapp.com';
    }

    // Server-side fallback
    return 'medbilldozer.firebaseapp.com';
};

const firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY || "your-api-key",
    authDomain: getAuthDomain(),
    projectId: "medbilldozer",
    storageBucket: "medbilldozer.appspot.com",
    messagingSenderId: "your-sender-id",
    appId: "your-app-id"
};

const app = initializeApp(firebaseConfig);

export default app;
