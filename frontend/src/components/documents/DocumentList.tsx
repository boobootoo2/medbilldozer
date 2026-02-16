/**
 * Document list component
 */
import { useState, useEffect } from 'react';
import { FileText, Download, Trash2, Clock } from 'lucide-react';
import { documentsService } from '../../services/documents.service';
import { Document } from '../../types';

interface DocumentListProps {
  onDocumentSelect?: (documentId: string) => void;
  selectedDocuments?: string[];
}

export const DocumentList = ({ onDocumentSelect, selectedDocuments = [] }: DocumentListProps) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await documentsService.listDocuments();
      setDocuments(docs);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await documentsService.deleteDocument(documentId);
      setDocuments(documents.filter(doc => doc.document_id !== documentId));
    } catch (err: any) {
      alert('Failed to delete document: ' + err.message);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-900">
        {error}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No documents uploaded yet</p>
        <p className="text-sm text-gray-500 mt-1">Upload your first medical bill to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => {
        const isSelected = selectedDocuments.includes(doc.document_id);

        return (
          <div
            key={doc.document_id}
            className={`
              p-4 border rounded-lg transition-all cursor-pointer
              ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}
            `}
            onClick={() => onDocumentSelect && onDocumentSelect(doc.document_id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 truncate">
                    {doc.filename}
                  </h3>
                  <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                    <span>{formatFileSize(doc.size_bytes)}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      {formatDate(doc.uploaded_at)}
                    </span>
                  </div>
                  {doc.document_type && (
                    <span className="inline-block mt-2 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      {doc.document_type.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 ml-4">
                {doc.download_url && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(doc.download_url, '_blank');
                    }}
                    className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Download"
                  >
                    <Download size={18} />
                  </button>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(doc.document_id);
                  }}
                  className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>

            {isSelected && (
              <div className="mt-2 text-sm text-blue-600 font-medium">
                ✓ Selected for analysis
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
