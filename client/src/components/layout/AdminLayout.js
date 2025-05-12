import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname.startsWith(path) ? 'active' : '';
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };
  
  // Determinar o título da página com base na rota atual
  const getPageTitle = () => {
    if (location.pathname === '/admin') return 'Dashboard Administrativo';
    if (location.pathname.startsWith('/admin/usuarios')) return 'Gestão de Usuários';
    if (location.pathname.startsWith('/admin/configuracoes')) return 'Configurações do Sistema';
    if (location.pathname.startsWith('/admin/metricas')) return 'Métricas e Estatísticas';
    if (location.pathname.startsWith('/admin/logs')) return 'Logs do Sistema';
    return 'Administração - Habitus Forecast';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarCollapsed ? 'hidden' : ''} bg-red-800`}>
        <div className="p-5 border-b border-red-900">
          <h4 className="text-white text-lg font-semibold">Admin - Habitus Forecast</h4>
        </div>
        <div className="mt-4">
          <Link to="/admin" className={`sidebar-link ${isActive('/admin')} ${location.pathname === '/admin' ? 'bg-red-700' : ''}`}>
            <i className="bi bi-speedometer2 mr-3"></i> Dashboard
          </Link>
          <Link to="/admin/usuarios" className={`sidebar-link ${isActive('/admin/usuarios')}`}>
            <i className="bi bi-people mr-3"></i> Usuários
          </Link>
          <Link to="/admin/configuracoes/email" className={`sidebar-link ${isActive('/admin/configuracoes')}`}>
            <i className="bi bi-sliders mr-3"></i> Configurações
          </Link>
          <Link to="/admin/metricas" className={`sidebar-link ${isActive('/admin/metricas')}`}>
            <i className="bi bi-bar-chart mr-3"></i> Métricas
          </Link>
          <Link to="/admin/logs" className={`sidebar-link ${isActive('/admin/logs')}`}>
            <i className="bi bi-journal-text mr-3"></i> Logs
          </Link>
          <Link to="/dashboard" className={`sidebar-link`}>
            <i className="bi bi-arrow-left-circle mr-3"></i> Área do Usuário
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col ${sidebarCollapsed ? '' : 'main-content'}`}>
        <header className="bg-white shadow-sm border-b p-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <button 
                className="p-1 mr-3 text-red-600 text-2xl" 
                onClick={toggleSidebar}
              >
                <i className="bi bi-list"></i>
              </button>
              <h2 className="text-lg font-semibold">{getPageTitle()}</h2>
            </div>
            <div className="flex items-center">
              <span className="mr-4 text-gray-600">{user?.name} (Admin)</span>
              <button
                onClick={handleLogout}
                className="btn-outline flex items-center text-sm"
              >
                <i className="bi bi-box-arrow-right mr-1"></i> Sair
              </button>
            </div>
          </div>
        </header>
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;