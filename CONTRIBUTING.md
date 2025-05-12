# Guia de Contribuição - Habitus Forecast

Obrigado pelo interesse em contribuir com o Habitus Forecast! Este documento fornece as diretrizes e práticas recomendadas para contribuir com o projeto.

## Sumário

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
  - [Reportando Bugs](#reportando-bugs)
  - [Sugerindo Melhorias](#sugerindo-melhorias)
  - [Pull Requests](#pull-requests)
- [Guia de Estilo](#guia-de-estilo)
  - [Código Python](#código-python)
  - [Código JavaScript/TypeScript](#código-javascripttypescript)
  - [Commits](#commits)
- [Processo de Desenvolvimento](#processo-de-desenvolvimento)
  - [Ambiente de Desenvolvimento](#ambiente-de-desenvolvimento)
  - [Fluxo de Trabalho Git](#fluxo-de-trabalho-git)
  - [Ciclo de Desenvolvimento](#ciclo-de-desenvolvimento)
- [Testes](#testes)
  - [Executando Testes](#executando-testes)
  - [Cobertura de Testes](#cobertura-de-testes)
  - [Escrevendo Testes](#escrevendo-testes)
- [Documentação](#documentação)
- [Segurança](#segurança)
- [Contato](#contato)

## Código de Conduta

Este projeto segue um Código de Conduta para criar um ambiente acolhedor e inclusivo. Ao participar, espera-se que você respeite este código. Por favor, reporte comportamentos inaceitáveis para a equipe do projeto.

## Como Contribuir

### Reportando Bugs

Bugs podem ser reportados através das issues do GitHub. Antes de criar uma nova issue, verifique se o bug já foi reportado.

Ao reportar um bug, inclua:
- Descrição clara e concisa do problema
- Passos detalhados para reproduzir o bug
- Comportamento esperado vs. comportamento atual
- Screenshots, logs ou mensagens de erro (se aplicável)
- Ambiente (sistema operacional, navegador, versões, etc.)

### Sugerindo Melhorias

Sugestões de melhorias também são bem-vindas através das issues do GitHub.

Para sugestões de melhorias, inclua:
- Descrição clara e detalhada da melhoria proposta
- Justificativa (como essa melhoria beneficiaria o projeto)
- Detalhes específicos da implementação (se possível)
- Mockups ou exemplos visuais (se aplicável)

### Pull Requests

1. Fork o repositório
2. Crie um branch para sua feature (`git checkout -b feature/nome-da-feature`)
3. Implemente suas mudanças
4. Adicione testes para sua funcionalidade
5. Certifique-se de que os testes passam (`pytest`)
6. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
7. Push para o branch (`git push origin feature/nome-da-feature`)
8. Abra um Pull Request

Para Pull Requests, certifique-se de:
- Descrever claramente o propósito do PR
- Vincular a issues relacionadas
- Seguir o guia de estilo de código
- Incluir testes relevantes
- Atualizar a documentação conforme necessário

## Guia de Estilo

### Código Python

- Seguimos o [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilizamos [Black](https://github.com/psf/black) para formatação automática
- Docstrings no formato Google ou NumPy
- Tipo de anotações para parâmetros e retornos
- 100 caracteres por linha
- Utilize imports separados em blocos:
  ```python
  # Imports da biblioteca padrão
  import os
  import sys
  from datetime import datetime
  
  # Imports de bibliotecas de terceiros
  import fastapi
  import pydantic
  import sqlalchemy
  
  # Imports internos do projeto
  from app.core import config
  from app.models import User
  ```

#### Exemplo

```python
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


def create_user(
    db: Session, user_data: UserCreate, is_active: bool = True
) -> Optional[User]:
    """
    Cria um novo usuário no banco de dados.
    
    Args:
        db: Sessão do banco de dados
        user_data: Dados do usuário a ser criado
        is_active: Se o usuário deve ser ativo inicialmente
        
    Returns:
        Objeto User criado ou None se falhar
    """
    try:
        db_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            name=user_data.name,
            is_active=is_active
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        return None
```

### Código JavaScript/TypeScript

- Utilizamos [ESLint](https://eslint.org/) e [Prettier](https://prettier.io/)
- 2 espaços para indentação
- Ponto e vírgula no final das instruções
- 100 caracteres por linha
- Componentes React em arquivos separados com extensão .tsx (para TypeScript)
- Utilize desestruturação e métodos de array funcionais
- Prefira funções assíncronas/await a callbacks
- Importe os módulos em ordem alfabética

#### Exemplo

```typescript
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { Button, Card, Form } from '../components';
import { useAuth } from '../hooks/useAuth';
import { createScenario } from '../services/api';
import { ScenarioData, ScenarioResponse } from '../types';

interface ScenarioFormProps {
  initialData?: ScenarioData;
  onSuccess?: (data: ScenarioResponse) => void;
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({ 
  initialData, 
  onSuccess 
}) => {
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await createScenario({
        name,
        description,
        user_id: user.id
      });
      
      if (onSuccess) {
        onSuccess(result);
      } else {
        navigate(`/scenarios/${result.id}`);
      }
    } catch (error) {
      console.error('Error creating scenario:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <Form onSubmit={handleSubmit}>
        {/* Form fields */}
      </Form>
    </Card>
  );
};
```

### Commits

- Utilize mensagens claras e descritivas
- Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/)
- Formato: `tipo(escopo): mensagem`
- Tipos comuns: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Mantenha commits pequenos e focados em uma única mudança
- Escreva mensagens no tempo presente imperativo

Exemplos:
- `feat(auth): adicionar autenticação por dois fatores`
- `fix(api): corrigir erro de validação no endpoint de usuários`
- `docs(readme): atualizar instruções de instalação`
- `test(scenarios): adicionar testes para geração de cenários`

## Processo de Desenvolvimento

### Ambiente de Desenvolvimento

1. Clone o repositório
   ```bash
   git clone https://github.com/seu-usuario/habitus-forecast.git
   cd habitus-forecast
   ```

2. Configure o ambiente virtual Python
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Dependências de desenvolvimento
   ```

3. Configure as variáveis de ambiente
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações locais
   ```

4. Execute as migrações do banco de dados
   ```bash
   python -m app.db.init_db
   ```

5. Inicie o servidor de desenvolvimento
   ```bash
   uvicorn app.main:app --reload
   ```

6. Para desenvolvimento frontend, em outro terminal:
   ```bash
   cd client
   npm install
   npm start
   ```

### Fluxo de Trabalho Git

Seguimos um fluxo de trabalho baseado em [GitHub Flow](https://guides.github.com/introduction/flow/):

1. `main` - Branch principal, contém código em produção
2. `develop` - Branch de desenvolvimento, integrando novas features
3. `feature/*` - Branches para desenvolvimento de novas funcionalidades
4. `bugfix/*` - Branches para correção de bugs
5. `hotfix/*` - Branches para correções urgentes em produção

Processo:
1. Crie um branch a partir de `develop` para sua feature/bugfix
2. Faça commits de suas mudanças
3. Abra um PR para `develop`
4. Após revisão e aprovação, o PR é mesclado
5. Periodicamente, `develop` é mesclado em `main` para releases

### Ciclo de Desenvolvimento

1. Selecione uma tarefa ou issue para trabalhar
2. Crie um novo branch para implementar a solução
3. Implemente as mudanças necessárias
4. Escreva ou atualize testes
5. Execute os testes para garantir que passam
6. Faça commit das mudanças
7. Atualize a documentação conforme necessário
8. Abra um Pull Request
9. Responda aos comentários da revisão de código
10. Após aprovação, seu código será mesclado

## Testes

### Executando Testes

Para executar todos os testes:
```bash
pytest
```

Para executar testes específicos:
```bash
# Testes de uma módulo específico
pytest tests/api/test_users.py

# Testes com uma determinada marca
pytest -m "unit"

# Com cobertura de código
pytest --cov=app
```

### Cobertura de Testes

Buscamos manter uma cobertura de testes de pelo menos 80%. Para verificar a cobertura:
```bash
pytest --cov=app --cov-report=term-missing
```

Para gerar um relatório HTML detalhado:
```bash
pytest --cov=app --cov-report=html
# O relatório estará disponível em htmlcov/index.html
```

### Escrevendo Testes

- Utilize [pytest](https://docs.pytest.org/) para testes Python
- Organize testes em classes por funcionalidade
- Utilize fixtures para configuração comum
- Nome de funções de teste devem começar com `test_`
- Utilize marcadores para categorizar testes (`@pytest.mark.unit`, `@pytest.mark.integration`)
- Separe testes unitários de testes de integração

#### Exemplo de Teste

```python
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.user import User
from tests.utils.users import create_test_user

client = TestClient(app)

class TestUserEndpoints:
    @pytest.fixture(scope="function")
    def test_user(self, db_session):
        # Criar um usuário de teste
        user = create_test_user(db_session)
        return user
    
    def test_get_current_user(self, client, test_user, user_token):
        # Configurar
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Executar
        response = client.get("/api/v1/users/me", headers=headers)
        
        # Verificar
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == str(test_user.id)
```

## Documentação

- Mantenha a documentação atualizada com as mudanças de código
- Documente novas funcionalidades, parâmetros e retornos
- Atualize README.md e outros arquivos de documentação
- Para a API, mantenha as descrições do Swagger/OpenAPI atualizadas
- Adicione exemplos de uso sempre que possível

## Segurança

- Nunca comprometa credenciais ou dados sensíveis no código
- Reporte vulnerabilidades de segurança diretamente à equipe (não crie issues públicas)
- Siga as melhores práticas de segurança para autenticação e autorização
- Evite SQL injection mantendo o uso de ORM e parâmetros parametrizados
- Valide todas as entradas do usuário

## Contato

Se tiver dúvidas que não estão cobertas neste guia:
- Abra uma issue com a tag "question"
- Entre em contato com os mantenedores do projeto 