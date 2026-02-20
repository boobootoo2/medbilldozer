/**
 * Document Management Page
 * Main page for viewing and managing documents with action tracking
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentsService } from '../services/documents.service';
import { EnrichedDocument, DocumentListResponse } from '../types';
import { AlertCircle, FileText, Flag, CheckCircle, XCircle, Clock, ArrowLeft } from 'lucide-react';
import DocumentFilters from '../components/documents/DocumentFilters';
import ExpandableDocumentCard from '../components/documents/ExpandableDocumentCard';

const DocumentManagementPage: React.FC = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<EnrichedDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    flagged: 0,
    pending: 0,
    followup: 0,
    resolved: 0
  });

  // Filter state
  const [profileFilter, setProfileFilter] = useState<string>('all');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [flaggedOnly, setFlaggedOnly] = useState(false);

  // Load documents
  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        profile_id: profileFilter !== 'all' ? profileFilter : undefined,
        action: actionFilter !== 'all' ? actionFilter : undefined,
        flagged_only: flaggedOnly
      };

      const response: DocumentListResponse = await documentsService.listDocumentsEnhanced(params);
      setDocuments(response.documents);

      // Calculate stats
      const newStats = {
        total: response.total,
        flagged: response.documents.filter(d => d.flagged).length,
        pending: response.documents.filter(d => !d.action && d.status === 'uploaded').length,
        followup: response.documents.filter(d => d.action === 'followup').length,
        resolved: response.documents.filter(d => d.action === 'resolved').length
      };
      setStats(newStats);

    } catch (err) {
      console.error('❌ Failed to load documents:', err);
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  // Load documents on mount and when filters change
  useEffect(() => {
    loadDocuments();
  }, [profileFilter, actionFilter, flaggedOnly]);

  // Handle document action update
  const handleDocumentUpdate = async (documentId: string) => {
    // Reload documents to reflect changes
    await loadDocuments();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Home
          </button>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-8 h-8 text-blue-600" />
            Document Management
          </h1>
          <p className="mt-2 text-gray-600">
            View, track, and manage your medical documents with action status
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <FileText className="w-8 h-8 text-gray-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Flagged</p>
                <p className="text-2xl font-bold text-red-600">{stats.flagged}</p>
              </div>
              <Flag className="w-8 h-8 text-red-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-600">{stats.pending}</p>
              </div>
              <Clock className="w-8 h-8 text-gray-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Follow-up</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.followup}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-yellow-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Resolved</p>
                <p className="text-2xl font-bold text-green-600">{stats.resolved}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <DocumentFilters
          profileFilter={profileFilter}
          setProfileFilter={setProfileFilter}
          actionFilter={actionFilter}
          setActionFilter={setActionFilter}
          flaggedOnly={flaggedOnly}
          setFlaggedOnly={setFlaggedOnly}
        />

        {/* Document List */}
        <div className="mt-8">
          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading documents...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Error loading documents</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && documents.length === 0 && (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 text-lg">No documents found</p>
              <p className="text-gray-500 text-sm mt-2">Try adjusting your filters or upload new documents</p>
            </div>
          )}

          {!loading && !error && documents.length > 0 && (
            <div className="space-y-4">
              {documents.map((document) => (
                <ExpandableDocumentCard
                  key={document.document_id}
                  document={document}
                  onUpdate={() => handleDocumentUpdate(document.document_id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentManagementPage;
