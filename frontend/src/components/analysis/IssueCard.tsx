/**
 * Issue card component with status management
 */
import { useState } from 'react';
import { AlertCircle, CheckCircle, Clock, X, DollarSign, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import { Issue } from '../../types';
import { issuesService } from '../../services/issues.service';

interface IssueCardProps {
  issue: Issue;
  onStatusUpdate?: () => void;
}

const STATUS_COLORS = {
  open: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  follow_up: 'bg-blue-100 text-blue-800 border-blue-300',
  resolved: 'bg-green-100 text-green-800 border-green-300',
  ignored: 'bg-gray-100 text-gray-800 border-gray-300',
};

const STATUS_ICONS = {
  open: AlertCircle,
  follow_up: Clock,
  resolved: CheckCircle,
  ignored: X,
};

const STATUS_LABELS = {
  open: 'Open',
  follow_up: 'Follow Up',
  resolved: 'Resolved',
  ignored: 'Ignored',
};

export const IssueCard = ({ issue, onStatusUpdate }: IssueCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [notes, setNotes] = useState(issue.notes || '');
  const [showNotesInput, setShowNotesInput] = useState(false);

  const StatusIcon = STATUS_ICONS[issue.status];
  const confidenceColor = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-blue-100 text-blue-800',
  }[issue.confidence || 'medium'];

  const sourceLabel = {
    llm: 'AI Analysis',
    deterministic: 'Rule-Based',
    clinical: 'Clinical Validation',
    text_analysis: 'Text Analysis',
    image_analysis: 'Image Analysis',
    cross_reference: 'Cross-Reference',
  }[issue.source || 'llm'];

  const handleStatusChange = async (newStatus: Issue['status']) => {
    try {
      setUpdatingStatus(true);
      await issuesService.updateIssueStatus(issue.issue_id, newStatus);
      setShowStatusMenu(false);
      if (onStatusUpdate) {
        onStatusUpdate();
      }
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('Failed to update issue status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleSaveNotes = async () => {
    try {
      await issuesService.addIssueNote(issue.issue_id, notes);
      setShowNotesInput(false);
      if (onStatusUpdate) {
        onStatusUpdate();
      }
    } catch (error) {
      console.error('Failed to save notes:', error);
      alert('Failed to save notes');
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-start gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${STATUS_COLORS[issue.status].replace('text-', 'bg-').replace('800', '200')}`}>
              <StatusIcon className="w-5 h-5 text-gray-700" />
            </div>

            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">
                {issue.summary}
              </h3>

              <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
                {issue.issue_type && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs">
                    <FileText size={12} />
                    {issue.issue_type.replace('_', ' ')}
                  </span>
                )}

                <span className={`text-xs px-2 py-1 rounded ${confidenceColor}`}>
                  {issue.confidence || 'medium'} confidence
                </span>

                <span className="text-xs px-2 py-1 rounded bg-gray-100">
                  {sourceLabel}
                </span>

                {issue.max_savings > 0 && (
                  <span className="font-medium text-green-600 flex items-center gap-1">
                    <DollarSign size={14} />
                    ${issue.max_savings.toFixed(2)}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Status Badge with Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowStatusMenu(!showStatusMenu)}
            disabled={updatingStatus}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-colors ${STATUS_COLORS[issue.status]} hover:shadow-md disabled:opacity-50`}
          >
            {updatingStatus ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
            ) : (
              <>
                {STATUS_LABELS[issue.status]}
                <ChevronDown size={14} />
              </>
            )}
          </button>

          {showStatusMenu && !updatingStatus && (
            <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
              {Object.entries(STATUS_LABELS).map(([status, label]) => (
                <button
                  key={status}
                  onClick={() => handleStatusChange(status as Issue['status'])}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${
                    status === issue.status ? 'font-semibold bg-gray-50' : ''
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Expand/Collapse Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="mt-3 flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium"
      >
        {isExpanded ? (
          <>
            <ChevronUp size={16} />
            Show less
          </>
        ) : (
          <>
            <ChevronDown size={16} />
            Show details
          </>
        )}
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="mt-4 space-y-3 pt-3 border-t border-gray-200">
          {issue.evidence && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-1">Evidence:</h4>
              <p className="text-sm text-gray-600 whitespace-pre-wrap">{issue.evidence}</p>
            </div>
          )}

          {issue.recommended_action && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-1">Recommended Action:</h4>
              <p className="text-sm text-gray-600">{issue.recommended_action}</p>
            </div>
          )}

          {issue.code && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-1">Code:</h4>
              <code className="text-sm bg-gray-100 px-2 py-1 rounded">{issue.code}</code>
            </div>
          )}

          {/* Notes Section */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-gray-700">Notes:</h4>
              {!showNotesInput && (
                <button
                  onClick={() => setShowNotesInput(true)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {notes ? 'Edit' : 'Add notes'}
                </button>
              )}
            </div>

            {showNotesInput ? (
              <div className="space-y-2">
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add notes about this issue..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleSaveNotes}
                    className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setNotes(issue.notes || '');
                      setShowNotesInput(false);
                    }}
                    className="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : notes ? (
              <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded whitespace-pre-wrap">
                {notes}
              </p>
            ) : (
              <p className="text-sm text-gray-400 italic">No notes yet</p>
            )}
          </div>

          {/* Metadata */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-100">
            <div>Created: {new Date(issue.created_at).toLocaleString()}</div>
            {issue.status_updated_at && (
              <div>Status updated: {new Date(issue.status_updated_at).toLocaleString()}</div>
            )}
            {issue.source && (
              <div>Source: {issue.source}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
