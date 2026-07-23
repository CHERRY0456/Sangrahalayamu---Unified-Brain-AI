import { apiClient } from '@/lib/api-client';

export class UploadService {
  /**
   * Uploads file queues and catalog parameters to backend storage nodes.
   */
  public async uploadDocuments(files: File[], category: string, description: string): Promise<boolean> {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      let allSuccess = true;
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('metadata', JSON.stringify({ category, description }));

        const accessToken = typeof window !== 'undefined' ? localStorage.getItem('ib-access-token') : null;
        const response = await fetch(`${baseUrl}/api/upload`, {
          method: 'POST',
          headers: {
            ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
          },
          body: formData,
        });
        
        if (!response.ok) {
           console.error(`Failed to upload ${file.name}`);
           allSuccess = false;
        }
      }
      return allSuccess;
    } catch (e) {
      console.warn('Backend API upload offline or error:', e);
      return false;
    }
  }

  /**
   * Pipeline indexing is now handled synchronously by the upload endpoint.
   * This method is retained for API compatibility and resolves immediately.
   */
  public async triggerPipelineIndex(): Promise<boolean> {
    return true;
  }
}

export const uploadService = new UploadService();
export default uploadService;
