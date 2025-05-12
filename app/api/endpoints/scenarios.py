"""
Endpoints para gestão de cenários financeiros no Habitus Forecast.

Este módulo contém os endpoints para criar, listar, visualizar e excluir
cenários financeiros baseados em dados processados de planilhas Excel.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Body, Path, Query
from typing import Dict, List, Any, Optional
from datetime import datetime
from bson import ObjectId

from app.schemas.scenarios import (
    ScenarioCreateRequest,
    ScenarioResponse,
    ScenarioListResponse,
    ScenarioType,
    ScenarioMetrics
)
from app.models.user import UserInDB
from app.db.mongodb import get_database
from app.utils.security import get_current_active_user, require_permission
from app.models.user import Permission
from app.utils.excel_processor import ExcelProcessor, FinancialCategory
from app.services.scenario_generator import ScenarioGenerator

router = APIRouter()

@router.post("/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario_data: ScenarioCreateRequest = Body(...),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Cria um novo cenário financeiro.
    
    Gera um cenário financeiro baseado em dados financeiros processados
    anteriormente, aplicando os parâmetros especificados.
    
    - **title**: Título do cenário (obrigatório)
    - **description**: Descrição opcional do cenário
    - **scenario_type**: Tipo de cenário (realista, pessimista, otimista, agressivo)
    - **financial_data_id**: ID dos dados financeiros a serem utilizados
    - **parameters**: Parâmetros opcionais para ajustar o cenário
    
    Retorna os dados do cenário gerado.
    
    Exemplo de chamada:
    ```
    curl -X POST "http://localhost:8000/api/scenarios/" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Cenário Otimista 2023",
            "description": "Projeção otimista para o ano fiscal de 2023",
            "scenario_type": "otimista",
            "financial_data_id": "60d9b5e7d2a68c001f45e123",
            "parameters": {
                "revenue_growth": 15.0,
                "cost_reduction": 7.5,
                "expense_growth": -5.0,
                "investment_growth": 20.0
            }
        }'
    ```
    """
    try:
        # Verificar se os dados financeiros existem
        financial_data = await db["financial_data"].find_one({"_id": ObjectId(scenario_data.financial_data_id)})
        if not financial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dados financeiros não encontrados"
            )
        
        # Verificar se o usuário tem acesso aos dados financeiros
        if financial_data.get("user_id") != str(current_user.id) and not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar estes dados financeiros"
            )
        
        # Inicializar o gerador de cenários
        scenario_generator = ScenarioGenerator()
        
        # Preparar parâmetros para o gerador de cenários
        generator_params = {}
        if scenario_data.parameters:
            generator_params = scenario_data.parameters.dict(exclude_unset=True, exclude_none=True)
        
        # Gerar o cenário
        result = scenario_generator.generate_scenario(
            financial_data=financial_data["data"],
            scenario_type=scenario_data.scenario_type.value,
            parameters=generator_params
        )
        
        # Calcular métricas do cenário
        scenario_metrics = ScenarioMetrics(
            total_revenue=result["metrics"].get("total_revenue", 0.0),
            total_costs=result["metrics"].get("total_costs", 0.0),
            total_expenses=result["metrics"].get("total_expenses", 0.0),
            total_margin=result["metrics"].get("total_margin", 0.0),
            total_cashflow=result["metrics"].get("total_cashflow", 0.0),
            final_balance=result["metrics"].get("final_balance", 0.0),
            margin_percentage=result["metrics"].get("margin_percentage", 0.0),
            roi=result["metrics"].get("roi", 0.0)
        )
        
        # Criar documento no banco de dados
        now = datetime.utcnow()
        scenario_doc = {
            "title": scenario_data.title,
            "description": scenario_data.description,
            "scenario_type": scenario_data.scenario_type.value,
            "financial_data_id": scenario_data.financial_data_id,
            "parameters": generator_params,
            "data": result["data"],
            "metrics": scenario_metrics.dict(),
            "created_at": now,
            "updated_at": now,
            "user_id": str(current_user.id)
        }
        
        result = await db["scenarios"].insert_one(scenario_doc)
        scenario_id = str(result.inserted_id)
        
        # Preparar resposta
        return {
            "id": scenario_id,
            "title": scenario_data.title,
            "description": scenario_data.description,
            "scenario_type": scenario_data.scenario_type.value,
            "created_at": now,
            "user_id": str(current_user.id),
            "financial_data_id": scenario_data.financial_data_id,
            "metrics": scenario_metrics,
            "parameters": generator_params
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar cenário: {str(e)}"
        )


