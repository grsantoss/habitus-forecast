from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List, Dict, Any
import pandas as pd

from app.services.excel_processor import ExcelProcessor
from app.schemas.financial import (
    FinancialDataResponse,
    FinancialCategory
)

router = APIRouter()

@router.post("/upload", response_model=FinancialDataResponse, status_code=status.HTTP_201_CREATED)
async def upload_financial_data(
    file: UploadFile = File(...),
):
    """
    Faz upload e processa um arquivo Excel contendo dados financeiros.
    """
    # Verificar extensão do arquivo
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo inválido. Apenas arquivos Excel (.xlsx, .xls) são suportados."
        )
    
    try:
        # Ler o conteúdo do arquivo
        contents = await file.read()
        
        # Processar com ExcelProcessor
        excel_processor = ExcelProcessor()
        financial_data = excel_processor.process_excel_data(contents)
        
        return financial_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )

@router.get("/categories", response_model=List[FinancialCategory])
async def get_financial_categories():
    """
    Retorna as categorias financeiras disponíveis para análise.
    """
    categories = [
        FinancialCategory(id="income", name="Receitas", description="Entradas de recursos financeiros"),
        FinancialCategory(id="costs", name="Custos", description="Custos diretos relacionados à operação"),
        FinancialCategory(id="expenses", name="Despesas", description="Despesas operacionais e administrativas"),
        FinancialCategory(id="investments", name="Investimentos", description="Aplicações de capital"),
    ]
    
    return categories 