import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Activity, Heart, ArrowLeft, WifiOff } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

interface VitalsPoint {
  time: string;
  heartRate?: number;
  oxygen?: number;
}

interface VitalUpdateMessage {
  type: 'vital_update';
  data: {
    value: { measurements?: { heart_rate?: number; oxygen_saturation?: number } };
    recorded_at: string;
  };
}

interface AlertMessage {
  type: 'alert';
  data: { severity: string; anomalies: string[] };
}

type WsMessage = VitalUpdateMessage | AlertMessage;

function gatewayWsUrl(patientId: string, token: string): string {
  const gatewayUrl = import.meta.env.VITE_GATEWAY_URL || 'https://localhost';
  const url = new URL(gatewayUrl);
  const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${url.host}/ws/monitoring/${patientId}/?token=${encodeURIComponent(token)}`;
}

export function MonitoringView() {
  const { patientId } = useParams<{ patientId: string }>();
  const navigate = useNavigate();
  const accessToken = useAuthStore((state) => state.accessToken);

  const [data, setData] = useState<VitalsPoint[]>([]);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'closed' | 'error'>('connecting');
  const [lastAlert, setLastAlert] = useState<AlertMessage['data'] | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!patientId || !accessToken) return;

    const ws = new WebSocket(gatewayWsUrl(patientId, accessToken));
    wsRef.current = ws;
    setStatus('connecting');

    ws.onopen = () => setStatus('connected');
    ws.onclose = () => setStatus('closed');
    ws.onerror = () => setStatus('error');

    ws.onmessage = (event) => {
      const message: WsMessage = JSON.parse(event.data);
      if (message.type === 'vital_update') {
        const m = message.data.value?.measurements || {};
        setData((prev) => [
          ...prev.slice(-49),
          {
            time: new Date(message.data.recorded_at).toLocaleTimeString([], { minute: '2-digit', second: '2-digit' }),
            heartRate: m.heart_rate,
            oxygen: m.oxygen_saturation,
          },
        ]);
      } else if (message.type === 'alert') {
        setLastAlert(message.data);
      }
    };

    return () => ws.close();
  }, [patientId, accessToken]);

  const latest = data[data.length - 1];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/monitoring')} className="text-gray-400 hover:text-gray-600" aria-label="Volver">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Monitoreo en Vivo</h1>
            <p className="text-gray-600 text-sm">Paciente {patientId?.slice(0, 8)}</p>
          </div>
        </div>
        {status === 'connected' ? (
          <div className="flex items-center gap-2 bg-success-50 text-success-700 px-3 py-1 rounded-full text-sm font-medium border border-success-200">
            <span className="w-2 h-2 rounded-full bg-success-500 animate-pulse"></span>
            Transmisión en Vivo
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm font-medium border border-gray-200">
            <WifiOff className="w-4 h-4" />
            {status === 'connecting' ? 'Conectando...' : status === 'error' ? 'Error de conexión' : 'Desconectado'}
          </div>
        )}
      </div>

      {lastAlert && (
        <div className="bg-error-50 border border-error-200 text-error-700 px-4 py-3 rounded-lg text-sm">
          Alerta ({lastAlert.severity}): {lastAlert.anomalies.join(', ')}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-gray-200 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-error-50 text-error-600 flex items-center justify-center">
            <Heart className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Frecuencia Cardíaca</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">{latest?.heartRate ?? '--'}</span>
              <span className="text-sm text-gray-500">bpm</span>
            </div>
          </div>
        </div>

        <div className="bg-surface p-6 rounded-lg shadow-sm border border-gray-200 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-info-50 text-info-600 flex items-center justify-center">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Saturación de Oxígeno (SpO2)</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">{latest?.oxygen ?? '--'}</span>
              <span className="text-sm text-gray-500">%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-surface p-6 rounded-lg shadow-sm border border-gray-200 h-100">
        <h3 className="text-sm font-bold text-gray-900 mb-6 uppercase tracking-wider">Histórico de Signos Vitales</h3>
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400 text-sm">
            Esperando datos del dispositivo IoT del paciente...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <Line type="monotone" dataKey="heartRate" stroke="#ef4444" strokeWidth={2} name="FC (bpm)" dot={false} isAnimationActive={false} connectNulls />
              <Line type="monotone" dataKey="oxygen" stroke="#3b82f6" strokeWidth={2} name="SpO2 (%)" dot={false} isAnimationActive={false} connectNulls />
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="5 5" vertical={false} />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
              <YAxis stroke="#9ca3af" fontSize={12} domain={['dataMin - 10', 'dataMax + 10']} />
              <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend verticalAlign="top" height={36} iconType="circle" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
