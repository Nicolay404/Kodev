import { Toaster } from 'react-hot-toast';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components/layout/ErrorBoundary';
import { MainLayout } from './components/layout/MainLayout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { Login } from './features/auth/Login';
import { Dashboard } from './features/dashboard/Dashboard';
import { AlertsList } from './features/monitoring/AlertsList';
import { TeleconsultRoom } from './features/teleconsult/TeleconsultRoom';
import { MonitoringView } from './features/monitoring/MonitoringView';
import { EmergenciesList } from './features/emergency/EmergenciesList';
import { NotificationsList } from './features/notifications/NotificationsList';
import { AdminPanel } from './features/admin/AdminPanel';
import { AuditLogList } from './features/audit/AuditLogList';

const CLINICAL_ROLES = ['professional', 'nurse', 'center_admin', 'system_admin'] as const;
const TELECONSULT_ROLES = ['professional', 'center_admin', 'system_admin'] as const;
const EMERGENCY_ROLES = ['patient', 'professional', 'nurse', 'center_admin', 'system_admin'] as const;

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
            <Route path="notifications" element={<NotificationsList />} />
            <Route
              path="emergencies"
              element={
                <ProtectedRoute allowedRoles={[...EMERGENCY_ROLES]}>
                  <EmergenciesList />
                </ProtectedRoute>
              }
            />
            <Route
              path="monitoring"
              element={
                <ProtectedRoute allowedRoles={[...CLINICAL_ROLES]}>
                  <AlertsList />
                </ProtectedRoute>
              }
            />
            <Route
              path="monitoring/:patientId"
              element={
                <ProtectedRoute allowedRoles={[...CLINICAL_ROLES]}>
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
