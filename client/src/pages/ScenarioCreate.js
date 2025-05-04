import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

// Chart components
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ScenarioCreate = () => {
  const { spreadsheetId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [spreadsheet, setSpreadsheet] = useState(null);
  const [scenarioData, setScenarioData] = useState({
    name: '',
    description: '',
    data: {
      revenues: [],
      variableExpenses: [],
      fixedExpenses: [],
      investments: []
    },
    summary: {
      monthlyNetIncome: Array(12).fill(0),
      annualNetIncome: 0,
      monthlyRevenues: Array(12).fill(0),
      annualRevenues: 0,
      monthlyExpenses: Array(12).fill(0),
      annualExpenses: 0,
      monthlyInvestments: Array(12).fill(0),
      annualInvestments: 0
    }
  });
  
  const [activeTab, setActiveTab] = useState('revenues');
  const [editingItem, setEditingItem] = useState(null);
  
  useEffect(() => {
    const fetchSpreadsheet = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`/api/spreadsheets/${spreadsheetId}`);
        setSpreadsheet(res.data);
        
        // Initialize scenario data from spreadsheet
        const initialData = {
          revenues: res.data.categories.revenues.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          })),
          variableExpenses: res.data.categories.variableExpenses.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          })),
          fixedExpenses: res.data.categories.fixedExpenses.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          })),
          investments: res.data.categories.investments.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          }))
        };
        
        setScenarioData(prev => ({
          ...prev,
          name: `Cenário baseado em ${res.data.name}`,
          data: initialData
        }));
        
        // Calculate initial summary
        calculateSummary(initialData);
      } catch (err) {
        console.error('Error fetching spreadsheet:', err);
        toast.error('Erro ao carregar planilha');
        navigate('/spreadsheets');
      } finally {
        setLoading(false);
      }
    };

    fetchSpreadsheet();
  }, [spreadsheetId, navigate]);
  
  const calculateSummary = (data) => {
    const summary = {
      monthlyNetIncome: Array(12).fill(0),
      annualNetIncome: 0,
      monthlyRevenues: Array(12).fill(0),
      annualRevenues: 0,
      monthlyExpenses: Array(12).fill(0),
      annualExpenses: 0,
      monthlyInvestments: Array(12).fill(0),
      annualInvestments: 0
    };

    // Calculate monthly and annual revenues
    data.revenues.forEach(item => {
      const total = item.values.reduce((acc, val) => acc + val, 0);
      item.total = total;
      item.values.forEach((value, index) => {
        summary.monthlyRevenues[index] += value;
      });
      summary.annualRevenues += total;
    });

    // Calculate monthly and annual expenses (variable + fixed)
    const calculateExpenses = (expenseType) => {
      data[expenseType].forEach(item => {
        const total = item.values.reduce((acc, val) => acc + val, 0);
        item.total = total;
        item.values.forEach((value, index) => {
          summary.monthlyExpenses[index] += value;
        });
        summary.annualExpenses += total;
      });
    };

    calculateExpenses('variableExpenses');
    calculateExpenses('fixedExpenses');

    // Calculate monthly and annual investments
    data.investments.forEach(item => {
      const total = item.values.reduce((acc, val) => acc + val, 0);
      item.total = total;
      item.values.forEach((value, index) => {
        summary.monthlyInvestments[index] += value;
      });
      summary.annualInvestments += total;
    });

    // Calculate monthly and annual net income
    for (let i = 0; i < 12; i++) {
      summary.monthlyNetIncome[i] = summary.monthlyRevenues[i] - summary.monthlyExpenses[i] - summary.monthlyInvestments[i];
    }
    summary.annualNetIncome = summary.annualRevenues - summary.annualExpenses - summary.annualInvestments;

    setScenarioData(prev => ({
      ...prev,
      summary
    }));
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setScenarioData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleItemEdit = (category, index) => {
    setEditingItem({
      category,
      index,
      item: { ...scenarioData.data[category][index] }
    });
  };
  
  const handleEditCancel = () => {
    setEditingItem(null);
  };
  
  const handleEditSave = () => {
    if (!editingItem) return;
    
    const { category, index, item } = editingItem;
    const newData = { ...scenarioData.data };
    
    // Mark as modified if values changed
    const isModified = JSON.stringify(item.values) !== JSON.stringify(newData[category][index].originalValues);
    
    newData[category][index] = {
      ...item,
      isModified
    };
    
    const updatedData = {
      ...scenarioData.data,
      [category]: newData[category]
    };
    
    setScenarioData(prev => ({
      ...prev,
      data: updatedData
    }));
    
    calculateSummary(updatedData);
    setEditingItem(null);
  };
  
  const handleValueChange = (monthIndex, value) => {
    if (!editingItem) return;
    
    const newValues = [...editingItem.item.values];
    newValues[monthIndex] = parseFloat(value) || 0;
    
    setEditingItem({
      ...editingItem,
      item: {
        ...editingItem.item,
        values: newValues
      }
    });
  };
  
  const handleResetItem = () => {
    if (!editingItem) return;
    
    setEditingItem({
      ...editingItem,
      item: {
        ...editingItem.item,
        values: [...editingItem.item.originalValues]
      }
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!scenarioData.name.trim()) {
      toast.error('Por favor, forneça um nome para o cenário');
      return;
    }
    
    try {
      setLoading(true);
      
      const payload = {
        name: scenarioData.name,
        description: scenarioData.description,
        spreadsheet: spreadsheetId,
        data: scenarioData.data
      };
      
      const res = await axios.post('/api/scenarios', payload);
      
      toast.success('Cenário criado com sucesso!');
      navigate(`/scenarios/${res.data._id}`);
    } catch (err) {
      console.error('Error creating scenario:', err);
      toast.error('Erro ao criar cenário');
    } finally {
      setLoading(false);
    }
  };
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };
  
  // Pie chart data
  const pieData = {
    labels: ['Receitas', 'Despesas', 'Investimentos'],
    datasets: [
      {
        data: [
          scenarioData.summary.annualRevenues,
          scenarioData.summary.annualExpenses,
          scenarioData.summary.annualInvestments
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
  };

  // Bar chart data
  const barData = {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
    datasets: [
      {
        label: 'Receitas',
        data: scenarioData.summary.monthlyRevenues,
        backgroundColor: 'rgba(52, 211, 153, 0.5)',
      },
      {
        label: 'Despesas',
        data: scenarioData.summary.monthlyExpenses,
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
      },
      {
        label: 'Resultado Líquido',
        data: scenarioData.summary.monthlyNetIncome,
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
      },
    ],
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
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Criar Novo Cenário</h2>
          <p className="mt-1 text-sm text-gray-500">
            Crie um cenário financeiro baseado na planilha {spreadsheet?.name}
          </p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
          <div className="px-4 py-5 sm:p-6">
            <div className="grid grid-cols-1 gap-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Nome do Cenário
                </label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  value={scenarioData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Descrição (opcional)
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows="3"
                  className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  value={scenarioData.description}
                  onChange={handleInputChange}
                ></textarea>
              </div>
            </div>
          </div>
        </div>
        
        {/* Summary Cards */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-6">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                  <svg className="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ScenarioCreate;