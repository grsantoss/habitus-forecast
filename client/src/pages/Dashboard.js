import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';

// Chart components
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    spreadsheetCount: 0,
    scenarioCount: 0,
    recentScenarios: [],
    summaryData: null
  });
  
  // Estado para o cenário selecionado (simulando o selector do mockup)
  const [selectedScenario, setSelectedScenario] = useState('latest');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch spreadsheet count
        const spreadsheetsRes = await axios.get('/api/spreadsheets');
        
        // Fetch scenarios
        const scenariosRes = await axios.get('/api/scenarios');
        
        // Process data for dashboard
        const spreadsheetCount = spreadsheetsRes.data.length;
        const scenarioCount = scenariosRes.data.length;
        const recentScenarios = scenariosRes.data
          .sort((a, b) => new Date(b.modifiedAt) - new Date(a.modifiedAt))
          .slice(0, 5);
        
        // Calculate summary data if scenarios exist
        let summaryData = null;
        if (scenariosRes.data.length > 0) {
          // Use the most recent scenario for summary
          const latestScenario = scenariosRes.data[0];
          summaryData = {
            annualRevenues: latestScenario.summary.annualRevenues,
            annualExpenses: latestScenario.summary.annualExpenses,
            annualInvestments: latestScenario.summary.annualInvestments,
            annualNetIncome: latestScenario.summary.annualNetIncome,
            monthlyData: {
              revenues: latestScenario.summary.monthlyRevenues,
              expenses: latestScenario.summary.monthlyExpenses,
              netIncome: latestScenario.summary.monthlyNetIncome
            }
          };
        }
        
        setStats({
          spreadsheetCount,
          scenarioCount,
          recentScenarios,
          summaryData
        });
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        toast.error('Erro ao carregar dados do dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('pt-BR', options);
  };

  // Pie chart data
  const pieData = stats.summaryData ? {
    labels: ['Receitas', 'Despesas', 'Investimentos'],
    datasets: [
      {
        data: [
          stats.summaryData.annualRevenues,
          stats.summaryData.annualExpenses,
          stats.summaryData.annualInvestments
        ],
        backgroundColor: [
          'rgba(47, 203, 110, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(59, 130, 246, 0.8)'
        ],
        borderColor: [
          'rgba(47, 203, 110, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(59, 130, 246, 1)'
        ],
        borderWidth: 1,
      },
    ],
  } : null;

  // Bar chart data
  const barData = stats.summaryData ? {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
    datasets: [
      {
        label: 'Receitas',
        data: stats.summaryData.monthlyData.revenues,
        backgroundColor: 'rgba(47, 203, 110, 0.6)',
      },
      {
        label: 'Despesas',
        data: stats.summaryData.monthlyData.expenses,
        backgroundColor: 'rgba(239, 68, 68, 0.6)',
      },
      {
        label: 'Resultado Líquido',
        data: stats.summaryData.monthlyData.netIncome,
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
      },
    ],
  } : null;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      {/* Scenario Selector */}
      {stats.summaryData && stats.recentScenarios.length > 0 && (
        <div className="card mb-6">
          <div className="p-4 flex flex-col md:flex-row justify-between items-center">
            <div>
              <h4 className="font-semibold mb-2">Cenário de Visualização</h4>
              <div className="flex flex-wrap">
                <span className="bg-primary-50 text-primary px-3 py-1 rounded-full text-sm font-medium mr-2 mb-2">
                  {stats.recentScenarios[0].name}
                </span>
              </div>
            </div>
            <div className="mt-3 md:mt-0">
              <Link to="/scenarios" className="btn-outline">
                <i className="bi bi-eye mr-1"></i> Ver Todos os Cenários
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-6">
        <div className="card">
          <div className="p-6 text-center">
            <div className="bg-primary-50 text-primary w-16 h-16 rounded-full flex items-center justify-center text-2xl mx-auto mb-4">
              <i className="bi bi-file-earmark-spreadsheet"></i>
            </div>
            <div className="text-3xl font-bold mb-1">{stats.spreadsheetCount}</div>
            <div className="text-gray-500 text-sm">Planilhas</div>
            <div className="mt-4">
              <Link to="/spreadsheets" className="text-primary hover:text-primary-600 text-sm font-medium">
                Ver todas <i className="bi bi-arrow-right"></i>
              </Link>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="p-6 text-center">
            <div className="bg-primary-50 text-primary w-16 h-16 rounded-full flex items-center justify-center text-2xl mx-auto mb-4">
              <i className="bi bi-graph-up-arrow"></i>
            </div>
            <div className="text-3xl font-bold mb-1">{stats.scenarioCount}</div>
            <div className="text-gray-500 text-sm">Cenários</div>
            <div className="mt-4">
              <Link to="/scenarios" className="text-primary hover:text-primary-600 text-sm font-medium">
                Ver todos <i className="bi bi-arrow-right"></i>
              </Link>
            </div>
          </div>
        </div>

        {stats.summaryData && (
          <div className="card">
            <div className="p-6 text-center">
              <div className="bg-primary-50 text-primary w-16 h-16 rounded-full flex items-center justify-center text-2xl mx-auto mb-4">
                <i className="bi bi-cash-coin"></i>
              </div>
              <div className={`text-3xl font-bold mb-1 ${stats.summaryData.annualNetIncome >= 0 ? 'text-primary' : 'text-red-600'}`}>
                {formatCurrency(stats.summaryData.annualNetIncome)}
              </div>
              <div className="text-gray-500 text-sm">Resultado Anual</div>
              <div className="mt-4 text-sm text-gray-500 flex justify-center space-x-2">
                <span>Receitas: {formatCurrency(stats.summaryData.annualRevenues)}</span>
                <span>|</span>
                <span>Despesas: {formatCurrency(stats.summaryData.annualExpenses)}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Charts Section */}
      {stats.summaryData && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-6">
          <div className="card">
            <div className="p-5 border-b border-gray-100">
              <h3 className="text-lg font-semibold">Distribuição Anual</h3>
            </div>
            <div className="p-5 h-80">
              <Pie data={pieData} options={{ maintainAspectRatio: false }} />
            </div>
          </div>

          <div className="card">
            <div className="p-5 border-b border-gray-100">
              <h3 className="text-lg font-semibold">Evolução Mensal</h3>
            </div>
            <div className="p-5 h-80">
              <Bar 
                data={barData} 
                options={{
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true
                    }
                  }
                }} 
              />
            </div>
          </div>
        </div>
      )}
      
      {/* Recent Scenarios */}
      <div className="card">
        <div className="p-5 border-b border-gray-100 flex justify-between items-center">
          <h3 className="text-lg font-semibold">Cenários Recentes</h3>
          <Link to="/scenarios" className="text-primary hover:text-primary-600 text-sm">Ver todos</Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data de Criação</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resultado Anual</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats.recentScenarios.length > 0 ? (
                stats.recentScenarios.map((scenario) => (
                  <tr key={scenario._id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{scenario.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(scenario.createdAt)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${scenario.summary.annualNetIncome >= 0 ? 'text-primary' : 'text-red-600'}`}>
                        {formatCurrency(scenario.summary.annualNetIncome)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/scenarios/${scenario._id}`}
                        className="text-primary hover:text-primary-600 font-medium mr-3"
                      >
                        <i className="bi bi-eye mr-1"></i> Ver
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="px-6 py-4 text-center text-sm text-gray-500">
                    Nenhum cenário encontrado. <Link to="/scenarios/create" className="text-primary hover:text-primary-600">Criar um novo cenário</Link>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
          <Link
            to="/spreadsheets/upload"
            className="btn-primary inline-flex items-center"
          >
            <i className="bi bi-plus-circle mr-2"></i> Importar Novos Dados
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;