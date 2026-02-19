/**
 * Invite Code Gate - Validates invite code before showing OAuth login
 */
import { useState } from 'react';
import { LoginButton } from './LoginButton';

// Valid invite codes from environment variable
const VALID_INVITE_CODES = (import.meta.env.VITE_INVITE_CODES || 'MEDBILL2024')
  .split(',')
  .map((code: string) => code.trim().toUpperCase());

export const InviteCodeGate = () => {
  const [inviteCode, setInviteCode] = useState('');
  const [isValidated, setIsValidated] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Validate invite code
    if (VALID_INVITE_CODES.includes(inviteCode.toUpperCase())) {
      setIsValidated(true);
      // Store in sessionStorage so it persists during OAuth flow
      sessionStorage.setItem('invite_code_validated', 'true');
      sessionStorage.setItem('used_invite_code', inviteCode.toUpperCase());
    } else {
      setError('Invalid invite code. Please contact admin for access.');
    }

    setLoading(false);
  };

  // If already validated, show the login button
  if (isValidated || sessionStorage.getItem('invite_code_validated') === 'true') {
    return <LoginButton />;
  }

  // Show invite code input
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">MedBillDozer</h1>
          <p className="text-gray-600">AI-Powered Medical Billing Analysis</p>
        </div>

        <div className="mb-6">
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
            <p className="text-sm text-blue-800">
              <span className="font-semibold">🔐 Invite-Only Access</span>
              <br />
              Enter your invite code to continue
            </p>
          </div>

          <form onSubmit={handleValidate}>
            <div className="mb-4">
              <label htmlFor="inviteCode" className="block text-sm font-medium text-gray-700 mb-2">
                Invite Code
              </label>
              <input
                type="text"
                id="inviteCode"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all uppercase"
                placeholder="Enter invite code"
                required
                autoFocus
                disabled={loading}
              />
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !inviteCode.trim()}
              className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Validating...
                </span>
              ) : (
                'Continue'
              )}
            </button>
          </form>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Don't have an invite code?</p>
          <a href="mailto:support@medbilldozer.com" className="text-blue-600 hover:text-blue-800 font-medium">
            Request Access
          </a>
        </div>
      </div>
    </div>
  );
};
