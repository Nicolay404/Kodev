import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as Dialog from '@radix-ui/react-dialog';
import { Mic, MicOff, Video, VideoOff, PhoneOff, Users, X, FileText, AlertTriangle } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export function TeleconsultRoom() {
  const navigate = useNavigate();
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const [micEnabled, setMicEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [confirmHangupOpen, setConfirmHangupOpen] = useState(false);

  useEffect(() => {
    // Solicitar acceso a cámara y micrófono simulado/real
    async function setupMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        setLocalStream(stream);
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accediendo a los dispositivos de medios.", err);
      }
    }
    setupMedia();

    return () => {
      // Limpiar stream al desmontar
      if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggleMic = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach(track => {
        track.enabled = !micEnabled;
      });
      setMicEnabled(!micEnabled);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach(track => {
        track.enabled = !videoEnabled;
      });
      setVideoEnabled(!videoEnabled);
    }
  };

  const handleHangup = () => {
    setConfirmHangupOpen(true);
  };

  const executeHangup = () => {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
    }
    setConfirmHangupOpen(false);
    navigate('/');
  };

  return (
    <div className="h-full flex flex-col space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sala de Teleconsulta</h1>
          <p className="text-gray-600 text-sm">Sesión #TC-9824</p>
        </div>
        <div className="flex items-center gap-2 bg-warning-50 text-warning-700 px-3 py-1 rounded-full text-sm font-medium border border-warning-200">
          <span className="w-2 h-2 rounded-full bg-warning-500 animate-pulse"></span>
          Esperando al paciente...
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 min-h-[400px]">
        {/* Main Remote Video Area (Simulated waiting) */}
        <div className="lg:col-span-3 bg-gray-900 rounded-lg overflow-hidden relative flex items-center justify-center border border-gray-800">
          <div className="text-center">
            <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 font-medium">El paciente aún no se ha conectado</p>
            <p className="text-gray-500 text-sm mt-1">Asegúrese de que su cámara y micrófono estén listos.</p>
          </div>
          
          {/* Controls Overlay */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-gray-800/80 backdrop-blur-md px-6 py-3 rounded-2xl border border-gray-700">
            <button 
              onClick={toggleMic}
              className={`p-3 rounded-full transition-colors ${micEnabled ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-error-600 hover:bg-error-700 text-white'}`}
            >
              {micEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
            </button>
            <button 
              onClick={toggleVideo}
              className={`p-3 rounded-full transition-colors ${videoEnabled ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-error-600 hover:bg-error-700 text-white'}`}
            >
              {videoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
            </button>
            <button 
              onClick={handleHangup}
              className="p-3 rounded-full bg-error-600 hover:bg-error-700 text-white ml-4"
              title="Finalizar Llamada"
            >
              <PhoneOff className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Sidebar: Local Video & Info */}
        <div className="flex flex-col gap-4">
          <div className="bg-gray-800 rounded-lg overflow-hidden relative aspect-video border border-gray-700">
            <video 
              ref={localVideoRef} 
              autoPlay 
              playsInline 
              muted 
              className={`w-full h-full object-cover ${!videoEnabled && 'hidden'}`}
            />
            {!videoEnabled && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                <VideoOff className="w-8 h-8 text-gray-600" />
              </div>
            )}
            <div className="absolute bottom-2 left-2 bg-black/60 px-2 py-1 rounded text-xs text-white font-medium">
              Tú (Médico)
            </div>
          </div>

          <div className="bg-surface p-4 rounded-lg border border-gray-200 flex-1">
            <h3 className="font-semibold text-gray-900 mb-4 border-b pb-2">Datos de la Consulta</h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-500 block text-xs">Paciente Asignado</span>
                <span className="font-medium">Ana Garcia</span>
              </div>
              <div>
                <span className="text-gray-500 block text-xs">Motivo Principal</span>
                <span>Control de hipertensión</span>
              </div>
              <div className="pt-4 mt-4 border-t border-gray-100">
                <Button variant="outline" className="w-full text-xs" onClick={() => setHistoryOpen(true)}>
                  Ver Historial Clínico completo
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Historial Clínico Modal */}
      <Dialog.Root open={historyOpen} onOpenChange={setHistoryOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
          <Dialog.Content className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-md bg-surface shadow-2xl p-6 animate-in slide-in-from-right duration-300 overflow-y-auto">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
              <Dialog.Title className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <FileText className="w-6 h-6 text-teal-600" />
                Historial Clínico
              </Dialog.Title>
              <Dialog.Close asChild>
                <button className="text-gray-400 hover:text-gray-600 transition-colors bg-gray-100 p-2 rounded-full" aria-label="Cerrar">
                  <X className="w-5 h-5" />
                </button>
              </Dialog.Close>
            </div>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Paciente</h3>
                <p className="text-lg font-bold text-gray-900">Ana Garcia</p>
                <p className="text-sm text-gray-600">45 años • C.I: 1700000001 • Sangre: O+</p>
              </div>

              <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
                <h3 className="text-sm font-bold text-warning-800 flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4" /> Alergias Conocidas
                </h3>
                <ul className="list-disc pl-5 text-sm text-warning-700">
                  <li>Penicilina</li>
                  <li>Ibuprofeno (Reacción leve)</li>
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Últimas Visitas</h3>
                <div className="space-y-3">
                  <div className="border-l-2 border-teal-500 pl-3">
                    <p className="text-xs text-gray-400">12 Oct 2023</p>
                    <p className="text-sm font-medium text-gray-900">Control de Hipertensión</p>
                    <p className="text-sm text-gray-600">Presión arterial estable (120/80). Se mantiene medicación actual.</p>
                  </div>
                  <div className="border-l-2 border-gray-300 pl-3">
                    <p className="text-xs text-gray-400">05 Jun 2023</p>
                    <p className="text-sm font-medium text-gray-900">Infección Respiratoria</p>
                    <p className="text-sm text-gray-600">Tratamiento con Azitromicina. Recuperación completa.</p>
                  </div>
                </div>
              </div>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      {/* Modal de Confirmación de Finalizar Llamada */}
      <Dialog.Root open={confirmHangupOpen} onOpenChange={setConfirmHangupOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-sm translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200">
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-error-50 text-error-600 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <Dialog.Title className="text-lg font-bold text-gray-900 mb-2">
                Finalizar Teleconsulta
              </Dialog.Title>
              <Dialog.Description className="text-sm text-gray-500 mb-6">
                ¿Estás seguro que deseas terminar esta llamada? El paciente será desconectado.
              </Dialog.Description>
              <div className="flex gap-3 w-full">
                <Button variant="outline" className="flex-1" onClick={() => setConfirmHangupOpen(false)}>
                  Cancelar
                </Button>
                <Button variant="primary" className="flex-1 bg-error-600 hover:bg-error-700 focus:ring-error-500 border-error-600 hover:border-error-700" onClick={executeHangup}>
                  Terminar Llamada
                </Button>
              </div>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

    </div>
  );
}
