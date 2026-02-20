/**
 * Document management service
 */
import api from './api';
import {
  Document,
  UploadUrlResponse,
  EnrichedDocument,
  DocumentListResponse,
  DocumentActionUpdate,
  DocumentMetadataUpdate,
  DocumentActionStatistics,
  BulkAnalyzeRequest,
  BulkAnalyzeResponse
} from '../types';

export const documentsService = {
  /**
   * Get signed URL for uploading a document
   */
  async getUploadUrl(filename: string, contentType: string, documentType?: string): Promise<UploadUrlResponse> {
    const response = await api.post<UploadUrlResponse>('/api/documents/upload-url', {
      filename,
      content_type: contentType,
      document_type: documentType
    });
    return response.data;
  },

  /**
   * Upload file directly to GCS using signed URL
   */
  async uploadToGCS(file: File, signedUrl: string): Promise<void> {
    await fetch(signedUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });
  },

  /**
   * Confirm document upload with backend
   */
  async confirmUpload(documentId: string, filename: string, gcsPath: string, sizeBytes: number, documentType?: string): Promise<void> {
    await api.post('/api/documents/confirm', {
      document_id: documentId,
      filename,
      gcs_path: gcsPath,
      size_bytes: sizeBytes,
      document_type: documentType
    });
  },

  /**
   * Complete upload flow: get signed URL, upload file, confirm
   */
  async uploadDocument(file: File, documentType?: string): Promise<string> {
    // 1. Get signed URL
    const { document_id, upload_url, gcs_path } = await this.getUploadUrl(
      file.name,
      file.type,
      documentType
    );

    // 2. Upload to GCS
    await this.uploadToGCS(file, upload_url);

    // 3. Confirm with backend
    await this.confirmUpload(document_id, file.name, gcs_path, file.size, documentType);

    return document_id;
  },

  /**
   * List all documents for current user
   */
  async listDocuments(limit = 50, offset = 0): Promise<Document[]> {
    const response = await api.get<{ documents: Document[] }>('/api/documents/', {
      params: { limit, offset }
    });
    return response.data.documents;
  },

  /**
   * Get single document with download URL
   */
  async getDocument(documentId: string): Promise<Document> {
    const response = await api.get<Document>(`/api/documents/${documentId}`);
    return response.data;
  },

  /**
   * Delete document
   */
  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/api/documents/${documentId}`);
  },

  // ============================================================================
  // ENHANCED DOCUMENT MANAGEMENT
  // ============================================================================

  /**
   * List documents with enhanced filtering
   */
  async listDocumentsEnhanced(params?: {
    profile_id?: string;
    action?: string;
    flagged_only?: boolean;
    status_filter?: string;
    limit?: number;
    offset?: number;
  }): Promise<DocumentListResponse> {
    const response = await api.get<DocumentListResponse>('/api/documents/', {
      params: {
        profile_id: params?.profile_id,
        action: params?.action,
        flagged_only: params?.flagged_only,
        status_filter: params?.status_filter,
        limit: params?.limit || 50,
        offset: params?.offset || 0
      }
    });
    return response.data;
  },

  /**
   * Update document action status
   */
  async updateDocumentAction(
    documentId: string,
    update: DocumentActionUpdate
  ): Promise<EnrichedDocument> {
    const response = await api.patch<EnrichedDocument>(
      `/api/documents/${documentId}/action`,
      update
    );
    return response.data;
  },

  /**
   * Update document metadata (profile info, amounts, etc)
   */
  async updateDocumentMetadata(
    documentId: string,
    metadata: DocumentMetadataUpdate
  ): Promise<EnrichedDocument> {
    const response = await api.patch<EnrichedDocument>(
      `/api/documents/${documentId}/metadata`,
      metadata
    );
    return response.data;
  },

  /**
   * Trigger bulk analysis on multiple documents
   */
  async bulkAnalyze(request: BulkAnalyzeRequest): Promise<BulkAnalyzeResponse> {
    const response = await api.post<BulkAnalyzeResponse>(
      '/api/documents/analyze-bulk',
      request
    );
    return response.data;
  },

  /**
   * Get document action statistics
   */
  async getActionStatistics(profileId?: string): Promise<DocumentActionStatistics> {
    const response = await api.get<DocumentActionStatistics>(
      '/api/documents/statistics',
      { params: { profile_id: profileId } }
    );
    return response.data;
  },

  /**
   * Export actioned documents to CSV
   */
  async exportActionedDocuments(profileId?: string, format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await api.get('/api/documents/export/actioned', {
      params: { profile_id: profileId, format },
      responseType: format === 'csv' ? 'blob' : 'json'
    });
    return response.data;
  }
};
