"""
Módulo de segurança para o Habitus Forecast.

Este módulo contém funções para gerenciamento de JWT, hashing de senhas,
e dependências FastAPI para proteção de rotas.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.models.user import UserInDB, Permission, UserRole, ROLE_PERMISSIONS
from app.db.mongodb import get_database

# Configuração do contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Classes para token JWT
class TokenData(BaseModel):
    """Dados contidos em um token JWT."""
    sub: str
    role: str
    permissions: List[str]
    exp: datetime

class Token(BaseModel):
    """Modelo para resposta de token."""
    access_token: str
    token_type: str
    expires_at: datetime


# Funções para hashing e verificação de senhas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto corresponde ao hash armazenado.
    
    Args:
        plain_password: Senha em texto plano.
        hashed_password: Hash da senha armazenada.
        
    Returns:
        bool: True se a senha corresponde ao hash, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro para a senha fornecida.
    
    Args:
        password: Senha em texto plano.
        
    Returns:
        str: Hash da senha.
    """
    return pwd_context.hash(password)


# Funções para criação e validação de tokens JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com os dados fornecidos.
    
    Args:
        data: Dados a serem codificados no token.
        expires_delta: Tempo de expiração do token.
        
    Returns:
        str: Token JWT.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_user_token(user_id: str, role: str, permissions: List[str]) -> Dict[str, Any]:
    """
    Cria um token JWT para um usuário específico.
    
    Args:
        user_id: ID do usuário.
        role: Papel do usuário.
        permissions: Lista de permissões do usuário.
        
    Returns:
        Dict[str, Any]: Dados do token.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.utcnow() + access_token_expires
    
    token_data = {
        "sub": user_id,
        "role": role,
        "permissions": permissions
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }


# Dependências FastAPI para proteção de rotas
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Obtém o usuário atual a partir do token JWT.
    
    Args:
        token: Token JWT de autenticação.
        
    Returns:
        UserInDB: Usuário autenticado.
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(
            sub=user_id,
            role=payload.get("role"),
            permissions=payload.get("permissions", []),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except (JWTError, ValidationError):
        raise credentials_exception
    
    db = await get_database()
    user = await db["users"].find_one({"_id": user_id})
    if user is None:
        raise credentials_exception
    
    return UserInDB(**user)


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Verifica se o usuário atual está ativo.
    
    Args:
        current_user: Usuário autenticado.
        
    Returns:
        UserInDB: Usuário ativo.
        
    Raises:
        HTTPException: Se o usuário estiver inativo.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


# Dependências para verificação de papéis e permissões
def require_role(allowed_roles: List[UserRole]):
    """
    Dependência para verificar se o usuário tem um dos papéis permitidos.
    
    Args:
        allowed_roles: Lista de papéis permitidos.
        
    Returns:
        Callable: Dependência FastAPI.
    """
    async def role_checker(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Requer um dos papéis: {allowed_roles}"
            )
        return current_user
    return role_checker


# Dependência para requerir papel de administrador
require_admin = require_role([UserRole.ADMIN])


def require_permission(required_permission: Permission):
    """
    Dependência para verificar se o usuário tem uma permissão específica.
    
    Args:
        required_permission: Permissão requerida.
        
    Returns:
        Callable: Dependência FastAPI.
    """
    async def permission_checker(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
        if not current_user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Requer: {required_permission}"
            )
        return current_user
    return permission_checker


# Utilidade para verificação de acesso a recursos
def check_resource_access(user: UserInDB, resource_owner_id: str) -> bool:
    """
    Verifica se um usuário pode acessar um recurso específico.
    
    Args:
        user: Usuário tentando acessar o recurso.
        resource_owner_id: ID do proprietário do recurso.
        
    Returns:
        bool: True se o acesso for permitido, False caso contrário.
    """
    # Administradores podem acessar qualquer recurso
    if user.is_admin():
        return True
    
    # Usuários regulares só podem acessar seus próprios recursos
    return str(user.id) == resource_owner_id


class RateLimiter:
    """
    Implementação simples de limitação de taxa baseada em memória.
    Em produção, seria recomendável usar Redis ou outro mecanismo distribuído.
    """
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        """
        Inicializa o limitador de taxa.
        
        Args:
            max_attempts: Número máximo de tentativas permitidas.
            window_seconds: Janela de tempo em segundos.
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = {}
        
    def is_rate_limited(self, key: str) -> bool:
        """
        Verifica se uma chave está limitada por taxa.
        
        Args:
            key: Chave a ser verificada (geralmente IP ou user_id).
            
        Returns:
            bool: True se a chave está limitada, False caso contrário.
        """
        now = datetime.utcnow()
        
        # Limpa tentativas antigas
        self._clean_old_attempts(now)
        
        # Verifica se a chave existe
        if key not in self.attempts:
            self.attempts[key] = []
        
        # Adiciona nova tentativa
        self.attempts[key].append(now)
        
        # Verifica se excedeu o limite
        return len(self.attempts[key]) > self.max_attempts
        
    def _clean_old_attempts(self, now: datetime):
        """
        Remove tentativas antigas que estão fora da janela de tempo.
        
        Args:
            now: Hora atual.
        """
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        for key in list(self.attempts.keys()):
            # Remove tentativas antigas
            self.attempts[key] = [t for t in self.attempts[key] if t >= cutoff]
            
            # Remove entradas vazias
            if not self.attempts[key]:
                del self.attempts[key]

# Instância global do limitador de taxa para login
login_rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)  # 5 tentativas a cada 5 minutos 