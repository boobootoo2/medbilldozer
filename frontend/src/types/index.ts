/**
 * TypeScript type definitions for MedBillDozer
 */

export interface User {
  user_id: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  created_at: string;
  last_login_at?: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  loading: boolean;
  error: string | null;
}

export interface Document {
  document_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  uploaded_at: string;
  status: 'uploaded' | 'processing' | 'analyzing' | 'completed' | 'failed';
  document_type?: 'medical_bill' | 'dental_bill' | 'insurance_eob' | 'pharmacy_receipt' | 'fsa_claim' | 'clinical_image' | 'other';
  download_url?: string;
}

export interface UploadUrlResponse {
  document_id: string;
  upload_url: string;
  gcs_path: string;
  expires_at: string;
}

export interface Issue {
  issue_id: string;
  analysis_id: string;
  document_id?: string;
  issue_type: string;
  summary: string;
  evidence?: string;
  code?: string;
  recommended_action?: string;
  max_savings: number;
  confidence?: 'high' | 'medium' | 'low';
  source?: 'llm' | 'deterministic' | 'clinical' | 'text_analysis' | 'image_analysis' | 'cross_reference';
  status: 'open' | 'follow_up' | 'resolved' | 'ignored';
  status_updated_at?: string;
  status_updated_by?: string;
  notes?: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface Analysis {
  analysis_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  provider: string;
  results?: {
    document_id: string;
    filename: string;
    facts?: Record<string, any>;
    analysis?: {
      issues: Issue[];
    };
  }[];
  coverage_matrix?: any;
  total_savings_detected?: number;
  issues_count: number;
  created_at: string;
  completed_at?: string;
}

export interface AnalyzeRequest {
  document_ids: string[];
  provider?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}
