import * as Dialog from '@radix-ui/react-dialog';
import { X, Calendar, AlertCircle, Link2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import type { Evaluacion } from '../../services/dashboardService';

interface ViewRequestModalProps {
  evaluacion: Evaluacion | null;
  onClose: () => void;
}

const RISK_LABEL: Record<Evaluacion['nivel_riesgo'], string> = {
  critico: 'Crítico',
  alto: 'Alto',
  medio: 'Medio',
  bajo: 'Bajo',
};

const RISK_STYLE: Record<Evaluacion['nivel_riesgo'], string> = {
  critico: 'bg-error-50 text-error-700 border-error-200',
  alto: 'bg-warning-50 text-warning-700 border-warning-200',
  medio: 'bg-info-50 text-info-700 border-info-200',
  bajo: 'bg-success-50 text-success-700 border-success-200',
};

export function ViewRequestModal({ evaluacion, onClose }: ViewRequestModalProps) {
  if (!evaluacion) return null;

  return (
    <Dialog.Root open={!!evaluacion} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200">
          <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
            <Dialog.Title className="text-lg font-bold text-gray-900 flex items-center gap-2">
              Detalle del Caso
              <span className="text-sm font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
                {evaluacion.id.slice(0, 8)}
              </span>
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-gray-400 hover:text-gray-600 transition-colors p-1" aria-label="Cerrar">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>

          <div className="space-y-4 text-sm">
            <div className="flex items-start gap-3">
              <Link2 className="w-5 h-5 text-teal-600 mt-0.5" />
              <div>
                <p className="font-semibold text-gray-900">Solicitud de origen</p>
                <p className="text-gray-500">{evaluacion.solicitud_id.slice(0, 8)}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-teal-600 mt-0.5" />
              <p className="text-gray-900">Evaluado el {new Date(evaluacion.created_at).toLocaleString()}</p>
            </div>

            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-teal-600" />
              <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${RISK_STYLE[evaluacion.nivel_riesgo]}`}>
                Riesgo {RISK_LABEL[evaluacion.nivel_riesgo]}
              </span>
            </div>

            <p className="text-xs text-gray-400 pt-2 border-t border-gray-100">
              El nivel de riesgo es fijado por evaluacion-service y es inmutable — no existe endpoint para editarlo.
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" className="flex-1" onClick={onClose}>
              Cerrar
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
