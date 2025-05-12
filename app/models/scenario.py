"""
Módulo de modelos de cenários financeiros para o Habitus Forecast.

Este módulo contém as definições dos modelos para cenários financeiros
gerados, com validação e relacionamento com dados financeiros e usuários.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

from app.models.user import PyObjectId, UserRole


class ScenarioType(str, Enum):
    """Tipos de cenários financeiros disponíveis."""
    REALISTIC = "realista"
    PESSIMISTIC = "pessimista"
    OPTIMISTIC = "otimista"
    AGGRESSIVE = "agressivo"


class ScenarioParameter(BaseModel):
    """
    Parâmetros para ajuste de cenários financeiros.
    
    Attributes:
        revenue_adjustment: Ajuste percentual para receitas.
        cost_adjustment: Ajuste percentual para custos.
        expense_adjustment: Ajuste percentual para despesas.
        investment_adjustment: Ajuste percentual para investimentos.
        growth_rate: Taxa de crescimento para cenários progressivos.
    """
    revenue_adjustment: Optional[float] = None
    cost_adjustment: Optional[float] = None
    expense_adjustment: Optional[float] = None
    investment_adjustment: Optional[float] = None
    growth_rate: Optional[float] = None
    
    @validator('revenue_adjustment', 'cost_adjustment', 'expense_adjustment', 'investment_adjustment')
    def validate_adjustment_range(cls, v):
        """Valida que o ajuste está dentro de um intervalo razoável."""
        if v is not None and (v < -0.9 or v > 5.0):
            raise ValueError('O ajuste deve estar entre -90% e 500%')
        return v


class ScenarioMetrics(BaseModel):
    """
    Métricas calculadas para um cenário financeiro.
    
    Attributes:
        total_revenue: Receita total.
        total_costs: Custos totais.
        total_expenses: Despesas totais.
        total_margin: Margem de contribuição total.
        total_cashflow: Fluxo de caixa total.
        final_balance: Saldo final.
        margin_percentage: Percentual de margem.
        roi: Retorno sobre investimento.
    """
    total_revenue: float
    total_costs: float
    total_expenses: float
    total_margin: float
    total_cashflow: float
    final_balance: float
    margin_percentage: float
    roi: float


class ScenarioBase(BaseModel):
    """
    Modelo base para cenários financeiros.
    
    Attributes:
        title: Título do cenário.
        description: Descrição opcional.
        scenario_type: Tipo de cenário.
        financial_data_id: ID dos dados financeiros usados como base.
        parameters: Parâmetros aplicados.
        data: Dados do cenário gerado.
        metrics: Métricas calculadas.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    scenario_type: ScenarioType
    financial_data_id: PyObjectId
    parameters: Optional[ScenarioParameter] = None
    data: Dict[str, Any]
    metrics: ScenarioMetrics
    
    @validator('title')
    def title_no_special_chars(cls, v):
        """Valida que o título não contém caracteres especiais."""
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_.,()]+$', v):
            raise ValueError('O título não deve conter caracteres especiais')
        return v
    
    @validator('data')
    def validate_data_structure(cls, v):
        """Valida que a estrutura de dados está correta."""
        if not v:
            raise ValueError('Os dados do cenário não podem estar vazios')
        
        # Verifica se os dados têm pelo menos uma categoria
        if len(v.keys()) == 0:
            raise ValueError('Pelo menos uma categoria financeira deve estar presente')
        
        return v


class ScenarioCreate(BaseModel):
    """
    Modelo para criação de cenários financeiros.
    
    Attributes:
        title: Título do cenário.
        description: Descrição opcional.
        scenario_type: Tipo de cenário.
        financial_data_id: ID dos dados financeiros usados como base.
        parameters: Parâmetros para ajuste do cenário.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    scenario_type: ScenarioType
    financial_data_id: str
    parameters: Optional[ScenarioParameter] = None


class ScenarioInDB(ScenarioBase):
    """
    Modelo de cenário financeiro como armazenado no banco de dados.
    
    Attributes:
        id: ID único do cenário.
        owner_id: ID do usuário proprietário.
        created_at: Data e hora de criação.
        updated_at: Data e hora da última atualização.
        is_public: Indica se o cenário é público.
        shared_with: Lista de IDs de usuários com quem o cenário foi compartilhado.
        is_favorite: Indica se o cenário é um favorito do proprietário.
        tags: Lista de tags para categorizar o cenário.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    owner_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    shared_with: List[PyObjectId] = []
    is_favorite: bool = False
    tags: List[str] = []
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "title": "Cenário Otimista Q2 2023",
                "description": "Análise otimista para o segundo trimestre de 2023",
                "scenario_type": "otimista",
                "financial_data_id": "60d6e04aec32c02a5a7c7d38",
                "owner_id": "60d6e04aec32c02a5a7c7d39",
                "is_public": False,
                "created_at": "2023-05-15T10:00:00",
                "updated_at": "2023-05-15T10:00:00",
                "is_favorite": True,
                "tags": ["2023", "Q2", "otimista"]
            }
        }

    def can_user_access(self, user_id: ObjectId, user_role: UserRole) -> bool:
        """
        Verifica se um usuário pode acessar este cenário.
        
        Args:
            user_id: ID do usuário que tenta acessar.
            user_role: Papel do usuário.
            
        Returns:
            True se o usuário pode acessar o cenário, False caso contrário.
        """
        # Admins podem acessar qualquer cenário
        if user_role == UserRole.ADMIN:
            return True
        
        # Proprietário pode acessar seu próprio cenário
        if str(self.owner_id) == str(user_id):
            return True
        
        # Cenários públicos podem ser acessados por qualquer um
        if self.is_public:
            return True
        
        # Verificar se o usuário está na lista de compartilhamento
        return any(str(shared_id) == str(user_id) for shared_id in self.shared_with)
    
    def can_user_modify(self, user_id: ObjectId, user_role: UserRole) -> bool:
        """
        Verifica se um usuário pode modificar este cenário.
        
        Args:
            user_id: ID do usuário que tenta modificar.
            user_role: Papel do usuário.
            
        Returns:
            True se o usuário pode modificar o cenário, False caso contrário.
        """
        # Admins podem modificar qualquer cenário
        if user_role == UserRole.ADMIN:
            return True
        
        # Apenas o proprietário pode modificar seu próprio cenário
        return str(self.owner_id) == str(user_id)


