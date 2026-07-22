import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertCircle, Eye, EyeOff, Activity, HeartPulse, Radio, ShieldCheck, X } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { register, login, getMe } from '../../services/authService';
import { Button } from '../../components/ui/Button';

const HIGHLIGHTS = [
  { icon: HeartPulse, text: 'Monitoreo de signos vitales en tiempo real' },
  { icon: Radio, text: 'Teleconsulta con videollamada segura' },
  { icon: ShieldCheck, text: 'Trazabilidad completa para auditoría clínica' },
];

const TERMS_VERSION = '1.0';

function TermsModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-surface rounded-2xl shadow-xl p-6 sm:p-8">
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">
            Términos y Condiciones, Tratamiento de Datos y uso de IA
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="text-gray-400 hover:text-gray-600 shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4 text-sm text-gray-600 leading-relaxed">
          <p className="text-xs text-gray-400">Versión {TERMS_VERSION} — Sistema de Atención Médica Remota (SAMR)</p>

          <section>
            <h3 className="font-semibold text-gray-800 mb-1">1. Responsable del tratamiento</h3>
            <p>
              SAMR (Sistema de Atención Médica Remota) es el responsable del tratamiento de tus datos personales
              recolectados a través de esta plataforma, en los términos de la Ley Orgánica de Protección de Datos
              Personales de Ecuador (LOPDP, Registro Oficial Suplemento 459 del 26 de mayo de 2021).
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-gray-800 mb-1">2. Datos que tratamos y finalidad</h3>
            <p>
              Recolectamos datos de identificación (correo, credenciales de acceso) y, una vez completes tu perfil,
              datos de salud (síntomas, signos vitales, historial clínico, resultados de teleconsultas). Los datos
              de salud son una <strong>categoría especial de datos</strong> según el Art. 9 de la LOPDP y solo se
              tratan con tu consentimiento explícito, para la finalidad exclusiva de brindarte atención médica
              remota, evaluar el riesgo de tu caso y coordinar tu atención con profesionales de salud y centros
              médicos del consorcio.
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-gray-800 mb-1">3. Uso de Inteligencia Artificial</h3>
            <p>
              SAMR utiliza componentes de Inteligencia Artificial (chatbot de orientación, evaluación automatizada
              del nivel de riesgo y recomendaciones clínicas asistidas) para agilizar tu atención. Estas decisiones
              automatizadas:
            </p>
            <ul className="list-disc pl-5 mt-1 space-y-0.5">
              <li>Nunca sustituyen el criterio de un profesional de salud humano — toda recomendación de la IA
                queda sujeta a validación médica antes de una decisión clínica definitiva.</li>
              <li>Quedan registradas de forma inalterable (append-only) junto con su nivel de confianza y las
                fuentes utilizadas, para que puedas solicitar una explicación de cualquier decisión que te afecte.</li>
              <li>Pueden ser auditadas por el Delegado de Protección de Datos (DPD) de SAMR.</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold text-gray-800 mb-1">4. Tus derechos como titular de los datos</h3>
            <p>De acuerdo con los Arts. 9 a 15 de la LOPDP, en cualquier momento puedes ejercer:</p>
            <ul className="list-disc pl-5 mt-1 space-y-0.5">
              <li><strong>Acceso:</strong> conocer qué datos tenemos sobre ti.</li>
              <li><strong>Rectificación:</strong> corregir datos inexactos desde tu perfil.</li>
              <li><strong>Eliminación (derecho al olvido):</strong> solicitar la baja de tu cuenta y tus datos.</li>
              <li><strong>Oposición y revocatoria:</strong> retirar tu consentimiento para el tratamiento con fines
                de IA en cualquier momento, sin afectar la licitud del tratamiento previo.</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold text-gray-800 mb-1">5. Compartición de datos</h3>
            <p>
              Tus datos clínicos solo se comparten con el Consorcio, el Ministerio de Salud Pública (MSP) y el
              IESS cuando exista una atención registrada y tu consentimiento de compartición esté activo, bajo
              cifrado en tránsito y verificación de identidad entre sistemas.
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-gray-800 mb-1">6. Aceptación</h3>
            <p>
              Al marcar la casilla de aceptación te registras como paciente de SAMR y confirmas que has leído y
              comprendido este documento, aceptando el tratamiento de tus datos personales y de salud, y el uso
              de Inteligencia Artificial descrito en la sección 3, en los términos de la LOPDP.
            </p>
          </section>
        </div>

        <Button type="button" onClick={onClose} className="w-full mt-6 rounded-lg">
          Cerrar
        </Button>
      </div>
    </div>
  );
}

function extractErrors(err: unknown): string[] {
  const data = (err as { response?: { data?: Record<string, string[]> } })?.response?.data;
  if (!data) return ['No se pudo conectar con el servidor. Verifica que el backend esté corriendo.'];
  return Object.values(data).flat();
}

export function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);

    if (password !== confirmPassword) {
      setErrors(['Las contraseñas no coinciden.']);
      return;
    }

    if (!termsAccepted) {
      setErrors(['Debes aceptar los Términos y Condiciones y el Tratamiento de Datos para registrarte.']);
      return;
    }

    setLoading(true);
    try {
      // El registro público del backend crea siempre rol `patient`.
      await register(email, password, termsAccepted);
      const tokens = await login(email, password);
      useAuthStore.getState().setAccessToken(tokens.access_token);
      const user = await getMe();
      setAuth(tokens, user);
      navigate('/', { replace: true });
    } catch (err: unknown) {
      setErrors(extractErrors(err));
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
              Crea tu cuenta de paciente.
            </h2>
            <p className="text-teal-100 text-sm">
              Regístrate para reportar síntomas, solicitar atención y hacer seguimiento a tu historial médico.
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
            El registro público solo crea cuentas de paciente. El personal clínico y administrativo se da de alta por otro medio.
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
            <h1 className="text-2xl font-bold text-gray-900">Crear cuenta</h1>
            <p className="text-sm text-gray-500 mt-1">Regístrate como paciente para empezar</p>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            {errors.length > 0 && (
              <div className="flex items-start gap-2 bg-error-50 text-error-700 text-sm px-3 py-2 rounded-md border border-error-200">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <ul className="space-y-0.5">
                  {errors.map((msg) => <li key={msg}>{msg}</li>)}
                </ul>
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
                placeholder="tucorreo@ejemplo.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={8}
                  autoComplete="new-password"
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
              <p className="text-xs text-gray-400 mt-1">Mínimo 8 caracteres, con letras y números.</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
              <input
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="********"
              />
            </div>

            <div className="flex items-start gap-2 pt-1">
              <input
                id="terms-checkbox"
                type="checkbox"
                required
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-0.5 w-4 h-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500 shrink-0"
              />
              <label htmlFor="terms-checkbox" className="text-sm text-gray-600">
                He leído y acepto los{' '}
                <button
                  type="button"
                  onClick={() => setShowTerms(true)}
                  className="text-teal-600 font-medium hover:underline"
                >
                  Términos y Condiciones, el Tratamiento de Datos y el uso de Inteligencia Artificial
                </button>{' '}
                de SAMR, conforme a la LOPDP de Ecuador.
              </label>
            </div>

            <Button type="submit" size="lg" className="w-full mt-2 rounded-lg" disabled={loading || !termsAccepted}>
              {loading ? 'Creando cuenta...' : 'Crear Cuenta'}
            </Button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="text-teal-600 font-medium hover:underline">
              Inicia sesión
            </Link>
          </p>
        </div>
      </div>

      {showTerms && <TermsModal onClose={() => setShowTerms(false)} />}
    </div>
  );
}
