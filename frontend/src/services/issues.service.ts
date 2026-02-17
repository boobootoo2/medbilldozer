/**
 * Issue management service
 */
import api from './api';
import { Issue } from '../types';

export interface IssueStatistics {
  analysis_id: string;
  open_count: number;
  follow_up_count: number;
  resolved_count: number;
  ignored_count: number;
  open_potential_savings: number;
  follow_up_potential_savings: number;
  resolved_savings: number;
}

export const issuesService = {
  /**
   * Get all issues for an analysis
   */
  async getAnalysisIssues(
    analysisId: string,
    statusFilter?: string
  ): Promise<Issue[]> {
    const params: Record<string, string> = {};
    if (statusFilter) {
      params.status_filter = statusFilter;
    }

    const response = await api.get<Issue[]>(
      `/api/issues/analysis/${analysisId}`,
      { params }
    );
    return response.data;
  },

  /**
   * Update issue status
   */
  async updateIssueStatus(
    issueId: string,
    status: 'open' | 'follow_up' | 'resolved' | 'ignored',
    notes?: string
  ): Promise<void> {
    await api.patch(`/api/issues/${issueId}/status`, {
      status,
      notes
    });
  },

  /**
   * Add notes to an issue
   */
  async addIssueNote(issueId: string, note: string): Promise<void> {
    await api.post(`/api/issues/${issueId}/notes`, { note });
  },

  /**
   * Get issue statistics
   */
  async getIssueStatistics(analysisId: string): Promise<IssueStatistics> {
    const response = await api.get<IssueStatistics>(
      `/api/issues/analysis/${analysisId}/statistics`
    );
    return response.data;
  },
};
