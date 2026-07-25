import { api } from '@/lib/api-client';

export interface UploadedDocument {
  id: number;
  uuid: string;
  name: string;
  mime_type: string;
  file_size: number;
  status: string;
  classification: string;
  required_clearance: string;
  department: string;
  created_at: string;
}

export class UploadService {
  public async uploadDocuments(files: File[], category: string, description: string): Promise<boolean> {
    let allSuccess = true;

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', JSON.stringify({ category, description }));

      try {
        const document = await api.post<UploadedDocument>('/api/v1/upload', formData, {}, 300000);
        
        if (document.status === 'FAILED') {
          console.error(`Document processing failed for ${file.name}`);
          allSuccess = false;
        }
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        allSuccess = false;
      }
    }

    return allSuccess;
  }

  public async listDocuments(): Promise<UploadedDocument[]> {
    try {
      const data = await api.get<{ documents: UploadedDocument[] }>('/api/v1/upload');
      return data.documents || [];
    } catch (error) {
      console.error('Failed to list documents:', error);
      throw error;
    }
  }
}

export const uploadService = new UploadService();
export default uploadService;
