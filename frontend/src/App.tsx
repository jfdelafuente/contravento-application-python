import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/routing/ProtectedRoute';
import { RegisterPage } from './pages/RegisterPage';

// Placeholder components (will be implemented in Phase 4+)
const HomePage: React.FC = () => (
  <div className="app">
    <h1>ContraVento</h1>
    <p>Plataforma social para ciclistas</p>
    <p>
      <a href="/login">Iniciar sesión</a> | <a href="/register">Registrarse</a>
    </p>
  </div>
);

const LoginPage: React.FC = () => (
  <div className="app">
    <h2>Iniciar Sesión</h2>
    <p>Formulario de login (Fase 4)</p>
  </div>
);

const VerifyEmailPage: React.FC = () => (
  <div className="app">
    <h2>Verificar Email</h2>
    <p>Página de verificación de email (Fase 6)</p>
  </div>
);

const ForgotPasswordPage: React.FC = () => (
  <div className="app">
    <h2>Recuperar Contraseña</h2>
    <p>Formulario de recuperación de contraseña (Fase 5)</p>
  </div>
);

const ResetPasswordPage: React.FC = () => (
  <div className="app">
    <h2>Restablecer Contraseña</h2>
    <p>Formulario de restablecimiento de contraseña (Fase 5)</p>
  </div>
);

const DashboardPage: React.FC = () => (
  <div className="app">
    <h2>Dashboard</h2>
    <p>Dashboard protegido (Fase 4)</p>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
