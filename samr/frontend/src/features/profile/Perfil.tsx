import { useEffect, useState } from 'react';
import { User, ShieldCheck, KeyRound, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuthStore } from '../../store/authStore';
import { useMyProfile, useUpdateMyProfile } from '../../hooks/usePatientProfile';
import { changePassword } from '../../services/authService';

function extractErrors(err: unknown): string[] {
  const data = (err as { response?: { data?: Record<string, string[] | string> } })?.response?.data;
  if (!data) return ['No se pudo conectar con el servidor.'];
  return Object.values(data).flat().map(String);
}

function ProfileSection() {
  const { data: profile, isLoading, isError, error } = useMyProfile();
  const { mutate: update, isPending } = useUpdateMyProfile();

  const notFound = isError && (error as { response?: { status?: number } })?.response?.status === 404;

  const [cedula, setCedula] = useState('');
  const [bloodType, setBloodType] = useState('');
  const [allergies, setAllergies] = useState('');
  const [conditions, setConditions] = useState('');
  const [consentData, setConsentData] = useState(false);
  const [consentAi, setConsentAi] = useState(false);
  const [consentSharing, setConsentSharing] = useState(false);

  useEffect(() => {
    if (profile) {
      setBloodType(profile.blood_type || '');
      setAllergies(profile.allergies.join(', '));
      setConditions(profile.chronic_conditions.join(', '));
      setConsentData(profile.consent_data);
      setConsentAi(profile.consent_ai);
      setConsentSharing(profile.consent_sharing);
    }
  }, [profile]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    update({
      ...(notFound ? { cedula } : {}),
      blood_type: bloodType,
      allergies: allergies.split(',').map((a) => a.trim()).filter(Boolean),
      chronic_conditions: conditions.split(',').map((c) => c.trim()).filter(Boolean),
      consent_data: consentData,
      consent_ai: consentAi,
      consent_sharing: consentSharing,
    });
  };

  if (isLoading) {
    return <div className="space-y-3"><Skeleton className="h-8 w-full" /><Skeleton className="h-8 w-full" /></div>;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {notFound && (
        <div className="bg-info-50 border border-info-100 text-info-700 text-sm px-3 py-2 rounded-md">
          Aún no completas tu perfil médico. Ingresa tu cédula para crearlo.
        </div>
      )}
      {notFound && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Cédula</label>
          <input
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            required
            minLength={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        </div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de sangre</label>
          <input
            value={bloodType}
            onChange={(e) => setBloodType(e.target.value)}
            placeholder="O+"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Alergias (separadas por coma)</label>
        <input
          value={allergies}
          onChange={(e) => setAllergies(e.target.value)}
          placeholder="Penicilina, Ibuprofeno"
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Condiciones crónicas (separadas por coma)</label>
        <input
          value={conditions}
          onChange={(e) => setConditions(e.target.value)}
          placeholder="Hipertensión, Diabetes tipo 2"
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
        />
      </div>

      <div className="pt-4 border-t border-gray-100 space-y-3">
        <p className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-teal-600" /> Consentimientos (LOPDP)
        </p>
        <label className="flex items-start gap-2 text-sm text-gray-700">
          <input type="checkbox" checked={consentData} onChange={(e) => setConsentData(e.target.checked)} className="mt-0.5" />
          Autorizo el tratamiento de mis datos personales de salud.
        </label>
        <label className="flex items-start gap-2 text-sm text-gray-700">
          <input type="checkbox" checked={consentAi} onChange={(e) => setConsentAi(e.target.checked)} className="mt-0.5" />
          Autorizo el uso de mis datos en las evaluaciones automatizadas del sistema.
        </label>
        <label className="flex items-start gap-2 text-sm text-gray-700">
          <input type="checkbox" checked={consentSharing} onChange={(e) => setConsentSharing(e.target.checked)} className="mt-0.5" />
          Autorizo compartir mi historial con centros médicos e interoperabilidad (MSP/IESS).
        </label>
      </div>

      <Button type="submit" disabled={isPending}>
        {isPending ? 'Guardando...' : notFound ? 'Crear Perfil' : 'Guardar Cambios'}
      </Button>
    </form>
  );
}

function PasswordSection() {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    setSuccess(false);
    if (next !== confirm) {
      setErrors(['Las contraseñas nuevas no coinciden.']);
      return;
    }
    setLoading(true);
    try {
      await changePassword(current, next);
      setSuccess(true);
      setCurrent('');
      setNext('');
      setConfirm('');
    } catch (err) {
      setErrors(extractErrors(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errors.length > 0 && (
        <div className="flex items-start gap-2 bg-error-50 text-error-700 text-sm px-3 py-2 rounded-md border border-error-200">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <ul>{errors.map((msg) => <li key={msg}>{msg}</li>)}</ul>
        </div>
      )}
      {success && (
        <div className="flex items-center gap-2 bg-success-50 text-success-700 text-sm px-3 py-2 rounded-md border border-success-200">
          <CheckCircle2 className="w-4 h-4" /> Contraseña actualizada.
        </div>
      )}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña actual</label>
        <input
          type="password"
          required
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña nueva</label>
        <input
          type="password"
          required
          minLength={8}
          value={next}
          onChange={(e) => setNext(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña nueva</label>
        <input
          type="password"
          required
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
        />
      </div>
      <Button type="submit" disabled={loading}>
        {loading ? 'Actualizando...' : 'Cambiar Contraseña'}
      </Button>
    </form>
  );
}

export function Perfil() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mi Cuenta</h1>
        <p className="text-gray-600 text-sm">Datos de tu cuenta y seguridad.</p>
      </div>

      <div className="bg-surface rounded-lg border border-gray-200 p-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center">
          <User className="w-5 h-5" />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-900">{user?.email}</p>
          <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
        </div>
      </div>

      {user?.role === 'patient' && (
        <div className="bg-surface rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Perfil Médico</h2>
          <ProfileSection />
        </div>
      )}

      <div className="bg-surface rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <KeyRound className="w-5 h-5 text-teal-600" /> Seguridad
        </h2>
        <PasswordSection />
      </div>
    </div>
  );
}
