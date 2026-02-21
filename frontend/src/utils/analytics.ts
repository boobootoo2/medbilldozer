/**
 * Google Analytics 4 (GA4) utility for privacy-focused event tracking
 *
 * Privacy Configuration:
 * - Anonymizes IP addresses
 * - Disables advertising features
 * - Disables Google signals
 * - Only tracks high-level navigation events (NO PHI)
 */

import ReactGA from 'react-ga4';

// Initialize flag to prevent double initialization
let isInitialized = false;

// Storage key for cookie consent (must match useCookieConsent hook)
const CONSENT_STORAGE_KEY = 'medbilldozer_cookie_consent';

/**
 * Check if user has consented to analytics cookies
 * @returns true if user has consented to analytics
 */
const hasAnalyticsConsent = (): boolean => {
  try {
    const storedConsent = localStorage.getItem(CONSENT_STORAGE_KEY);
    if (!storedConsent) {
      return false; // No consent given yet
    }

    const preferences = JSON.parse(storedConsent);
    return preferences.analytics === true;
  } catch (error) {
    console.error('❌ GA4: Failed to check consent:', error);
    return false;
  }
};

/**
 * Initialize Google Analytics 4 with privacy-focused configuration
 * Only initializes if user has consented to analytics cookies
 *
 * @returns true if initialization successful, false otherwise
 */
export const initGA = (): boolean => {
  const measurementId = import.meta.env.VITE_GA4_MEASUREMENT_ID;

  // Skip if no measurement ID provided
  if (!measurementId) {
    console.warn('⚠️  GA4: No measurement ID provided. Analytics disabled.');
    return false;
  }

  // Check for user consent before initializing
  if (!hasAnalyticsConsent()) {
    console.log('ℹ️  GA4: User has not consented to analytics. Skipping initialization.');
    return false;
  }

  // Skip if already initialized
  if (isInitialized) {
    console.log('✅ GA4: Already initialized');
    return true;
  }

  try {
    ReactGA.initialize(measurementId, {
      gtagOptions: {
        // Privacy-focused configuration
        anonymize_ip: true,                      // Anonymize IP addresses (HIPAA consideration)
        allow_ad_personalization_signals: false, // Disable ad personalization
        allow_google_signals: false,             // Disable Google signals
        cookie_flags: 'SameSite=Strict;Secure',  // Secure cookie settings
      },
    });

    isInitialized = true;
    console.log('✅ GA4: Initialized with measurement ID:', measurementId);
    return true;
  } catch (error) {
    console.error('❌ GA4: Initialization failed:', error);
    return false;
  }
};

/**
 * Track a page view event
 * Only tracks if user has consented to analytics
 *
 * @param path - Page path (sanitized, no query params with PHI)
 * @param title - Optional page title
 */
export const trackPageView = (path: string, title?: string): void => {
  if (!isInitialized || !hasAnalyticsConsent()) {
    return;
  }

  try {
    // Sanitize path: remove query parameters to avoid tracking PHI
    const sanitizedPath = path.split('?')[0];

    ReactGA.send({
      hitType: 'pageview',
      page: sanitizedPath,
      title: title || sanitizedPath,
    });

    console.log('📊 GA4: Page view tracked:', sanitizedPath);
  } catch (error) {
    console.error('❌ GA4: Page view tracking failed:', error);
  }
};

/**
 * Track a custom event (high-level only, NO PHI)
 * Only tracks if user has consented to analytics
 *
 * Allowed events:
 * - login (with method parameter only)
 * - logout
 * - navigation
 *
 * @param eventName - Name of the event
 * @param parameters - Optional event parameters (must NOT contain PHI)
 */
export const trackEvent = (
  eventName: string,
  parameters?: Record<string, any>
): void => {
  if (!isInitialized || !hasAnalyticsConsent()) {
    return;
  }

  try {
    // Sanitize parameters: only allow specific safe parameters
    const safeParameters = sanitizeEventParameters(parameters);

    ReactGA.event(eventName, safeParameters);

    console.log('📊 GA4: Event tracked:', eventName, safeParameters);
  } catch (error) {
    console.error('❌ GA4: Event tracking failed:', error);
  }
};

/**
 * Sanitize event parameters to ensure no PHI is tracked
 *
 * Allowed parameters:
 * - method (for login events: 'google', 'github')
 * - category (general categorization)
 * - action (general action type)
 *
 * NEVER track:
 * - User email, name, or any PII
 * - Document names or contents
 * - Medical data or amounts
 * - Any PHI
 */
const sanitizeEventParameters = (
  parameters?: Record<string, any>
): Record<string, any> => {
  if (!parameters) {
    return {};
  }

  const allowedKeys = ['method', 'category', 'action', 'label'];
  const sanitized: Record<string, any> = {};

  for (const key of allowedKeys) {
    if (parameters[key] !== undefined) {
      // Only include safe, non-PHI values
      sanitized[key] = String(parameters[key]);
    }
  }

  return sanitized;
};

/**
 * Track user login event (authentication method only)
 *
 * @param method - Authentication method ('google', 'github', etc.)
 */
export const trackLogin = (method: string): void => {
  trackEvent('login', {
    method: method,
    category: 'authentication',
  });
};

/**
 * Track user logout event
 */
export const trackLogout = (): void => {
  trackEvent('logout', {
    category: 'authentication',
  });
};

/**
 * Check if GA4 is initialized and available
 *
 * @returns true if GA4 is initialized, false otherwise
 */
export const isGAInitialized = (): boolean => {
  return isInitialized;
};
