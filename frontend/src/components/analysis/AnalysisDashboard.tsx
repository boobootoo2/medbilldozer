/**
 * Analysis dashboard - displays analysis results with polling
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AlertCircle, Loader2, ArrowLeft } from 'lucide-react';
import { analysisService } from '../../services/analysis.service';
import { Analysis } from '../../types';
import { IssueCard } from './IssueCard';
import { SavingsCalculator } from './SavingsCalculator';

export const AnalysisDashboard = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) return;

    const pollAnalysis = async () => {
      try {
        await analysisService.pollAnalysis(
          analysisId,
          (updatedAnalysis) => {
            setAnalysis(updatedAnalysis);
            setLoading(updatedAnalysis.status === 'queued' || updatedAnalysis.status === 'processing');
          }
        );
      } catch (err: any) {
        setError(err.message || 'Failed to load analysis');
        setLoading(false);
      }
    };

    pollAnalysis();
  }, [analysisId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing your documents</h2>
          <p className="text-gray-600">
            {analysis?.status === 'queued' && 'Analysis queued, waiting to start...'}
            {analysis?.status === 'processing' && 'MedGemma is analyzing your medical bills...'}
          </p>
          <p className="text-sm text-gray-500 mt-4">This typically takes 30-60 seconds</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
            <p className="text-red-700 mt-1">{error || 'Analysis not found'}</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (analysis.status === 'failed') {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
          <p className="text-red-700 mt-1">An error occurred during analysis. Please try again.</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const allIssues = analysis.results?.flatMap(result => result.analysis?.issues || []) || [];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
        <p className="text-gray-600 mt-1">
          Analyzed {analysis.results?.length || 0} document(s) with {analysis.provider}
        </p>
      </div>

      {/* Savings Summary */}
      <SavingsCalculator
        totalSavings={analysis.total_savings_detected || 0}
        issuesCount={analysis.issues_count}
      />

      {/* Issues List */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Detected Issues ({allIssues.length})
        </h2>

        {allIssues.length === 0 ? (
          <div className="p-8 bg-green-50 border border-green-200 rounded-lg text-center">
            <h3 className="text-lg font-semibold text-green-900">No Issues Found</h3>
            <p className="text-green-700 mt-1">
              Your medical bills appear to be correct. No billing errors detected!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {allIssues.map((issue, index) => (
              <IssueCard key={issue.issue_id || index} issue={issue} />
            ))}
          </div>
        )}
      </div>

      {/* Coverage Matrix */}
      {analysis.coverage_matrix && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Cross-Document Analysis</h2>
          <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-gray-700">Coverage matrix analysis available</p>
            <pre className="mt-4 text-xs text-gray-600 overflow-auto">
              {JSON.stringify(analysis.coverage_matrix, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
