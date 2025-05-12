import React, { createContext, useState, useContext } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const AdminContext = createContext();

export const useAdmin = () => useContext(AdminContext);

export const AdminProvider = ({ children }) => {
  const [users, setUsers] = useState([]);
  const [userCount, setUserCount] = useState(0);
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [systemSettings, setSystemSettings] = useState(null);
  const [loading, setLoading] = useState(false);

  // Carregar usuários com paginação e filtros
  const fetchUsers = async (page = 1, limit = 10, filters = {}) => {
    setLoading(true);
    try {
      const params = { page, limit, ...filters };
      const res = await axios.get('/api/admin/users', { params });
      setUsers(res.data.items);
      setUserCount(res.data.total);
      return res.data;
    } catch (err) {
      toast.error('Erro ao carregar usuários');
      console.error(err);
      return { items: [], total: 0 };
    } finally {
      setLoading(false);
    }
  };

  // Carregar métricas do sistema
  const fetchMetrics = async (period = 'week') => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/admin/metrics?period=${period}`);
      setSystemMetrics(res.data);
      return res.data;
    } catch (err) {
      toast.error('Erro ao carregar métricas do sistema');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Carregar logs do sistema
  const fetchLogs = async (page = 1, limit = 50, filters = {}) => {
    setLoading(true);
    try {
      const params = { page, limit, ...filters };
      const res = await axios.get('/api/admin/logs', { params });
      setLogs(res.data.items);
      return res.data;
    } catch (err) {
      toast.error('Erro ao carregar logs do sistema');
      console.error(err);
      return { items: [], total: 0 };
    } finally {
      setLoading(false);
    }
  };

  // Carregar configurações do sistema
  const fetchSystemSettings = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/admin/settings');
      setSystemSettings(res.data);
      return res.data;
    } catch (err) {
      toast.error('Erro ao carregar configurações do sistema');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar configurações do sistema
  const updateSystemSettings = async (settings) => {
    setLoading(true);
    try {
      const res = await axios.put('/api/admin/settings', settings);
      setSystemSettings(res.data);
      toast.success('Configurações atualizadas com sucesso');
      return res.data;
    } catch (err) {
      toast.error('Erro ao atualizar configurações');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Criar novo usuário
  const createUser = async (userData) => {
    setLoading(true);
    try {
      const res = await axios.post('/api/admin/users', userData);
      toast.success('Usuário criado com sucesso');
      return res.data;
    } catch (err) {
      toast.error('Erro ao criar usuário');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar usuário existente
  const updateUser = async (userId, userData) => {
    setLoading(true);
    try {
      const res = await axios.put(`/api/admin/users/${userId}`, userData);
      toast.success('Usuário atualizado com sucesso');
      return res.data;
    } catch (err) {
      toast.error('Erro ao atualizar usuário');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Alternar status do usuário (ativo/inativo)
  const toggleUserStatus = async (userId, isActive) => {
    setLoading(true);
    try {
      const res = await axios.patch(`/api/admin/users/${userId}/status`, { is_active: isActive });
      toast.success(`Usuário ${isActive ? 'ativado' : 'desativado'} com sucesso`);
      return res.data;
    } catch (err) {
      toast.error(`Erro ao ${isActive ? 'ativar' : 'desativar'} usuário`);
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Excluir usuário
  const deleteUser = async (userId) => {
    setLoading(true);
    try {
      await axios.delete(`/api/admin/users/${userId}`);
      toast.success('Usuário excluído com sucesso');
      return true;
    } catch (err) {
      toast.error('Erro ao excluir usuário');
      console.error(err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdminContext.Provider
      value={{
        users,
        userCount,
        systemMetrics,
        logs,
        systemSettings,
        loading,
        fetchUsers,
        fetchMetrics,
        fetchLogs,
        fetchSystemSettings,
        updateSystemSettings,
        createUser,
        updateUser,
        toggleUserStatus,
        deleteUser
      }}
    >
      {children}
    </AdminContext.Provider>
  );
}; 