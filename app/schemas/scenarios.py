"""
Schemas para validação e formatação de dados para os endpoints de cenários.

Este módulo contém schemas Pydantic usados para validar entradas e formatar saídas
dos endpoints relacionados a cenários financeiros.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile, File

class ScenarioType(str, Enum):
    """Tipos de cenários financeiros disponíveis."""
    REALISTIC = "realista"
    PESSIMISTIC = "pessimista"
    OPTIMISTIC = "otimista"
    AGGRESSIVE = "agressivo"

class ScenarioParameter(BaseModel):
    """
    Parâmetros para personalizar a geração de cenários.
    
    Attributes:
        revenue_growth: Percentual de crescimento para receitas.
        cost_reduction: Percentual de redução para custos.
        expense_growth: Percentual de crescimento para despesas.
        investment_growth: Percentual de crescimento para investimentos.
    """
    revenue_growth: Optional[float] = Field(None, ge=-100, description="Percentual de crescimento para receitas")
    cost_reduction: Optional[float] = Field(None, ge=-100, description="Percentual de redução para custos")
    expense_growth: Optional[float] = Field(None, ge=-100, description="Percentual de crescimento para despesas")
    investment_growth: Optional[float] = Field(None, ge=-100, description="Percentual de crescimento para investimentos")
    
    class Config:
        schema_extra = {
            "example": {
                "revenue_growth": 10.0,
                "cost_reduction": 5.0,
                "expense_growth": -3.0,
                "investment_growth": 15.0
            }
        }

class ScenarioCreateRequest(BaseModel):
    """
    Requisição para criar um novo cenário financeiro.
    
    Attributes:
        title: Título do cenário.
        description: Descrição opcional do cenário.
        scenario_type: Tipo de cenário a ser gerado.
        financial_data_id: ID dos dados financeiros a serem utilizados.
        parameters: Parâmetros opcionais para ajustar o cenário.
    """
    title: str = Field(..., min_length=3, max_length=100, description="Título do cenário")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do cenário")
    scenario_type: ScenarioType = Field(..., description="Tipo de cenário a ser gerado")
    financial_data_id: str = Field(..., description="ID dos dados financeiros a serem utilizados")
    parameters: Optional[ScenarioParameter] = Field(None, description="Parâmetros para ajustar o cenário")
    
    class Config:
        schema_extra = {
            "example": {
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
            }
        }

class ScenarioMetrics(BaseModel):
    """
    Métricas calculadas para um cenário financeiro.
    
    Attributes:
        total_revenue: Receita total projetada.
        total_costs: Custos totais projetados.
        total_expenses: Despesas totais projetadas.
        total_margin: Margem de contribuição total.
        total_cashflow: Fluxo de caixa total.
        final_balance: Saldo final projetado.
        margin_percentage: Percentual de margem sobre receita.
        roi: Retorno sobre investimento estimado.
    """
    total_revenue: float = Field(..., ge=0, description="Receita total projetada")
    total_costs: float = Field(..., ge=0, description="Custos totais projetados")
    total_expenses: float = Field(..., ge=0, description="Despesas totais projetadas")
    total_margin: float = Field(..., description="Margem de contribuição total")
    total_cashflow: float = Field(..., description="Fluxo de caixa total")
    final_balance: float = Field(..., description="Saldo final projetado")
    margin_percentage: float = Field(..., description="Percentual de margem sobre receita")
    roi: float = Field(..., description="Retorno sobre investimento estimado")
    
    class Config:
        schema_extra = {
            "example": {
                "total_revenue": 1250000.0,
                "total_costs": 450000.0,
                "total_expenses": 350000.0,
                "total_margin": 800000.0,
                "total_cashflow": 450000.0,
                "final_balance": 500000.0,
                "margin_percentage": 64.0,
                "roi": 28.5
            }
        }

class ScenarioResponse(BaseModel):
    """
    Resposta com dados de um cenário financeiro.
    
    Attributes:
        id: ID único do cenário.
        title: Título do cenário.
        description: Descrição do cenário.
        scenario_type: Tipo de cenário.
        created_at: Data de criação.
        user_id: ID do usuário que criou o cenário.
        financial_data_id: ID dos dados financeiros utilizados.
        metrics: Métricas calculadas para o cenário.
        parameters: Parâmetros utilizados para gerar o cenário.
    """
    id: str = Field(..., description="ID único do cenário")
    title: str = Field(..., description="Título do cenário")
    description: Optional[str] = Field(None, description="Descrição do cenário")
    scenario_type: str = Field(..., description="Tipo de cenário")
    created_at: datetime = Field(..., description="Data de criação")
    user_id: str = Field(..., description="ID do usuário que criou o cenário")
    financial_data_id: str = Field(..., description="ID dos dados financeiros utilizados")
    metrics: ScenarioMetrics = Field(..., description="Métricas calculadas para o cenário")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parâmetros utilizados para gerar o cenário")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d9b5e7d2a68c001f45e124",
                "title": "Cenário Otimista 2023",
                "description": "Projeção otimista para o ano fiscal de 2023",
                "scenario_type": "otimista",
                "created_at": "2023-03-15T14:30:00",
                "user_id": "60d6e04aec32c02a5a7c7d40",
                "financial_data_id": "60d9b5e7d2a68c001f45e123",
                "metrics": {
                    "total_revenue": 1250000.0,
                    "total_costs": 450000.0,
                    "total_expenses": 350000.0,
                    "total_margin": 800000.0,
                    "total_cashflow": 450000.0,
                    "final_balance": 500000.0,
                    "margin_percentage": 64.0,
                    "roi": 28.5
                },
                "parameters": {
                    "revenue_growth": 15.0,
                    "cost_reduction": 7.5,
                    "expense_growth": -5.0,
                    "investment_growth": 20.0
                }
            }
        }

class ScenarioListResponse(BaseModel):
    """
    Resposta com lista paginada de cenários financeiros.
    
    Attributes:
        total: Número total de cenários.
        scenarios: Lista de cenários.
    """
    total: int = Field(..., description="Número total de cenários")
    scenarios: List[ScenarioResponse] = Field(..., description="Lista de cenários")
    
    class Config:
        schema_extra = {
            "example": {
                "total": 3,
                "scenarios": [
                    {
                        "id": "60d9b5e7d2a68c001f45e124",
                        "title": "Cenário Otimista 2023",
                        "description": "Projeção otimista para o ano fiscal de 2023",
                        "scenario_type": "otimista",
                        "created_at": "2023-03-15T14:30:00",
                        "user_id": "60d6e04aec32c02a5a7c7d40",
                        "financial_data_id": "60d9b5e7d2a68c001f45e123",
                        "metrics": {
                            "total_revenue": 1250000.0,
                            "total_costs": 450000.0,
                            "total_expenses": 350000.0,
                            "total_margin": 800000.0,
                            "total_cashflow": 450000.0,
                            "final_balance": 500000.0,
                            "margin_percentage": 64.0,
                            "roi": 28.5
                        }
                    }
                ]
            }
        }

class SpreadsheetUploadResponse(BaseModel):
    """
    Resposta para upload de planilha.
    
    Attributes:
        id: ID único da planilha.
        filename: Nome do arquivo.
        upload_date: Data de upload.
        size: Tamanho do arquivo em bytes.
        status: Status do processamento.
        message: Mensagem informativa.
    """
    id: str = Field(..., description="ID único da planilha")
    filename: str = Field(..., description="Nome do arquivo")
    upload_date: datetime = Field(..., description="Data de upload")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    status: str = Field(..., description="Status do processamento")
    message: str = Field(..., description="Mensagem informativa")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d9b5e7d2a68c001f45e125",
                "filename": "dados_financeiros_2023.xlsx",
                "upload_date": "2023-03-15T14:30:00",
                "size": 102400,
                "status": "success",
                "message": "Planilha enviada com sucesso. Pronta para processamento."
            }
        }

class SpreadsheetProcessResponse(BaseModel):
    """
    Resposta para processamento de planilha.
    
    Attributes:
        id: ID único da planilha.
        filename: Nome do arquivo.
        status: Status do processamento.
        message: Mensagem informativa.
        categories: Categorias financeiras identificadas.
        sheets_processed: Número de planilhas processadas.
        processed_date: Data de processamento.
    """
    id: str = Field(..., description="ID único da planilha")
    filename: str = Field(..., description="Nome do arquivo")
    status: str = Field(..., description="Status do processamento")
    message: str = Field(..., description="Mensagem informativa")
    categories: List[str] = Field(..., description="Categorias financeiras identificadas")
    sheets_processed: int = Field(..., description="Número de planilhas processadas")
    processed_date: datetime = Field(..., description="Data de processamento")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d9b5e7d2a68c001f45e125",
                "filename": "dados_financeiros_2023.xlsx",
                "status": "success",
                "message": "Processamento concluído com sucesso",
                "categories": ["receitas", "custos_variaveis", "despesas_pessoal", "investimentos"],
                "sheets_processed": 5,
                "processed_date": "2023-03-15T14:35:00"
            }
        } 