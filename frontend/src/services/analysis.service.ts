/**
 * Analysis service
 */
import api from './api';
import { Analysis, AnalyzeRequest } from '../types';

export const analysisService = {
  /**
   * Trigger analysis for documents
   */
  async triggerAnalysis(documentIds: string[], provider = 'medgemma-ensemble'): Promise<{ analysis_id: string }> {
    const response = await api.post<{ analysis_id: string }>('/api/analyze/', {
      document_ids: documentIds,
      provider
    } as AnalyzeRequest);
    return response.data;
  },

  /**
   * Get analysis results (for polling)
   */
  async getAnalysis(analysisId: string): Promise<Analysis> {
    const response = await api.get<Analysis>(`/api/analyze/${analysisId}/`);
    return response.data;
  },

  /**
   * List all analyses for current user
   */
  async listAnalyses(limit = 20, offset = 0): Promise<Analysis[]> {
    const response = await api.get<{ analyses: Analysis[] }>('/api/analyze/', {
      params: { limit, offset }
    });
    return response.data.analyses;
  },

  /**
   * Poll for analysis completion
   */
  async pollAnalysis(analysisId: string, onUpdate: (analysis: Analysis) => void, interval = 2000): Promise<Analysis> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const analysis = await this.getAnalysis(analysisId);
          onUpdate(analysis);

          if (analysis.status === 'completed' || analysis.status === 'failed') {
            resolve(analysis);
          } else {
            setTimeout(poll, interval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  },
};
