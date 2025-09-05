import { useState, useCallback } from 'react';
import { apiClient, endpoints } from '@/lib/api';
import { UploadProgress } from '@/types';
import { useToast } from '@/hooks/use-toast';

export interface UseUploadOptions {
  onSuccess?: (file: File, response: any) => void;
  onError?: (file: File, error: Error) => void;
  onProgress?: (file: File, progress: number) => void;
  maxFileSize?: number; // in bytes
  allowedTypes?: string[];
  multiple?: boolean;
}

export function useUpload(options: UseUploadOptions = {}) {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();

  const {
    onSuccess,
    onError,
    onProgress,
    maxFileSize = 100 * 1024 * 1024, // 100MB default
    allowedTypes = ['image/*', 'video/*', 'audio/*'],
    multiple = true,
  } = options;

  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > maxFileSize) {
      return `Файл "${file.name}" слишком большой. Максимальный размер: ${Math.round(maxFileSize / 1024 / 1024)} МБ`;
    }

    // Check file type
    const isValidType = allowedTypes.some(type => {
      if (type.endsWith('/*')) {
        return file.type.startsWith(type.slice(0, -1));
      }
      return file.type === type;
    });

    if (!isValidType) {
      return `Неподдерживаемый тип файла "${file.name}". Разрешенные типы: ${allowedTypes.join(', ')}`;
    }

    return null;
  }, [maxFileSize, allowedTypes]);

  const uploadFile = useCallback(async (file: File, pageId?: string): Promise<any> => {
    const validationError = validateFile(file);
    if (validationError) {
      throw new Error(validationError);
    }

    // Add to uploads list
    const uploadProgress: UploadProgress = {
      file,
      progress: 0,
      status: 'uploading',
    };

    setUploads(prev => [...prev, uploadProgress]);

    try {
      // Upload file
      const response = await apiClient.uploadWithProgress(
        endpoints.media.upload(),
        file,
        (progress) => {
          setUploads(prev => 
            prev.map(upload => 
              upload.file === file 
                ? { ...upload, progress }
                : upload
            )
          );
          onProgress?.(file, progress);
        }
      );

      // Update status to completed
      setUploads(prev => 
        prev.map(upload => 
          upload.file === file 
            ? { ...upload, status: 'completed', progress: 100 }
            : upload
        )
      );

      // Attach to page if pageId provided
      if (pageId && response.data?.id) {
        await apiClient.post(endpoints.media.attach(response.data.id), {
          page_id: pageId,
        });
      }

      onSuccess?.(file, response.data);
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки файла';
      
      // Update status to error
      setUploads(prev => 
        prev.map(upload => 
          upload.file === file 
            ? { ...upload, status: 'error', error: errorMessage }
            : upload
        )
      );

      onError?.(file, error as Error);
      throw error;
    }
  }, [validateFile, onSuccess, onError, onProgress]);

  const uploadFiles = useCallback(async (files: File[], pageId?: string): Promise<any[]> => {
    if (!multiple && files.length > 1) {
      throw new Error('Можно загрузить только один файл');
    }

    setIsUploading(true);
    const results: any[] = [];

    try {
      // Upload files sequentially to avoid overwhelming the server
      for (const file of files) {
        try {
          const result = await uploadFile(file, pageId);
          results.push(result);
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
          // Continue with other files even if one fails
        }
      }

      return results;
    } finally {
      setIsUploading(false);
    }
  }, [multiple, uploadFile]);

  const clearUploads = useCallback(() => {
    setUploads([]);
  }, []);

  const removeUpload = useCallback((file: File) => {
    setUploads(prev => prev.filter(upload => upload.file !== file));
  }, []);

  const retryUpload = useCallback(async (file: File, pageId?: string) => {
    // Remove the failed upload
    removeUpload(file);
    
    // Retry upload
    return uploadFile(file, pageId);
  }, [removeUpload, uploadFile]);

  return {
    uploads,
    isUploading,
    uploadFile,
    uploadFiles,
    clearUploads,
    removeUpload,
    retryUpload,
    validateFile,
  };
}
