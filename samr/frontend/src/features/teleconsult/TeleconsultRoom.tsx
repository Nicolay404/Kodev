import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as Dialog from '@radix-ui/react-dialog';
import { Mic, MicOff, Video, VideoOff, PhoneOff, Users, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '../../components/ui/Button';
import { useWebRTC } from '../../hooks/useWebRTC';
import { createTeleconsultSession, type TeleconsultSession } from '../../services/teleconsultSessionService';

export function TeleconsultRoom() {
  const navigate = useNavigate();
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);

  const [patientIdInput, setPatientIdInput] = useState('');
  const [session, setSession] = useState<TeleconsultSession | null>(null);
  const [creating, setCreating] = useState(false);

  const [micEnabled, setMicEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [confirmHangupOpen, setConfirmHangupOpen] = useState(false);

  const { isConnected, error, remoteStream, attachLocalStream } = useWebRTC({
    roomToken: session?.room_token ?? null,
  });

  const handleStartSession = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const created = await createTeleconsultSession(patientIdInput.trim());
      setSession(created);
    } catch {
      // El interceptor de gatewayClient ya muestra el toast de error
    } finally {
      setCreating(false);
    }
  };

  useEffect(() => {
    if (!session) return;
    async function setupMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        setLocalStream(stream);
        if (localVideoRef.current) localVideoRef.current.srcObject = stream;
        attachLocalStream(stream);
      } catch {
        toast.error('No se pudo acceder a la cámara/micrófono.');
      }
    }
    setupMedia();
    return () => {
      localStream?.getTracks().forEach((track) => track.stop());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session]);

  useEffect(() => {
    if (remoteVideoRef.current && remoteStream) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

  const toggleMic = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach((track) => { track.enabled = !micEnabled; });
      setMicEnabled(!micEnabled);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach((track) => { track.enabled = !videoEnabled; });
      setVideoEnabled(!videoEnabled);
    }
  };

  const executeHangup = () => {
    localStream?.getTracks().forEach((track) => track.stop());
    setConfirmHangupOpen(false);
    navigate('/');
  };

  if (!session) {
    return (
      <div className="h-full flex items-center justify-center">
        <form onSubmit={handleStartSession} className="w-full max-w-sm bg-surface p-6 rounded-lg border border-gray-200 shadow-sm space-y-4">
          <div>
            <h1 className="text-lg font-bold text-gray-900">Iniciar Teleconsulta</h1>
            <p className="text-sm text-gray-500 mt-1">
              El backend aún no expone un listado de pacientes; ingresa el ID (UUID) del paciente a atender.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ID del paciente</label>
            <input
              type="text"
              required
              value={patientIdInput}
              onChange={(e) => setPatientIdInput(e.target.value)}
              placeholder="00000000-0000-0000-0000-000000000000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <Button type="submit" className="w-full" disabled={creating}>
            {creating ? 'Creando sesión...' : 'Crear sesión y unirse'}
          </Button>
        </form>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sala de Teleconsulta</h1>
          <p className="text-gray-600 text-sm">Paciente {session.patient_id.slice(0, 8)}</p>
        </div>
        {isConnected ? (
          <div className="flex items-center gap-2 bg-success-50 text-success-700 px-3 py-1 rounded-full text-sm font-medium border border-success-200">
            <span className="w-2 h-2 rounded-full bg-success-500 animate-pulse"></span>
            Señalización conectada
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-warning-50 text-warning-700 px-3 py-1 rounded-full text-sm font-medium border border-warning-200">
            <span className="w-2 h-2 rounded-full bg-warning-500 animate-pulse"></span>
            {error || 'Conectando...'}
          </div>
        )}
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 min-h-100">
        <div className="lg:col-span-3 bg-gray-900 rounded-lg overflow-hidden relative flex items-center justify-center border border-gray-800">
          {remoteStream ? (
            <video ref={remoteVideoRef} autoPlay playsInline className="w-full h-full object-cover" />
          ) : (
            <div className="text-center">
              <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 font-medium">El paciente aún no se ha conectado</p>
              <p className="text-gray-500 text-sm mt-1">Asegúrese de que su cámara y micrófono estén listos.</p>
            </div>
          )}

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
              onClick={() => setConfirmHangupOpen(true)}
              className="p-3 rounded-full bg-error-600 hover:bg-error-700 text-white ml-4"
              title="Finalizar Llamada"
            >
              <PhoneOff className="w-5 h-5" />
            </button>
          </div>
        </div>

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
              Tú
            </div>
          </div>

          <div className="bg-surface p-4 rounded-lg border border-gray-200 flex-1">
            <h3 className="font-semibold text-gray-900 mb-4 border-b pb-2">Datos de la Sesión</h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-500 block text-xs">ID de sesión</span>
                <span className="font-medium">{session.id.slice(0, 8)}</span>
              </div>
              <div>
                <span className="text-gray-500 block text-xs">Estado</span>
                <span className="font-medium">{session.status}</span>
              </div>
              {session.emergency_id && (
                <div>
                  <span className="text-gray-500 block text-xs">Emergencia asociada</span>
                  <span className="font-medium">{session.emergency_id.slice(0, 8)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

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
                ¿Estás seguro que deseas terminar esta llamada?
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
