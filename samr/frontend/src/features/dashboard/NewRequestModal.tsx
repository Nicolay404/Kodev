import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Button } from '../../components/ui/Button';

interface NewRequestModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: (data: { cedula: string; reason: string }) => void;
}

export function NewRequestModal({ open, onOpenChange, onSuccess }: NewRequestModalProps) {
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData(e.currentTarget);
    const data = {
      cedula: formData.get('cedula') as string,
      reason: formData.get('reason') as string,
    };
    
    // Simular llamada al BFF
    setTimeout(() => {
      setLoading(false);
      onOpenChange(false);
      toast.success('Solicitud creada exitosamente');
      onSuccess(data);
    }, 1500);
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200">
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title className="text-lg font-bold text-gray-900">
              Nueva Solicitud Médica
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-gray-400 hover:text-gray-600 transition-colors" aria-label="Cerrar">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>
          
          <Dialog.Description className="text-sm text-gray-500 mb-6">
            Ingresa los datos iniciales para la solicitud de teleconsulta.
          </Dialog.Description>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cédula del Paciente</label>
              <input 
                name="cedula"
                type="text" 
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent" 
                placeholder="17xxxxxxxx"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Motivo de Consulta</label>
              <textarea 
                name="reason"
                required
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent" 
                placeholder="Describa brevemente los síntomas..."
              />
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <Dialog.Close asChild>
                <Button type="button" variant="ghost">Cancelar</Button>
              </Dialog.Close>
              <Button type="submit" disabled={loading}>
                {loading ? 'Procesando...' : 'Crear Solicitud'}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
