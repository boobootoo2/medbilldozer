/**
 * Multi-file upload component with drag & drop support
 */
import { useState, useCallback } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { documentsService } from '../../services/documents.service';

interface UploadFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  documentId?: string;
  error?: string;
}

interface MultiFileUploadProps {
  onUploadComplete?: (documentIds: string[]) => void;
  maxFiles?: number;
}

export const MultiFileUpload = ({ onUploadComplete, maxFiles = 10 }: MultiFileUploadProps) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files).filter(file =>
      file.type === 'application/pdf' ||
      file.type === 'text/plain' ||
      file.type.startsWith('image/')
    );

    addFiles(droppedFiles);
  }, [files, maxFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  }, [files, maxFiles]);

  const addFiles = (newFiles: File[]) => {
    const remainingSlots = maxFiles - files.length;
    const filesToAdd = newFiles.slice(0, remainingSlots);

    const uploadFiles: UploadFile[] = filesToAdd.map(file => ({
      file,
      status: 'pending',
      progress: 0
    }));

    setFiles(prev => [...prev, ...uploadFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const uploadFile = async (uploadFile: UploadFile, index: number) => {
    try {
      // Update status to uploading
      setFiles(prev => prev.map((f, i) =>
        i === index ? { ...f, status: 'uploading', progress: 0 } : f
      ));

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setFiles(prev => prev.map((f, i) =>
          i === index && f.progress < 90 ? { ...f, progress: f.progress + 10 } : f
        ));
      }, 200);

      // Upload the document
      const documentId = await documentsService.uploadDocument(uploadFile.file);

      clearInterval(progressInterval);

      // Update to success
      setFiles(prev => prev.map((f, i) =>
        i === index ? { ...f, status: 'success', progress: 100, documentId } : f
      ));

      return documentId;
    } catch (error: any) {
      setFiles(prev => prev.map((f, i) =>
        i === index ? { ...f, status: 'error', error: error.message } : f
      ));
      throw error;
    }
  };

  const uploadAll = async () => {
    const pendingFiles = files.filter(f => f.status === 'pending');

    try {
      const uploadPromises = pendingFiles.map((file) => {
        const actualIndex = files.findIndex(f => f === file);
        return uploadFile(file, actualIndex);
      });

      const documentIds = await Promise.all(uploadPromises);

      if (onUploadComplete) {
        onUploadComplete(documentIds);
      }
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const successCount = files.filter(f => f.status === 'success').length;
  const errorCount = files.filter(f => f.status === 'error').length;
  const pendingCount = files.filter(f => f.status === 'pending').length;

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${files.length >= maxFiles ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <input
          type="file"
          multiple
          accept=".pdf,.txt,.png,.jpg,.jpeg"
          onChange={handleFileSelect}
          disabled={files.length >= maxFiles}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-blue-600' : 'text-gray-400'}`} />
        <p className="text-lg font-medium text-gray-900 mb-1">
          Drag & drop your medical documents
        </p>
        <p className="text-sm text-gray-600">
          or click to browse (PDF, TXT, PNG, JPG)
        </p>
        <p className="text-xs text-gray-500 mt-2">
          Up to {maxFiles} files • Max size 25MB each
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between px-2">
            <h3 className="text-sm font-medium text-gray-700">
              {files.length} file{files.length !== 1 ? 's' : ''} selected
            </h3>
            {pendingCount > 0 && (
              <button
                onClick={uploadAll}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Upload All ({pendingCount})
              </button>
            )}
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {files.map((uploadFile, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-white border rounded-lg"
              >
                <div className={`
                  w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
                  ${uploadFile.status === 'success' ? 'bg-green-100' :
                    uploadFile.status === 'error' ? 'bg-red-100' :
                    uploadFile.status === 'uploading' ? 'bg-blue-100' :
                    'bg-gray-100'}
                `}>
                  {uploadFile.status === 'success' ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : uploadFile.status === 'error' ? (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  ) : (
                    <FileText className="w-5 h-5 text-gray-600" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {uploadFile.file.name}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>{(uploadFile.file.size / 1024).toFixed(1)} KB</span>
                    {uploadFile.status === 'uploading' && (
                      <>
                        <span>•</span>
                        <span>{uploadFile.progress}%</span>
                      </>
                    )}
                    {uploadFile.status === 'success' && (
                      <>
                        <span>•</span>
                        <span className="text-green-600">Uploaded</span>
                      </>
                    )}
                    {uploadFile.status === 'error' && (
                      <>
                        <span>•</span>
                        <span className="text-red-600">{uploadFile.error}</span>
                      </>
                    )}
                  </div>

                  {/* Progress Bar */}
                  {uploadFile.status === 'uploading' && (
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${uploadFile.progress}%` }}
                      />
                    </div>
                  )}
                </div>

                {(uploadFile.status === 'pending' || uploadFile.status === 'error') && (
                  <button
                    onClick={() => removeFile(index)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Summary */}
          {(successCount > 0 || errorCount > 0) && (
            <div className="flex items-center gap-4 px-2 text-sm">
              {successCount > 0 && (
                <span className="text-green-600 font-medium">
                  ✓ {successCount} uploaded
                </span>
              )}
              {errorCount > 0 && (
                <span className="text-red-600 font-medium">
                  ✗ {errorCount} failed
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
