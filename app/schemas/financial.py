from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum
import pandas as pd


class FinancialCategory(BaseModel):
    """Modelo para categorias financeiras."""
    id: str
    name: str
    description: Optional[str] = None


class FinancialDataResponse(BaseModel):
    """Resposta para dados financeiros processados."""
    status: str = "success"
    message: str = "Dados financeiros processados com sucesso"
    categories: List[FinancialCategory]
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    class Config:
        arbitrary_types_allowed = True  # Para permitir pandas.DataFrame
        
    def dict(self, **kwargs):
        """Sobrescreve o método dict para lidar com pandas DataFrames."""
        result = super().dict(**kwargs)
        # Converte DataFrames para dicionários
        if "data" in result:
            data_dict = {}
            for key, value in result["data"].items():
                if isinstance(value, pd.DataFrame):
                    data_dict[key] = value.to_dict(orient="records")
                else:
                    data_dict[key] = value
            result["data"] = data_dict
        return result 