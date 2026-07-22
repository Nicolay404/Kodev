import { Toaster } from 'react-hot-toast';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components/layout/ErrorBoundary';
import { MainLayout } from './components/layout/MainLayout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { Login } from './features/auth/Login';
import { Register } from './features/auth/Register';
import { ForgotPassword } from './features/auth/ForgotPassword';
import { Dashboard } from './features/dashboard/Dashboard';
import { AlertsList } from './features/monitoring/AlertsList';
import { TeleconsultRoom } from './features/teleconsult/TeleconsultRoom';
import { MonitoringView } from './features/monitoring/MonitoringView';
import { EmergenciesList } from './features/emergency/EmergenciesList';
import { NotificationsList } from './features/notifications/NotificationsList';
import { AdminPanel } from './features/admin/AdminPanel';
import { AuditLogList } from './features/audit/AuditLogList';
import { Chatbot } from './features/chat/Chatbot';
import { HistorialClinico } from './features/historial/HistorialClinico';
import { CierreCasoList } from './features/cierre/CierreCasoList';
import { Perfil } from './features/profile/Perfil';

// system_admin queda deliberadamente fuera de todos los grupos clínicos: su ámbito es
// solo Administración (centros/dispositivos/FAQ), Notificaciones y Mi Cuenta.
const EMERGENCY_ROLES = ['patient', 'professional', 'nurse', 'center_admin'] as const;
const HISTORIAL_ROLES = ['patient', 'professional', 'nurse'] as const;
const HISTORIAL_DETAIL_ROLES = ['professional', 'nurse'] as const;
const CIERRE_CASO_ROLES = ['patient', 'professional', 'center_admin'] as const;
const MONITORING_ROLES = ['professional', 'nurse', 'center_admin'] as const;
const TELECONSULT_ROLES = ['professional', 'center_admin'] as const;

function Unauthorized() {
  return (
    <div className="p-8 text-center flex flex-col items-center justify-center h-full">
      <h1 className="text-2xl font-bold text-error-600 mb-2">Acceso Denegado</h1>
      <p className="text-gray-600">No tienes permisos para ver esta página.</p>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary moduleName="RootApp">
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="profile" element={<Perfil />} />
            <Route path="notifications" element={<NotificationsList />} />
            <Route
              path="help"
              element={
                <ProtectedRoute allowedRoles={['patient']}>
                  <Chatbot />
                </ProtectedRoute>
              }
            />
            <Route
              path="emergencies"
              element={
                <ProtectedRoute allowedRoles={[...EMERGENCY_ROLES]}>
                  <EmergenciesList />
                </ProtectedRoute>
              }
            />
            <Route
              path="historial"
              element={
                <ProtectedRoute allowedRoles={[...HISTORIAL_ROLES]}>
                  <HistorialClinico />
                </ProtectedRoute>
              }
            />
            <Route
              path="historial/:patientId"
              element={
                <ProtectedRoute allowedRoles={[...HISTORIAL_DETAIL_ROLES]}>
                  <HistorialClinico />
                </ProtectedRoute>
              }
            />
            <Route
              path="cierre-casos"
              element={
                <ProtectedRoute allowedRoles={[...CIERRE_CASO_ROLES]}>
                  <CierreCasoList />
                </ProtectedRoute>
              }
            />
            <Route
              path="monitoring"
              element={
                <ProtectedRoute allowedRoles={[...MONITORING_ROLES]}>
                  <AlertsList />
                </ProtectedRoute>
              }
            />
            <Route
              path="monitoring/:patientId"
              element={
                <ProtectedRoute allowedRoles={[...MONITORING_ROLES]}>
                  <MonitoringView />
                </ProtectedRoute>
              }
            />
            <Route
              path="teleconsult"
              element={
                <ProtectedRoute allowedRoles={[...TELECONSULT_ROLES]}>
                  <TeleconsultRoom />
                </ProtectedRoute>
              }
            />
            <Route
              path="admin"
              element={
                <ProtectedRoute allowedRoles={['system_admin']}>
                  <AdminPanel />
                </ProtectedRoute>
              }
            />
            <Route
              path="audit"
              element={
                <ProtectedRoute allowedRoles={['dpd_delegate']}>
                  <AuditLogList />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          className: 'text-sm font-medium',
        }}
      />
    </ErrorBoundary>
  );
}

export default App;
