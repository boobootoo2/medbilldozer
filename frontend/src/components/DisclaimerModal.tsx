/**
 * Legal Disclaimer Modal - Must be accepted before using the application
 */
import { useState, useEffect } from 'react';

export const DisclaimerModal = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Check if user has already accepted the disclaimer
    const hasAccepted = localStorage.getItem('disclaimer_accepted');
    if (!hasAccepted) {
      setIsOpen(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('disclaimer_accepted', 'true');
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-75 transition-opacity"></div>

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all w-full max-w-2xl">
          {/* Header */}
          <div className="bg-gradient-to-r from-red-600 to-orange-600 px-6 py-4">
            <div className="flex items-center gap-3">
              <svg
                className="h-8 w-8 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <h2 className="text-2xl font-bold text-white">
                Important Legal Disclaimer
              </h2>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            <div className="space-y-4 text-gray-700">
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                <p className="font-semibold text-yellow-800 text-lg mb-2">
                  ⚠️ PROTOTYPE SYSTEM - READ CAREFULLY
                </p>
              </div>

              <div className="space-y-3 text-sm">
                <p className="font-semibold text-lg text-gray-900">
                  By using this system, you acknowledge and agree to the following:
                </p>

                <div className="space-y-3 pl-4">
                  <div className="flex gap-2">
                    <span className="text-red-600 font-bold">❌</span>
                    <p>
                      <strong>This is a PROTOTYPE system</strong> that has NOT undergone legal or regulatory review.
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <span className="text-red-600 font-bold">❌</span>
                    <p>
                      <strong>DO NOT post any personal medical information</strong> (PHI) or personally identifiable information (PII) in this system.
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <span className="text-red-600 font-bold">❌</span>
                    <p>
                      <strong>NO data protection guarantees.</strong> This system is not HIPAA-compliant and offers no security or privacy guarantees.
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <span className="text-orange-600 font-bold">⚠️</span>
                    <p>
                      <strong>Data will be periodically purged</strong> from this system without notice. Do not rely on this system for permanent storage.
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <span className="text-orange-600 font-bold">⚠️</span>
                    <p>
                      <strong>NO service guarantees.</strong> This system may be unavailable, modified, or discontinued at any time without notice.
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <span className="text-orange-600 font-bold">⚠️</span>
                    <p>
                      <strong>FOR DEMONSTRATION PURPOSES ONLY.</strong> Do not use this system for actual medical billing decisions or patient care.
                    </p>
                  </div>
                </div>

                <div className="bg-gray-100 p-4 rounded-lg mt-4">
                  <p className="text-xs text-gray-600 italic">
                    This system uses AI models that may produce inaccurate or incomplete results.
                    Always consult qualified medical billing professionals and legal counsel for actual billing matters.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 flex justify-end gap-4">
            <button
              onClick={() => window.location.href = 'https://google.com'}
              className="px-6 py-3 text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              I Do Not Accept (Exit)
            </button>
            <button
              onClick={handleAccept}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              I Understand and Accept
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
