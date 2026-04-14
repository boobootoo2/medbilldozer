/**
 * Authentication hook with Firebase Auth integration
 */
import { useEffect, useRef } from 'react';
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
import axios from 'axios';

export const useAuth = () => {
  const { user, accessToken, loading, error, setUser, setAccessToken, setLoading, setError, logout } = useAuthStore();
  const isProcessingRef = useRef(false);

  useEffect(() => {

    // Listen for auth state changes from Firebase
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      // Prevent concurrent authentication attempts
      if (isProcessingRef.current) {
        console.log('⏭️  Skipping - authentication already in progress');
        return;
      }

      if (firebaseUser) {
        // Check if we already have a valid token in localStorage
        const existingToken = localStorage.getItem('access_token');
        if (existingToken && user) {
          // Verify token is not expired
          try {
            const payload = JSON.parse(atob(existingToken.split('.')[1]));
            const isExpired = Date.now() > payload.exp * 1000;
            if (!isExpired) {
              console.log('✅ Already authenticated - using existing valid session');
              setLoading(false);
              return;
            }
            console.log('⚠️  Token expired - re-authenticating with backend...');
          } catch (e) {
            console.log('⚠️  Invalid token - re-authenticating with backend...');
          }
        }

        isProcessingRef.current = true;
        setLoading(true);

        try {
          console.log('🔄 Authenticating with backend...');

          // Add token debugging
          const idToken = await firebaseUser.getIdToken();
          console.log('🔑 ID Token length:', idToken.length);
          console.log('🔑 Token preview:', idToken.substring(0, 50) + '...');

          const response = await axios.post(
            `${import.meta.env.VITE_API_URL}/api/auth/login`,
            {},
            {
              headers: {
                'Authorization': `Bearer ${idToken}`,
                'Content-Type': 'application/json',
              },
              withCredentials: true, // Important for cookies
            }
          );

          const { access_token, refresh_token, user: backendUser } = response.data;

          // Store tokens
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          // Update store
          setUser(backendUser);
          setAccessToken(access_token);
          setLoading(false);
          console.log('✅ Authentication successful!');
        } catch (err: any) {
          console.error('Backend authentication failed:', err);
          
          // Provide user-friendly error messages
          let errorMessage = 'Authentication failed';
          
          if (err.response?.status === 503 || err.response?.status === 500) {
            errorMessage = 'Service temporarily unavailable. Please try again in a moment.';
          } else if (err.response?.status === 401) {
            errorMessage = 'Authentication failed. Please try logging in again.';
          } else if (err.code === 'ERR_NETWORK') {
            errorMessage = 'Network error. Please check your connection.';
          }
          
          setError(errorMessage);
          setLoading(false);
          // Sign out from Firebase on backend auth failure
          await signOut(auth);
        } finally {
          isProcessingRef.current = false;
        }
      } else {
        // User logged out
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
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
