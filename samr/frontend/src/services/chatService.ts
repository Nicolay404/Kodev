import { gatewayClient } from '../config/gatewayClient';

export interface ChatResponse {
  chat_id: string;
  response: string;
  confidence: number;
  source: 'faq' | 'human_escalation';
  timestamp: string;
}

/**
 * POST /api/solicitud/chat/ (solicitud-service, vía Gateway) — exclusivo `patient`.
 * No es un LLM: compara solapamiento de palabras contra las FAQ administradas
 * (MVPChatAdapter, umbral MVP_FAQ_CONFIDENCE_THRESHOLD). Sin match suficiente,
 * responde con `source: "human_escalation"`.
 */
export const sendChatMessage = async (message: string, chatId?: string): Promise<ChatResponse> => {
  const { data } = await gatewayClient.post<ChatResponse>('/api/solicitud/chat/', {
    message,
    ...(chatId ? { chat_id: chatId } : {}),
  });
  return data;
};

/** DELETE /api/solicitud/conversations/<id>/ */
export const deleteConversation = async (id: string): Promise<void> => {
  await gatewayClient.delete(`/api/solicitud/conversations/${id}/`);
};
