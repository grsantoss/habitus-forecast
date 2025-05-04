import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const ScenarioList = () => {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const res = await axios.get('/api/scenarios');
        setScenarios(res.data);
      } catch (err) {
        console.error('Error fetching scenarios:', err);
        toast.error('Erro ao carregar cenários');
      } finally {
        setLoading(false);
      }
    };

    fetchScenarios();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir este cenário?')) {
      try {
        await axios.delete(`/api/scenarios/${id}`);
        setScenarios(scenarios.filter(scenario => scenario._id !== id));
        toast.success('Cenário excluído com sucesso!');
      } catch (err) {
        console.error('Error deleting scenario:', err);
        toast.error('Erro ao excluir cenário');
      }
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('pt-BR', options);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
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
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Cenários</h2>
          <p className="mt-1 text-sm text-gray-500">
            Gerencie seus cenários financeiros
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <Link
            to="/spreadsheets"
            className="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Criar Novo Cenário
          </Link>
        </div>
      </div>

      {scenarios.length === 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6 text-center">
          <p className="text-gray-500">Nenhum cenário encontrado</p>
          <p className="mt-2">
            <Link
              to="/spreadsheets"
              className="text-primary-600 hover:text-primary-500"
            >
              Selecione uma planilha para criar seu primeiro cenário
            </Link>
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <ul className="divide-y divide-gray-200">
            {scenarios.map((scenario) => (
              <li key={scenario._id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-medium text-gray-900 truncate">{scenario.name}</h3>
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <span className="truncate">Criado em {formatDate(scenario.createdAt)}</span>
                      <span className="mx-2">•</span>
                      <span>Modificado em {formatDate(scenario.modifiedAt)}</span>
                      <span className="mx-2">•</span>
                      <span className={`font-medium ${scenario.summary.annualNetIncome >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        Resultado Anual: {formatCurrency(scenario.summary.annualNetIncome)}
                      </span>
                    </div>
                    {scenario.description && (
                      <p className="mt-1 text-sm text-gray-500 truncate">{scenario.description}</p>
                    )}
                  </div>
                  <div className="flex-shrink-0 flex">
                    <Link
                      to={`/scenarios/${scenario._id}`}
                      className="mr-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      Visualizar
                    </Link>
                    <button
                      onClick={() => handleDelete(scenario._id)}
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

export default ScenarioList;