import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

// Chart components
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ScenarioDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  useEffect(() => {
    const fetchScenario = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`/api/scenarios/${id}`);
        setScenario(res.data);
      } catch (err) {
        console.error('Error fetching scenario:', err);
        toast.error('Erro ao carregar cenário');
        navigate('/scenarios');
      } finally {
        setLoading(false);
      }
    };

    fetchScenario();
  }, [id, navigate]);
  
  const handleDelete = async () => {
    if (window.confirm('Tem certeza que deseja excluir este cenário?')) {
      try {
        await axios.delete(`/api/scenarios/${id}`);
        toast.success('Cenário excluído com sucesso!');
        navigate('/scenarios');
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

  // Pie chart data
  const pieData = scenario ? {
    labels: ['Receitas', 'Despesas', 'Investimentos'],
    datasets: [
      {
        data: [
          scenario.summary.annualRevenues,
          scenario.summary.annualExpenses,
          scenario.summary.annualInvestments
        ],
        backgroundColor: [
          'rgba(52, 211, 153, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(59, 130, 246, 0.8)'
        ],
        borderColor: [
          'rgba(52, 211, 153, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(59, 130, 246, 1)'
        ],
        borderWidth: 1,
      },
    ],
  } : null;

  // Bar chart data
  const barData = scenario ? {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
    datasets: [
      {
        label: 'Receitas',
        data: scenario.summary.monthlyRevenues,
        backgroundColor: 'rgba(52, 211, 153, 0.5)',
      },
      {
        label: 'Despesas',
        data: scenario.summary.monthlyExpenses,
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
      },
      {
        label: 'Resultado Líquido',
        data: scenario.summary.monthlyNetIncome,
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
      },
    ],
  } : null;

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
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">{scenario.name}</h2>
          <p className="mt-1 text-sm text-gray-500">
            Criado em {formatDate(scenario.createdAt)} • Modificado em {formatDate(scenario.modifiedAt)}
          </p>
          {scenario.description && (
            <p className="mt-2 text-sm text-gray-700">{scenario.description}</p>
          )}
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <button
            onClick={handleDelete}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Excluir Cenário
          </button>
          <Link
            to="/scenarios"
            className="ml-3 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Voltar
          </Link>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Receitas Anuais</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {formatCurrency(scenario.summary.annualRevenues)}
            </dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Despesas Anuais</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {formatCurrency(scenario.summary.annualExpenses)}
            </dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Investimentos Anuais</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {formatCurrency(scenario.summary.annualInvestments)}
            </dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Resultado Anual</dt>
            <dd className={`mt-1 text-3xl font-semibold ${scenario.summary.annualNetIncome >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(scenario.summary.annualNetIncome)}
            </dd>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('overview')}
            className={`${activeTab === 'overview' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Visão Geral
          </button>
          <button
            onClick={() => setActiveTab('revenues')}
            className={`${activeTab === 'revenues' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Receitas
          </button>
          <button
            onClick={() => setActiveTab('expenses')}
            className={`${activeTab === 'expenses' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Despesas
          </button>
          <button
            onClick={() => setActiveTab('investments')}
            className={`${activeTab === 'investments' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Investimentos
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
        {activeTab === 'overview' && (
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Distribuição Anual</h3>
                <div className="h-64">
                  {pieData && <Pie data={pieData} options={{ maintainAspectRatio: false }} />}
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Evolução Mensal</h3>
                <div className="h-64">
                  {barData && <Bar data={barData} options={{ maintainAspectRatio: false }} />}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'revenues' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Receitas</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                    {Array.from({ length: 12 }, (_, i) => (
                      <th key={i} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][i]}
                      </th>
                    ))}
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {scenario.data.revenues.map((item, index) => (
                    <tr key={index} className={item.isModified ? 'bg-yellow-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.name}</td>
                      {item.values.map((value, i) => (
                        <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatCurrency(value)}
                        </td>
                      ))}
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(item.total)}
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total</td>
                    {scenario.summary.monthlyRevenues.map((value, i) => (
                      <td key={i} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(value)}
                      </td>
                    ))}
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(scenario.summary.annualRevenues)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'expenses' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Despesas</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                    {Array.from({ length: 12 }, (_, i) => (
                      <th key={i} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][i]}
                      </th>
                    ))}
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {scenario.data.expenses.map((item, index) => (
                    <tr key={index} className={item.isModified ? 'bg-yellow-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.name}</td>
                      {item.values.map((value, i) => (
                        <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatCurrency(value)}
                        </td>
                      ))}
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(item.total)}
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total</td>
                    {scenario.summary.monthlyExpenses.map((value, i) => (
                      <td key={i} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(value)}
                      </td>
                    ))}
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(scenario.summary.annualExpenses)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'investments' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Investimentos</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                    {Array.from({ length: 12 }, (_, i) => (
                      <th key={i} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][i]}
                      </th>
                    ))}
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {scenario.data.investments.map((item, index) => (
                    <tr key={index} className={item.isModified ? 'bg-yellow-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.name}</td>
                      {item.values.map((value, i) => (
                        <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatCurrency(value)}
                        </td>
                      ))}
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(item.total)}
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total</td>
                    {scenario.summary.monthlyInvestments.map((value, i) => (
                      <td key={i} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(value)}
                      </td>
                    ))}
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(scenario.summary.annualInvestments)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScenarioDetail;