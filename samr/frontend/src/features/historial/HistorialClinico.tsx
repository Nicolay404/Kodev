import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Stethoscope, FolderCheck, Send } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuthStore } from '../../store/authStore';
import { useHistorial, useAddClinicalNote } from '../../hooks/useHistorial';
import type { HistorialEvent } from '../../services/historialService';

const CAN_WRITE = ['professional', 'nurse'];

function EventCard({ event }: { event: HistorialEvent }) {
  if (event.event_type === 'clinical.note') {
    return (
      <div className="flex gap-3">
        <div className="w-8 h-8 rounded-full bg-info-50 text-info-600 flex items-center justify-center shrink-0">
          <FileText className="w-4 h-4" />
        </div>
        <div className="bg-gray-50 border border-gray-100 rounded-lg p-3 flex-1">
          <p className="text-sm text-gray-900">{String(event.note)}</p>
          <p className="text-xs text-gray-400 mt-1">
            {event.created_at ? new Date(String(event.created_at)).toLocaleString() : ''} · Nota clínica
          </p>
        </div>
      </div>
    );
  }

  if (event.event_type === 'caso.cerrado') {
    return (
      <div className="flex gap-3">
        <div className="w-8 h-8 rounded-full bg-success-50 text-success-600 flex items-center justify-center shrink-0">
          <FolderCheck className="w-4 h-4" />
        </div>
        <div className="bg-success-50 border border-success-100 rounded-lg p-3 flex-1">
          <p className="text-sm text-gray-900">{String(event.clinical_notes ?? 'Caso cerrado')}</p>
          <p className="text-xs text-gray-400 mt-1">
            {event.closed_at ? new Date(String(event.closed_at)).toLocaleString() : ''} · Cierre de caso
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center shrink-0">
        <Stethoscope className="w-4 h-4" />
      </div>
      <div className="bg-gray-50 border border-gray-100 rounded-lg p-3 flex-1">
        <p className="text-sm font-medium text-gray-700">{event.event_type}</p>
        <pre className="text-xs text-gray-500 mt-1 overflow-x-auto">{JSON.stringify(event, null, 2)}</pre>
      </div>
    </div>
  );
}

export function HistorialClinico() {
  const { patientId: routeParam } = useParams<{ patientId: string }>();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const [manualId, setManualId] = useState('');
  const [note, setNote] = useState('');

  const patientId = user?.role === 'patient' ? user.id : routeParam;
  const { data: historial, isLoading, isError, error } = useHistorial(patientId);
  const { mutate: addNote, isPending } = useAddClinicalNote(patientId);

  const notFound = isError && (error as { response?: { status?: number } })?.response?.status === 404;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualId.trim()) navigate(`/historial/${manualId.trim()}`);
  };

  const handleAddNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (!note.trim()) return;
    addNote(note.trim(), { onSuccess: () => setNote('') });
  };

  if (!patientId) {
    return (
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Historial Clínico</h1>
        <p className="text-gray-500 text-sm mb-4">
          No hay un directorio de pacientes en el backend todavía — ingresa el ID (UUID) del paciente.
        </p>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            value={manualId}
            onChange={(e) => setManualId(e.target.value)}
            placeholder="00000000-0000-0000-0000-000000000000"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
          <Button type="submit">Buscar</Button>
        </form>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Historial Clínico</h1>
        <p className="text-gray-600 text-sm">Paciente {patientId.slice(0, 8)}</p>
      </div>

      <div className="bg-surface rounded-lg border border-gray-200 p-4 space-y-4">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)
        ) : notFound || !historial?.eventos?.length ? (
          <p className="text-center text-gray-500 py-8">Sin eventos registrados en el historial todavía.</p>
        ) : (
          [...historial.eventos].reverse().map((event, i) => <EventCard key={event.event_key ?? i} event={event} />)
        )}
      </div>

      {user && CAN_WRITE.includes(user.role) && (
        <form onSubmit={handleAddNote} className="bg-surface rounded-lg border border-gray-200 p-4 space-y-3">
          <label className="block text-sm font-medium text-gray-700">Agregar nota clínica</label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            placeholder="Observación clínica..."
          />
          <Button type="submit" disabled={isPending || !note.trim()}>
            <Send className="w-4 h-4 mr-1" /> {isPending ? 'Guardando...' : 'Agregar Nota'}
          </Button>
        </form>
      )}
    </div>
  );
}
