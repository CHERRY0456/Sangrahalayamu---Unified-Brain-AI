import { apiClient } from '@/lib/api-client';
import { ExplanationData } from '@/features/transparency/transparency-panel';

export class ChatService {
  /**
   * Submits operational clearance requests for locked context categories.
   */
  public async submitAccessRequest(resourceId: string, reason: string): Promise<boolean> {
    try {
      const response = await apiClient.post<{ success: boolean }>('/api/v1/access/request', {
        document_id: parseInt(resourceId, 10),
        requested_sections: [],
        justification: reason,
      });
      return !!response;
    } catch (e) {
      console.error('Access request submission failed:', e);
      return false;
    }
  }

  /**
   * Fetches RAG explainability traces and node graphs for specific messages.
   */
  public async getTraceExplanation(messageId: string): Promise<ExplanationData | null> {
    try {
      return await apiClient.get<ExplanationData>(`/api/v1/chat/explain/${messageId}`);
    } catch (e) {
      return null;
    }
  }
}

export const chatService = new ChatService();
export default chatService;
