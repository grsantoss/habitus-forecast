"""
Endpoints de autenticação e gerenciamento de usuários para o Habitus Forecast.

Este módulo contém os endpoints para registro, login, refresh token,
recuperação de senha e gerenciamento de usuários e papéis.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import (
    Token,
    LoginRequest,
    RegisterRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ChangePasswordRequest,
    UpdateRoleRequest,
    UserResponse,
    UserDetailResponse,
    UserListResponse
)
from app.models.user import UserCreate, UserRole, Permission, ROLE_PERMISSIONS
from app.services.auth_service import (
    create_user,
    login,
    refresh_token,
    start_password_reset,
    reset_password,
    update_user_password,
    get_user_by_id,
    get_users_list,
    update_user_role,
    update_user_active_status
)
from app.db.mongodb import get_database
from app.utils.security import (
    get_current_active_user, 
    require_admin,
    require_permission
)
from app.models.user import UserInDB

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    user_data: RegisterRequest = Body(...),
    db = Depends(get_database)
):
    """
    Registra um novo usuário no sistema.
    
    Por padrão, usuários registrados recebem o papel USER.
    
    - **name**: Nome completo do usuário (nome e sobrenome)
    - **email**: Email do usuário (deve ser único)
    - **password**: Senha (mínimo 8 caracteres)
    - **password_confirm**: Confirmação da senha
    
    Retorna os dados do usuário criado.
    """
    # Converte o schema de requisição para o modelo de criação de usuário
    user_create = UserCreate(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        role=UserRole.USER
    )
    
    # Cria o usuário no banco de dados
    user = await create_user(db, user_create)
    
    # Converte o modelo de usuário para o schema de resposta
    return {
        "_id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.post("/login", response_model=Token)
async def login_user(
    request: Request,
    login_data: LoginRequest = Body(...),
    db = Depends(get_database)
):
    """
    Realiza o login de um usuário e retorna um token JWT.
    
    - **email**: Email do usuário
    - **password**: Senha do usuário
    
    Retorna um token JWT com papel e permissões do usuário.
    """
    # Obtém o endereço IP do cliente para rate limiting
    client_ip = request.client.host
    
    # Realiza o login e obtém o token
    token_data = await login(
        db=db,
        email=login_data.email,
        password=login_data.password,
        client_ip=client_ip
    )
    
    return token_data


@router.post("/refresh", response_model=Token)
async def refresh_user_token(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Atualiza o token JWT de um usuário autenticado.
    
    Requer autenticação via token JWT válido.
    
    Retorna um novo token JWT com validade estendida.
    """
    # Atualiza o token para o usuário atual
    token_data = await refresh_token(db, str(current_user.id))
    
    return token_data


@router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    request: PasswordResetRequest = Body(...),
    db = Depends(get_database)
):
    """
    Inicia o processo de recuperação de senha.
    
    - **email**: Email do usuário
    
    Em produção, enviaria um email com link para recuperação.
    Aqui, retorna o token para fins de teste.
    """
    # Inicia o processo de recuperação e obtém o token
    success, reset_token = await start_password_reset(db, request.email)
    
    # Em produção, enviaria um email com o link de recuperação
    # Para fins de API, retornamos o token apenas para testes
    return {
        "message": "Se o email estiver cadastrado, você receberá instruções para redefinir sua senha.",
        "debug_token": reset_token if success else "Email não encontrado"
    }


