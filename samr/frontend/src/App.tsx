import { Toaster } from 'react-hot-toast';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components/layout/ErrorBoundary';
import { MainLayout } from './components/layout/MainLayout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { Login } from './features/auth/Login';
import { Dashboard } from './features/dashboard/Dashboard';
import { PatientList } from './features/patient/PatientList';
import { TeleconsultRoom } from './features/teleconsult/TeleconsultRoom';
import { MonitoringView } from './features/monitoring/MonitoringView';

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
            <Route path="patients" element={<PatientList />} />
            <Route path="teleconsult" element={<TeleconsultRoom />} />
            <Route path="monitoring" element={<MonitoringView />} />
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
