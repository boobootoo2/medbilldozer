/**
 * Document upload component with drag-and-drop
 */
import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { documentsService } from '../../services/documents.service';

interface DocumentUploadProps {
  onUploadComplete?: (documentId: string) => void;
}

export const DocumentUpload = ({ onUploadComplete }: DocumentUploadProps) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);
    setSuccess(false);
    setProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      // Upload document
      const documentId = await documentsService.uploadDocument(file, 'medical_bill');

      clearInterval(progressInterval);
      setProgress(100);
      setSuccess(true);
      setUploading(false);

      if (onUploadComplete) {
        onUploadComplete(documentId);
      }

      // Reset after 2 seconds
      setTimeout(() => {
        setSuccess(false);
        setProgress(0);
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
      setUploading(false);
      setProgress(0);
    }
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt']
    },
    multiple: false,
    disabled: uploading
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          {!uploading && !success && (
            <>
              <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <p className="text-lg font-semibold text-gray-900 mb-1">
                  {isDragActive ? 'Drop file here' : 'Drag & drop your medical bill'}
                </p>
                <p className="text-sm text-gray-500">
                  or click to browse (PDF, PNG, JPG, TXT)
                </p>
              </div>
            </>
          )}

          {uploading && (
            <>
              <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
                <FileText className="w-8 h-8 text-blue-600 animate-pulse" />
              </div>
              <div className="w-full max-w-xs">
                <p className="text-sm font-medium text-gray-900 mb-2">
                  Uploading... {progress}%
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            </>
          )}

          {success && (
            <>
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-lg font-semibold text-green-900">
                Upload successful!
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-900">Upload failed</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        <p>Supported formats: PDF, PNG, JPG, TXT (max 10MB)</p>
      </div>
    </div>
  );
};
