import { useMutation } from '@tanstack/react-query';
import { sendChatMessage, deleteConversation } from '../services/chatService';

export const useSendChatMessage = () => {
  return useMutation({
    mutationFn: ({ message, chatId }: { message: string; chatId?: string }) => sendChatMessage(message, chatId),
  });
};

export const useDeleteConversation = () => {
  return useMutation({
    mutationFn: (id: string) => deleteConversation(id),
  });
};
