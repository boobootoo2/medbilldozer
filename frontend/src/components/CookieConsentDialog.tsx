/**
 * Cookie consent dialog with granular preferences
 * Shows after user authentication to allow control over analytics and cookies
 */
import { useState } from 'react';
import { X, Cookie, Shield, BarChart3, Settings } from 'lucide-react';
import { useCookieConsent, CookiePreferences } from '../hooks/useCookieConsent';
import { useAuth } from '../hooks/useAuth';

export const CookieConsentDialog = () => {
  const { isAuthenticated } = useAuth();
  const {
    preferences: savedPreferences,
    showDialog,
    setShowDialog,
    savePreferences,
    acceptAll,
    acceptNecessary,
  } = useCookieConsent();

  const [showCustomize, setShowCustomize] = useState(false);
  const [customPreferences, setCustomPreferences] = useState<CookiePreferences>(savedPreferences);

  // Only show dialog if user is authenticated
  if (!showDialog || !isAuthenticated) {
    return null;
  }

  const handleAcceptAll = () => {
    acceptAll();
  };

  const handleAcceptNecessary = () => {
    acceptNecessary();
  };

  const handleSaveCustom = () => {
    savePreferences(customPreferences);
  };

  const togglePreference = (key: keyof CookiePreferences) => {
    if (key === 'necessary') return; // Cannot disable necessary cookies
    setCustomPreferences((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white rounded-2xl shadow-2xl m-4">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Cookie className="w-6 h-6" />
              <h2 className="text-xl font-bold">Cookie Preferences</h2>
            </div>
          </div>
          <p className="text-blue-100 text-sm mt-2">
            We use cookies to improve your experience and understand how our app is used.
          </p>
        </div>

        {/* Content */}
        <div className="p-6">
          {!showCustomize ? (
            // Simple view
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">Your Privacy Matters</h3>
                    <p className="text-sm text-gray-700">
                      We respect your privacy and are committed to protecting your personal
                      information. You can choose which cookies to accept below.
                    </p>
                  </div>
                </div>
              </div>

              {/* Quick options */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div className="border-2 border-gray-200 rounded-xl p-4 hover:border-blue-400 transition-colors">
                  <h3 className="font-semibold text-gray-900 mb-2">Essential Only</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Only cookies required for the app to function. No analytics or tracking.
                  </p>
                  <button
                    onClick={handleAcceptNecessary}
                    className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                  >
                    Accept Essential
                  </button>
                </div>

                <div className="border-2 border-blue-500 rounded-xl p-4 bg-blue-50">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-gray-900">All Cookies</h3>
                    <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">
                      Recommended
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">
                    Help us improve by allowing analytics. We anonymize all data and never track PHI.
                  </p>
                  <button
                    onClick={handleAcceptAll}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    Accept All
                  </button>
                </div>
              </div>

              {/* Customize button */}
              <div className="text-center mt-6">
                <button
                  onClick={() => setShowCustomize(true)}
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center gap-2 mx-auto"
                >
                  <Settings className="w-4 h-4" />
                  Customize Preferences
                </button>
              </div>
            </div>
          ) : (
            // Detailed customization view
            <div className="space-y-4">
              <button
                onClick={() => setShowCustomize(false)}
                className="text-blue-600 hover:text-blue-700 font-medium text-sm mb-4"
              >
                ← Back to simple view
              </button>

              {/* Necessary cookies */}
              <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <Shield className="w-5 h-5 text-gray-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h3 className="font-semibold text-gray-900">Necessary Cookies</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Required for authentication and core app functionality. These cannot be
                        disabled.
                      </p>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="w-12 h-6 bg-gray-300 rounded-full flex items-center px-1">
                      <div className="w-4 h-4 bg-white rounded-full shadow-sm ml-auto"></div>
                    </div>
                    <span className="text-xs text-gray-500 mt-1 block">Always On</span>
                  </div>
                </div>
              </div>

              {/* Analytics cookies */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <BarChart3 className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h3 className="font-semibold text-gray-900">Analytics Cookies</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Help us understand how you use the app so we can improve it. We use Google
                        Analytics with IP anonymization and never track PHI or personal data.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => togglePreference('analytics')}
                    className="ml-4"
                  >
                    <div
                      className={`w-12 h-6 rounded-full flex items-center px-1 transition-colors ${
                        customPreferences.analytics ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${
                          customPreferences.analytics ? 'ml-auto' : ''
                        }`}
                      ></div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Functional cookies */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <Settings className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h3 className="font-semibold text-gray-900">Functional Cookies</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Remember your preferences and settings for a better experience (theme,
                        language, etc.).
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => togglePreference('functional')}
                    className="ml-4"
                  >
                    <div
                      className={`w-12 h-6 rounded-full flex items-center px-1 transition-colors ${
                        customPreferences.functional ? 'bg-purple-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${
                          customPreferences.functional ? 'ml-auto' : ''
                        }`}
                      ></div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Save button */}
              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleSaveCustom}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Save Preferences
                </button>
                <button
                  onClick={handleAcceptAll}
                  className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
                >
                  Accept All
                </button>
              </div>
            </div>
          )}

          {/* Footer note */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              You can change your cookie preferences at any time in your account settings. For more
              information, see our Privacy Policy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
