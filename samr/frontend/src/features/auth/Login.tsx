import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AlertCircle, Eye, EyeOff, Activity, ShieldCheck, Radio, HeartPulse } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { login, getMe } from '../../services/authService';
import { Button } from '../../components/ui/Button';

const HIGHLIGHTS = [
  { icon: HeartPulse, text: 'Monitoreo de signos vitales en tiempo real' },
  { icon: Radio, text: 'Teleconsulta con videollamada segura' },
  { icon: ShieldCheck, text: 'Trazabilidad completa para auditoría clínica' },
];

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await login(email, password);
      // El JWT trae `rol`/`email`, pero /api/auth/me/ es la fuente de verdad tipada.
      useAuthStore.getState().setAccessToken(tokens.access_token);
      const user = await getMe();
      setAuth(tokens, user);
      const from = (location.state as { from?: Location })?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 401) {
        setError('Correo o contraseña incorrectos.');
      } else if (status === 429) {
        setError('Cuenta bloqueada temporalmente por demasiados intentos fallidos. Intenta más tarde.');
      } else {
        setError('No se pudo conectar con el servidor. Verifica que el backend esté corriendo.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 rounded-3xl shadow-xl overflow-hidden bg-surface">
        {/* Panel izquierdo — branding, oculto en mobile */}
        <div className="relative hidden lg:flex flex-col justify-between p-10 bg-linear-to-br from-teal-700 via-teal-800 to-gray-900 text-white overflow-hidden">
          <div className="absolute -top-16 -right-16 w-72 h-72 rounded-full bg-teal-500/20 blur-3xl" />
          <div className="absolute -bottom-24 -left-10 w-72 h-72 rounded-full bg-info-500/20 blur-3xl" />

          <div className="relative flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
            <span className="font-bold text-lg tracking-tight">SAMR</span>
          </div>

          <div className="relative space-y-6">
            <h2 className="text-3xl font-bold leading-tight">
              Atención médica remota, conectada y segura.
            </h2>
            <p className="text-teal-100 text-sm">
              Sistema de Atención Médica Remota — pacientes, personal clínico y administración en una sola plataforma.
            </p>
            <ul className="space-y-3 pt-2">
              {HIGHLIGHTS.map(({ icon: Icon, text }) => (
                <li key={text} className="flex items-center gap-3 text-sm text-teal-50">
                  <span className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                    <Icon className="w-4 h-4" />
                  </span>
                  {text}
                </li>
              ))}
            </ul>
          </div>

          <p className="relative text-xs text-teal-200/70">
            Acceso exclusivo para pacientes y personal autorizado.
          </p>
        </div>

        {/* Panel derecho — formulario real */}
        <div className="p-8 sm:p-10 flex flex-col justify-center">
          <div className="mb-8">
            <div className="flex items-center gap-2 lg:hidden mb-6">
              <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center">
                <Activity className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-lg text-gray-900">SAMR</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Bienvenido de nuevo</h1>
            <p className="text-sm text-gray-500 mt-1">Inicia sesión en tu cuenta para continuar</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="flex items-start gap-2 bg-error-50 text-error-700 text-sm px-3 py-2 rounded-md border border-error-200">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="usuario@samr.test"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2.5 pr-10 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="********"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <Button type="submit" size="lg" className="w-full mt-2 rounded-lg" disabled={loading}>
              {loading ? 'Iniciando sesión...' : 'Ingresar'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
