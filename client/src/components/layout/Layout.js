import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Layout = () => {
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
          <Link to="/spreadsheets" className={`sidebar-link ${isActive('/spreadsheets')}`}>
            <i className="bi bi-file-earmark-spreadsheet mr-3"></i> Dados Financeiros
          </Link>
          <Link to="/scenarios" className={`sidebar-link ${isActive('/scenarios')}`}>
            <i className="bi bi-graph-up-arrow mr-3"></i> Cenários
          </Link>
          <Link to="#" className={`sidebar-link`}>
            <i className="bi bi-file-earmark-pdf mr-3"></i> Relatórios
          </Link>
          {user?.role === 'admin' && (
            <Link to="/admin" className={`sidebar-link ${isActive('/admin')}`}>
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
              <h2 className="text-lg font-semibold">{location.pathname === '/dashboard' ? 'Dashboard' : 
                location.pathname.includes('/spreadsheets') ? 'Dados Financeiros' : 
                location.pathname.includes('/scenarios') ? 'Cenários' : 'Habitus Forecast'}</h2>
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