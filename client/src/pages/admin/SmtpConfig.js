import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const SmtpConfig = () => {
  const [formData, setFormData] = useState({
    host: '',
    port: 587,
    secure: false,
    user: '',
    password: '',
    fromEmail: '',
    fromName: 'Habitus Finance',
    isActive: true
  });
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [hasConfig, setHasConfig] = useState(false);

  const { host, port, secure, user, password, fromEmail, fromName, isActive } = formData;

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/smtp-config');
      setFormData({
        host: res.data.host,
        port: res.data.port,
        secure: res.data.secure,
        user: res.data.user,
        password: '', // Não recebemos a senha do servidor
        fromEmail: res.data.fromEmail,
        fromName: res.data.fromName,
        isActive: res.data.isActive
      });
      setHasConfig(true);
    } catch (err) {
      if (err.response?.status !== 404) {
        toast.error('Erro ao carregar configuração SMTP');
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await axios.post('/api/smtp-config', formData);
      setFormData({
        ...formData,
        password: '' // Limpar a senha após o envio
      });
      setHasConfig(true);
      toast.success('Configuração SMTP salva com sucesso');
    } catch (err) {
      toast.error(
        err.response?.data?.msg || 
        'Erro ao salvar configuração SMTP'
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async (e) => {
    e.preventDefault();
    
    if (!testEmail) {
      toast.error('Por favor, insira um email para teste');
      return;
    }
    
    setTestLoading(true);
    
    try {
      const res = await axios.post('/api/smtp-config/test', { email: testEmail });
      if (res.data.success) {
        toast.success('Email de teste enviado com sucesso');
      } else {
        toast.error('Falha ao enviar email de teste');
      }
    } catch (err) {
      toast.error(
        err.response?.data?.msg || 
        'Erro ao enviar email de teste'
      );
      console.error(err);
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-6 px-4">
      <h1 className="text-2xl font-semibold mb-6">Configuração SMTP</h1>
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="p-6">
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <label htmlFor="host" className="block text-sm font-medium text-gray-700">
                  Host SMTP
                </label>
                <input
                  type="text"
                  name="host"
                  id="host"
                  value={host}
                  onChange={handleChange}
                  required
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="smtp.example.com"
                />
              </div>
              
              <div className="space-y-1">
                <label htmlFor="port" className="block text-sm font-medium text-gray-700">
                  Porta
                </label>
                <input
                  type="number"
                  name="port"
                  id="port"
                  value={port}
                  onChange={handleChange}
                  required
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              
              <div className="space-y-1">
                <label htmlFor="user" className="block text-sm font-medium text-gray-700">
                  Usuário
                </label>
                <input
                  type="text"
                  name="user"
                  id="user"
                  value={user}
                  onChange={handleChange}
                  required
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="seu@email.com"
                />
              </div>
              
              <div className="space-y-1">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Senha
                </label>
                <input
                  type="password"
                  name="password"
                  id="password"
                  value={password}
                  onChange={handleChange}
                  required={!hasConfig}
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder={hasConfig ? "Deixe em branco para manter a mesma" : "Senha SMTP"}
                />
              </div>
              
              <div className="space-y-1">
                <label htmlFor="fromEmail" className="block text-sm font-medium text-gray-700">
                  Email de Origem
                </label>
                <input
                  type="email"
                  name="fromEmail"
                  id="fromEmail"
                  value={fromEmail}
                  onChange={handleChange}
                  required
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="noreply@seudominio.com"
                />
              </div>
              
              <div className="space-y-1">
                <label htmlFor="fromName" className="block text-sm font-medium text-gray-700">
                  Nome de Origem
                </label>
                <input
                  type="text"
                  name="fromName"
                  id="fromName"
                  value={fromName}
                  onChange={handleChange}
                  required
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="Habitus Finance"
                />
              </div>
            </div>
            
            <div className="mt-4 space-y-2">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="secure"
                  id="secure"
                  checked={secure}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="secure" className="ml-2 block text-sm text-gray-700">
                  Conexão segura (SSL/TLS)
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="isActive"
                  id="isActive"
                  checked={isActive}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="isActive" className="ml-2 block text-sm text-gray-700">
                  Ativar configuração SMTP
                </label>
              </div>
            </div>
            
            <div className="mt-6">
              <button
                type="submit"
                disabled={loading}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                {loading ? 'Salvando...' : 'Salvar Configuração'}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      {hasConfig && (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="px-6 py-4 bg-white border-b">
            <h2 className="text-lg font-semibold">Testar Configuração</h2>
          </div>
          
          <div className="p-6">
            <form onSubmit={handleTestEmail} className="space-y-4">
              <div>
                <label htmlFor="testEmail" className="block text-sm font-medium text-gray-700 mb-1">
                  Email para Teste
                </label>
                <input
                  type="email"
                  id="testEmail"
                  value={testEmail}
                  onChange={(e) => setTestEmail(e.target.value)}
                  required
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="seu@email.com"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Enviaremos um email de teste para este endereço para verificar a configuração SMTP.
                </p>
              </div>
              
              <div>
                <button
                  type="submit"
                  disabled={testLoading}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  {testLoading ? 'Enviando...' : 'Enviar Email de Teste'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmtpConfig; 