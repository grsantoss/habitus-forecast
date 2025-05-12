"""
Schemas para autenticação e gerenciamento de usuários.

Este módulo contém os schemas Pydantic utilizados nas operações de
autenticação, como login, registro, recuperação de senha, etc.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


class Token(BaseModel):
    """
    Modelo para resposta de token JWT.
    
    Attributes:
        access_token: Token JWT de acesso.
        token_type: Tipo do token (bearer).
        expires_at: Data e hora de expiração do token.
    """
    access_token: str
    token_type: str
    expires_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_at": "2023-05-15T11:00:00"
            }
        }


class LoginRequest(BaseModel):
    """
    Modelo para requisição de login.
    
    Attributes:
        email: Email do usuário.
        password: Senha do usuário.
    """
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@exemplo.com",
                "password": "senha_segura_123"
            }
        }


class RegisterRequest(BaseModel):
    """
    Modelo para requisição de registro de usuário.
    
    Attributes:
        name: Nome completo do usuário.
        email: Email do usuário.
        password: Senha do usuário.
        password_confirm: Confirmação da senha.
    """
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    
    @validator("name")
    def name_must_contain_space(cls, v):
        """Valida que o nome tem pelo menos um espaço (nome e sobrenome)."""
        if ' ' not in v:
            raise ValueError("O nome deve conter pelo menos nome e sobrenome")
        return v
    
    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        """Valida que as senhas coincidem."""
        if "password" in values and v != values["password"]:
            raise ValueError("As senhas não coincidem")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "João Silva",
                "email": "joao.silva@exemplo.com",
                "password": "senha_segura_123",
                "password_confirm": "senha_segura_123"
            }
        }


class PasswordResetRequest(BaseModel):
    """
    Modelo para requisição de redefinição de senha.
    
    Attributes:
        email: Email do usuário.
    """
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@exemplo.com"
            }
        }


class PasswordResetConfirmRequest(BaseModel):
    """
    Modelo para confirmação de redefinição de senha.
    
    Attributes:
        token: Token de redefinição de senha.
        new_password: Nova senha do usuário.
        new_password_confirm: Confirmação da nova senha.
    """
    token: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)
    
    @validator("new_password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        """Valida que as senhas coincidem."""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("As senhas não coincidem")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "abcdef123456789...",
                "new_password": "nova_senha_segura_123",
                "new_password_confirm": "nova_senha_segura_123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """
    Modelo para alteração de senha.
    
    Attributes:
        current_password: Senha atual do usuário.
        new_password: Nova senha do usuário.
        new_password_confirm: Confirmação da nova senha.
    """
    current_password: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)
    
    @validator("new_password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        """Valida que as senhas coincidem."""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("As senhas não coincidem")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "senha_atual_123",
                "new_password": "nova_senha_segura_123",
                "new_password_confirm": "nova_senha_segura_123"
            }
        }


class UpdateRoleRequest(BaseModel):
    """
    Modelo para alteração de papel de usuário.
    
    Attributes:
        role: Novo papel do usuário.
    """
    role: str = Field(..., pattern="^(user|admin)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "admin"
            }
        }


class UserResponse(BaseModel):
    """
    Modelo para resposta com dados do usuário.
    
    Attributes:
        id: ID do usuário.
        name: Nome completo do usuário.
        email: Email do usuário.
        role: Papel do usuário no sistema.
        is_active: Indica se o usuário está ativo.
        created_at: Data e hora de criação do usuário.
    """
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "name": "João Silva",
                "email": "joao.silva@exemplo.com",
                "role": "user",
                "is_active": True,
                "created_at": "2023-05-15T10:00:00"
            }
        }


class UserDetailResponse(UserResponse):
    """
    Modelo para resposta detalhada com dados do usuário.
    
    Attributes:
        updated_at: Data e hora da última atualização do usuário.
        last_login: Data e hora do último login.
        permissions: Lista de permissões do usuário.
    """
    updated_at: datetime
    last_login: Optional[datetime] = None
    permissions: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "name": "João Silva",
                "email": "joao.silva@exemplo.com",
                "role": "user",
                "is_active": True,
                "created_at": "2023-05-15T10:00:00",
                "updated_at": "2023-05-15T10:00:00",
                "last_login": "2023-05-15T15:30:00",
                "permissions": [
                    "read_own",
                    "write_own",
                    "delete_own",
                    "export_data"
                ]
            }
        }


class UserListResponse(BaseModel):
    """
    Modelo para resposta com lista de usuários.
    
    Attributes:
        total: Total de usuários.
        users: Lista de usuários.
    """
    total: int
    users: List[UserResponse] 