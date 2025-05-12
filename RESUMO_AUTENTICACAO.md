# Sistema de Autenticação do Habitus Forecast

## Arquivos Implementados

1. **utils/security.py**:
   - Funções para JWT e hashing de senhas
   - Dependências FastAPI para proteção de rotas
   - Sistema RBAC para verificação de permissões
   - Rate limiting para proteção contra brute force

2. **services/auth_service.py**:
   - Lógica de autenticação e operações de usuário
   - Funções para gerenciar papéis e permissões
   - Métodos para promoção/rebaixamento de usuários

3. **schemas/auth.py**:
   - Modelos Pydantic para validação de dados
   - Schemas para requisições e respostas da API

4. **api/endpoints/auth.py**:
   - Endpoints para registro, login, e gerenciamento de usuários
   - Documentação OpenAPI com exemplos
   - Proteção de rotas administrativas

## Funcionalidades Implementadas

### Autenticação
- Registro de usuários (papel USER por padrão)
- Login com JWT (incluindo papel e permissões no token)
- Refresh token
- Recuperação de senha
- Alteração de senha
- Obtenção do perfil do usuário atual

### Controle de Acesso (RBAC)
- Dois papéis: USER e ADMIN
- Lista de permissões específicas para cada papel
- Verificação de permissões em nível de função
- Proteção de rotas com base em papel ou permissão

### Gerenciamento de Usuários (Admin)
- Listagem de usuários com filtragem e paginação
- Visualização detalhada de usuário
- Alteração de papel (promoção/rebaixamento)
- Ativação/desativação de usuários

### Segurança
- Hashing de senhas com bcrypt
- Tokens JWT com algoritmo HS256
- Rate limiting para tentativas de login
- Proteção contra timing attacks nas verificações
- Validação robusta de dados com Pydantic

## Como Usar

### Registro e Login
```python
# Registro
response = await client.post(
    "/api/v1/auth/register",
    json={
        "name": "João Silva",
        "email": "joao.silva@exemplo.com",
        "password": "senha_segura_123",
        "password_confirm": "senha_segura_123"
    }
)

# Login
response = await client.post(
    "/api/v1/auth/login",
    json={
        "email": "joao.silva@exemplo.com",
        "password": "senha_segura_123"
    }
)
token = response.json()["access_token"]
```

### Uso do Token
```python
# Obter perfil do usuário atual
response = await client.get(
    "/api/v1/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)

# Alterar senha
response = await client.post(
    "/api/v1/auth/change-password",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "current_password": "senha_atual",
        "new_password": "nova_senha_123",
        "new_password_confirm": "nova_senha_123"
    }
)
```

### Operações Administrativas
```python
# Listar usuários (requer papel ADMIN)
response = await client.get(
    "/api/v1/auth/users",
    headers={"Authorization": f"Bearer {admin_token}"},
    params={"skip": 0, "limit": 50, "active_only": True}
)

# Alterar papel de um usuário (requer papel ADMIN)
response = await client.patch(
    f"/api/v1/auth/users/{user_id}/role",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={"role": "admin"}
)
```

## Modelo de Permissões

### USER
- read_own: Ler dados próprios
- write_own: Modificar dados próprios
- delete_own: Excluir dados próprios
- export_data: Exportar dados
- import_data: Importar dados
- generate_scenarios: Gerar cenários

### ADMIN
Todas as permissões de USER, mais:
- read_any: Ler dados de qualquer usuário
- write_any: Modificar dados de qualquer usuário
- delete_any: Excluir dados de qualquer usuário
- manage_users: Gerenciar usuários 