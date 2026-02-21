/**
 * Expandable Document Card Component
 * Shows document summary with expand/collapse for full details and action management
 */
import React, { useState } from 'react';
import { EnrichedDocument } from '../../types';
import {
  ChevronDown,
  ChevronUp,
  Flag,
  Calendar,
  DollarSign,
  User,
  FileText,
  AlertCircle,
  Building2
} from 'lucide-react';
import ActionManagementPanel from './ActionManagementPanel';

interface ExpandableDocumentCardProps {
  document: EnrichedDocument;
  onUpdate: () => void;
}

const ExpandableDocumentCard: React.FC<ExpandableDocumentCardProps> = ({ document, onUpdate }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Format date
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Format currency
  const formatCurrency = (amount?: number) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  // Get status badge styling
  const getStatusBadge = () => {
    switch (document.status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
      case 'analyzing':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get action badge styling
  const getActionBadge = () => {
    switch (document.action) {
      case 'followup':
        return { style: 'bg-yellow-100 text-yellow-800', icon: '🔔', label: 'Follow-up' };
      case 'resolved':
        return { style: 'bg-green-100 text-green-800', icon: '✅', label: 'Resolved' };
      case 'ignored':
        return { style: 'bg-gray-100 text-gray-800', icon: '⊘', label: 'Ignored' };
      default:
        return null;
    }
  };

  const actionBadge = getActionBadge();

  return (
    <div className={`bg-white rounded-lg shadow-md border-2 transition-all ${
      document.flagged ? 'border-red-300' : 'border-gray-200'
    }`}>
      {/* Card Header - Always Visible */}
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-5 h-5 text-gray-600" />
              <h3 className="font-semibold text-gray-900 text-lg">
                {document.filename}
              </h3>

              {/* Flagged Indicator */}
              {document.flagged && (
                <div className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
                  <Flag className="w-3 h-3" />
                  Flagged
                </div>
              )}

              {/* Status Badge */}
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge()}`}>
                {document.status}
              </span>

              {/* Action Badge */}
              {actionBadge && (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${actionBadge.style}`}>
                  {actionBadge.icon} {actionBadge.label}
                </span>
              )}
            </div>

            {/* Quick Info */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
              {document.profile_name && (
                <div className="flex items-center gap-1">
                  <User className="w-4 h-4" />
                  {document.profile_name}
                </div>
              )}

              {document.service_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {formatDate(document.service_date)}
                </div>
              )}

              {document.patient_responsibility_amount && (
                <div className="flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  {formatCurrency(document.patient_responsibility_amount)}
                </div>
              )}

              {/* Issue Count */}
              {document.total_issues_count > 0 && (
                <div className="flex items-center gap-1 text-orange-600">
                  <AlertCircle className="w-4 h-4" />
                  {document.high_confidence_issues_count > 0 && (
                    <span className="font-medium">
                      {document.high_confidence_issues_count} high-priority
                    </span>
                  )}
                  {document.high_confidence_issues_count > 0 && document.total_issues_count > document.high_confidence_issues_count && (
                    <span> + {document.total_issues_count - document.high_confidence_issues_count} more</span>
                  )}
                  {document.high_confidence_issues_count === 0 && (
                    <span>{document.total_issues_count} issues</span>
                  )}
                </div>
              )}

              <div className="ml-auto text-xs text-gray-500">
                Uploaded {formatDate(document.uploaded_at)}
              </div>
            </div>
          </div>

          {/* Expand/Collapse Icon */}
          <button className="ml-4 text-gray-400 hover:text-gray-600">
            {isExpanded ? (
              <ChevronUp className="w-6 h-6" />
            ) : (
              <ChevronDown className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column - Document Details */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Document Details
              </h4>

              <dl className="space-y-2 text-sm">
                <div>
                  <dt className="text-gray-600 inline">Document ID:</dt>
                  <dd className="text-gray-900 inline ml-2 font-mono text-xs">
                    {document.document_id}
                  </dd>
                </div>

                <div>
                  <dt className="text-gray-600 inline">Type:</dt>
                  <dd className="text-gray-900 inline ml-2">
                    {document.document_type?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
                  </dd>
                </div>

                <div>
                  <dt className="text-gray-600 inline">Size:</dt>
                  <dd className="text-gray-900 inline ml-2">
                    {document.size_bytes > 0
                      ? `${(document.size_bytes / 1024).toFixed(1)} KB`
                      : 'Unknown'}
                  </dd>
                </div>

                {document.provider_name && (
                  <div>
                    <dt className="text-gray-600 inline flex items-center gap-1">
                      <Building2 className="w-4 h-4 inline" />
                      Provider:
                    </dt>
                    <dd className="text-gray-900 ml-2">
                      {document.provider_name}
                    </dd>
                  </div>
                )}

                {document.profile_id && (
                  <div>
                    <dt className="text-gray-600 inline">Profile ID:</dt>
                    <dd className="text-gray-900 inline ml-2 font-mono text-xs">
                      {document.profile_id}
                    </dd>
                  </div>
                )}

                {document.profile_type && (
                  <div>
                    <dt className="text-gray-600 inline">Profile Type:</dt>
                    <dd className="text-gray-900 inline ml-2 capitalize">
                      {document.profile_type}
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Right Column - Action Management */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                Action Management
              </h4>

              <ActionManagementPanel
                document={document}
                onUpdate={onUpdate}
              />

              {/* Action History */}
              {document.action_date && (
                <div className="mt-4 p-3 bg-white rounded border border-gray-200">
                  <p className="text-xs text-gray-600">
                    Last action: {formatDate(document.action_date)}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Issues Summary (if any) */}
          {document.flagged && document.high_confidence_issues_count > 0 && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-2">
                <Flag className="w-5 h-5 text-red-600 mt-0.5" />
                <div>
                  <p className="font-medium text-red-900">
                    This document has been flagged for review
                  </p>
                  <p className="text-sm text-red-700 mt-1">
                    {document.high_confidence_issues_count} high-confidence issue(s) detected that may require your attention.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExpandableDocumentCard;
