/**
 * Mock Insurance & Provider Connection Interface
 * Demonstrates what integration would look like with real partners
 */
import { useState } from 'react';
import { X, Shield, AlertCircle } from 'lucide-react';

interface InsuranceProvider {
  id: string;
  name: string;
  logo: string;
  type: 'insurance' | 'provider';
  description: string;
}

const MOCK_INSURERS: InsuranceProvider[] = [
  { id: 'uhc', name: 'UnitedHealthcare', logo: '🏥', type: 'insurance', description: 'National health insurance provider' },
  { id: 'anthem', name: 'Anthem', logo: '🔵', type: 'insurance', description: 'Blue Cross Blue Shield affiliate' },
  { id: 'aetna', name: 'Aetna', logo: '💚', type: 'insurance', description: 'CVS Health insurance division' },
  { id: 'cigna', name: 'Cigna', logo: '🌐', type: 'insurance', description: 'Global health services company' },
  { id: 'bcbs', name: 'Blue Cross Blue Shield', logo: '🔷', type: 'insurance', description: 'Federation of health insurance organizations' },
  { id: 'humana', name: 'Humana', logo: '💛', type: 'insurance', description: 'Medicare Advantage specialist' },
];

const MOCK_PROVIDERS: InsuranceProvider[] = [
  { id: 'mayo', name: 'Mayo Clinic', logo: '🏨', type: 'provider', description: 'Leading academic medical center' },
  { id: 'cleveland', name: 'Cleveland Clinic', logo: '🏥', type: 'provider', description: 'Nonprofit academic medical center' },
  { id: 'kaiser', name: 'Kaiser Permanente', logo: '⚕️', type: 'provider', description: 'Integrated managed care consortium' },
  { id: 'hca', name: 'HCA Healthcare', logo: '🏥', type: 'provider', description: 'Largest for-profit hospital operator' },
];

interface InsuranceConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect?: (providerId: string) => void;
}

export const InsuranceConnectionModal = ({ isOpen, onClose, onConnect }: InsuranceConnectionModalProps) => {
  const [selectedTab, setSelectedTab] = useState<'insurance' | 'provider'>('insurance');
  const [connecting, setConnecting] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleConnect = async (provider: InsuranceProvider) => {
    setSelectedProvider(provider.id);
    setConnecting(true);

    // Simulate connection process
    await new Promise(resolve => setTimeout(resolve, 2000));

    setConnecting(false);
    setSelectedProvider(null);

    if (onConnect) {
      onConnect(provider.id);
    }
  };

  const providers = selectedTab === 'insurance' ? MOCK_INSURERS : MOCK_PROVIDERS;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose}></div>

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all w-full max-w-4xl">
          {/* Disclaimer Banner */}
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-semibold mb-1">PROTOTYPE DEMONSTRATION ONLY</p>
                <p>
                  This is a mockup of what real insurance & provider integrations would look like
                  if MedBillDozer had partnerships similar to Plaid's banking connections.
                  <strong className="block mt-1">No actual connections are made. This is for demonstration purposes only.</strong>
                </p>
              </div>
            </div>
          </div>

          {/* Header */}
          <div className="px-6 py-4 border-b">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Shield className="w-6 h-6 text-blue-600" />
                  Connect Your Healthcare Accounts
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Securely import your medical bills and claims data
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b">
            <div className="flex px-6">
              <button
                onClick={() => setSelectedTab('insurance')}
                className={`
                  px-6 py-3 font-medium border-b-2 transition-colors
                  ${selectedTab === 'insurance'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'}
                `}
              >
                Insurance Companies ({MOCK_INSURERS.length})
              </button>
              <button
                onClick={() => setSelectedTab('provider')}
                className={`
                  px-6 py-3 font-medium border-b-2 transition-colors
                  ${selectedTab === 'provider'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'}
                `}
              >
                Healthcare Providers ({MOCK_PROVIDERS.length})
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-6 max-h-[60vh] overflow-y-auto">
            <div className="grid grid-cols-2 gap-4">
              {providers.map((provider) => (
                <div
                  key={provider.id}
                  className="p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer group"
                  onClick={() => !connecting && handleConnect(provider)}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-2xl flex-shrink-0">
                      {provider.logo}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {provider.name}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {provider.description}
                      </p>
                      {selectedProvider === provider.id && connecting ? (
                        <div className="mt-3 flex items-center gap-2 text-sm text-blue-600">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                          Connecting...
                        </div>
                      ) : (
                        <button className="mt-3 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors group-hover:shadow-md">
                          Connect Account
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Security Notice */}
          <div className="px-6 py-4 bg-gray-50 border-t">
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-gray-700">
                <p className="font-medium text-gray-900">Bank-level security</p>
                <p className="text-gray-600 mt-1">
                  In a production system, connections would use OAuth 2.0 and 256-bit encryption.
                  We never store your login credentials.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
