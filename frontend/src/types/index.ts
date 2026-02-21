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

export interface DocumentProgress {
  phase: 'pre_extraction_active' | 'extraction_active' | 'line_items_active' | 'analysis_active' | 'complete' | 'failed';
  started_at: string;
  updated_at?: string;
  completed_at?: string;
  failed_at?: string;
  error_message?: string;
  workflow_log?: {
    workflow_id: string;
    timestamp: string;
    pre_extraction?: {
      classification: any;
      facts: any;
      extractor_selected: string;
      extractor_reason: string;
    };
    extraction?: {
      extractor: string;
      facts: any;
      fact_count: number;
      receipt_item_count?: number;
      medical_item_count?: number;
      dental_item_count?: number;
      insurance_item_count?: number;
      fsa_item_count?: number;
      receipt_extraction_error?: string;
      medical_extraction_error?: string;
      dental_extraction_error?: string;
      insurance_extraction_error?: string;
      fsa_extraction_error?: string;
    };
    analysis?: {
      analyzer: string;
      mode: string;
      result: any;
    };
  };
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
    progress?: DocumentProgress;
    error?: string;
    status?: string;
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

// ============================================================================
// DOCUMENT MANAGEMENT (Enhanced)
// ============================================================================

export interface EnrichedDocument extends Document {
  // Profile metadata
  profile_id?: string;
  profile_name?: string;
  profile_type?: 'policyholder' | 'dependent';
  provider_name?: string;
  service_date?: string;
  patient_responsibility_amount?: number;

  // Action tracking
  action?: 'ignored' | 'followup' | 'resolved' | null;
  action_notes?: string;
  action_date?: string;
  action_updated_by?: string;

  // Computed fields
  flagged: boolean;
  high_confidence_issues_count: number;
  total_issues_count: number;
}

export interface DocumentListResponse {
  documents: EnrichedDocument[];
  total: number;
  offset: number;
  limit: number;
}

export interface DocumentActionUpdate {
  action?: 'ignored' | 'followup' | 'resolved' | null;
  action_notes?: string;
}

export interface DocumentMetadataUpdate {
  profile_id?: string;
  profile_name?: string;
  profile_type?: 'policyholder' | 'dependent';
  provider_name?: string;
  service_date?: string;
  patient_responsibility_amount?: number;
}

export interface DocumentActionStatistics {
  user_id: string;
  profile_id?: string;
  profile_name?: string;
  total_documents: number;
  followup_count: number;
  ignored_count: number;
  resolved_count: number;
  pending_count: number;
  completed_count: number;
  followup_amount: number;
  resolved_amount: number;
  total_amount: number;
  last_action_date?: string;
  last_upload_date?: string;
}

export interface BulkAnalyzeRequest {
  document_ids: string[];
  profile_id?: string;
  exclude_flagged?: boolean;
  provider?: string;
}

export interface BulkAnalyzeResponse {
  analysis_id: string;
  status: string;
  documents_submitted: number;
  documents_excluded: number;
  excluded_reason?: string;
  estimated_completion: string;
}
