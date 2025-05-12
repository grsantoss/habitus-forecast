# Documentação da API - Habitus Forecast

Esta documentação detalha os endpoints disponíveis na API do Habitus Forecast, incluindo permissões necessárias, parâmetros, respostas e exemplos de uso.

## Sumário

- [Autenticação](#autenticação)
- [Formato de Respostas](#formato-de-respostas)
- [Paginação](#paginação)
- [Limitação de Taxa](#limitação-de-taxa)
- [Endpoints para Usuários Regulares](#endpoints-para-usuários-regulares)
  - [Autenticação](#endpoints-de-autenticação)
  - [Usuários](#endpoints-de-usuários)
  - [Cenários](#endpoints-de-cenários)
  - [Projeções](#endpoints-de-projeções)
  - [Dados Financeiros](#endpoints-de-dados-financeiros)
  - [Exportação](#endpoints-de-exportação)
- [Endpoints para Administradores](#endpoints-para-administradores)
  - [Gestão de Usuários](#endpoints-de-gestão-de-usuários)
  - [Métricas do Sistema](#endpoints-de-métricas-do-sistema)
  - [Configurações](#endpoints-de-configurações)
  - [Logs](#endpoints-de-logs)
- [Códigos de Erro](#códigos-de-erro)
- [Alterações da API](#alterações-da-api)

## Autenticação

A API do Habitus Forecast utiliza autenticação JWT (JSON Web Token). Para acessar recursos protegidos, é necessário incluir um token de acesso válido no cabeçalho HTTP `Authorization`.

### Obtenção de Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "password": "senha123"
}
```

Resposta:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Renovação de Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Resposta:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Resposta:

```json
{
  "detail": "Logout realizado com sucesso"
}
```

## Formato de Respostas

A API retorna dados em formato JSON. As respostas seguem uma estrutura consistente:

- Para operações bem-sucedidas:
  - Status HTTP 200, 201, 204, etc., dependendo da operação
  - Corpo JSON com dados solicitados

- Para operações com erro:
  - Status HTTP 4xx ou 5xx
  - Corpo JSON com detalhes do erro

Exemplo de erro:

```json
{
  "detail": "Descrição do erro",
  "code": "ERROR_CODE",
  "timestamp": "2023-11-15T14:30:45.123Z"
}
```

## Paginação

Endpoints que retornam múltiplos itens suportam paginação através dos parâmetros `page` e `limit`:

```http
GET /api/v1/scenarios?page=2&limit=10
```

Resposta paginada:

```json
{
  "items": [...],
  "total": 45,
  "page": 2,
  "limit": 10,
  "pages": 5
}
```

## Limitação de Taxa

A API implementa limitação de taxa para prevenir abusos. Os limites são:

- 100 requisições por minuto para usuários autenticados
- 20 requisições por minuto para usuários não autenticados

Os cabeçalhos HTTP incluem informações sobre limites:

- `X-RateLimit-Limit`: número máximo de requisições
- `X-RateLimit-Remaining`: requisições restantes no período
- `X-RateLimit-Reset`: tempo (em segundos) até o reset do contador

## Endpoints para Usuários Regulares

### Endpoints de Autenticação

#### Login

```http
POST /api/v1/auth/login
```

**Descrição**: Autentica um usuário e retorna tokens de acesso e atualização.

**Corpo da Requisição**:
- `email` (string, obrigatório): Email do usuário
- `password` (string, obrigatório): Senha do usuário

**Resposta**: Tokens JWT (access e refresh)

**Permissão**: Pública

#### Renovação de Token

```http
POST /api/v1/auth/refresh
```

**Descrição**: Renova um token de acesso expirado usando o refresh token.

**Corpo da Requisição**:
- `refresh_token` (string, obrigatório): Token de atualização válido

**Resposta**: Novo token de acesso

**Permissão**: Pública (com refresh token válido)

#### Logout

```http
POST /api/v1/auth/logout
```

**Descrição**: Invalida o token atual e o refresh token associado.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Resposta**: Confirmação de logout

**Permissão**: Usuário autenticado

#### Redefinição de Senha

```http
POST /api/v1/auth/forgot-password
```

**Descrição**: Envia um email com link para redefinição de senha.

**Corpo da Requisição**:
- `email` (string, obrigatório): Email do usuário

**Resposta**: Confirmação de envio do email

**Permissão**: Pública

```http
POST /api/v1/auth/reset-password
```

**Descrição**: Redefine a senha usando um token de recuperação.

**Corpo da Requisição**:
- `token` (string, obrigatório): Token de recuperação
- `password` (string, obrigatório): Nova senha
- `password_confirmation` (string, obrigatório): Confirmação da nova senha

**Resposta**: Confirmação de alteração

**Permissão**: Pública (com token válido)

### Endpoints de Usuários

#### Obter Perfil do Usuário Atual

```http
GET /api/v1/users/me
```

**Descrição**: Retorna detalhes do usuário autenticado.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Resposta**: Dados do perfil do usuário

**Permissão**: Usuário autenticado

#### Atualizar Perfil

```http
PUT /api/v1/users/me
```

**Descrição**: Atualiza dados do perfil do usuário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Corpo da Requisição**:
- `name` (string, opcional): Nome do usuário
- `email` (string, opcional): Email do usuário
- `preferences` (objeto, opcional): Preferências do usuário

**Resposta**: Dados atualizados do perfil

**Permissão**: Usuário autenticado

#### Alterar Senha

```http
PUT /api/v1/users/me/password
```

**Descrição**: Altera a senha do usuário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Corpo da Requisição**:
- `current_password` (string, obrigatório): Senha atual
- `new_password` (string, obrigatório): Nova senha
- `new_password_confirmation` (string, obrigatório): Confirmação da nova senha

**Resposta**: Confirmação de alteração

**Permissão**: Usuário autenticado

### Endpoints de Cenários

#### Listar Cenários

```http
GET /api/v1/scenarios
```

**Descrição**: Retorna a lista de cenários do usuário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Query**:
- `page` (inteiro, opcional): Página a ser retornada (padrão: 1)
- `limit` (inteiro, opcional): Número de itens por página (padrão: 10)
- `sort` (string, opcional): Campo para ordenação (padrão: "created_at")
- `order` (string, opcional): Direção da ordenação ("asc" ou "desc", padrão: "desc")
- `search` (string, opcional): Termo de busca para filtrar resultados

**Resposta**: Lista paginada de cenários

**Permissão**: Usuário autenticado

#### Obter Cenário

```http
GET /api/v1/scenarios/{scenario_id}
```

**Descrição**: Retorna detalhes de um cenário específico.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Resposta**: Detalhes do cenário

**Permissão**: Proprietário do cenário ou Administrador

#### Criar Cenário

```http
POST /api/v1/scenarios
```

**Descrição**: Cria um novo cenário financeiro.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Corpo da Requisição**:
- `name` (string, obrigatório): Nome do cenário
- `description` (string, opcional): Descrição do cenário
- `type` (string, opcional): Tipo do cenário (padrão: "custom")
- `initial_data` (objeto, opcional): Dados iniciais para o cenário

**Resposta**: Detalhes do cenário criado

**Permissão**: Usuário autenticado

#### Atualizar Cenário

```http
PUT /api/v1/scenarios/{scenario_id}
```

**Descrição**: Atualiza um cenário existente.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Corpo da Requisição**:
- `name` (string, opcional): Nome do cenário
- `description` (string, opcional): Descrição do cenário
- `type` (string, opcional): Tipo do cenário

**Resposta**: Detalhes do cenário atualizado

**Permissão**: Proprietário do cenário ou Administrador

#### Excluir Cenário

```http
DELETE /api/v1/scenarios/{scenario_id}
```

**Descrição**: Remove um cenário existente.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Resposta**: Confirmação de exclusão

**Permissão**: Proprietário do cenário ou Administrador

#### Duplicar Cenário

```http
POST /api/v1/scenarios/{scenario_id}/duplicate
```

**Descrição**: Cria uma cópia de um cenário existente.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário original

**Corpo da Requisição**:
- `name` (string, opcional): Nome para o novo cenário (padrão: "Cópia de [original]")
- `description` (string, opcional): Descrição para o novo cenário

**Resposta**: Detalhes do novo cenário

**Permissão**: Proprietário do cenário original ou Administrador

### Endpoints de Projeções

#### Gerar Projeção

```http
POST /api/v1/scenarios/{scenario_id}/projections
```

**Descrição**: Gera uma projeção financeira baseada no cenário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Corpo da Requisição**:
- `type` (string, obrigatório): Tipo de projeção ("realistic", "pessimistic", "optimistic", "aggressive")
- `period` (inteiro, opcional): Período em meses para projeção (padrão: 12)
- `parameters` (objeto, opcional): Parâmetros específicos para a projeção

**Resposta**: Dados da projeção gerada

**Permissão**: Proprietário do cenário ou Administrador

#### Listar Projeções

```http
GET /api/v1/scenarios/{scenario_id}/projections
```

**Descrição**: Lista projeções existentes para um cenário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Resposta**: Lista de projeções

**Permissão**: Proprietário do cenário ou Administrador

#### Obter Projeção

```http
GET /api/v1/scenarios/{scenario_id}/projections/{projection_id}
```

**Descrição**: Retorna detalhes de uma projeção específica.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário
- `projection_id` (string, obrigatório): ID da projeção

**Resposta**: Detalhes da projeção

**Permissão**: Proprietário do cenário ou Administrador

### Endpoints de Dados Financeiros

#### Importar Dados

```http
POST /api/v1/scenarios/{scenario_id}/data/import
```

**Descrição**: Importa dados financeiros para um cenário existente.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token
- `Content-Type` (string, obrigatório): multipart/form-data

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Corpo da Requisição**:
- `file` (arquivo, obrigatório): Arquivo Excel ou CSV com dados financeiros
- `options` (objeto, opcional): Opções de importação

**Resposta**: Resumo da importação

**Permissão**: Proprietário do cenário ou Administrador

#### Listar Dados Financeiros

```http
GET /api/v1/scenarios/{scenario_id}/data
```

**Descrição**: Lista dados financeiros de um cenário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Parâmetros de Query**:
- `category` (string, opcional): Filtrar por categoria
- `date_from` (string, opcional): Data inicial (formato ISO)
- `date_to` (string, opcional): Data final (formato ISO)
- `page` (inteiro, opcional): Página a ser retornada
- `limit` (inteiro, opcional): Itens por página

**Resposta**: Lista paginada de dados financeiros

**Permissão**: Proprietário do cenário ou Administrador

#### Adicionar Dado Financeiro

```http
POST /api/v1/scenarios/{scenario_id}/data
```

**Descrição**: Adiciona um novo registro financeiro ao cenário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Corpo da Requisição**:
- `category` (string, obrigatório): Categoria ("revenue", "expense", "investment")
- `subcategory` (string, opcional): Subcategoria
- `description` (string, obrigatório): Descrição do item
- `amount` (número, obrigatório): Valor
- `date` (string, obrigatório): Data (formato ISO)
- `recurring` (booleano, opcional): Se é recorrente
- `recurrence_interval` (string, opcional): Intervalo de recorrência
- `tags` (array de strings, opcional): Tags para categorização

**Resposta**: Detalhes do item criado

**Permissão**: Proprietário do cenário ou Administrador

### Endpoints de Exportação

#### Exportar Cenário

```http
GET /api/v1/scenarios/{scenario_id}/export
```

**Descrição**: Exporta dados de um cenário em diferentes formatos.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário

**Parâmetros de Query**:
- `format` (string, obrigatório): Formato de exportação ("xlsx", "csv", "pdf", "json")
- `include_projections` (booleano, opcional): Incluir projeções (padrão: true)

**Resposta**: Arquivo do cenário no formato solicitado

**Permissão**: Proprietário do cenário ou Administrador

#### Exportar Projeção

```http
GET /api/v1/scenarios/{scenario_id}/projections/{projection_id}/export
```

**Descrição**: Exporta dados de uma projeção específica.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `scenario_id` (string, obrigatório): ID do cenário
- `projection_id` (string, obrigatório): ID da projeção

**Parâmetros de Query**:
- `format` (string, obrigatório): Formato de exportação ("xlsx", "csv", "pdf", "json")

**Resposta**: Arquivo da projeção no formato solicitado

**Permissão**: Proprietário do cenário ou Administrador

## Endpoints para Administradores

### Endpoints de Gestão de Usuários

#### Listar Usuários

```http
GET /api/v1/admin/users
```

**Descrição**: Lista todos os usuários do sistema.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Query**:
- `page` (inteiro, opcional): Página a ser retornada
- `limit` (inteiro, opcional): Itens por página
- `sort` (string, opcional): Campo para ordenação
- `order` (string, opcional): Direção da ordenação
- `search` (string, opcional): Termo de busca
- `status` (string, opcional): Filtro por status ("active", "inactive")

**Resposta**: Lista paginada de usuários

**Permissão**: Administrador

#### Obter Usuário

```http
GET /api/v1/admin/users/{user_id}
```

**Descrição**: Retorna detalhes de um usuário específico.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `user_id` (string, obrigatório): ID do usuário

**Resposta**: Detalhes do usuário

**Permissão**: Administrador

#### Criar Usuário

```http
POST /api/v1/admin/users
```

**Descrição**: Cria um novo usuário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Corpo da Requisição**:
- `name` (string, obrigatório): Nome do usuário
- `email` (string, obrigatório): Email do usuário
- `password` (string, opcional): Senha inicial
- `role` (string, obrigatório): Papel ("user" ou "admin")
- `is_active` (booleano, opcional): Se a conta está ativa (padrão: true)
- `send_welcome_email` (booleano, opcional): Se deve enviar email de boas-vindas (padrão: true)

**Resposta**: Detalhes do usuário criado

**Permissão**: Administrador

#### Atualizar Usuário

```http
PUT /api/v1/admin/users/{user_id}
```

**Descrição**: Atualiza dados de um usuário existente.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `user_id` (string, obrigatório): ID do usuário

**Corpo da Requisição**:
- `name` (string, opcional): Nome do usuário
- `email` (string, opcional): Email do usuário
- `role` (string, opcional): Papel ("user" ou "admin")
- `is_active` (booleano, opcional): Se a conta está ativa

**Resposta**: Detalhes do usuário atualizado

**Permissão**: Administrador

#### Desativar/Ativar Usuário

```http
PATCH /api/v1/admin/users/{user_id}/status
```

**Descrição**: Altera o status de um usuário (ativo/inativo).

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `user_id` (string, obrigatório): ID do usuário

**Corpo da Requisição**:
- `is_active` (booleano, obrigatório): Novo status

**Resposta**: Confirmação da alteração

**Permissão**: Administrador

#### Redefinir Senha de Usuário

```http
POST /api/v1/admin/users/{user_id}/reset-password
```

**Descrição**: Redefine a senha de um usuário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Path**:
- `user_id` (string, obrigatório): ID do usuário

**Corpo da Requisição**:
- `send_email` (booleano, opcional): Se deve enviar email com a nova senha (padrão: true)
- `new_password` (string, opcional): Nova senha (se `send_email` for false)

**Resposta**: Confirmação da operação

**Permissão**: Administrador

### Endpoints de Métricas do Sistema

#### Métricas Gerais

```http
GET /api/v1/admin/metrics
```

**Descrição**: Retorna métricas gerais do sistema.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Query**:
- `period` (string, opcional): Período de análise ("day", "week", "month", "year", padrão: "week")

**Resposta**: Conjunto de métricas do sistema

**Permissão**: Administrador

#### Métricas de Usuários

```http
GET /api/v1/admin/metrics/users
```

**Descrição**: Retorna métricas relacionadas a usuários.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Query**:
- `period` (string, opcional): Período de análise ("day", "week", "month", "year", padrão: "week")

**Resposta**: Métricas detalhadas de usuários

**Permissão**: Administrador

#### Métricas de Recursos

```http
GET /api/v1/admin/metrics/resources
```

**Descrição**: Retorna métricas de utilização de recursos.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Resposta**: Utilização atual e histórica de recursos

**Permissão**: Administrador

### Endpoints de Configurações

#### Obter Configurações

```http
GET /api/v1/admin/settings
```

**Descrição**: Retorna configurações globais do sistema.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Resposta**: Objeto com configurações

**Permissão**: Administrador

#### Atualizar Configurações

```http
PUT /api/v1/admin/settings
```

**Descrição**: Atualiza configurações globais.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Corpo da Requisição**:
- `user_limits` (objeto, opcional): Limites dos usuários
- `auth` (objeto, opcional): Configurações de autenticação
- `emails` (objeto, opcional): Configurações de email
- `backups` (objeto, opcional): Configurações de backup
- `projections` (objeto, opcional): Configurações de projeções

**Resposta**: Objeto com configurações atualizadas

**Permissão**: Administrador

#### Obter Modelo de Cenário

```http
GET /api/v1/admin/scenario-templates
```

**Descrição**: Retorna todos os modelos de cenários disponíveis.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Resposta**: Lista de modelos de cenários

**Permissão**: Administrador

#### Criar Modelo de Cenário

```http
POST /api/v1/admin/scenario-templates
```

**Descrição**: Cria um novo modelo de cenário.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Corpo da Requisição**:
- `name` (string, obrigatório): Nome do modelo
- `description` (string, opcional): Descrição do modelo
- `structure` (objeto, obrigatório): Estrutura do cenário modelo
- `is_public` (booleano, opcional): Se disponível para todos os usuários (padrão: true)

**Resposta**: Modelo criado

**Permissão**: Administrador

### Endpoints de Logs

#### Listar Logs

```http
GET /api/v1/admin/logs
```

**Descrição**: Retorna logs do sistema.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Query**:
- `page` (inteiro, opcional): Página a ser retornada
- `limit` (inteiro, opcional): Itens por página
- `level` (string, opcional): Nível de log ("info", "warning", "error")
- `start_date` (string, opcional): Data inicial (formato ISO)
- `end_date` (string, opcional): Data final (formato ISO)
- `search` (string, opcional): Termo de busca

**Resposta**: Lista paginada de logs

**Permissão**: Administrador

#### Logs de Atividade

```http
GET /api/v1/admin/logs/activity
```

**Descrição**: Retorna logs de atividade dos usuários.

**Cabeçalhos**:
- `Authorization` (string, obrigatório): Bearer token

**Parâmetros de Query**:
- `page` (inteiro, opcional): Página a ser retornada
- `limit` (inteiro, opcional): Itens por página
- `user_id` (string, opcional): Filtrar por usuário específico
- `action` (string, opcional): Filtrar por tipo de ação
- `start_date` (string, opcional): Data inicial (formato ISO)
- `end_date` (string, opcional): Data final (formato ISO)

**Resposta**: Lista paginada de logs de atividade

**Permissão**: Administrador

## Códigos de Erro

| Código | Descrição | HTTP Status |
|--------|-----------|-------------|
| `AUTHENTICATION_ERROR` | Erro de autenticação | 401 |
| `INVALID_CREDENTIALS` | Credenciais inválidas | 401 |
| `TOKEN_EXPIRED` | Token expirado | 401 |
| `FORBIDDEN` | Acesso negado | 403 |
| `RESOURCE_NOT_FOUND` | Recurso não encontrado | 404 |
| `VALIDATION_ERROR` | Erro de validação de dados | 422 |
| `RATE_LIMIT_EXCEEDED` | Limite de requisições excedido | 429 |
| `INTERNAL_ERROR` | Erro interno do servidor | 500 |
| `DATABASE_ERROR` | Erro no banco de dados | 500 |

## Alterações da API

Esta documentação refere-se à API v1. Alterações significativas são comunicadas com antecedência e seguem o versionamento semântico.

Para detalhes sobre o uso da API, incluindo exemplos em diferentes linguagens, consulte [https://api.habitus-forecast.com/api/docs](https://api.habitus-forecast.com/api/docs). 