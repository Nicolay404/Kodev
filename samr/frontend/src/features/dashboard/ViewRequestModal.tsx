import * as Dialog from '@radix-ui/react-dialog';
import { X, Calendar, User, FileText, AlertCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import type { TeleconsultRequest } from '../../services/dashboardService';

interface ViewRequestModalProps {
  request: TeleconsultRequest | null;
  onClose: () => void;
}

export function ViewRequestModal({ request, onClose }: ViewRequestModalProps) {
  if (!request) return null;

  return (
    <Dialog.Root open={!!request} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200">
          <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
            <div>
              <Dialog.Title className="text-lg font-bold text-gray-900 flex items-center gap-2">
                Detalle del Caso
                <span className="text-sm font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
                  {request.id}
                </span>
              </Dialog.Title>
            </div>
            <Dialog.Close asChild>
              <button className="text-gray-400 hover:text-gray-600 transition-colors p-1" aria-label="Cerrar">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>
          
          <div className="space-y-4 text-sm">
            <div className="flex items-start gap-3">
              <User className="w-5 h-5 text-teal-600 mt-0.5" />
              <div>
                <p className="font-semibold text-gray-900">{request.patient}</p>
                <p className="text-gray-500">Cédula: {request.cedula}</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-teal-600 mt-0.5" />
              <div>
                <p className="text-gray-900">Registrado hoy a las {request.time}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-teal-600" />
              <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${
                request.status === 'En Espera' ? 'bg-warning-50 text-warning-700 border-warning-200' : 
                'bg-info-50 text-info-700 border-info-200'
              }`}>
                {request.status === 'En Espera' ? 'En Espera' : 'En Atención'}
              </span>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-start gap-3">
                <FileText className="w-5 h-5 text-teal-600 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-gray-900 mb-1">Motivo de la Consulta</p>
                  <p className="text-gray-600 bg-gray-50 p-3 rounded-md border border-gray-100">
                    {request.reason}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex gap-3 pt-2">
            <Button variant="outline" className="flex-1" onClick={onClose}>
              {request.status === 'En Espera' ? 'Cerrar' : 'Volver al Dashboard'}
            </Button>
            {request.status === 'En Espera' && (
              <Button variant="primary" className="flex-1">
                Atender Ahora
              </Button>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
