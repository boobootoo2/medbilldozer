/**
 * Action Management Panel Component
 * Allows users to set action status and notes on documents
 */
import React, { useState, useEffect } from 'react';
import { EnrichedDocument } from '../../types';
import { documentsService } from '../../services/documents.service';
import { Save, X, CheckCircle } from 'lucide-react';

interface ActionManagementPanelProps {
  document: EnrichedDocument;
  onUpdate: () => void;
}

const ActionManagementPanel: React.FC<ActionManagementPanelProps> = ({ document, onUpdate }) => {
  const [action, setAction] = useState<string>(document.action || 'none');
  const [actionNotes, setActionNotes] = useState<string>(document.action_notes || '');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);

  // Track changes
  useEffect(() => {
    const currentAction = document.action || 'none';
    const currentNotes = document.action_notes || '';
    setHasChanges(action !== currentAction || actionNotes !== currentNotes);
  }, [action, actionNotes, document.action, document.action_notes]);

  // Handle save
  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSaveSuccess(false);

      await documentsService.updateDocumentAction(document.document_id, {
        action: action === 'none' ? null : action,
        action_notes: actionNotes || undefined
      });

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);

      // Notify parent to refresh
      onUpdate();
    } catch (err) {
      console.error('Failed to update action:', err);
      setError(err instanceof Error ? err.message : 'Failed to update action');
    } finally {
      setSaving(false);
    }
  };

  // Handle reset
  const handleReset = () => {
    setAction(document.action || 'none');
    setActionNotes(document.action_notes || '');
    setError(null);
    setSaveSuccess(false);
  };

  return (
    <div className="space-y-4">
      {/* Action Dropdown */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Action Status
        </label>
        <select
          value={action}
          onChange={(e) => setAction(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          disabled={saving}
        >
          <option value="none">⊗ No Action</option>
          <option value="followup">🔔 Follow-up Required</option>
          <option value="ignored">⊘ Ignored</option>
          <option value="resolved">✅ Resolved</option>
        </select>
      </div>

      {/* Action Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Notes
        </label>
        <textarea
          value={actionNotes}
          onChange={(e) => setActionNotes(e.target.value)}
          placeholder="Add notes about this document (optional)"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          disabled={saving}
        />
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            hasChanges && !saving
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {saving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Changes
            </>
          )}
        </button>

        {hasChanges && !saving && (
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            <X className="w-4 h-4" />
            Reset
          </button>
        )}
      </div>

      {/* Success Message */}
      {saveSuccess && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800">
          <CheckCircle className="w-4 h-4" />
          <span className="text-sm font-medium">Action updated successfully!</span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800">
          <X className="w-4 h-4 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Failed to update action</p>
            <p className="text-xs mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="text-xs text-gray-500">
        <p>💡 <strong>Tip:</strong> Use action statuses to track your document workflow:</p>
        <ul className="mt-1 ml-4 space-y-0.5">
          <li>• <strong>Follow-up:</strong> Needs attention or action</li>
          <li>• <strong>Ignored:</strong> No action required</li>
          <li>• <strong>Resolved:</strong> Issue addressed and completed</li>
        </ul>
      </div>
    </div>
  );
};

export default ActionManagementPanel;
