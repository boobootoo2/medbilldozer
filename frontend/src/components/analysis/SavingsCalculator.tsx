/**
 * Savings calculator component - displays total savings summary
 */
import { DollarSign, TrendingUp, AlertCircle } from 'lucide-react';

interface SavingsCalculatorProps {
  totalSavings: number;
  issuesCount: number;
}

export const SavingsCalculator = ({ totalSavings, issuesCount }: SavingsCalculatorProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Total Savings */}
      <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
            <DollarSign className="w-5 h-5 text-green-600" />
          </div>
          <h3 className="text-sm font-medium text-gray-600">Potential Savings</h3>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-green-900">
            ${totalSavings.toFixed(2)}
          </span>
        </div>
        <p className="text-sm text-green-700 mt-2">
          Maximum savings if all issues are resolved
        </p>
      </div>

      {/* Issues Count */}
      <div className="p-6 bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200 rounded-xl">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
            <AlertCircle className="w-5 h-5 text-red-600" />
          </div>
          <h3 className="text-sm font-medium text-gray-600">Issues Detected</h3>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-red-900">{issuesCount}</span>
        </div>
        <p className="text-sm text-red-700 mt-2">
          Billing errors and discrepancies found
        </p>
      </div>

      {/* Average Savings per Issue */}
      <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="text-sm font-medium text-gray-600">Avg per Issue</h3>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-blue-900">
            ${issuesCount > 0 ? (totalSavings / issuesCount).toFixed(2) : '0.00'}
          </span>
        </div>
        <p className="text-sm text-blue-700 mt-2">
          Average savings per detected issue
        </p>
      </div>
    </div>
  );
};
