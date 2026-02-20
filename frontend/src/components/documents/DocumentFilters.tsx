/**
 * Document Filters Component
 * Filters for profile, action status, and flagged documents
 */
import React from 'react';
import { Filter, User, Users, Flag } from 'lucide-react';

interface DocumentFiltersProps {
  profileFilter: string;
  setProfileFilter: (value: string) => void;
  actionFilter: string;
  setActionFilter: (value: string) => void;
  flaggedOnly: boolean;
  setFlaggedOnly: (value: boolean) => void;
}

const DocumentFilters: React.FC<DocumentFiltersProps> = ({
  profileFilter,
  setProfileFilter,
  actionFilter,
  setActionFilter,
  flaggedOnly,
  setFlaggedOnly
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-5 h-5 text-gray-600" />
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Profile Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <User className="w-4 h-4 inline mr-1" />
            Profile
          </label>
          <select
            value={profileFilter}
            onChange={(e) => setProfileFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Profiles</option>
            <option value="PH-001">👨 Policyholder</option>
            <option value="DEP-001">👧 Dependent</option>
          </select>
        </div>

        {/* Action Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Users className="w-4 h-4 inline mr-1" />
            Action Status
          </label>
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Actions</option>
            <option value="">No Action</option>
            <option value="followup">🔔 Follow-up Required</option>
            <option value="ignored">⊘ Ignored</option>
            <option value="resolved">✅ Resolved</option>
          </select>
        </div>

        {/* Flagged Only Toggle */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Flag className="w-4 h-4 inline mr-1" />
            Flagged
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={flaggedOnly}
              onChange={(e) => setFlaggedOnly(e.target.checked)}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              Show flagged only
            </span>
          </label>
        </div>

        {/* Clear Filters Button */}
        <div className="flex items-end">
          <button
            onClick={() => {
              setProfileFilter('all');
              setActionFilter('all');
              setFlaggedOnly(false);
            }}
            className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentFilters;