class ScenarioResponse(BaseModel):
    """
    Modelo para resposta da API com cenário financeiro.
    
    Attributes:
        id: ID único do cenário.
        title: Título do cenário.
        description: Descrição opcional.
        scenario_type: Tipo de cenário.
        financial_data_id: ID dos dados financeiros usados como base.
        metrics: Métricas calculadas.
        created_at: Data e hora de criação.
        is_public: Indica se o cenário é público.
        owner_id: ID do usuário proprietário.
        is_favorite: Indica se o cenário é um favorito do proprietário.
        tags: Lista de tags para categorizar o cenário.
    """
    id: str = Field(..., alias="_id")
    title: str
    description: Optional[str] = None
    scenario_type: ScenarioType
    financial_data_id: str
    metrics: ScenarioMetrics
    created_at: datetime
    is_public: bool
    owner_id: str
    is_favorite: bool
    tags: List[str] = []
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "title": "Cenário Otimista Q2 2023",
                "description": "Análise otimista para o segundo trimestre de 2023",
                "scenario_type": "otimista",
                "financial_data_id": "60d6e04aec32c02a5a7c7d38",
                "metrics": {
                    "total_revenue": 150000,
                    "total_costs": 75000,
                    "total_expenses": 30000,
                    "total_margin": 75000,
                    "total_cashflow": 45000,
                    "final_balance": 45000,
                    "margin_percentage": 50,
                    "roi": 30
                },
                "created_at": "2023-05-15T10:00:00",
                "is_public": False,
                "owner_id": "60d6e04aec32c02a5a7c7d39",
                "is_favorite": True,
                "tags": ["2023", "Q2", "otimista"]
            }
        }


class ScenarioResponseDetail(ScenarioResponse):
    """
    Modelo para resposta detalhada da API com cenário financeiro.
    
    Attributes:
        parameters: Parâmetros aplicados.
        data: Dados do cenário gerado.
    """
    parameters: Optional[ScenarioParameter] = None
    data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "title": "Cenário Otimista Q2 2023",
                "description": "Análise otimista para o segundo trimestre de 2023",
                "scenario_type": "otimista",
                "financial_data_id": "60d6e04aec32c02a5a7c7d38",
                "parameters": {
                    "revenue_adjustment": 0.2,
                    "cost_adjustment": -0.05,
                    "expense_adjustment": -0.05
                },
                "data": {"receitas": {}, "despesas": {}},
                "metrics": {
                    "total_revenue": 150000,
                    "total_costs": 75000,
                    "total_expenses": 30000,
                    "total_margin": 75000,
                    "total_cashflow": 45000,
                    "final_balance": 45000,
                    "margin_percentage": 50,
                    "roi": 30
                },
                "created_at": "2023-05-15T10:00:00",
                "is_public": False,
                "owner_id": "60d6e04aec32c02a5a7c7d39",
                "is_favorite": True,
                "tags": ["2023", "Q2", "otimista"]
            }
        }


class ScenarioResponseAdmin(ScenarioResponseDetail):
    """
    Modelo para resposta da API com informações completas do cenário (admin).
    
    Attributes:
        updated_at: Data e hora da última atualização.
        shared_with: Lista de IDs de usuários com quem o cenário foi compartilhado.
    """
    updated_at: datetime
    shared_with: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "title": "Cenário Otimista Q2 2023",
                "description": "Análise otimista para o segundo trimestre de 2023",
                "scenario_type": "otimista",
                "financial_data_id": "60d6e04aec32c02a5a7c7d38",
                "parameters": {
                    "revenue_adjustment": 0.2,
                    "cost_adjustment": -0.05,
                    "expense_adjustment": -0.05
                },
                "data": {"receitas": {}, "despesas": {}},
                "metrics": {
                    "total_revenue": 150000,
                    "total_costs": 75000,
                    "total_expenses": 30000,
                    "total_margin": 75000,
                    "total_cashflow": 45000,
                    "final_balance": 45000,
                    "margin_percentage": 50,
                    "roi": 30
                },
                "created_at": "2023-05-15T10:00:00",
                "updated_at": "2023-05-15T10:00:00",
                "is_public": False,
                "owner_id": "60d6e04aec32c02a5a7c7d39",
                "shared_with": ["60d6e04aec32c02a5a7c7d38"],
                "is_favorite": True,
                "tags": ["2023", "Q2", "otimista"]
            }
        }


# Configuração para índices no MongoDB
scenario_indexes = [
    IndexModel([("owner_id", ASCENDING)]),
    IndexModel([("created_at", DESCENDING)]),
    IndexModel([("scenario_type", ASCENDING)]),
    IndexModel([("financial_data_id", ASCENDING)]),
    IndexModel([("is_public", ASCENDING)]),
    IndexModel([("tags", ASCENDING)]),
    IndexModel([("title", "text"), ("description", "text")])
] 