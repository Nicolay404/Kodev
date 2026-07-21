import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Activity, Heart, Thermometer } from 'lucide-react';

interface VitalsData {
  time: string;
  heartRate: number;
  oxygen: number;
}

export function MonitoringView() {
  const [data, setData] = useState<VitalsData[]>([]);

  // Simulate real-time data ingestion via WebSockets
  useEffect(() => {
    // Generar datos históricos iniciales
    const initialData: VitalsData[] = Array.from({ length: 20 }).map((_, i) => ({
      time: new Date(Date.now() - (20 - i) * 3000).toLocaleTimeString([], { minute: '2-digit', second: '2-digit' }),
      heartRate: 70 + Math.random() * 15,
      oxygen: 95 + Math.random() * 4,
    }));
    
    setData(initialData);

    const interval = setInterval(() => {
      setData((prev) => {
        const newData = [...prev.slice(1)];
        newData.push({
          time: new Date().toLocaleTimeString([], { minute: '2-digit', second: '2-digit' }),
          heartRate: 70 + Math.random() * 15,
          oxygen: 95 + Math.random() * 4,
        });
        return newData;
      });
    }, 3000); // Actualiza cada 3 segundos

    return () => clearInterval(interval);
  }, []);

  const latestData = data[data.length - 1] || { heartRate: 0, oxygen: 0 };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Monitoreo de Paciente</h1>
          <p className="text-gray-600 text-sm">Dispositivo conectado: BioMonitor X1 (Ana Garcia)</p>
        </div>
        <div className="flex items-center gap-2 bg-success-50 text-success-700 px-3 py-1 rounded-full text-sm font-medium border border-success-200">
          <span className="w-2 h-2 rounded-full bg-success-500 animate-pulse"></span>
          Transmisión en Vivo
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* KPI: Heart Rate */}
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-gray-200 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-error-50 text-error-600 flex items-center justify-center">
            <Heart className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Frecuencia Cardíaca</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">{Math.round(latestData.heartRate)}</span>
              <span className="text-sm text-gray-500">bpm</span>
            </div>
          </div>
        </div>

        {/* KPI: Oxygen */}
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-gray-200 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-info-50 text-info-600 flex items-center justify-center">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Saturación de Oxígeno (SpO2)</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">{Math.round(latestData.oxygen)}</span>
              <span className="text-sm text-gray-500">%</span>
            </div>
          </div>
        </div>

        {/* KPI: Temp (Static Mock) */}
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-gray-200 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-warning-50 text-warning-600 flex items-center justify-center">
            <Thermometer className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Temperatura</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">36.8</span>
              <span className="text-sm text-gray-500">°C</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-surface p-6 rounded-lg shadow-sm border border-gray-200 h-[400px]">
        <h3 className="text-sm font-bold text-gray-900 mb-6 uppercase tracking-wider">Histórico de Signos Vitales (Tiempo Real)</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <Line type="monotone" dataKey="heartRate" stroke="#ef4444" strokeWidth={2} name="FC (bpm)" dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="oxygen" stroke="#3b82f6" strokeWidth={2} name="SpO2 (%)" dot={false} isAnimationActive={false} />
            <CartesianGrid stroke="#e5e7eb" strokeDasharray="5 5" vertical={false} />
            <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
            <YAxis stroke="#9ca3af" fontSize={12} domain={['dataMin - 10', 'dataMax + 10']} />
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
