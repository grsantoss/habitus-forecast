import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Layout = () => {
  const { user, logout, isAdmin } = useAuth();
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
    if (location.pathname === '/dashboard') return 'Dashboard';
    if (location.pathname.startsWith('/dados-financeiros')) return 'Dados Financeiros';
    if (location.pathname.startsWith('/cenarios')) return 'Cenários Financeiros';
    return 'Habitus Forecast';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarCollapsed ? 'hidden' : ''}`}>
        <div className="p-5 border-b border-gray-800">
          <h4 className="text-white text-lg font-semibold">Habitus Forecast</h4>
        </div>
        <div className="mt-4">
          <Link to="/dashboard" className={`sidebar-link ${isActive('/dashboard')}`}>
            <i className="bi bi-speedometer2 mr-3"></i> Dashboard
          </Link>
          <Link to="/dados-financeiros" className={`sidebar-link ${isActive('/dados-financeiros')}`}>
            <i className="bi bi-file-earmark-spreadsheet mr-3"></i> Dados Financeiros
          </Link>
          <Link to="/cenarios" className={`sidebar-link ${isActive('/cenarios')}`}>
            <i className="bi bi-graph-up-arrow mr-3"></i> Cenários
          </Link>
          <Link to="#" className={`sidebar-link`}>
            <i className="bi bi-file-earmark-pdf mr-3"></i> Relatórios
          </Link>
          {isAdmin() && (
            <Link to="/admin" className={`sidebar-link`}>
              <i className="bi bi-gear mr-3"></i> Administração
            </Link>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col ${sidebarCollapsed ? '' : 'main-content'}`}>
        <header className="bg-white shadow-sm border-b p-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <button 
                className="p-1 mr-3 text-primary text-2xl" 
                onClick={toggleSidebar}
              >
                <i className="bi bi-list"></i>
              </button>
              <h2 className="text-lg font-semibold">{getPageTitle()}</h2>
            </div>
            <div className="flex items-center">
              <span className="mr-4 text-gray-600">Olá, {user?.name}</span>
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

export default Layout;