import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Activity, Info } from 'lucide-react';
import { requestPasswordReset, confirmPasswordReset } from '../../services/authService';
import { Button } from '../../components/ui/Button';

export function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [requested, setRequested] = useState(false);
  const [loading, setLoading] = useState(false);

  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [confirmSuccess, setConfirmSuccess] = useState(false);

  const handleRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await requestPasswordReset(email);
    } finally {
      setLoading(false);
      setRequested(true);
    }
  };

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    setConfirmError(null);
    if (newPassword !== confirmPw) {
      setConfirmError('Las contraseñas no coinciden.');
      return;
    }
    setConfirmLoading(true);
    try {
      await confirmPasswordReset(token, newPassword);
      setConfirmSuccess(true);
    } catch {
      setConfirmError('El código es inválido o expiró (dura 15 minutos). Solicita uno nuevo.');
    } finally {
      setConfirmLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-md bg-surface rounded-3xl shadow-xl p-8">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center">
            <Activity className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg text-gray-900">SAMR</span>
        </div>

        {confirmSuccess ? (
          <div className="text-center space-y-4">
            <CheckCircle2 className="w-12 h-12 text-success-600 mx-auto" />
            <h1 className="text-xl font-bold text-gray-900">Contraseña restablecida</h1>
            <Link to="/login">
              <Button className="w-full">Ir a Iniciar Sesión</Button>
            </Link>
          </div>
        ) : (
          <>
            <h1 className="text-xl font-bold text-gray-900">Recuperar contraseña</h1>
            <p className="text-sm text-gray-500 mt-1 mb-4">
              Paso 1: solicita el código. Paso 2: pégalo aquí junto con tu nueva contraseña.
            </p>

            {!requested ? (
              <form onSubmit={handleRequest} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="usuario@samr.test"
                  />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Enviando...' : 'Solicitar código'}
                </Button>
              </form>
            ) : (
              <>
                <div className="flex items-start gap-2 bg-info-50 text-info-700 text-sm px-3 py-2 rounded-md border border-info-100 mb-4">
                  <Info className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>
                    Si la cuenta existe, se generó un código. En este entorno de prueba (MVP) el código <strong>no se envía por correo</strong> —
                    aún no hay integración de email. Pídeselo al equipo de soporte, o si tienes acceso, revisa la bandeja de <strong>Notificaciones</strong>
                    con esa cuenta (evento <code>auth.password_reset_requested</code>).
                  </span>
                </div>

                <form onSubmit={handleConfirm} className="space-y-4">
                  {confirmError && (
                    <div className="flex items-start gap-2 bg-error-50 text-error-700 text-sm px-3 py-2 rounded-md border border-error-200">
                      <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                      <span>{confirmError}</span>
                    </div>
                  )}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Código de recuperación</label>
                    <textarea
                      required
                      value={token}
                      onChange={(e) => setToken(e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono"
                      placeholder="Pega aquí el token"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña nueva</label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
                    <input
                      type="password"
                      required
                      value={confirmPw}
                      onChange={(e) => setConfirmPw(e.target.value)}
                      className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={confirmLoading}>
                    {confirmLoading ? 'Restableciendo...' : 'Restablecer Contraseña'}
                  </Button>
                </form>
              </>
            )}
          </>
        )}

        <p className="text-center text-sm text-gray-500 mt-6">
          <Link to="/login" className="text-teal-600 font-medium hover:underline">
            Volver a Iniciar Sesión
          </Link>
        </p>
      </div>
    </div>
  );
}
