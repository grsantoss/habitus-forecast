from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
from pydantic import UUID4, BaseModel, EmailStr, Field, validator

from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_active_user, require_admin
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.admin import (
    SystemStats, ResourceUsage, SystemConfig, 
    SystemConfigUpdate, UserActivityLog
)
from app.services.user_service import UserService
from app.services.stats_service import StatsService
from app.services.system_service import SystemService


router = APIRouter(prefix="/admin", tags=["admin"])


# ============= Dependências =============

def get_user_service():
    return UserService()


def get_stats_service():
    return StatsService()


def get_system_service():
    return SystemService()


# ============= Gestão de Usuários =============

@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filtrar por status (active, inactive)"),
    search: Optional[str] = Query(None, description="Buscar por nome ou email"),
    role: Optional[UserRole] = Query(None, description="Filtrar por papel (regular, admin)"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Lista todos os usuários do sistema com paginação e filtros.
    Apenas administradores podem acessar este endpoint.
    """
    users, total = await user_service.get_users(
        page=pagination.page,
        limit=pagination.limit,
        status=status,
        search=search,
        role=role
    )
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID4 = Path(..., description="ID do usuário"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Obtém detalhes de um usuário específico pelo ID.
    Apenas administradores podem acessar este endpoint.
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Cria um novo usuário.
    Apenas administradores podem acessar este endpoint.
    """
    # Verificar se o email já existe
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já está em uso"
        )
    
    # Criar o usuário
    user = await user_service.create_user(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    # Enviar email de boas-vindas se solicitado
    if user_data.send_welcome_email:
        await user_service.send_welcome_email(user.email)
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID4,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Atualiza os dados de um usuário existente.
    Apenas administradores podem acessar este endpoint.
    """
    # Verificar se o usuário existe
    existing_user = await user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar se o email já está em uso (se estiver sendo alterado)
    if user_data.email and user_data.email != existing_user.email:
        email_user = await user_service.get_user_by_email(user_data.email)
        if email_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já está em uso"
            )
    
    # Atualizar o usuário
    updated_user = await user_service.update_user(
        user_id=user_id,
        data=user_data
    )
    
    return updated_user


@router.patch("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: UUID4,
    is_active: bool = Body(..., embed=True),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Atualiza o status (ativo/inativo) de um usuário.
    Apenas administradores podem acessar este endpoint.
    """
    # Verificar se o usuário existe
    existing_user = await user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permitir desativar o próprio usuário
    if user_id == current_user.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar sua própria conta"
        )
    
    # Atualizar status
    updated_user = await user_service.update_user_status(
        user_id=user_id,
        is_active=is_active
    )
    
    return updated_user


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_200_OK)
async def reset_user_password(
    user_id: UUID4,
    send_email: bool = Body(True),
    new_password: Optional[str] = Body(None),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Redefine a senha de um usuário.
    Pode enviar email ao usuário ou definir uma senha específica.
    Apenas administradores podem acessar este endpoint.
    """
    # Verificar se o usuário existe
    existing_user = await user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Redefinir a senha
    if send_email:
        await user_service.send_password_reset(existing_user.email)
        return {"detail": "Email de redefinição de senha enviado"}
    else:
        if not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nova senha é obrigatória quando send_email é falso"
            )
        
        await user_service.admin_reset_password(user_id, new_password)
        return {"detail": "Senha redefinida com sucesso"}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID4,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Remove um usuário do sistema.
    Apenas administradores podem acessar este endpoint.
    """
    # Verificar se o usuário existe
    existing_user = await user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permitir excluir o próprio usuário
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir sua própria conta"
        )
    
    # Excluir o usuário
    await user_service.delete_user(user_id)
    
    return None


# ============= Estatísticas do Sistema =============

@router.get("/metrics", response_model=SystemStats)
async def get_system_stats(
    period: str = Query("week", description="Período de análise (day, week, month, year)"),
    stats_service: StatsService = Depends(get_stats_service),
    current_user: User = Depends(require_admin)
):
    """
    Retorna métricas gerais do sistema.
    Apenas administradores podem acessar este endpoint.
    """
    # Mapear período para timedelta
    period_map = {
        "day": timedelta(days=1),
        "week": timedelta(days=7),
        "month": timedelta(days=30),
        "year": timedelta(days=365)
    }
    
    time_period = period_map.get(period, timedelta(days=7))
    stats = await stats_service.get_system_stats(time_period)
    
    return stats


@router.get("/metrics/users", response_model=Dict[str, Any])
async def get_user_metrics(
    period: str = Query("week", description="Período de análise (day, week, month, year)"),
    stats_service: StatsService = Depends(get_stats_service),
    current_user: User = Depends(require_admin)
):
    """
    Retorna métricas detalhadas sobre usuários.
    Apenas administradores podem acessar este endpoint.
    """
    # Mapear período para timedelta
    period_map = {
        "day": timedelta(days=1),
        "week": timedelta(days=7),
        "month": timedelta(days=30),
        "year": timedelta(days=365)
    }
    
    time_period = period_map.get(period, timedelta(days=7))
    metrics = await stats_service.get_user_metrics(time_period)
    
    return metrics


@router.get("/metrics/resources", response_model=ResourceUsage)
async def get_resource_usage(
    stats_service: StatsService = Depends(get_stats_service),
    current_user: User = Depends(require_admin)
):
    """
    Retorna métricas de utilização de recursos do sistema.
    Apenas administradores podem acessar este endpoint.
    """
    resource_usage = await stats_service.get_resource_usage()
    
    return resource_usage


