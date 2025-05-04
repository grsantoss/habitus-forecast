import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const SpreadsheetList = () => {
  const [spreadsheets, setSpreadsheets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSpreadsheets = async () => {
      try {
        const res = await axios.get('/api/spreadsheets');
        setSpreadsheets(res.data);
      } catch (err) {
        console.error('Error fetching spreadsheets:', err);
        toast.error('Erro ao carregar planilhas');
      } finally {
        setLoading(false);
      }
    };

    fetchSpreadsheets();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir esta planilha?')) {
      try {
        await axios.delete(`/api/spreadsheets/${id}`);
        setSpreadsheets(spreadsheets.filter(sheet => sheet._id !== id));
        toast.success('Planilha excluída com sucesso!');
      } catch (err) {
        console.error('Error deleting spreadsheet:', err);
        toast.error('Erro ao excluir planilha');
      }
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('pt-BR', options);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="md:flex md:items-center md:justify-between mb-6">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Planilhas</h2>
          <p className="mt-1 text-sm text-gray-500">
            Gerencie suas planilhas financeiras e crie cenários
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <Link
            to="/spreadsheets/upload"
            className="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Nova Planilha
          </Link>
        </div>
      </div>

      {spreadsheets.length === 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6 text-center">
          <p className="text-gray-500">Nenhuma planilha encontrada</p>
          <p className="mt-2">
            <Link
              to="/spreadsheets/upload"
              className="text-primary-600 hover:text-primary-500"
            >
              Faça upload da sua primeira planilha
            </Link>
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <ul className="divide-y divide-gray-200">
            {spreadsheets.map((spreadsheet) => (
              <li key={spreadsheet._id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-medium text-gray-900 truncate">{spreadsheet.name}</h3>
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <span className="truncate">Enviado em {formatDate(spreadsheet.uploadDate)}</span>
                      <span className="mx-2">•</span>
                      <span>{formatFileSize(spreadsheet.fileSize)}</span>
                      <span className="mx-2">•</span>
                      <span>Status: {spreadsheet.status === 'processed' ? 'Processado' : spreadsheet.status === 'error' ? 'Erro' : 'Processando'}</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0 flex">
                    {spreadsheet.status === 'processed' && (
                      <Link
                        to={`/scenarios/create/${spreadsheet._id}`}
                        className="mr-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                      >
                        Criar Cenário
                      </Link>
                    )}
                    <button
                      onClick={() => handleDelete(spreadsheet._id)}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SpreadsheetList;