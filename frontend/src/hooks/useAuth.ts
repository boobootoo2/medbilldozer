/**
 * Authentication hook with Firebase Auth integration
 */
import { useEffect } from 'react';
import {
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  User as FirebaseUser
} from 'firebase/auth';
import { auth, googleProvider, githubProvider } from '../lib/firebase';
import { useAuthStore } from '../stores/authStore';
import api from '../services/api';
import { LoginResponse } from '../types';

export const useAuth = () => {
  const { user, accessToken, loading, error, setUser, setAccessToken, setLoading, setError, logout } = useAuthStore();

  useEffect(() => {
    // Listen for auth state changes from Firebase
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      if (firebaseUser) {
        try {
          // Get Firebase ID token
          const idToken = await firebaseUser.getIdToken();

          // Exchange Firebase token with backend
          const response = await api.post<LoginResponse>('/api/auth/login', {
            firebase_id_token: idToken
          });

          const { access_token, refresh_token, user: backendUser } = response.data;

          // Store tokens
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          // Update store
          setUser(backendUser);
          setAccessToken(access_token);
          setLoading(false);
        } catch (err: any) {
          console.error('Backend authentication failed:', err);
          setError(err.message || 'Authentication failed');
          setLoading(false);
        }
      } else {
        // User logged out
        setUser(null);
        setAccessToken(null);
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [setUser, setAccessToken, setLoading, setError]);

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      setError(null);
      await signInWithPopup(auth, googleProvider);
      // onAuthStateChanged will handle the rest
    } catch (err: any) {
      console.error('Google login failed:', err);
      setError(err.message || 'Login failed');
      setLoading(false);
    }
  };

  const loginWithGithub = async () => {
    try {
      setLoading(true);
      setError(null);
      await signInWithPopup(auth, githubProvider);
      // onAuthStateChanged will handle the rest
    } catch (err: any) {
      console.error('GitHub login failed:', err);
      setError(err.message || 'Login failed');
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      // Logout from Firebase
      await signOut(auth);

      // Logout from backend
      await api.post('/api/auth/logout');

      // Clear local state
      logout();
    } catch (err: any) {
      console.error('Logout failed:', err);
      setError(err.message || 'Logout failed');
    }
  };

  return {
    user,
    accessToken,
    loading,
    error,
    loginWithGoogle,
    loginWithGithub,
    logout: handleLogout,
    isAuthenticated: !!user && !!accessToken,
  };
};
