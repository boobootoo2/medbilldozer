/**
 * Document Status Card - Real-time pipeline progress tracking
 */
import { useEffect, useState } from 'react';
import { CheckCircle, Loader2, AlertCircle, Clock } from 'lucide-react';
import { DocumentProgress } from '../../types';

interface DocumentStatusCardProps {
  documentId: string;
  filename: string;
  progress?: DocumentProgress;
  error?: string;
}

// Phase mapping with icons and labels
const PHASE_MAP = {
  pre_extraction_active: { icon: '🔍', label: 'Pre-Extraction', desc: 'Classifying document', order: 1 },
  extraction_active: { icon: '📋', label: 'Fact Extraction', desc: 'Extracting information', order: 2 },
  line_items_active: { icon: '📊', label: 'Line Items', desc: 'Parsing line items', order: 3 },
  analysis_active: { icon: '🔬', label: 'Issue Analysis', desc: 'Analyzing issues', order: 4 },
  complete: { icon: '✅', label: 'Complete', desc: 'Analysis finished', order: 5 },
  failed: { icon: '❌', label: 'Failed', desc: 'Error occurred', order: -1 }
};

const ALL_PHASES = ['pre_extraction_active', 'extraction_active', 'line_items_active', 'analysis_active', 'complete'];

export const DocumentStatusCard = ({ documentId, filename, progress, error }: DocumentStatusCardProps) => {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Calculate elapsed time
  useEffect(() => {
    if (!progress?.started_at) return;

    const calculateElapsed = () => {
      const startTime = new Date(progress.started_at).getTime();
      const now = Date.now();
      setElapsedTime(Math.floor((now - startTime) / 1000));
    };

    calculateElapsed();
    const interval = setInterval(calculateElapsed, 1000);

    return () => clearInterval(interval);
  }, [progress?.started_at]);

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  const currentPhase = progress?.phase || 'pre_extraction_active';
  const isComplete = currentPhase === 'complete';
  const isFailed = currentPhase === 'failed' || error;

  // Calculate progress percentage
  const calculateProgress = (): number => {
    if (isComplete) return 100;
    if (isFailed) return 0;

    const phaseOrder = PHASE_MAP[currentPhase as keyof typeof PHASE_MAP]?.order || 0;
    if (phaseOrder <= 0) return 0;

    return Math.floor(((phaseOrder - 1) / ALL_PHASES.length) * 100);
  };

  const progressPercent = calculateProgress();

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 flex-1">
          {isComplete && <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />}
          {isFailed && <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />}
          {!isComplete && !isFailed && <Loader2 className="w-5 h-5 text-blue-600 animate-spin flex-shrink-0" />}
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-gray-900 truncate">{filename}</h3>
            <p className="text-xs text-gray-500 truncate">{documentId}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600 flex-shrink-0">
          <Clock className="w-4 h-4" />
          <span className="font-medium">{formatTime(elapsedTime)}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
          <span>Progress</span>
          <span>{progressPercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${
              isComplete ? 'bg-green-600' : isFailed ? 'bg-red-600' : 'bg-blue-600'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Error Message */}
      {isFailed && (error || progress?.error_message) && (
        <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          <strong>Error:</strong> {error || progress?.error_message}
        </div>
      )}

      {/* Phase Checklist */}
      <div className="space-y-1">
        <p className="text-xs font-medium text-gray-700 mb-2">Pipeline Progress:</p>
        {ALL_PHASES.map((phaseKey) => {
          const phase = PHASE_MAP[phaseKey as keyof typeof PHASE_MAP];
          const phaseOrder = phase.order;
          const currentOrder = PHASE_MAP[currentPhase as keyof typeof PHASE_MAP]?.order || 0;

          const isPhaseComplete = phaseOrder < currentOrder || (currentPhase === phaseKey && isComplete);
          const isPhaseActive = currentPhase === phaseKey && !isComplete && !isFailed;
          const isPhaseFailed = currentPhase === phaseKey && isFailed;

          return (
            <div key={phaseKey} className="flex items-center gap-2 text-sm">
              {isPhaseComplete && (
                <>
                  <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                  <span className="text-gray-900 font-medium">{phase.label}</span>
                </>
              )}
              {isPhaseActive && (
                <>
                  <Loader2 className="w-4 h-4 text-blue-600 animate-spin flex-shrink-0" />
                  <span className="text-blue-900 font-medium">{phase.label} — {phase.desc}...</span>
                </>
              )}
              {isPhaseFailed && (
                <>
                  <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                  <span className="text-red-900 font-medium">{phase.label} — Failed</span>
                </>
              )}
              {!isPhaseComplete && !isPhaseActive && !isPhaseFailed && (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-gray-300 flex-shrink-0" />
                  <span className="text-gray-500">{phase.label}</span>
                </>
              )}
            </div>
          );
        })}
      </div>

      {/* Success Message */}
      {isComplete && (
        <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded text-sm text-green-700 font-medium">
          ✨ Analysis complete in {formatTime(elapsedTime)}
        </div>
      )}

      {/* Processing Message */}
      {!isComplete && !isFailed && (
        <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700">
          🔄 {PHASE_MAP[currentPhase as keyof typeof PHASE_MAP]?.desc || 'Processing'}...
        </div>
      )}
    </div>
  );
};
