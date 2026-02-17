/**
 * Document management service
 */
import api from './api';
import { Document, UploadUrlResponse } from '../types';

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
};
