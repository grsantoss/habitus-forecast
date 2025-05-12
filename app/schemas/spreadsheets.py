"""
Schemas para validação e formatação de dados para os endpoints de planilhas.

Este módulo contém schemas Pydantic usados para validar entradas e formatar saídas
dos endpoints relacionados a planilhas financeiras.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile, File

class SpreadsheetUploadRequest(BaseModel):
    """
    Requisição para upload de planilha Excel.
    
    Attributes:
        description: Descrição opcional da planilha.
    """
    description: Optional[str] = Field(None, max_length=500, description="Descrição da planilha")
    
    class Config:
        schema_extra = {
            "example": {
                "description": "Dados financeiros do primeiro trimestre de 2023"
            }
        }

class SpreadsheetMetadata(BaseModel):
    """
    Metadados de uma planilha processada.
    
    Attributes:
        sheet_names: Lista de nomes das planilhas.
        total_sheets: Número total de planilhas.
        processing_date: Data de processamento.
        categories_found: Categorias financeiras identificadas.
        total_categories: Número total de categorias identificadas.
    """
    sheet_names: List[str] = Field(..., description="Lista de nomes das planilhas")
    total_sheets: int = Field(..., description="Número total de planilhas")
    processing_date: datetime = Field(..., description="Data de processamento")
    categories_found: List[str] = Field(..., description="Categorias financeiras identificadas")
    total_categories: int = Field(..., description="Número total de categorias identificadas")
    
    class Config:
        schema_extra = {
            "example": {
                "sheet_names": ["Receitas", "Custos", "Despesas", "Investimentos", "Resumo"],
                "total_sheets": 5,
                "processing_date": "2023-03-15T14:35:00",
                "categories_found": ["receitas", "custos_variaveis", "despesas_pessoal", "investimentos"],
                "total_categories": 4
            }
        }

class CategoryInfo(BaseModel):
    """
    Informações sobre uma categoria financeira.
    
    Attributes:
        id: Identificador da categoria.
        name: Nome formatado da categoria.
        description: Descrição da categoria.
    """
    id: str = Field(..., description="Identificador da categoria")
    name: str = Field(..., description="Nome formatado da categoria")
    description: Optional[str] = Field(None, description="Descrição da categoria")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "receitas",
                "name": "Receitas",
                "description": "Receitas e faturamento da empresa"
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
        user_id: ID do usuário que enviou a planilha.
        description: Descrição opcional fornecida pelo usuário.
    """
    id: str = Field(..., description="ID único da planilha")
    filename: str = Field(..., description="Nome do arquivo")
    upload_date: datetime = Field(..., description="Data de upload")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    status: str = Field(..., description="Status do processamento")
    message: str = Field(..., description="Mensagem informativa")
    user_id: str = Field(..., description="ID do usuário que enviou a planilha")
    description: Optional[str] = Field(None, description="Descrição fornecida pelo usuário")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d9b5e7d2a68c001f45e125",
                "filename": "dados_financeiros_2023.xlsx",
                "upload_date": "2023-03-15T14:30:00",
                "size": 102400,
                "status": "success",
                "message": "Planilha enviada com sucesso. Pronta para processamento.",
                "user_id": "60d6e04aec32c02a5a7c7d40",
                "description": "Dados financeiros do primeiro trimestre de 2023"
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
        categories: Lista de informações sobre categorias identificadas.
        metadata: Metadados do processamento.
        user_id: ID do usuário que enviou a planilha.
    """
    id: str = Field(..., description="ID único da planilha")
    filename: str = Field(..., description="Nome do arquivo")
    status: str = Field(..., description="Status do processamento")
    message: str = Field(..., description="Mensagem informativa")
    categories: List[CategoryInfo] = Field(..., description="Lista de informações sobre categorias")
    metadata: SpreadsheetMetadata = Field(..., description="Metadados do processamento")
    user_id: str = Field(..., description="ID do usuário que enviou a planilha")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d9b5e7d2a68c001f45e125",
                "filename": "dados_financeiros_2023.xlsx",
                "status": "success",
                "message": "Processamento concluído com sucesso",
                "categories": [
                    {
                        "id": "receitas",
                        "name": "Receitas",
                        "description": "Receitas e faturamento da empresa"
                    },
                    {
                        "id": "custos_variaveis",
                        "name": "Custos Variáveis",
                        "description": "Custos que variam de acordo com a produção"
                    }
                ],
                "metadata": {
                    "sheet_names": ["Receitas", "Custos", "Despesas", "Investimentos", "Resumo"],
                    "total_sheets": 5,
                    "processing_date": "2023-03-15T14:35:00",
                    "categories_found": ["receitas", "custos_variaveis", "despesas_pessoal", "investimentos"],
                    "total_categories": 4
                },
                "user_id": "60d6e04aec32c02a5a7c7d40"
            }
        }

class SpreadsheetListResponse(BaseModel):
    """
    Resposta para listagem de planilhas.
    
    Attributes:
        total: Número total de planilhas.
        spreadsheets: Lista de planilhas.
    """
    total: int = Field(..., description="Número total de planilhas")
    spreadsheets: List[SpreadsheetUploadResponse] = Field(..., description="Lista de planilhas")
    
    class Config:
        schema_extra = {
            "example": {
                "total": 2,
                "spreadsheets": [
                    {
                        "id": "60d9b5e7d2a68c001f45e125",
                        "filename": "dados_financeiros_2023_Q1.xlsx",
                        "upload_date": "2023-03-15T14:30:00",
                        "size": 102400,
                        "status": "processed",
                        "message": "Planilha processada com sucesso",
                        "user_id": "60d6e04aec32c02a5a7c7d40",
                        "description": "Dados financeiros do primeiro trimestre de 2023"
                    },
                    {
                        "id": "60d9b5e7d2a68c001f45e126",
                        "filename": "dados_financeiros_2023_Q2.xlsx",
                        "upload_date": "2023-06-15T10:15:00",
                        "size": 98304,
                        "status": "uploaded",
                        "message": "Planilha enviada. Pendente de processamento.",
                        "user_id": "60d6e04aec32c02a5a7c7d40",
                        "description": "Dados financeiros do segundo trimestre de 2023"
                    }
                ]
            }
        }