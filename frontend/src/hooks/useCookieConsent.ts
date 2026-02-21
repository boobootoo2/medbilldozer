/**
 * Hook for managing cookie consent preferences
 * Stores user's analytics and cookie preferences in localStorage
 */
import { useState, useEffect } from 'react';

export interface CookiePreferences {
  necessary: boolean; // Always true, required for app functionality
  analytics: boolean; // Google Analytics tracking
  functional: boolean; // Future: feature preferences, settings
}

const STORAGE_KEY = 'medbilldozer_cookie_consent';
const CONSENT_SHOWN_KEY = 'medbilldozer_consent_shown';

const DEFAULT_PREFERENCES: CookiePreferences = {
  necessary: true, // Always enabled
  analytics: false, // Opt-in
  functional: true, // Enabled by default
};

export const useCookieConsent = () => {
  const [preferences, setPreferences] = useState<CookiePreferences>(DEFAULT_PREFERENCES);
  const [hasConsented, setHasConsented] = useState<boolean>(false);
  const [showDialog, setShowDialog] = useState<boolean>(false);

  // Load preferences from localStorage on mount
  useEffect(() => {
    const storedPreferences = localStorage.getItem(STORAGE_KEY);
    const consentShown = localStorage.getItem(CONSENT_SHOWN_KEY);

    if (storedPreferences) {
      try {
        const parsed = JSON.parse(storedPreferences);
        setPreferences({ ...DEFAULT_PREFERENCES, ...parsed });
        setHasConsented(true);
      } catch (error) {
        console.error('Failed to parse cookie preferences:', error);
      }
    }

    // Show dialog if user has never seen it
    if (!consentShown) {
      setShowDialog(true);
    }
  }, []);

  /**
   * Save user's cookie preferences
   */
  const savePreferences = (newPreferences: Partial<CookiePreferences>) => {
    const updated: CookiePreferences = {
      necessary: true, // Always true
      analytics: newPreferences.analytics ?? preferences.analytics,
      functional: newPreferences.functional ?? preferences.functional,
    };

    setPreferences(updated);
    setHasConsented(true);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    localStorage.setItem(CONSENT_SHOWN_KEY, 'true');
    setShowDialog(false);
  };

  /**
   * Accept all cookies
   */
  const acceptAll = () => {
    savePreferences({
      analytics: true,
      functional: true,
    });
  };

  /**
   * Accept only necessary cookies
   */
  const acceptNecessary = () => {
    savePreferences({
      analytics: false,
      functional: false,
    });
  };

  /**
   * Reset consent and show dialog again
   */
  const resetConsent = () => {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(CONSENT_SHOWN_KEY);
    setPreferences(DEFAULT_PREFERENCES);
    setHasConsented(false);
    setShowDialog(true);
  };

  return {
    preferences,
    hasConsented,
    showDialog,
    setShowDialog,
    savePreferences,
    acceptAll,
    acceptNecessary,
    resetConsent,
  };
};
