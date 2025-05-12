"""
Módulo de segurança para o Habitus Forecast.

Este módulo contém funções para gerenciamento de senhas, tokens
e autenticação de usuários.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from jose import jwt
from passlib.context import CryptContext
from bson import ObjectId

from app.core.config import settings
from app.models.user import UserInDB, UserRole

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.models.user import User
from app.services.user_service import UserService


# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Algoritmo utilizado para JWT
ALGORITHM = "HS256"

# Configuração de autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def create_access_token(subject: Union[str, ObjectId], role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso.
    
    Args:
        subject: ID do usuário ou assunto do token.
        role: Papel do usuário no sistema.
        expires_delta: Tempo opcional de validade do token.
        
    Returns:
        Token JWT codificado.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto simples corresponde ao hash armazenado.
    
    Args:
        plain_password: Senha em texto simples.
        hashed_password: Hash da senha armazenada.
        
    Returns:
        True se a senha corresponder, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro para uma senha.
    
    Args:
        password: Senha em texto simples.
        
    Returns:
        Hash da senha.
    """
    return pwd_context.hash(password)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica um token JWT e retorna suas informações.
    
    Args:
        token: Token JWT.
        
    Returns:
        Dicionário com as informações do token.
        
    Raises:
        JWTError: Se o token for inválido ou estiver expirado.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def create_refresh_token(data: dict) -> str:
    """
    Cria um token JWT de atualização com validade prolongada.
    
    Args:
        data: Dados a serem codificados no token
        
    Returns:
        Token JWT de atualização codificado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(lambda: UserService())
) -> User:
    """
    Obtém o usuário atual a partir do token JWT.
    
    Args:
        token: Token JWT de acesso
        user_service: Serviço de usuário
        
    Returns:
        Objeto User correspondente ao token
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o token JWT
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Extrai o ID do usuário do token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Verificar se o token não é um refresh token
        token_type = payload.get("token_type")
        if token_type == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não é possível usar refresh token para autenticação",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError:
        raise credentials_exception
    
    # Busca o usuário no banco de dados
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica se o usuário atual está ativo.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Usuário ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    return current_user


async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Verifica se o usuário atual tem papel de administrador.
    Use esta dependência para proteger rotas administrativas.
    
    Args:
        current_user: Usuário atual autenticado e ativo
        
    Returns:
        Usuário administrador
        
    Raises:
        HTTPException: Se o usuário não for administrador
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Função de administrador necessária para esta operação."
        )
    
    return current_user 