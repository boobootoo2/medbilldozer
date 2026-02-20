/**
 * Home page - Document upload and analysis
 */
import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Link as LinkIcon, FileText } from 'lucide-react';
import { UserMenu } from '../components/auth/UserMenu';
import { MultiFileUpload } from '../components/documents/MultiFileUpload';
import { DocumentList, DocumentListRef } from '../components/documents/DocumentList';
import { InsuranceConnectionModal } from '../components/insurance/InsuranceConnectionModal';
import { AnalysisProgress } from '../components/analysis/AnalysisProgress';
import { analysisService } from '../services/analysis.service';

export const HomePage = () => {
  const navigate = useNavigate();
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [showInsuranceModal, setShowInsuranceModal] = useState(false);
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);
  const documentListRef = useRef<DocumentListRef>(null);

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocuments(prev =>
      prev.includes(documentId)
        ? prev.filter(id => id !== documentId)
        : [...prev, documentId]
    );
  };

  const handleUploadComplete = async () => {
    console.log('📤 HomePage: Upload complete, waiting briefly for DB commit...');
    // Small delay to ensure database transaction completes
    await new Promise(resolve => setTimeout(resolve, 500));
    console.log('🔄 HomePage: Now refreshing document list...');
    console.log('📍 HomePage: documentListRef.current =', documentListRef.current);

    if (!documentListRef.current) {
      console.error('❌ HomePage: documentListRef.current is null! Ref not attached.');
      return;
    }

    await documentListRef.current.refresh();
    console.log('✅ HomePage: Document list refresh complete');
  };

  const handleAnalyze = async () => {
    if (selectedDocuments.length === 0) {
      alert('Please select at least one document to analyze');
      return;
    }

    try {
      setAnalyzing(true);
      const { analysis_id } = await analysisService.triggerAnalysis(
        selectedDocuments,
        'medgemma-ensemble'
      );

      // Show analysis progress inline (no navigation)
      setCurrentAnalysisId(analysis_id);
    } catch (err: any) {
      alert('Failed to start analysis: ' + err.message);
      setAnalyzing(false);
    }
  };

  const handleBackToDocuments = async () => {
    setCurrentAnalysisId(null);
    setAnalyzing(false);
    setSelectedDocuments([]);
    await documentListRef.current?.refresh();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">MedBillDozer</h1>
            <p className="text-sm text-gray-600">AI-Powered Medical Billing Analysis</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/documents')}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors font-medium"
            >
              <FileText className="w-5 h-5" />
              Manage Documents
            </button>
            <UserMenu />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Show Analysis Progress when analyzing */}
        {currentAnalysisId ? (
          <AnalysisProgress
            analysisId={currentAnalysisId}
            onBack={handleBackToDocuments}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Upload */}
            <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h2>
              <p className="text-gray-600">
                Upload medical bills, insurance EOBs, or receipts for analysis
              </p>
            </div>
            <MultiFileUpload onUploadComplete={async (documentIds) => {
              await handleUploadComplete();
              // Show success message
              if (documentIds.length > 0) {
                alert(`Successfully uploaded ${documentIds.length} document(s)!`);
              }
            }} />

            {/* Insurance Connection Button */}
            <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <LinkIcon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Connect Insurance or Provider (Demo)
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    See what automatic data import would look like
                  </p>
                  <button
                    onClick={() => setShowInsuranceModal(true)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Demo Integration
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Documents & Analysis */}
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Documents</h2>
                <p className="text-gray-600">
                  Select documents to analyze for billing errors
                </p>
              </div>
              {selectedDocuments.length > 0 && (
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {analyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play size={20} />
                      Analyze ({selectedDocuments.length})
                    </>
                  )}
                </button>
              )}
            </div>

            <DocumentList
              ref={documentListRef}
              onDocumentSelect={handleDocumentSelect}
              selectedDocuments={selectedDocuments}
            />
          </div>
        </div>
        )}

        {/* Features - Only show when not analyzing */}
        {!currentAnalysisId && (
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🤖</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
            <p className="text-gray-600 text-sm">
              MedGemma-ensemble analyzes bills using medical domain expertise
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">💰</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Find Savings</h3>
            <p className="text-gray-600 text-sm">
              Detect overcharges, duplicate billing, and coding errors
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Cross-Document</h3>
            <p className="text-gray-600 text-sm">
              Analyze multiple bills together to find duplicate payments
            </p>
          </div>
        </div>
        )}
      </div>

      {/* Insurance Connection Modal */}
      <InsuranceConnectionModal
        isOpen={showInsuranceModal}
        onClose={() => setShowInsuranceModal(false)}
        onConnect={(providerId) => {
          console.log('Connected to:', providerId);
          alert(`Demo: Successfully connected to ${providerId}. In production, this would import your medical bills and claims automatically.`);
          setShowInsuranceModal(false);
        }}
      />
    </div>
  );
};