@router.get("/", response_model=ScenarioListResponse)
async def list_scenarios(
    skip: int = Query(0, ge=0, description="Itens a pular (paginação)"),
    limit: int = Query(10, ge=1, le=100, description="Limite de itens a retornar"),
    scenario_type: Optional[str] = Query(None, description="Filtrar por tipo de cenário"),
    financial_data_id: Optional[str] = Query(None, description="Filtrar por ID de dados financeiros"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Lista os cenários financeiros do usuário.
    
    Retorna uma lista paginada de cenários criados pelo usuário,
    com opções de filtragem por tipo de cenário e dados financeiros.
    
    - **skip**: Número de itens a pular (para paginação)
    - **limit**: Número máximo de itens a retornar
    - **scenario_type**: Filtrar por tipo de cenário (realista, pessimista, otimista, agressivo)
    - **financial_data_id**: Filtrar por ID de dados financeiros
    
    Exemplo de chamada:
    ```
    curl -X GET "http://localhost:8000/api/scenarios/?skip=0&limit=10&scenario_type=otimista" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    # Monta a query
    query = {"user_id": str(current_user.id)}
    
    # Adiciona filtros
    if scenario_type:
        if scenario_type not in [t.value for t in ScenarioType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de cenário inválido: {scenario_type}"
            )
        query["scenario_type"] = scenario_type
    
    if financial_data_id:
        query["financial_data_id"] = financial_data_id
    
    # Conta o total de documentos
    total = await db["scenarios"].count_documents(query)
    
    # Obtém os documentos com paginação
    cursor = db["scenarios"].find(query).sort("created_at", -1).skip(skip).limit(limit)
    scenarios = await cursor.to_list(length=limit)
    
    # Formata a resposta
    scenario_list = []
    for scenario in scenarios:
        scenario_list.append({
            "id": str(scenario["_id"]),
            "title": scenario["title"],
            "description": scenario.get("description"),
            "scenario_type": scenario["scenario_type"],
            "created_at": scenario["created_at"],
            "user_id": scenario["user_id"],
            "financial_data_id": scenario["financial_data_id"],
            "metrics": scenario["metrics"],
            "parameters": scenario.get("parameters")
        })
    
    return {
        "total": total,
        "scenarios": scenario_list
    }


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: str = Path(..., description="ID do cenário"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Obtém detalhes de um cenário específico.
    
    Retorna informações detalhadas sobre um cenário financeiro específico,
    incluindo métricas e parâmetros utilizados para sua geração.
    
    - **scenario_id**: ID do cenário a consultar
    
    Exemplo de chamada:
    ```
    curl -X GET "http://localhost:8000/api/scenarios/60d9b5e7d2a68c001f45e124" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    scenario = await db["scenarios"].find_one({"_id": ObjectId(scenario_id)})
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cenário não encontrado"
        )
    
    # Verifica se pertence ao usuário
    if scenario.get("user_id") != str(current_user.id) and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este cenário"
        )
    
    return {
        "id": str(scenario["_id"]),
        "title": scenario["title"],
        "description": scenario.get("description"),
        "scenario_type": scenario["scenario_type"],
        "created_at": scenario["created_at"],
        "user_id": scenario["user_id"],
        "financial_data_id": scenario["financial_data_id"],
        "metrics": scenario["metrics"],
        "parameters": scenario.get("parameters")
    }


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: str = Path(..., description="ID do cenário a ser excluído"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Exclui um cenário financeiro.
    
    Remove permanentemente um cenário financeiro específico.
    
    - **scenario_id**: ID do cenário a ser excluído
    
    Exemplo de chamada:
    ```
    curl -X DELETE "http://localhost:8000/api/scenarios/60d9b5e7d2a68c001f45e124" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    # Busca o cenário
    scenario = await db["scenarios"].find_one({"_id": ObjectId(scenario_id)})
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cenário não encontrado"
        )
    
    # Verifica se pertence ao usuário
    if scenario.get("user_id") != str(current_user.id) and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para excluir este cenário"
        )
    
    # Exclui o cenário
    await db["scenarios"].delete_one({"_id": ObjectId(scenario_id)})
    
    # Não retorna conteúdo (204 No Content)


@router.get("/types", response_model=List[Dict[str, str]])
async def get_scenario_types():
    """
    Lista os tipos de cenários disponíveis.
    
    Retorna uma lista com todos os tipos de cenários que podem ser gerados,
    incluindo seus identificadores e descrições.
    
    Exemplo de chamada:
    ```
    curl -X GET "http://localhost:8000/api/scenarios/types" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    scenario_types = [
        {
            "id": ScenarioType.REALISTIC.value,
            "name": "Realista",
            "description": "Cenário baseado nos dados atuais sem alterações significativas"
        },
        {
            "id": ScenarioType.PESSIMISTIC.value,
            "name": "Pessimista",
            "description": "Cenário com redução de receitas e aumento de despesas"
        },
        {
            "id": ScenarioType.OPTIMISTIC.value,
            "name": "Otimista",
            "description": "Cenário com aumento de receitas e redução de despesas"
        },
        {
            "id": ScenarioType.AGGRESSIVE.value,
            "name": "Agressivo",
            "description": "Cenário com crescimento exponencial de receitas e aumento de investimentos"
        }
    ]
    
    return scenario_types 