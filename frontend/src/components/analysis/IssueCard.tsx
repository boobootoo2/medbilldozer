/**
 * Issue card component - displays a single billing issue
 */
import { AlertTriangle, DollarSign, TrendingUp } from 'lucide-react';
import { Issue } from '../../types';

interface IssueCardProps {
  issue: Issue;
}

export const IssueCard = ({ issue }: IssueCardProps) => {
  const confidenceColor = {
    high: 'bg-red-100 text-red-800 border-red-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    low: 'bg-blue-100 text-blue-800 border-blue-300',
  }[issue.confidence];

  const sourceLabel = {
    llm: 'AI Analysis',
    deterministic: 'Rule-Based',
    clinical: 'Clinical Validation',
  }[issue.source];

  return (
    <div className="p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-300 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-5 h-5 text-red-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{issue.summary}</h3>
            <div className="flex items-center gap-2 mt-2">
              <span className={`px-2 py-1 text-xs font-medium rounded border ${confidenceColor}`}>
                {issue.confidence.toUpperCase()} CONFIDENCE
              </span>
              <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                {sourceLabel}
              </span>
              {issue.code && (
                <span className="px-2 py-1 text-xs font-mono bg-gray-100 text-gray-700 rounded">
                  {issue.code}
                </span>
              )}
            </div>
          </div>
        </div>

        {issue.max_savings > 0 && (
          <div className="ml-4 text-right">
            <div className="flex items-center gap-1 text-green-600">
              <DollarSign size={20} />
              <span className="text-2xl font-bold">{issue.max_savings.toFixed(2)}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Potential Savings</p>
          </div>
        )}
      </div>

      {/* Evidence */}
      {issue.evidence && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm font-medium text-gray-700 mb-1">Evidence:</p>
          <p className="text-sm text-gray-600">{issue.evidence}</p>
        </div>
      )}

      {/* Recommended Action */}
      {issue.recommended_action && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-blue-900 mb-1">Recommended Action:</p>
              <p className="text-sm text-blue-700">{issue.recommended_action}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
