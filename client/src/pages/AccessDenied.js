import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AccessDenied = () => {
  const { isAdmin } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white rounded-card shadow-card p-8">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-red-100 flex items-center justify-center">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-10 w-10 text-red-600" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
                />
              </svg>
            </div>
          </div>
          
          <h2 className="mt-6 text-2xl font-bold text-gray-900">Acesso Negado</h2>
          
          <p className="mt-3 text-gray-600">
            Você não tem permissão para acessar esta área do sistema.
          </p>
          
          <div className="mt-8">
            <Link 
              to={isAdmin() ? "/admin" : "/dashboard"} 
              className="btn-primary block w-full"
            >
              Voltar para {isAdmin() ? "Painel Admin" : "Dashboard"}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccessDenied; 