@router.get("/logs", response_model=PaginatedResponse[Dict[str, Any]])
async def get_system_logs(
    pagination: PaginationParams = Depends(),
    level: Optional[str] = Query(None, description="Filtrar por nível (info, warning, error)"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    search: Optional[str] = Query(None, description="Termo de busca"),
    stats_service: StatsService = Depends(get_stats_service),
    current_user: User = Depends(require_admin)
):
    """
    Retorna logs do sistema com filtros e paginação.
    Apenas administradores podem acessar este endpoint.
    """
    logs, total = await stats_service.get_system_logs(
        page=pagination.page,
        limit=pagination.limit,
        level=level,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    return PaginatedResponse(
        items=logs,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/logs/activity", response_model=PaginatedResponse[UserActivityLog])
async def get_user_activity_logs(
    pagination: PaginationParams = Depends(),
    user_id: Optional[UUID4] = Query(None, description="Filtrar por usuário"),
    action: Optional[str] = Query(None, description="Filtrar por tipo de ação"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    stats_service: StatsService = Depends(get_stats_service),
    current_user: User = Depends(require_admin)
):
    """
    Retorna logs de atividade dos usuários.
    Apenas administradores podem acessar este endpoint.
    """
    logs, total = await stats_service.get_user_activity_logs(
        page=pagination.page,
        limit=pagination.limit,
        user_id=user_id,
        action=action,
        start_date=start_date,
        end_date=end_date
    )
    
    return PaginatedResponse(
        items=logs,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


# ============= Configurações do Sistema =============

@router.get("/settings", response_model=SystemConfig)
async def get_system_settings(
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Retorna as configurações globais do sistema.
    Apenas administradores podem acessar este endpoint.
    """
    settings = await system_service.get_system_config()
    
    return settings


@router.put("/settings", response_model=SystemConfig)
async def update_system_settings(
    config_data: SystemConfigUpdate,
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Atualiza as configurações globais do sistema.
    Apenas administradores podem acessar este endpoint.
    """
    updated_config = await system_service.update_system_config(config_data)
    
    return updated_config


@router.get("/scenario-templates", response_model=List[Dict[str, Any]])
async def get_scenario_templates(
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Retorna os modelos de cenários disponíveis.
    Apenas administradores podem acessar este endpoint.
    """
    templates = await system_service.get_scenario_templates()
    
    return templates


@router.post("/scenario-templates", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_scenario_template(
    template_data: Dict[str, Any] = Body(...),
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Cria um novo modelo de cenário.
    Apenas administradores podem acessar este endpoint.
    """
    # Validação básica dos campos necessários
    required_fields = ["name", "structure"]
    for field in required_fields:
        if field not in template_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campo obrigatório ausente: {field}"
            )
    
    new_template = await system_service.create_scenario_template(template_data)
    
    return new_template


@router.put("/scenario-templates/{template_id}", response_model=Dict[str, Any])
async def update_scenario_template(
    template_id: str,
    template_data: Dict[str, Any] = Body(...),
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Atualiza um modelo de cenário existente.
    Apenas administradores podem acessar este endpoint.
    """
    template = await system_service.update_scenario_template(template_id, template_data)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo de cenário não encontrado"
        )
    
    return template


@router.delete("/scenario-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario_template(
    template_id: str,
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Remove um modelo de cenário.
    Apenas administradores podem acessar este endpoint.
    """
    success = await system_service.delete_scenario_template(template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo de cenário não encontrado"
        )
    
    return None


# ============= Backup e Manutenção =============

@router.post("/backup", status_code=status.HTTP_202_ACCEPTED)
async def create_backup(
    full_backup: bool = Body(True, embed=True),
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Inicia um backup do sistema.
    Apenas administradores podem acessar este endpoint.
    """
    backup_job = await system_service.start_backup(full=full_backup)
    
    return {
        "job_id": backup_job.id,
        "status": backup_job.status,
        "created_at": backup_job.created_at,
        "detail": "Backup iniciado, verifique o status pelo job_id"
    }


@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
async def get_job_status(
    job_id: str,
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Verifica o status de um job do sistema (backup, restauração, etc).
    Apenas administradores podem acessar este endpoint.
    """
    job = await system_service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job não encontrado"
        )
    
    return job


@router.post("/restore", status_code=status.HTTP_202_ACCEPTED)
async def restore_backup(
    backup_id: str = Body(..., embed=True),
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Inicia uma restauração de backup.
    Apenas administradores podem acessar este endpoint.
    """
    # Verificar se o backup existe
    backup = await system_service.get_backup(backup_id)
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup não encontrado"
        )
    
    # Iniciar restauração
    restore_job = await system_service.start_restore(backup_id)
    
    return {
        "job_id": restore_job.id,
        "status": restore_job.status,
        "created_at": restore_job.created_at,
        "detail": "Restauração iniciada, verifique o status pelo job_id"
    }


@router.post("/database/optimize", status_code=status.HTTP_202_ACCEPTED)
async def optimize_database(
    collections: List[str] = Body(None),
    system_service: SystemService = Depends(get_system_service),
    current_user: User = Depends(require_admin)
):
    """
    Inicia um processo de otimização do banco de dados.
    Apenas administradores podem acessar este endpoint.
    """
    optimize_job = await system_service.optimize_database(collections)
    
    return {
        "job_id": optimize_job.id,
        "status": optimize_job.status,
        "created_at": optimize_job.created_at,
        "detail": "Otimização iniciada, verifique o status pelo job_id"
    } 