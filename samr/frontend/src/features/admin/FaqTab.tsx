import { useState } from 'react';
import { Plus, Pencil } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useFAQs, useCreateFAQ, useUpdateFAQ } from '../../hooks/useAdmin';
import type { FAQ } from '../../services/adminService';

export function FaqTab() {
  const { data: faqs, isLoading } = useFAQs();
  const { mutate: create, isPending: creating } = useCreateFAQ();
  const { mutate: update, isPending: updating } = useUpdateFAQ();
  const [editing, setEditing] = useState<FAQ | null>(null);
  const [formOpen, setFormOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fd = new FormData(form);
    const question = fd.get('question') as string;
    const answer = fd.get('answer') as string;

    if (editing) {
      update({ id: editing.id, question, answer }, { onSuccess: () => { setEditing(null); form.reset(); } });
    } else {
      create({ question, answer }, { onSuccess: () => { setFormOpen(false); form.reset(); } });
    }
  };

  const activeForm = formOpen || editing;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">FAQ consultadas por el chatbot de orientación (solicitud-service).</p>
        <Button size="sm" onClick={() => { setEditing(null); setFormOpen((v) => !v); }}>
          <Plus className="w-4 h-4 mr-1" /> Nueva FAQ
        </Button>
      </div>

      {activeForm && (
        <form onSubmit={handleSubmit} className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
          <input
            name="question"
            required
            defaultValue={editing?.question}
            placeholder="Pregunta"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
          <textarea
            name="answer"
            required
            rows={3}
            defaultValue={editing?.answer}
            placeholder="Respuesta"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={creating || updating}>
              {editing ? (updating ? 'Guardando...' : 'Guardar Cambios') : (creating ? 'Creando...' : 'Crear FAQ')}
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => { setFormOpen(false); setEditing(null); }}>
              Cancelar
            </Button>
          </div>
        </form>
      )}

      <div className="bg-surface rounded-lg border border-gray-200 divide-y divide-gray-100">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => <div key={i} className="p-4"><Skeleton className="h-4 w-3/4" /></div>)
        ) : !faqs || faqs.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No hay preguntas frecuentes configuradas.</div>
        ) : (
          faqs.map((faq) => (
            <div key={faq.id} className="p-4 flex justify-between items-start gap-4">
              <div>
                <p className="text-sm font-medium text-gray-900">{faq.question}</p>
                <p className="text-sm text-gray-500 mt-1">{faq.answer}</p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => { setEditing(faq); setFormOpen(false); }}>
                <Pencil className="w-4 h-4" />
              </Button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
