# Guia de Migração do Habitus Forecast

Este guia fornece instruções detalhadas para migrar do Habitus Forecast Node.js para a nova versão em Python.

## Sumário

- [Visão Geral da Migração](#visão-geral-da-migração)
- [Diferenças entre as Versões](#diferenças-entre-as-versões)
- [Migração de Dados](#migração-de-dados)
- [Mudanças na API](#mudanças-na-api)
- [Considerações para o Frontend](#considerações-para-o-frontend)
- [Problemas Comuns e Soluções](#problemas-comuns-e-soluções)
- [Cronograma de Desativação](#cronograma-de-desativação)

## Visão Geral da Migração

O Habitus Forecast está evoluindo de uma plataforma baseada em Node.js (Express) para uma implementação em Python (FastAPI). Esta migração visa melhorar o desempenho, escalabilidade e manutenibilidade do sistema, além de aproveitar as capacidades avançadas do Python para processamento de dados e análise financeira.

### Principais Motivações

- **Melhor Desempenho**: FastAPI oferece maior velocidade e eficiência
- **Bibliotecas de Análise de Dados**: Acesso direto ao ecossistema Python (pandas, numpy, scikit-learn)
- **Tipagem Estática**: TypeScript no frontend e Python com tipagem no backend
- **Documentação Automática**: Geração automática de documentação OpenAPI
- **Manutenibilidade**: Código mais limpo e estruturado

### Cronograma da Migração

1. **Fase Atual**: Ambas as versões (Node.js e Python) operando em paralelo
2. **Transição**: Migração gradual dos usuários para a nova versão
3. **Desativação**: Desligamento programado da versão Node.js (ver [Cronograma de Desativação](#cronograma-de-desativação))

## Diferenças entre as Versões

### Arquitetura

| Aspecto | Versão Node.js | Versão Python |
|---------|---------------|---------------|
| Framework | Express | FastAPI |
| Banco de Dados | MongoDB (driver nativo) | MongoDB (com ODM) |
| Autenticação | JWT com Passport.js | JWT com OAuth2 |
| Documentação | Swagger manual | OpenAPI automático |
| Processamento Assíncrono | Promises/Callbacks | Async/Await nativo |
| Validação | Joi | Pydantic |

### Tecnologias

| Componente | Versão Node.js | Versão Python |
|------------|---------------|---------------|
| Servidor | Express 4.x | FastAPI 0.103.x |
| ORM/ODM | Mongoose | Motor + Classes próprias |
| Frontend | React 17 | React 18 com TypeScript |
| Validação | Joi | Pydantic |
| Cache | Redis | Redis |
| Tarefas Assíncronas | Bull | Celery |
| Logging | Winston | Loguru |

### Funcionalidades

| Funcionalidade | Status na Nova Versão | Notas |
|----------------|----------------------|-------|
| Autenticação de Usuários | ✅ Completo | Implementação melhorada |
| Gerenciamento de Cenários | ✅ Completo | API redesenhada |
| Análise Financeira | ✅ Aprimorado | Novos algoritmos |
| Projeções | ✅ Aprimorado | Maior precisão |
| Exportação de Relatórios | ✅ Completo | Novos formatos |
| Dashboards | ✅ Completo | Nova interface |
| Administração | ✅ Completo | Novas funcionalidades |
| Integrações com Terceiros | ⚠️ Parcial | Algumas APIs ainda em desenvolvimento |

## Migração de Dados

A migração de dados do sistema Node.js para o sistema Python é realizada através de scripts dedicados. Os dados são transferidos mantendo a integridade referencial e convertendo formatos quando necessário.

### Executando a Migração

1. Configure os parâmetros de conexão nos arquivos de ambiente:

```bash
# .env
SOURCE_MONGODB_URI=mongodb://usuario:senha@host:porta/habitus_node
TARGET_MONGODB_URI=mongodb://usuario:senha@host:porta/habitus_python
```

2. Execute o script de migração:

```bash
python -m app.utils.migrate_data --source $SOURCE_MONGODB_URI --target $TARGET_MONGODB_URI
```

3. Verifique o relatório de migração gerado:

```bash
cat migration_report_YYYYMMDD_HHMMSS.json
```

### Entidades Migradas

- Usuários (incluindo autenticação)
- Dados Financeiros
- Cenários e Projeções
- Configurações do Sistema
- Logs de Atividade

### Validação Pós-Migração

O script realiza validações para garantir que os dados foram migrados corretamente:

- Contagem de documentos entre origem e destino
- Verificação de relações entre entidades
- Validação de estrutura de dados
- Verificação de integridade

Para executar apenas a validação sem migrar dados:

```bash
python -m app.utils.migrate_data --source $SOURCE_MONGODB_URI --target $TARGET_MONGODB_URI --dry-run
```

## Mudanças na API

A API foi redesenhada para seguir princípios RESTful mais consistentes e fornecer uma experiência de desenvolvedor melhorada.

### Diferenças nos Endpoints

| Função | API Node.js | API Python | Notas |
|--------|------------|------------|-------|
| Autenticação | POST /api/auth/login | POST /api/v1/auth/login | Formato do token alterado |
| Listar Cenários | GET /api/scenarios | GET /api/v1/scenarios | Paginação aprimorada |
| Criar Cenário | POST /api/scenarios | POST /api/v1/scenarios | Validação mais rigorosa |
| Detalhes do Usuário | GET /api/users/:id | GET /api/v1/users/{id} | Mudança no formato de URL |
| Criar Projeção | POST /api/scenarios/:id/projections | POST /api/v1/scenarios/{id}/projections | Novos parâmetros |

### Alterações no Formato de Respostas

#### Versão Node.js:
```json
{
  "success": true,
  "data": {
    "id": "5f8d43e1e4b0b1f2c3d4e5f6",
    "name": "Cenário 2023",
    "createdAt": "2023-01-15T10:30:00.000Z"
  }
}
```

#### Versão Python:
```json
{
  "id": "5f8d43e1e4b0b1f2c3d4e5f6",
  "name": "Cenário 2023",
  "created_at": "2023-01-15T10:30:00",
  "updated_at": "2023-01-15T10:30:00"
}
```

### Alterações na Autenticação

- **Token JWT**: Estrutura do token modificada, inclui mais metadados
- **Refresh Token**: Implementação aprimorada para renovação de tokens
- **Duração**: Tokens de acesso com duração mais curta (30 minutos vs. 24 horas)
- **Revogação**: Suporte para revogação de tokens

### Nova Documentação da API

A documentação da API está disponível em:

- **Swagger UI**: [/api/docs](https://api.habitus-forecast.com/api/docs)
- **ReDoc**: [/api/redoc](https://api.habitus-forecast.com/api/redoc)

## Considerações para o Frontend

A nova versão é compatível com clientes existentes, mas requer algumas adaptações para aproveitar todos os recursos.

### Atualizações Necessárias

1. **Autenticação**: Atualizar o fluxo de autenticação para suportar refresh tokens
2. **Formato de Requests/Responses**: Adaptar para os novos formatos
3. **Endpoints**: Atualizar as URLs dos endpoints
4. **Tratamento de Erros**: Adaptar para o novo formato de erros

### Exemplo de Integração (TypeScript)

```typescript
// Configuração do cliente API
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.habitus-forecast.com/api/v1',
  timeout: 10000,
});

// Interceptor para token de autenticação
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(
          'https://api.habitus-forecast.com/api/v1/auth/refresh',
          { refresh_token: refreshToken }
        );
        
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        
        // Refazer requisição original com novo token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Direcionar para tela de login
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Exemplo de uso da API
export const scenariosApi = {
  getAll: async (page = 1, limit = 10) => {
    const response = await api.get('/scenarios', {
      params: { page, limit },
    });
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/scenarios/${id}`);
    return response.data;
  },
  
  create: async (scenarioData) => {
    const response = await api.post('/scenarios', scenarioData);
    return response.data;
  },
  
  update: async (id, scenarioData) => {
    const response = await api.put(`/scenarios/${id}`, scenarioData);
    return response.data;
  },
  
  delete: async (id) => {
    await api.delete(`/scenarios/${id}`);
  },
};
```

### Interface Administrativa

A interface administrativa foi completamente redesenhada e oferece:

- **Dashboard Unificado**: Visão geral de todos os usuários e atividades
- **Gerenciamento de Usuários**: Interface aprimorada
- **Monitoramento**: Métricas em tempo real
- **Logs**: Visualização e pesquisa avançada de logs

## Problemas Comuns e Soluções

### Erro na Autenticação
**Problema**: Tokens antigos não funcionam no novo sistema.
**Solução**: Implementar fluxo de login para obter novos tokens.

### Formato de Dados Incompatível
**Problema**: Formato de dados diferente entre versões.
**Solução**: Utilizar adaptadores para converter dados.

```typescript
// Exemplo de adaptador
function adaptScenario(legacyScenario) {
  return {
    id: legacyScenario.id,
    name: legacyScenario.name,
    description: legacyScenario.description || '',
    created_at: legacyScenario.createdAt,
    user_id: legacyScenario.userId,
    // Converter outros campos
  };
}
```

### Respostas de Erro Diferentes
**Problema**: Formato de erros alterado.
**Solução**: Adaptar tratamento de erros.

```typescript
function handleApiError(error) {
  // Nova versão da API
  if (error.response && error.response.data && error.response.data.detail) {
    return error.response.data.detail;
  }
  
  // Versão antiga da API
  if (error.response && error.response.data && error.response.data.message) {
    return error.response.data.message;
  }
  
  // Fallback
  return 'Ocorreu um erro desconhecido';
}
```

## Cronograma de Desativação

A versão Node.js será desativada gradualmente, seguindo este cronograma:

1. **Fase 1** (Atual): Ambas versões operando, novas contas direcionadas para a versão Python
2. **Fase 2** (Em 3 meses): Migração compulsória para usuários existentes
3. **Fase 3** (Em 6 meses): Versão Node.js disponível apenas para leitura
4. **Fase 4** (Em 9 meses): Desativação completa da versão Node.js

### Comunicação com Usuários

- E-mails periódicos sobre o processo de migração
- Banners informativos na aplicação
- Documentação detalhada e suporte durante a transição

Para dúvidas ou suporte durante a migração, contate a equipe de suporte em `support@habitus-forecast.com`. 