import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Bar, Pie } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalScenarios: 0,
    totalSpreadsheets: 0,
    usersThisMonth: 0,
    scenariosThisMonth: 0
  });
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch admin dashboard data
        const statsRes = await axios.get('/api/users/admin/stats');
        setStats(statsRes.data);
        
        // Fetch recent activity logs
        const logsRes = await axios.get('/api/users/admin/logs');
        setLogs(logsRes.data);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching admin data:', error);
        toast.error('Falha ao carregar dados administrativos');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const userActivityData = {
    labels: ['Usuários', 'Planilhas', 'Cenários'],
    datasets: [
      {
        label: 'Total',
        data: [stats.totalUsers, stats.totalSpreadsheets, stats.totalScenarios],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 159, 64, 0.6)'
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1,
      },
    ],
  };

  const monthlyActivityData = {
    labels: ['Usuários', 'Cenários'],
    datasets: [
      {
        label: 'Este Mês',
        data: [stats.usersThisMonth, stats.scenariosThisMonth],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 159, 64, 0.6)',
        ],
      },
    ],
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard Administrativo</h1>
      
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-600 mb-2">Total de Usuários</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.totalUsers}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-600 mb-2">Total de Planilhas</h3>
          <p className="text-3xl font-bold text-teal-600">{stats.totalSpreadsheets}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-600 mb-2">Total de Cenários</h3>
          <p className="text-3xl font-bold text-orange-600">{stats.totalScenarios}</p>
        </div>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Visão Geral</h2>
          <div className="h-64">
            <Bar 
              data={userActivityData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Distribuição Total'
                  }
                }
              }}
            />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Atividade Mensal</h2>
          <div className="h-64">
            <Pie 
              data={monthlyActivityData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Atividade Este Mês'
                  }
                }
              }}
            />
          </div>
        </div>
      </div>
      
      {/* Activity Logs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Log de Atividades Recentes</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr>
                <th className="py-3 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuário
                </th>
                <th className="py-3 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ação
                </th>
                <th className="py-3 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recurso
                </th>
                <th className="py-3 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data/Hora
                </th>
              </tr>
            </thead>
            <tbody>
              {logs.length > 0 ? (
                logs.map((log, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="py-4 px-4 border-b border-gray-200 text-sm">
                      {log.user?.email || 'Usuário Anônimo'}
                    </td>
                    <td className="py-4 px-4 border-b border-gray-200 text-sm">
                      {log.action}
                    </td>
                    <td className="py-4 px-4 border-b border-gray-200 text-sm">
                      {log.resource}
                    </td>
                    <td className="py-4 px-4 border-b border-gray-200 text-sm">
                      {new Date(log.timestamp).toLocaleString('pt-BR')}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="py-4 px-4 border-b border-gray-200 text-sm text-center text-gray-500">
                    Nenhuma atividade registrada recentemente.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard; 