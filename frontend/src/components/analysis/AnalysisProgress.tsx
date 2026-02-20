/**
 * Analysis Progress - Polls for analysis status and displays per-document progress
 */
import { useState, useEffect } from 'react';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { analysisService } from '../../services/analysis.service';
import { Analysis } from '../../types';
import { DocumentStatusCard } from './DocumentStatusCard';
import { IssueCard } from './IssueCard';
import { SavingsCalculator } from './SavingsCalculator';

interface AnalysisProgressProps {
  analysisId: string;
  onBack?: () => void;
}

interface ErrorDetails {
  message: string;
  correlationId?: string;
  error?: string;
  path?: string;
  method?: string;
  help?: string;
  statusCode?: number;
}

export const AnalysisProgress = ({ analysisId, onBack }: AnalysisProgressProps) => {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState<ErrorDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!analysisId) return;

    const pollAnalysis = async () => {
      try {
        await analysisService.pollAnalysis(
          analysisId,
          (updatedAnalysis) => {
            setAnalysis(updatedAnalysis);
            setLoading(false);
          }
        );
      } catch (err: any) {
        console.error('Analysis polling error:', err);

        // Extract detailed error information
        const errorDetails: ErrorDetails = {
          message: err.message || 'Failed to load analysis',
          statusCode: err.response?.status
        };

        // If the error response has detailed information
        if (err.response?.data) {
          const data = err.response.data;
          if (typeof data === 'object') {
            errorDetails.error = data.error;
            errorDetails.correlationId = data.correlation_id;
            errorDetails.path = data.path;
            errorDetails.method = data.method;
            errorDetails.help = data.help;
            // Use the detailed message if available
            if (data.message) {
              errorDetails.message = data.message;
            }
          }
        }

        setError(errorDetails);
        setLoading(false);
      }
    };

    pollAnalysis();
  }, [analysisId]);

  const isProcessing = analysis?.status === 'queued' || analysis?.status === 'processing';
  const isComplete = analysis?.status === 'completed';
  const isFailed = analysis?.status === 'failed';

  const allIssues = analysis?.results?.flatMap(result => result.analysis?.issues || []) || [];

  // Show loading spinner while waiting for first poll
  if (loading && !analysis && !error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
        <p className="text-lg font-medium text-gray-700">Starting analysis...</p>
        <p className="text-sm text-gray-500 mt-2">This may take a moment</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            {onBack && (
              <button
                onClick={onBack}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Back to documents"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </button>
            )}
            <h2 className="text-2xl font-bold text-gray-900">
              {isProcessing && '📊 Analysis in Progress'}
              {isComplete && '✅ Analysis Complete'}
              {isFailed && '❌ Analysis Failed'}
            </h2>
          </div>
          <p className="text-gray-600">
            {analysis?.results?.length || 0} document(s) • {analysis?.provider || 'medgemma-ensemble'}
          </p>
        </div>
      </div>

      {/* Overall Status Message */}
      {isProcessing && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-900 font-medium">
            {analysis?.status === 'queued' && '⏳ Analysis queued, waiting to start...'}
            {analysis?.status === 'processing' && '🔄 MedGemma is analyzing your medical bills...'}
          </p>
          <p className="text-sm text-blue-700 mt-1">This typically takes 30-60 seconds per document</p>
        </div>
      )}

      {isFailed && (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
            <p className="text-red-700 mt-1">An error occurred during analysis. Please try again.</p>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-900">
                {error.statusCode ? `Error ${error.statusCode}` : 'Error'}
              </h3>
              <p className="text-red-700 mt-1">{error.message}</p>

              {/* Additional error details */}
              {error.help && (
                <div className="mt-3 p-3 bg-red-100 rounded border border-red-300">
                  <p className="text-sm text-red-800">
                    <strong>💡 Help:</strong> {error.help}
                  </p>
                </div>
              )}

              {/* Debug information (collapsible) */}
              {(error.correlationId || error.path || error.method || error.error) && (
                <details className="mt-4 text-sm">
                  <summary className="cursor-pointer text-red-800 hover:text-red-900 font-medium">
                    🔍 Debug Information
                  </summary>
                  <div className="mt-2 p-3 bg-white rounded border border-red-200 font-mono text-xs space-y-1">
                    {error.correlationId && (
                      <div>
                        <span className="text-gray-600">Correlation ID:</span>{' '}
                        <span className="text-gray-900">{error.correlationId}</span>
                      </div>
                    )}
                    {error.error && (
                      <div>
                        <span className="text-gray-600">Error Type:</span>{' '}
                        <span className="text-gray-900">{error.error}</span>
                      </div>
                    )}
                    {error.method && error.path && (
                      <div>
                        <span className="text-gray-600">Request:</span>{' '}
                        <span className="text-gray-900">{error.method} {error.path}</span>
                      </div>
                    )}
                    {error.statusCode && (
                      <div>
                        <span className="text-gray-600">Status Code:</span>{' '}
                        <span className="text-gray-900">{error.statusCode}</span>
                      </div>
                    )}
                    <div className="mt-2 pt-2 border-t border-red-200 text-gray-600">
                      Include the Correlation ID when reporting this issue for faster support.
                    </div>
                  </div>
                </details>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Document Status Cards */}
      {analysis?.results && analysis.results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Document Progress</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {analysis.results.map((result) => (
              <DocumentStatusCard
                key={result.document_id}
                documentId={result.document_id}
                filename={result.filename}
                progress={result.progress}
                error={result.error}
              />
            ))}
          </div>
        </div>
      )}

      {/* Results Section - Only show when complete */}
      {isComplete && analysis && (
        <>
          {/* Savings Summary */}
          <SavingsCalculator
            totalSavings={analysis.total_savings_detected || 0}
            issuesCount={analysis.issues_count}
          />

          {/* Issues List */}
          <div>
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
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Cross-Document Analysis</h2>
              <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
                <p className="text-gray-700">Coverage matrix analysis available</p>
                <pre className="mt-4 text-xs text-gray-600 overflow-auto">
                  {JSON.stringify(analysis.coverage_matrix, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
