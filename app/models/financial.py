"""
Módulo de modelos de dados financeiros para o Habitus Forecast.

Este módulo contém as definições dos modelos para dados financeiros
importados, com validação e relacionamento com usuários.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

from app.models.user import PyObjectId, UserRole


class FinancialCategory(BaseModel):
    """
    Modelo para categoria financeira.
    
    Attributes:
        id: Identificador da categoria.
        name: Nome da categoria.
        description: Descrição opcional da categoria.
    """
    id: str
    name: str
    description: Optional[str] = None


class FinancialMetadata(BaseModel):
    """
    Metadados para dados financeiros importados.
    
    Attributes:
        file_name: Nome do arquivo original importado.
        file_size: Tamanho do arquivo em bytes.
        import_date: Data de importação.
        sheet_names: Lista de nomes das planilhas.
        processing_time: Tempo de processamento em segundos.
        categories_found: Lista de categorias encontradas.
    """
    file_name: str
    file_size: int
    import_date: datetime = Field(default_factory=datetime.utcnow)
    sheet_names: List[str] = []
    processing_time: Optional[float] = None
    categories_found: List[str] = []
    total_sheets: Optional[int] = None
    total_categories: Optional[int] = None


class FinancialDataBase(BaseModel):
    """
    Modelo base para dados financeiros importados.
    
    Attributes:
        title: Título para o conjunto de dados.
        description: Descrição opcional.
        categories: Lista de categorias financeiras.
        data: Dados financeiros estruturados por categoria.
        metadata: Metadados da importação.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    categories: List[FinancialCategory]
    data: Dict[str, Any]
    metadata: FinancialMetadata
    
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
            raise ValueError('Os dados financeiros não podem estar vazios')
        
        # Verifica se os dados têm pelo menos uma categoria
        if len(v.keys()) == 0:
            raise ValueError('Pelo menos uma categoria financeira deve estar presente')
        
        return v


class FinancialDataCreate(FinancialDataBase):
    """Modelo para criação de dados financeiros."""
    pass


class FinancialDataInDB(FinancialDataBase):
    """
    Modelo de dados financeiros como armazenado no banco de dados.
    
    Attributes:
        id: ID único dos dados financeiros.
        owner_id: ID do usuário proprietário dos dados.
        created_at: Data e hora de criação.
        updated_at: Data e hora da última atualização.
        is_public: Indica se os dados são públicos.
        shared_with: Lista de IDs de usuários com quem os dados foram compartilhados.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    owner_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    shared_with: List[PyObjectId] = []
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "title": "Dados financeiros Q2 2023",
                "description": "Dados financeiros para o segundo trimestre de 2023",
                "owner_id": "60d6e04aec32c02a5a7c7d39",
                "is_public": False,
                "created_at": "2023-05-15T10:00:00",
                "updated_at": "2023-05-15T10:00:00"
            }
        }

    def can_user_access(self, user_id: ObjectId, user_role: UserRole) -> bool:
        """
        Verifica se um usuário pode acessar estes dados financeiros.
        
        Args:
            user_id: ID do usuário que tenta acessar.
            user_role: Papel do usuário.
            
        Returns:
            True se o usuário pode acessar os dados, False caso contrário.
        """
        # Admins podem acessar qualquer dado
        if user_role == UserRole.ADMIN:
            return True
        
        # Proprietário pode acessar seus próprios dados
        if str(self.owner_id) == str(user_id):
            return True
        
        # Dados públicos podem ser acessados por qualquer um
        if self.is_public:
            return True
        
        # Verificar se o usuário está na lista de compartilhamento
        return any(str(shared_id) == str(user_id) for shared_id in self.shared_with)


class FinancialDataResponse(BaseModel):
    """
    Modelo para resposta da API com dados financeiros.
    
    Attributes:
        id: ID único dos dados financeiros.
        title: Título para o conjunto de dados.
        description: Descrição opcional.
        categories: Lista de categorias financeiras.
        data: Dados financeiros estruturados por categoria.
        created_at: Data e hora de criação.
        is_public: Indica se os dados são públicos.
        owner_id: ID do usuário proprietário dos dados.
    """
    id: str = Field(..., alias="_id")
    title: str
    description: Optional[str] = None
    categories: List[FinancialCategory]
    data: Dict[str, Any]
    created_at: datetime
    is_public: bool
    owner_id: str
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "title": "Dados financeiros Q2 2023",
                "description": "Dados financeiros para o segundo trimestre de 2023",
                "categories": [
                    {
                        "id": "receitas",
                        "name": "Receitas",
                        "description": "Entradas de recursos financeiros"
                    }
                ],
                "data": {"receitas": {}},
                "created_at": "2023-05-15T10:00:00",
                "is_public": False,
                "owner_id": "60d6e04aec32c02a5a7c7d39"
            }
        }


class FinancialDataResponseAdmin(FinancialDataResponse):
    """
    Modelo para resposta da API com dados financeiros completos (admin).
    
    Attributes:
        updated_at: Data e hora da última atualização.
        metadata: Metadados da importação.
        shared_with: Lista de IDs de usuários com quem os dados foram compartilhados.
    """
    updated_at: datetime
    metadata: FinancialMetadata
    shared_with: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "60d6e04aec32c02a5a7c7d40",
                "title": "Dados financeiros Q2 2023",
                "description": "Dados financeiros para o segundo trimestre de 2023",
                "categories": [
                    {
                        "id": "receitas",
                        "name": "Receitas",
                        "description": "Entradas de recursos financeiros"
                    }
                ],
                "data": {"receitas": {}},
                "created_at": "2023-05-15T10:00:00",
                "updated_at": "2023-05-15T10:00:00",
                "is_public": False,
                "owner_id": "60d6e04aec32c02a5a7c7d39",
                "shared_with": ["60d6e04aec32c02a5a7c7d38"],
                "metadata": {
                    "file_name": "dados_q2_2023.xlsx",
                    "file_size": 25600,
                    "import_date": "2023-05-15T10:00:00",
                    "sheet_names": ["Receitas", "Despesas"],
                    "processing_time": 1.5,
                    "categories_found": ["receitas", "despesas"]
                }
            }
        }


# Configuração para índices no MongoDB
financial_data_indexes = [
    IndexModel([("owner_id", ASCENDING)]),
    IndexModel([("created_at", DESCENDING)]),
    IndexModel([("is_public", ASCENDING)]),
    IndexModel([("title", "text"), ("description", "text")])
] 