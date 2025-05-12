# Endpoints de Gestão de Cenários e Planilhas - Habitus Forecast

## Visão Geral

Foram implementados os endpoints para gestão de planilhas e cenários financeiros no Habitus Forecast, permitindo:

1. Upload e processamento de planilhas Excel
2. Geração de cenários financeiros baseados nos dados processados
3. Listagem e visualização de cenários salvos
4. Exclusão de cenários

Todos os endpoints são protegidos pelo sistema de autenticação JWT com RBAC (Role-Based Access Control).

## Endpoints de Planilhas

### 1. Upload de Planilha (`POST /api/spreadsheets/`)

- **Descrição**: Realiza o upload de uma planilha Excel para processamento.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `file`: Arquivo Excel (formato .xlsx ou .xls)
  - `description`: Descrição opcional da planilha
- **Resposta**: Informações sobre o upload realizado, incluindo ID da planilha.

### 2. Processamento de Planilha (`POST /api/spreadsheets/{spreadsheet_id}/process`)

- **Descrição**: Processa uma planilha previamente enviada, extraindo dados financeiros.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `spreadsheet_id`: ID da planilha a ser processada
  - `required_categories`: Lista opcional de categorias financeiras obrigatórias
- **Resposta**: Resultado do processamento, incluindo categorias encontradas e metadados.

### 3. Listagem de Planilhas (`GET /api/spreadsheets/`)

- **Descrição**: Lista as planilhas do usuário atual.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `skip`: Itens a pular (paginação)
  - `limit`: Limite de itens a retornar
  - `status`: Filtrar por status (uploaded, processed)
- **Resposta**: Lista paginada de planilhas com metadados.

### 4. Detalhes de Planilha (`GET /api/spreadsheets/{spreadsheet_id}`)

- **Descrição**: Obtém detalhes sobre uma planilha específica.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `spreadsheet_id`: ID da planilha
- **Resposta**: Detalhes completos da planilha.

### 5. Exclusão de Planilha (`DELETE /api/spreadsheets/{spreadsheet_id}`)

- **Descrição**: Exclui uma planilha e seus dados associados.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `spreadsheet_id`: ID da planilha a ser excluída
- **Resposta**: Sem conteúdo (204 No Content).

## Endpoints de Cenários

### 1. Criação de Cenário (`POST /api/scenarios/`)

- **Descrição**: Cria um novo cenário financeiro baseado em dados processados.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `title`: Título do cenário
  - `description`: Descrição opcional do cenário
  - `scenario_type`: Tipo de cenário (realista, pessimista, otimista, agressivo)
  - `financial_data_id`: ID dos dados financeiros a serem utilizados
  - `parameters`: Parâmetros opcionais para ajustar o cenário
- **Resposta**: Dados do cenário gerado, incluindo métricas calculadas.

### 2. Listagem de Cenários (`GET /api/scenarios/`)

- **Descrição**: Lista os cenários financeiros do usuário.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `skip`: Itens a pular (paginação)
  - `limit`: Limite de itens a retornar
  - `scenario_type`: Filtrar por tipo de cenário
  - `financial_data_id`: Filtrar por ID de dados financeiros
- **Resposta**: Lista paginada de cenários com metadados.

### 3. Detalhes de Cenário (`GET /api/scenarios/{scenario_id}`)

- **Descrição**: Obtém detalhes de um cenário específico.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `scenario_id`: ID do cenário
- **Resposta**: Detalhes completos do cenário, incluindo métricas e parâmetros.

### 4. Exclusão de Cenário (`DELETE /api/scenarios/{scenario_id}`)

- **Descrição**: Exclui um cenário financeiro.
- **Autenticação**: Requer usuário autenticado.
- **Parâmetros**:
  - `scenario_id`: ID do cenário a ser excluído
- **Resposta**: Sem conteúdo (204 No Content).

### 5. Tipos de Cenários (`GET /api/scenarios/types`)

- **Descrição**: Lista os tipos de cenários disponíveis.
- **Autenticação**: Requer usuário autenticado.
- **Resposta**: Lista de tipos de cenários com descrições.

## Características Implementadas

1. **Validação de Dados**: Todos os endpoints utilizam schemas Pydantic para validação de dados de entrada e saída.
2. **Segurança**: Todos os endpoints são protegidos por autenticação JWT.
3. **Documentação**: Documentação OpenAPI completa com exemplos de requisições e respostas.
4. **Tratamento de Erros**: Respostas de erro claras e informativas.
5. **Controle de Acesso**: Verificação de propriedade dos recursos (os usuários só podem acessar seus próprios dados).
6. **Paginação**: Suporte para paginação nas listas de recursos.
7. **Filtragem**: Opções de filtragem para refinamento das consultas.

## Exemplos de Uso

### Upload de Planilha

```bash
curl -X POST "http://localhost:8000/api/spreadsheets/" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -F "file=@dados_financeiros.xlsx" \
    -F "description=Dados do primeiro trimestre de 2023"
```

### Criação de Cenário

```bash
curl -X POST "http://localhost:8000/api/scenarios/" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Cenário Otimista 2023",
        "description": "Projeção otimista para o ano fiscal de 2023",
        "scenario_type": "otimista",
        "financial_data_id": "60d9b5e7d2a68c001f45e123",
        "parameters": {
            "revenue_growth": 15.0,
            "cost_reduction": 7.5,
            "expense_growth": -5.0,
            "investment_growth": 20.0
        }
    }'
``` 