import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Layout Components
import Layout from './components/layout/Layout';
import AdminLayout from './components/layout/AdminLayout';

// Public Pages
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

// Protected Pages - Usuário Regular
import Dashboard from './pages/Dashboard';
import SpreadsheetUpload from './pages/SpreadsheetUpload';
import SpreadsheetList from './pages/SpreadsheetList';
import ScenarioCreate from './pages/ScenarioCreate';
import ScenarioDetail from './pages/ScenarioDetail';
import ScenarioList from './pages/ScenarioList';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import UserManagement from './pages/admin/UserManagement';
import SmtpConfig from './pages/admin/SmtpConfig';

// Página de acesso negado
import AccessDenied from './pages/AccessDenied';

// Route Guards
const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <div className="flex items-center justify-center h-screen">Carregando...</div>;
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AdminRoute = ({ children }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  
  if (loading) return <div className="flex items-center justify-center h-screen">Carregando...</div>;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!isAdmin()) {
    return <Navigate to="/acesso-negado" />;
  }
  
  return children;
};

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password/:token" element={<ResetPassword />} />
      <Route path="/acesso-negado" element={<AccessDenied />} />
      
      {/* Protected User Routes */}
      <Route path="/" element={
        <PrivateRoute>
          <Layout />
        </PrivateRoute>
      }>
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="dados-financeiros">
          <Route index element={<SpreadsheetList />} />
          <Route path="upload" element={<SpreadsheetUpload />} />
        </Route>
        <Route path="cenarios">
          <Route index element={<ScenarioList />} />
          <Route path="criar/:spreadsheetId" element={<ScenarioCreate />} />
          <Route path=":id" element={<ScenarioDetail />} />
        </Route>
      </Route>
      
      {/* Admin Routes */}
      <Route path="/admin" element={
        <AdminRoute>
          <AdminLayout />
        </AdminRoute>
      }>
        <Route index element={<AdminDashboard />} />
        <Route path="usuarios" element={<UserManagement />} />
        <Route path="configuracoes">
          <Route path="email" element={<SmtpConfig />} />
        </Route>
        <Route path="metricas" element={<AdminDashboard />} />
        <Route path="logs" element={<AdminDashboard />} />
      </Route>
      
      {/* Fallback Route */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;