@router.post("/password-reset-confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    reset_data: PasswordResetConfirmRequest = Body(...),
    db = Depends(get_database)
):
    """
    Confirma a redefinição de senha usando um token.
    
    - **token**: Token de redefinição recebido por email
    - **new_password**: Nova senha (mínimo 8 caracteres)
    - **new_password_confirm**: Confirmação da nova senha
    
    Retorna uma confirmação da alteração.
    """
    # Redefine a senha usando o token
    success = await reset_password(
        db=db,
        token=reset_data.token,
        new_password=reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível redefinir a senha"
        )
    
    return {"message": "Senha redefinida com sucesso"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest = Body(...),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Altera a senha do usuário atual.
    
    Requer autenticação via token JWT válido.
    
    - **current_password**: Senha atual
    - **new_password**: Nova senha (mínimo 8 caracteres)
    - **new_password_confirm**: Confirmação da nova senha
    
    Retorna uma confirmação da alteração.
    """
    # Atualiza a senha do usuário atual
    success = await update_user_password(
        db=db,
        user_id=str(current_user.id),
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível alterar a senha"
        )
    
    return {"message": "Senha alterada com sucesso"}


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Obtém o perfil do usuário atual.
    
    Requer autenticação via token JWT válido.
    
    Retorna os dados completos do usuário, incluindo papel e permissões.
    """
    # Obtém as permissões do usuário
    permissions = [p.value for p in ROLE_PERMISSIONS.get(current_user.role, [])]
    
    # Retorna os dados do usuário atual
    return {
        "_id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "last_login": current_user.last_login,
        "permissions": permissions
    }


# Endpoints administrativos (requerem papel ADMIN)

@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
    role: str = None,
    current_user: UserInDB = Depends(require_admin),
    db = Depends(get_database)
):
    """
    Lista usuários do sistema.
    
    Requer autenticação via token JWT válido e papel ADMIN.
    
    - **skip**: Quantidade de registros a pular (paginação)
    - **limit**: Quantidade máxima de registros a retornar
    - **active_only**: Se True, retorna apenas usuários ativos
    - **role**: Filtrar por papel específico (user ou admin)
    
    Retorna uma lista paginada de usuários.
    """
    # Converte o papel para o enum se fornecido
    role_filter = None
    if role:
        try:
            role_filter = UserRole(role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Papel inválido: {role}. Opções válidas: user, admin"
            )
    
    # Obtém a lista de usuários
    users = await get_users_list(
        db=db,
        skip=skip,
        limit=limit,
        active_only=active_only,
        role_filter=role_filter
    )
    
    # Converte a lista para o formato de resposta
    user_list = [
        {
            "_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]
    
    return {
        "total": len(user_list),
        "users": user_list
    }


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_profile(
    user_id: str,
    current_user: UserInDB = Depends(require_admin),
    db = Depends(get_database)
):
    """
    Obtém o perfil detalhado de um usuário.
    
    Requer autenticação via token JWT válido e papel ADMIN.
    
    - **user_id**: ID do usuário
    
    Retorna os dados completos do usuário, incluindo papel e permissões.
    """
    # Obtém o usuário pelo ID
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Obtém as permissões do usuário
    permissions = [p.value for p in ROLE_PERMISSIONS.get(user.role, [])]
    
    # Retorna os dados do usuário
    return {
        "_id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "permissions": permissions
    }


@router.patch("/users/{user_id}/role", response_model=UserDetailResponse)
async def update_user_role_endpoint(
    user_id: str,
    role_data: UpdateRoleRequest = Body(...),
    current_user: UserInDB = Depends(require_admin),
    db = Depends(get_database)
):
    """
    Atualiza o papel de um usuário.
    
    Requer autenticação via token JWT válido e papel ADMIN.
    
    - **user_id**: ID do usuário
    - **role**: Novo papel (user ou admin)
    
    Retorna os dados atualizados do usuário.
    """
    # Converte o papel para o enum
    try:
        new_role = UserRole(role_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Papel inválido: {role_data.role}. Opções válidas: user, admin"
        )
    
    # Atualiza o papel do usuário
    updated_user = await update_user_role(
        db=db,
        user_id=user_id,
        new_role=new_role,
        admin_user_id=str(current_user.id)
    )
    
    # Obtém as permissões do usuário
    permissions = [p.value for p in ROLE_PERMISSIONS.get(updated_user.role, [])]
    
    # Retorna os dados atualizados do usuário
    return {
        "_id": str(updated_user.id),
        "name": updated_user.name,
        "email": updated_user.email,
        "role": updated_user.role.value,
        "is_active": updated_user.is_active,
        "created_at": updated_user.created_at,
        "updated_at": updated_user.updated_at,
        "last_login": updated_user.last_login,
        "permissions": permissions
    }


@router.patch("/users/{user_id}/status", response_model=UserDetailResponse)
async def update_user_status(
    user_id: str,
    status_data: dict = Body(..., example={"is_active": True}),
    current_user: UserInDB = Depends(require_admin),
    db = Depends(get_database)
):
    """
    Ativa ou desativa um usuário.
    
    Requer autenticação via token JWT válido e papel ADMIN.
    
    - **user_id**: ID do usuário
    - **is_active**: Novo status (true para ativar, false para desativar)
    
    Retorna os dados atualizados do usuário.
    """
    # Verifica se o campo is_active está presente
    if "is_active" not in status_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campo 'is_active' é obrigatório"
        )
    
    is_active = status_data["is_active"]
    if not isinstance(is_active, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campo 'is_active' deve ser um booleano"
        )
    
    # Atualiza o status do usuário
    updated_user = await update_user_active_status(
        db=db,
        user_id=user_id,
        is_active=is_active,
        admin_user_id=str(current_user.id)
    )
    
    # Obtém as permissões do usuário
    permissions = [p.value for p in ROLE_PERMISSIONS.get(updated_user.role, [])]
    
    # Retorna os dados atualizados do usuário
    return {
        "_id": str(updated_user.id),
        "name": updated_user.name,
        "email": updated_user.email,
        "role": updated_user.role.value,
        "is_active": updated_user.is_active,
        "created_at": updated_user.created_at,
        "updated_at": updated_user.updated_at,
        "last_login": updated_user.last_login,
        "permissions": permissions
    } 