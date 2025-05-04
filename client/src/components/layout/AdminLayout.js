import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path ? 'bg-red-700 text-white' : 'text-gray-300 hover:bg-red-600 hover:text-white';
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-red-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-white font-bold text-xl">Habitus Forecast - Admin</h1>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <Link
                    to="/admin"
                    className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/admin')}`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/admin/users"
                    className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/admin/users')}`}
                  >
                    Usuários
                  </Link>
                  <Link
                    to="/admin/smtp-config"
                    className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/admin/smtp-config')}`}
                  >
                    Configuração SMTP
                  </Link>
                </div>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="ml-4 flex items-center md:ml-6">
                <div className="relative ml-3">
                  <div className="flex items-center">
                    <span className="text-white mr-4">{user?.name} (Admin)</span>
                    <Link
                      to="/dashboard"
                      className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 mr-2"
                    >
                      Área do Usuário
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500"
                    >
                      Sair
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-300 hover:bg-red-700 hover:text-white focus:outline-none"
              >
                <span className="sr-only">Abrir menu</span>
                <svg
                  className="h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              <Link
                to="/admin"
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive('/admin') ? 'bg-red-700 text-white' : 'text-gray-300 hover:bg-red-700 hover:text-white'
                }`}
                onClick={() => setMobileMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link
                to="/admin/users"
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive('/admin/users') ? 'bg-red-700 text-white' : 'text-gray-300 hover:bg-red-700 hover:text-white'
                }`}
                onClick={() => setMobileMenuOpen(false)}
              >
                Usuários
              </Link>
              <Link
                to="/admin/smtp-config"
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive('/admin/smtp-config') ? 'bg-red-700 text-white' : 'text-gray-300 hover:bg-red-700 hover:text-white'
                }`}
                onClick={() => setMobileMenuOpen(false)}
              >
                Configuração SMTP
              </Link>
              <div className="pt-4 border-t border-red-700">
                <Link
                  to="/dashboard"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:bg-red-700 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Área do Usuário
                </Link>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:bg-red-700 hover:text-white"
                >
                  Sair
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main>
        <div className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;