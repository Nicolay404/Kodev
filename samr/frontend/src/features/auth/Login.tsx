import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/ui/Button';

export function Login() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleMockLogin = () => {
    setLoading(true);
    // Simulate API call to BFF
    setTimeout(() => {
      setAuth('mock-jwt-token-12345', {
        id: '1',
        name: 'Dr. Usuario Médico',
        role: 'medical_staff'
      });
      setLoading(false);
      navigate('/');
    }, 1000);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-sm bg-surface p-8 rounded-lg shadow-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-teal-600">SAMR</h1>
          <p className="text-sm text-gray-500 mt-2">Inicia sesión en tu cuenta</p>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
            <input 
              type="text" 
              disabled 
              value="demo_medico"
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 text-sm" 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input 
              type="password" 
              disabled 
              value="********"
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 text-sm" 
            />
          </div>
          
          <Button 
            className="w-full mt-6" 
            onClick={handleMockLogin}
            disabled={loading}
          >
            {loading ? 'Iniciando sesión...' : 'Ingresar (Demo)'}
          </Button>
        </div>
      </div>
    </div>
  );
}
