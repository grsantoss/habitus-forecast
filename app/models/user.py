"""
Módulo de modelos de usuário para o Habitus Forecast.

Este módulo contém as definições dos modelos de usuário, incluindo
roles, permissões e métodos auxiliares para validação de acesso.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from bson import ObjectId
from pymongo import IndexModel, ASCENDING

# Classes auxiliares para trabalhar com MongoDB e FastAPI
class PyObjectId(ObjectId):
    """Classe customizada para converter ObjectId para string e vice-versa."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("ID inválido")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {"type": "string"}


class UserRole(str, Enum):
    """Enumeração de papéis de usuário no sistema."""
    USER = "user"
    ADMIN = "admin"


class Permission(str, Enum):
    """Enumeração de permissões no sistema."""
    READ_OWN = "read_own"
    WRITE_OWN = "write_own"
    DELETE_OWN = "delete_own"
    READ_ANY = "read_any"
    WRITE_ANY = "write_any" 
    DELETE_ANY = "delete_any"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    GENERATE_SCENARIOS = "generate_scenarios"
    MANAGE_USERS = "manage_users"


# Mapeamento de papel para permissões
ROLE_PERMISSIONS = {
    UserRole.USER: [
        Permission.READ_OWN,
        Permission.WRITE_OWN,
        Permission.DELETE_OWN,
        Permission.EXPORT_DATA,
        Permission.IMPORT_DATA,
        Permission.GENERATE_SCENARIOS
    ],
    UserRole.ADMIN: [
        Permission.READ_OWN,
        Permission.WRITE_OWN,
        Permission.DELETE_OWN,
        Permission.READ_ANY,
        Permission.WRITE_ANY,
        Permission.DELETE_ANY,
        Permission.EXPORT_DATA,
        Permission.IMPORT_DATA,
        Permission.GENERATE_SCENARIOS,
        Permission.MANAGE_USERS
    ]
}


class UserBase(BaseModel):
    """
    Modelo base para usuários do sistema.
    
    Attributes:
        name: Nome completo do usuário.
        email: Email do usuário (usado para login).
        role: Papel do usuário no sistema.
        is_active: Indica se o usuário está ativo.
    """
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    
    @validator('name')
    def name_must_contain_space(cls, v):
        """Valida que o nome tem pelo menos um espaço (nome e sobrenome)."""
        if ' ' not in v:
            raise ValueError('O nome deve conter pelo menos nome e sobrenome')
        return v


class UserCreate(UserBase):
    """
    Modelo para criação de usuários.
    
    Attributes:
        password: Senha para o usuário (será hash).
    """
    password: str = Field(..., min_length=8)


class UserInDB(UserBase):
    """
    Modelo de usuário como armazenado no banco de dados.
    
    Attributes:
        id: ID único do usuário.
        password_hash: Hash da senha do usuário.
        created_at: Data e hora de criação do usuário.
        updated_at: Data e hora da última atualização do usuário.
        last_login: Data e hora do último login.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "name": "João Silva",
                "email": "joao.silva@exemplo.com",
                "role": "user",
                "is_active": True,
                "created_at": "2023-05-15T10:00:00",
                "updated_at": "2023-05-15T10:00:00",
                "last_login": "2023-05-15T15:30:00"
            }
        }
    
    def has_permission(self, permission: Permission) -> bool:
        """
        Verifica se o usuário tem uma permissão específica.
        
        Args:
            permission: A permissão a ser verificada.
            
        Returns:
            True se o usuário tem a permissão, False caso contrário.
        """
        if not self.is_active:
            return False
        
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def is_admin(self) -> bool:
        """
        Verifica se o usuário tem papel de administrador.
        
        Returns:
            True se o usuário é admin, False caso contrário.
        """
        return self.role == UserRole.ADMIN
    
    def is_regular_user(self) -> bool:
        """
        Verifica se o usuário tem papel regular (não admin).
        
        Returns:
            True se o usuário é regular, False caso contrário.
        """
        return self.role == UserRole.USER
    
    def can_access_resource(self, resource_owner_id: ObjectId) -> bool:
        """
        Verifica se o usuário pode acessar um recurso específico.
        
        Args:
            resource_owner_id: ID do proprietário do recurso.
            
        Returns:
            True se o usuário pode acessar o recurso, False caso contrário.
        """
        # Administradores podem acessar qualquer recurso
        if self.is_admin():
            return True
        
        # Usuários regulares só podem acessar seus próprios recursos
        return str(self.id) == str(resource_owner_id)


class UserResponse(BaseModel):
    """
    Modelo para resposta da API com informações do usuário.
    
    Attributes:
        id: ID único do usuário.
        name: Nome completo do usuário.
        email: Email do usuário.
        role: Papel do usuário no sistema.
        is_active: Indica se o usuário está ativo.
        created_at: Data e hora de criação do usuário.
    """
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        populate_by_name = True
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


class UserResponseAdmin(UserResponse):
    """
    Modelo para resposta da API com informações completas do usuário (admin).
    
    Attributes:
        updated_at: Data e hora da última atualização do usuário.
        last_login: Data e hora do último login.
    """
    updated_at: datetime
    last_login: Optional[datetime]
    
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
                "last_login": "2023-05-15T15:30:00"
            }
        }


# Configuração para índices no MongoDB
user_indexes = [
    IndexModel([("email", ASCENDING)], unique=True),
    IndexModel([("created_at", ASCENDING)])
] 