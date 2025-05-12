"""
Pacote de modelos de dados para o Habitus Forecast.

Este pacote contém as definições dos modelos Pydantic para validação
e integração com MongoDB, incluindo usuários, dados financeiros e cenários.
"""

from app.models.user import (
    PyObjectId, 
    UserRole, 
    Permission, 
    UserBase, 
    UserCreate, 
    UserInDB, 
    UserResponse, 
    UserResponseAdmin, 
    ROLE_PERMISSIONS
)

from app.models.financial import (
    FinancialCategory,
    FinancialMetadata,
    FinancialDataBase,
    FinancialDataCreate,
    FinancialDataInDB,
    FinancialDataResponse,
    FinancialDataResponseAdmin
)

from app.models.scenario import (
    ScenarioType,
    ScenarioParameter,
    ScenarioMetrics,
    ScenarioBase,
    ScenarioCreate,
    ScenarioInDB,
    ScenarioResponse,
    ScenarioResponseDetail,
    ScenarioResponseAdmin
)

__all__ = [
    # User models
    "PyObjectId",
    "UserRole",
    "Permission",
    "UserBase",
    "UserCreate",
    "UserInDB",
    "UserResponse",
    "UserResponseAdmin",
    "ROLE_PERMISSIONS",
    
    # Financial data models
    "FinancialCategory",
    "FinancialMetadata",
    "FinancialDataBase",
    "FinancialDataCreate",
    "FinancialDataInDB",
    "FinancialDataResponse",
    "FinancialDataResponseAdmin",
    
    # Scenario models
    "ScenarioType",
    "ScenarioParameter",
    "ScenarioMetrics",
    "ScenarioBase",
    "ScenarioCreate",
    "ScenarioInDB",
    "ScenarioResponse",
    "ScenarioResponseDetail",
    "ScenarioResponseAdmin"
] 