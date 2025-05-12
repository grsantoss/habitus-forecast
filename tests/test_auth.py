"""
Testes unitários para o sistema de autenticação.

Este módulo contém testes para validar o funcionamento dos serviços de autenticação,
verificando registro de usuários, login e validação de tokens JWT.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from bson import ObjectId

from app.services.auth_service import (
    authenticate_user,
    create_user,
    login,
    refresh_token,
    validate_reset_token,
    get_user_by_email,
    get_user_by_id
)
from app.utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_user_token,
    get_current_user,
    login_rate_limiter
)
from app.models.user import UserInDB, UserCreate, UserRole, Permission


@pytest.fixture
def user_create_data():
    """Fixture que cria dados para criação de usuário."""
    return UserCreate(
        name="João Silva",
        email="joao.silva@exemplo.com",
        password="senha_segura_123",
        role=UserRole.USER
    )


@pytest.fixture
def user_in_db():
    """Fixture que cria um usuário armazenado no banco de dados."""
    return UserInDB(
        id=ObjectId("60d6e04aec32c02a5a7c7d40"),
        name="João Silva",
        email="joao.silva@exemplo.com",
        password_hash=get_password_hash("senha_segura_123"),
        role=UserRole.USER,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def admin_user_in_db():
    """Fixture que cria um usuário administrador."""
    return UserInDB(
        id=ObjectId("60d6e04aec32c02a5a7c7d41"),
        name="Admin User",
        email="admin@exemplo.com",
        password_hash=get_password_hash("admin_senha_123"),
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def db_mock():
    """Fixture que cria um mock do banco de dados MongoDB."""
    db = MagicMock()
    # Configura o mock das coleções
    db.__getitem__ = MagicMock()
    db["users"] = MagicMock()
    db["users"].find_one = AsyncMock()
    db["users"].insert_one = AsyncMock()
    db["users"].update_one = AsyncMock()
    db["password_resets"] = MagicMock()
    db["password_resets"].find_one = AsyncMock()
    db["password_resets"].update_one = AsyncMock()
    db["password_resets"].delete_one = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_user(db_mock, user_create_data):
    """Testa a criação de um novo usuário."""
    # Configura o mock para retornar None (usuário não existe)
    db_mock["users"].find_one.return_value = None
    
    # Configura o resultado da inserção
    db_mock["users"].insert_one.return_value = MagicMock(inserted_id=ObjectId("60d6e04aec32c02a5a7c7d40"))
    
    # Executa a função
    user = await create_user(db_mock, user_create_data)
    
    # Verifica se o usuário foi criado corretamente
    assert user.name == user_create_data.name
    assert user.email == user_create_data.email
    assert user.role == UserRole.USER
    assert user.is_active == True
    
    # Verifica se a senha foi hashada
    assert user.password_hash != user_create_data.password
    assert verify_password(user_create_data.password, user.password_hash)
    
    # Verifica se a função insert_one foi chamada
    db_mock["users"].insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_email_already_exists(db_mock, user_create_data, user_in_db):
    """Testa a tentativa de criar um usuário com email já cadastrado."""
    # Configura o mock para retornar um usuário existente
    db_mock["users"].find_one.return_value = user_in_db.model_dump(by_alias=True)
    
    # Verifica se a exceção é lançada
    with pytest.raises(HTTPException) as excinfo:
        await create_user(db_mock, user_create_data)
    
    # Verifica a mensagem e o status code
    assert excinfo.value.status_code == 400
    assert "Email já está em uso" in excinfo.value.detail
    
    # Verifica se a função insert_one não foi chamada
    db_mock["users"].insert_one.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_user_success(db_mock, user_in_db):
    """Testa a autenticação de um usuário com credenciais corretas."""
    # Configura o mock para retornar o usuário
    db_mock["users"].find_one.return_value = user_in_db.model_dump(by_alias=True)
    
    # Executa a função
    authenticated_user = await authenticate_user(
        db=db_mock,
        email=user_in_db.email,
        password="senha_segura_123"
    )
    
    # Verifica se o usuário foi autenticado corretamente
    assert authenticated_user is not None
    assert authenticated_user.email == user_in_db.email
    assert authenticated_user.id == user_in_db.id


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_mock, user_in_db):
    """Testa a autenticação de um usuário com senha incorreta."""
    # Configura o mock para retornar o usuário
    db_mock["users"].find_one.return_value = user_in_db.model_dump(by_alias=True)
    
    # Executa a função
    authenticated_user = await authenticate_user(
        db=db_mock,
        email=user_in_db.email,
        password="senha_incorreta"
    )
    
    # Verifica se a autenticação falhou
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent(db_mock):
    """Testa a autenticação de um usuário inexistente."""
    # Configura o mock para retornar None (usuário não existe)
    db_mock["users"].find_one.return_value = None
    
    # Executa a função
    authenticated_user = await authenticate_user(
        db=db_mock,
        email="naoexiste@exemplo.com",
        password="qualquer_senha"
    )
    
    # Verifica se a autenticação falhou
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_login_success(db_mock, user_in_db):
    """Testa o login de um usuário com credenciais corretas."""
    # Configura o mock para retornar o usuário
    db_mock["users"].find_one.return_value = user_in_db.model_dump(by_alias=True)
    
    # Mock para o rate limiter
    with patch('app.services.auth_service.login_rate_limiter') as mock_rate_limiter:
        mock_rate_limiter.is_rate_limited.return_value = False
        
        # Executa a função
        token_data = await login(
            db=db_mock,
            email=user_in_db.email,
            password="senha_segura_123",
            client_ip="127.0.0.1"
        )
        
        # Verifica se o token foi gerado corretamente
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert "expires_at" in token_data
        
        # Verifica se o token contém os dados corretos do usuário
        token = token_data["access_token"]
        payload = jwt.decode(token, "secret_key_for_testing", algorithms=["HS256"])
        assert payload["sub"] == str(user_in_db.id)
        assert payload["role"] == user_in_db.role.value
        
        # Verifica se o último login foi atualizado
        db_mock["users"].update_one.assert_called_once()


@pytest.mark.asyncio
async def test_login_wrong_credentials(db_mock, user_in_db):
    """Testa o login de um usuário com credenciais incorretas."""
    # Configura o mock para retornar o usuário
    db_mock["users"].find_one.return_value = user_in_db.model_dump(by_alias=True)
    
    # Mock para o rate limiter
    with patch('app.services.auth_service.login_rate_limiter') as mock_rate_limiter:
        mock_rate_limiter.is_rate_limited.return_value = False
        
        # Verifica se a exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            await login(
                db=db_mock,
                email=user_in_db.email,
                password="senha_incorreta",
                client_ip="127.0.0.1"
            )
        
        # Verifica a mensagem e o status code
        assert excinfo.value.status_code == 401
        assert "Email ou senha incorretos" in excinfo.value.detail


@pytest.mark.asyncio
async def test_login_rate_limited(db_mock):
    """Testa o login quando o usuário excedeu o limite de tentativas."""
    # Mock para o rate limiter
    with patch('app.services.auth_service.login_rate_limiter') as mock_rate_limiter:
        mock_rate_limiter.is_rate_limited.return_value = True
        
        # Verifica se a exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            await login(
                db=db_mock,
                email="qualquer@exemplo.com",
                password="qualquer_senha",
                client_ip="127.0.0.1"
            )
        
        # Verifica a mensagem e o status code
        assert excinfo.value.status_code == 429
        assert "Muitas tentativas de login" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_current_user_valid_token(db_mock, user_in_db):
    """Testa a obtenção do usuário atual a partir de um token válido."""
    # Cria um token válido
    payload = {
        "sub": str(user_in_db.id),
        "role": user_in_db.role.value,
        "permissions": ["read_own", "write_own"],
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, "secret_key_for_testing", algorithm="HS256")
    
    # Configura o mock para retornar o usuário
    db_mock["users"].find_one.return_value = user_in_db.model_dump(by_alias=True)
    
    # Mock para a função de decodificação do token
    with patch('app.utils.security.jwt.decode') as mock_decode:
        mock_decode.return_value = payload
        
        # Mock para a função get_database
        with patch('app.utils.security.get_database', return_value=db_mock):
            # Executa a função
            current_user = await get_current_user(token)
            
            # Verifica se o usuário foi obtido corretamente
            assert current_user is not None
            assert current_user.id == user_in_db.id
            assert current_user.email == user_in_db.email
            assert current_user.role == user_in_db.role


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_mock):
    """Testa a obtenção do usuário atual a partir de um token inválido."""
    # Cria um token inválido
    token = "token_invalido"
    
    # Mock para a função de decodificação do token
    with patch('app.utils.security.jwt.decode') as mock_decode:
        mock_decode.side_effect = jwt.PyJWTError("Token inválido")
        
        # Verifica se a exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(token)
        
        # Verifica a mensagem e o status code
        assert excinfo.value.status_code == 401
        assert "Credenciais inválidas" in excinfo.value.detail


@pytest.mark.asyncio
async def test_refresh_token(db_mock, user_in_db):
    """Testa a atualização do token JWT de um usuário."""
    # Configura o mock para retornar o usuário
    db_mock["users"].find_one.return_value = user_in_db.model_dump(by_alias=True)
    
    # Executa a função
    token_data = await refresh_token(db_mock, str(user_in_db.id))
    
    # Verifica se o token foi gerado corretamente
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "expires_at" in token_data
    
    # Verifica se o token contém os dados corretos do usuário
    token = token_data["access_token"]
    payload = jwt.decode(token, "secret_key_for_testing", algorithms=["HS256"])
    assert payload["sub"] == str(user_in_db.id)
    assert payload["role"] == user_in_db.role.value


@pytest.mark.asyncio
async def test_validate_reset_token_valid(db_mock):
    """Testa a validação de um token de redefinição de senha válido."""
    # Configura os dados do token
    user_id = "60d6e04aec32c02a5a7c7d40"
    token = "token_valido_123"
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    # Configura o mock para retornar os dados do token
    db_mock["password_resets"].find_one.return_value = {
        "user_id": ObjectId(user_id),
        "token": token,
        "expires_at": expiration
    }
    
    # Executa a função
    result = await validate_reset_token(db_mock, token)
    
    # Verifica o resultado
    assert result == user_id


@pytest.mark.asyncio
async def test_validate_reset_token_invalid(db_mock):
    """Testa a validação de um token de redefinição de senha inválido."""
    # Configura o mock para retornar None (token inválido)
    db_mock["password_resets"].find_one.return_value = None
    
    # Executa a função
    result = await validate_reset_token(db_mock, "token_invalido")
    
    # Verifica o resultado
    assert result is None


# Testes para verificar a funcionalidade básica do JWT
def test_create_access_token():
    """Testa a criação de um token JWT."""
    # Dados para o token
    data = {"sub": "usuario_id", "role": "user"}
    expires_delta = timedelta(minutes=30)
    
    # Cria o token
    token = create_access_token(data, expires_delta)
    
    # Verifica se o token foi criado e é uma string
    assert token is not None
    assert isinstance(token, str)
    
    # Decodifica o token e verifica os dados
    payload = jwt.decode(token, "secret_key_for_testing", algorithms=["HS256"])
    assert payload["sub"] == "usuario_id"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_create_user_token():
    """Testa a criação de um token de usuário com dados específicos."""
    # Cria o token
    token_data = create_user_token(
        user_id="usuario_id",
        role="admin",
        permissions=["read_any", "write_any"]
    )
    
    # Verifica se o token foi criado corretamente
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "expires_at" in token_data
    
    # Decodifica o token e verifica os dados
    token = token_data["access_token"]
    payload = jwt.decode(token, "secret_key_for_testing", algorithms=["HS256"])
    assert payload["sub"] == "usuario_id"
    assert payload["role"] == "admin"
    assert "read_any" in payload["permissions"]
    assert "write_any" in payload["permissions"]


def test_password_hashing():
    """Testa a funcionalidade de hashing e verificação de senha."""
    # Hash da senha
    password = "senha_segura_123"
    hashed = get_password_hash(password)
    
    # Verifica se o hash foi criado
    assert hashed is not None
    assert hashed != password
    
    # Verifica se a validação funciona
    assert verify_password(password, hashed) == True
    assert verify_password("senha_errada", hashed) == False 