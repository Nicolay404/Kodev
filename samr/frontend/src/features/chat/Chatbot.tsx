import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Bot, User, AlertTriangle, RotateCcw } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { useSendChatMessage, useDeleteConversation } from '../../hooks/useChat';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  source?: 'faq' | 'human_escalation';
  confidence?: number;
}

export function Chatbot() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hola, cuéntame qué síntomas tienes o qué necesitas saber. Si es una emergencia, usa el botón de Emergencias en vez de este chat.' },
  ]);
  const [input, setInput] = useState('');
  const [chatId, setChatId] = useState<string | undefined>(undefined);
  const { mutate: send, isPending } = useSendChatMessage();
  const { mutate: reset } = useDeleteConversation();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isPending) return;

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');

    send(
      { message: text, chatId },
      {
        onSuccess: (res) => {
          setChatId(res.chat_id);
          setMessages((prev) => [
            ...prev,
            { role: 'assistant', content: res.response, source: res.source, confidence: res.confidence },
          ]);
        },
        onError: () => {
          setMessages((prev) => [
            ...prev,
            { role: 'assistant', content: 'No se pudo procesar tu mensaje. Intenta de nuevo.' },
          ]);
        },
      }
    );
  };

  const handleNewConversation = () => {
    if (chatId) reset(chatId);
    setChatId(undefined);
    setMessages([
      { role: 'assistant', content: 'Nueva conversación. Cuéntame qué síntomas tienes o qué necesitas saber.' },
    ]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Asistente de Orientación</h1>
          <p className="text-gray-600 text-sm">
            Respuestas basadas en preguntas frecuentes administradas — no es un diagnóstico médico.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={handleNewConversation}>
          <RotateCcw className="w-4 h-4 mr-1" /> Nueva conversación
        </Button>
      </div>

      <div className="flex-1 bg-surface rounded-lg border border-gray-200 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
            )}
            <div className={`max-w-[75%] rounded-lg px-4 py-2.5 text-sm ${
              m.role === 'user' ? 'bg-teal-600 text-white' : 'bg-gray-100 text-gray-900'
            }`}>
              <p>{m.content}</p>
              {m.source === 'human_escalation' && (
                <div className="flex items-center gap-1 mt-2 text-xs text-warning-700">
                  <AlertTriangle className="w-3 h-3" /> Sin respuesta verificada — considera reportar una solicitud
                </div>
              )}
            </div>
            {m.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        {isPending && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-gray-100 rounded-lg px-4 py-2.5 text-sm text-gray-400">Escribiendo...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="flex gap-2 mt-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribe tu mensaje..."
          className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
        />
        <Button type="submit" disabled={isPending || !input.trim()}>
          <Send className="w-4 h-4" />
        </Button>
      </form>

      <button
        type="button"
        onClick={() => navigate('/emergencies')}
        className="text-xs text-error-600 hover:underline mt-2 self-center"
      >
        ¿Es una emergencia? Repórtala directamente
      </button>
    </div>
  );
}
