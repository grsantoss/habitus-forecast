"""
Serviço de autenticação para o Habitus Forecast.

Este módulo contém a lógica de negócio para autenticação e autorização,
incluindo registro, login, gerenciamento de papéis e permissões.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
import uuid
import secrets
import string

from fastapi import HTTPException, status, Request, Depends
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult
from pydantic import EmailStr

from app.db.mongodb import get_database
from app.models.user import UserInDB, UserCreate, UserRole, Permission, ROLE_PERMISSIONS
from app.utils.security import (
    get_password_hash, 
    verify_password, 
    create_user_token,
    login_rate_limiter
)
from app.core.config import settings


async def get_user_by_email(db: Database, email: str) -> Optional[UserInDB]:
    """
    Busca um usuário pelo email.
    
    Args:
        db: Instância do banco de dados.
        email: Email do usuário.
        
    Returns:
        Optional[UserInDB]: Usuário encontrado ou None.
    """
    user_data = await db["users"].find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None


async def get_user_by_id(db: Database, user_id: str) -> Optional[UserInDB]:
    """
    Busca um usuário pelo ID.
    
    Args:
        db: Instância do banco de dados.
        user_id: ID do usuário.
        
    Returns:
        Optional[UserInDB]: Usuário encontrado ou None.
    """
    try:
        object_id = ObjectId(user_id)
        user_data = await db["users"].find_one({"_id": object_id})
        if user_data:
            return UserInDB(**user_data)
    except:
        pass
    return None


async def authenticate_user(db: Database, email: str, password: str) -> Optional[UserInDB]:
    """
    Autentica um usuário pelo email e senha.
    
    Args:
        db: Instância do banco de dados.
        email: Email do usuário.
        password: Senha do usuário.
        
    Returns:
        Optional[UserInDB]: Usuário autenticado ou None.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def create_user(db: Database, user_data: UserCreate) -> UserInDB:
    """
    Cria um novo usuário.
    
    Args:
        db: Instância do banco de dados.
        user_data: Dados do usuário a ser criado.
        
    Returns:
        UserInDB: Usuário criado.
        
    Raises:
        HTTPException: Se o email já estiver em uso.
    """
    # Verifica se o email já está em uso
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    # Criar novo usuário com hash da senha
    user_in_db = UserInDB(
        **user_data.model_dump(exclude={"password"}),
        password_hash=get_password_hash(user_data.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Inserir no banco de dados
    result = await db["users"].insert_one(user_in_db.model_dump(by_alias=True))
    
    # Atualiza o ID
    user_in_db.id = result.inserted_id
    
    return user_in_db


async def login(db: Database, email: str, password: str, client_ip: str) -> Dict[str, Any]:
    """
    Realiza o login de um usuário e gera um token JWT.
    
    Args:
        db: Instância do banco de dados.
        email: Email do usuário.
        password: Senha do usuário.
        client_ip: Endereço IP do cliente (para rate limiting).
        
    Returns:
        Dict[str, Any]: Dados do token JWT.
        
    Raises:
        HTTPException: Se as credenciais estiverem incorretas ou houver muitas tentativas.
    """
    # Verifica rate limiting
    if login_rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login. Tente novamente mais tarde."
        )
    
    # Autentica o usuário
    user = await authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Atualiza a última data de login
    await db["users"].update_one(
        {"_id": user.id},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Cria o token JWT
    token_data = create_user_token(
        user_id=str(user.id),
        role=user.role.value,
        permissions=[p.value for p in ROLE_PERMISSIONS.get(user.role, [])]
    )
    
    return token_data


async def refresh_token(db: Database, user_id: str) -> Dict[str, Any]:
    """
    Atualiza o token JWT de um usuário.
    
    Args:
        db: Instância do banco de dados.
        user_id: ID do usuário.
        
    Returns:
        Dict[str, Any]: Dados do novo token JWT.
        
    Raises:
        HTTPException: Se o usuário não for encontrado ou estiver inativo.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Cria o token JWT
    token_data = create_user_token(
        user_id=str(user.id),
        role=user.role.value,
        permissions=[p.value for p in ROLE_PERMISSIONS.get(user.role, [])]
    )
    
    return token_data


async def update_user_role(
    db: Database, 
    user_id: str, 
    new_role: UserRole,
    admin_user_id: str
) -> UserInDB:
    """
    Atualiza o papel de um usuário.
    
    Args:
        db: Instância do banco de dados.
        user_id: ID do usuário a ser atualizado.
        new_role: Novo papel para o usuário.
        admin_user_id: ID do administrador realizando a alteração.
        
    Returns:
        UserInDB: Usuário atualizado.
        
    Raises:
        HTTPException: Se o usuário não for encontrado ou a operação falhar.
    """
    # Verifica se o admin existe
    admin = await get_user_by_id(db, admin_user_id)
    if not admin or not admin.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem alterar papéis de usuários"
        )
    
    # Verifica se o usuário existe
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualiza o papel do usuário
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "role": new_role.value,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível atualizar o papel do usuário"
        )
    
    # Retorna o usuário atualizado
    updated_user = await get_user_by_id(db, user_id)
    return updated_user


async def start_password_reset(db: Database, email: str) -> Tuple[bool, str]:
    """
    Inicia o processo de recuperação de senha.
    
    Args:
        db: Instância do banco de dados.
        email: Email do usuário.
        
    Returns:
        Tuple[bool, str]: Tupla com indicador de sucesso e token de reset.
    """
    user = await get_user_by_email(db, email)
    if not user:
        # Não revelamos se o email existe ou não por segurança
        return False, ""
    
    # Gera um token aleatório
    reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    # Define a expiração (24 horas)
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    # Salva o token no banco
    await db["password_resets"].update_one(
        {"user_id": user.id},
        {
            "$set": {
                "token": reset_token,
                "expires_at": expiration,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Em produção, aqui enviaríamos um email com o link de recuperação
    # Para simplificar, apenas retornamos o token
    return True, reset_token


async def validate_reset_token(db: Database, token: str) -> Optional[str]:
    """
    Valida um token de recuperação de senha.
    
    Args:
        db: Instância do banco de dados.
        token: Token de recuperação.
        
    Returns:
        Optional[str]: ID do usuário se o token for válido, None caso contrário.
    """
    reset_data = await db["password_resets"].find_one({
        "token": token,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if not reset_data:
        return None
    
    return str(reset_data["user_id"])


async def reset_password(db: Database, token: str, new_password: str) -> bool:
    """
    Redefine a senha de um usuário usando um token de recuperação.
    
    Args:
        db: Instância do banco de dados.
        token: Token de recuperação.
        new_password: Nova senha para o usuário.
        
    Returns:
        bool: True se a senha foi redefinida, False caso contrário.
        
    Raises:
        HTTPException: Se o token for inválido ou expirado.
    """
    user_id = await validate_reset_token(db, token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )
    
    # Atualiza a senha
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "password_hash": get_password_hash(new_password),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Remove o token usado
    await db["password_resets"].delete_one({"token": token})
    
    return result.modified_count > 0


async def update_user_password(
    db: Database,
    user_id: str,
    current_password: str,
    new_password: str
) -> bool:
    """
    Atualiza a senha de um usuário.
    
    Args:
        db: Instância do banco de dados.
        user_id: ID do usuário.
        current_password: Senha atual.
        new_password: Nova senha.
        
    Returns:
        bool: True se a senha foi atualizada, False caso contrário.
        
    Raises:
        HTTPException: Se a senha atual for incorreta.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica a senha atual
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Atualiza a senha
    result = await db["users"].update_one(
        {"_id": user.id},
        {
            "$set": {
                "password_hash": get_password_hash(new_password),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return result.modified_count > 0


async def get_users_list(
    db: Database,
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
    role_filter: Optional[UserRole] = None
) -> List[UserInDB]:
    """
    Obtém uma lista de usuários com filtros.
    
    Args:
        db: Instância do banco de dados.
        skip: Quantidade de registros a pular.
        limit: Quantidade máxima de registros a retornar.
        active_only: Se True, retorna apenas usuários ativos.
        role_filter: Filtrar por papel específico.
        
    Returns:
        List[UserInDB]: Lista de usuários.
    """
    query = {}
    
    if active_only:
        query["is_active"] = True
    
    if role_filter:
        query["role"] = role_filter.value
    
    users_data = await db["users"].find(query).skip(skip).limit(limit).to_list(length=limit)
    
    return [UserInDB(**user_data) for user_data in users_data]


async def update_user_active_status(
    db: Database,
    user_id: str,
    is_active: bool,
    admin_user_id: str
) -> UserInDB:
    """
    Ativa ou desativa um usuário.
    
    Args:
        db: Instância do banco de dados.
        user_id: ID do usuário a ser atualizado.
        is_active: Novo status de ativação.
        admin_user_id: ID do administrador realizando a alteração.
        
    Returns:
        UserInDB: Usuário atualizado.
        
    Raises:
        HTTPException: Se o usuário não for encontrado ou a operação falhar.
    """
    # Verifica se o admin existe
    admin = await get_user_by_id(db, admin_user_id)
    if not admin or not admin.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem alterar status de usuários"
        )
    
    # Verifica se o usuário existe
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Impede que um admin desative a si mesmo
    if str(user.id) == admin_user_id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar sua própria conta"
        )
    
    # Atualiza o status do usuário
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_active": is_active,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível atualizar o status do usuário"
        )
    
    # Retorna o usuário atualizado
    updated_user = await get_user_by_id(db, user_id)
    return updated_user 