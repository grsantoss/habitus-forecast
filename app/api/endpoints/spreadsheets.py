"""
Endpoints para manipulação de planilhas Excel no Habitus Forecast.

Este módulo contém rotas para upload e processamento de planilhas financeiras,
essenciais para a geração de cenários financeiros.
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Path, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from pathlib import Path
import tempfile
import json
from datetime import datetime
import shutil

from app.core.config import settings
from app.api.endpoints.auth import get_current_user
from app.models.user import UserModel, UserInDB
from app.services.spreadsheet_service import SpreadsheetService
from app.utils.excel_processor import ExcelProcessor, FinancialCategory, ExcelValidationError
from app.schemas.spreadsheets import (
    SpreadsheetUploadRequest,
    SpreadsheetUploadResponse,
    SpreadsheetProcessResponse,
    SpreadsheetListResponse,
    CategoryInfo
)
from app.db.mongodb import get_database
from app.utils.security import get_current_active_user, require_permission
from app.models.user import Permission

router = APIRouter(prefix="/spreadsheets", tags=["Spreadsheets"])


@router.post("/", response_model=SpreadsheetUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_spreadsheet(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Realiza o upload de uma planilha Excel para processamento.
    
    A planilha Excel deve conter dados financeiros estruturados que serão
    processados para gerar cenários financeiros posteriormente.
    
    - **file**: Arquivo Excel a ser enviado (formato .xlsx ou .xls)
    - **description**: Descrição opcional da planilha
    
    Retorna informações sobre o upload realizado.
    
    Exemplo de upload:
    ```
    curl -X POST "http://localhost:8000/api/spreadsheets/" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -F "file=@dados_financeiros.xlsx" \
        -F "description=Dados do primeiro trimestre de 2023"
    ```
    """
    # Verificar se é um arquivo Excel
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos Excel (.xlsx, .xls) são permitidos"
        )
    
    # Cria diretório de upload se não existir
    upload_dir = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Gera nome único para o arquivo
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(ObjectId())[10:]}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Salva o arquivo
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Obtém o tamanho do arquivo
    file_size = os.path.getsize(file_path)
    
    # Cria registro no banco de dados
    spreadsheet_data = {
        "filename": file.filename,
        "system_filename": unique_filename,
        "path": file_path,
        "upload_date": datetime.utcnow(),
        "size": file_size,
        "status": "uploaded",
        "processed": False,
        "description": description,
        "user_id": str(current_user.id)
    }
    
    result = await db["spreadsheets"].insert_one(spreadsheet_data)
    spreadsheet_id = str(result.inserted_id)
    
    # Prepara resposta
    response = {
        "id": spreadsheet_id,
        "filename": file.filename,
        "upload_date": spreadsheet_data["upload_date"],
        "size": file_size,
        "status": "success",
        "message": "Planilha enviada com sucesso. Pronta para processamento.",
        "user_id": str(current_user.id),
        "description": description
    }
    
    return response


@router.post("/{spreadsheet_id}/process", response_model=SpreadsheetProcessResponse)
async def process_spreadsheet(
    spreadsheet_id: str = Path(..., description="ID da planilha a ser processada"),
    required_categories: Optional[List[str]] = Query(None, description="Categorias financeiras obrigatórias"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Processa uma planilha Excel previamente enviada.
    
    Este endpoint extrai os dados financeiros da planilha e os prepara para
    a geração de cenários. Identifica automaticamente as categorias financeiras
    presentes na planilha.
    
    - **spreadsheet_id**: ID da planilha a ser processada
    - **required_categories**: Categorias financeiras que devem estar presentes
    
    Retorna o resultado do processamento, incluindo categorias encontradas e metadados.
    
    Exemplo de chamada:
    ```
    curl -X POST "http://localhost:8000/api/spreadsheets/60d9b5e7d2a68c001f45e125/process" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"required_categories": ["receitas", "custos_variaveis"]}'
    ```
    """
    try:
        # Busca informações da planilha no banco de dados
        spreadsheet = await db["spreadsheets"].find_one({"_id": ObjectId(spreadsheet_id)})
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planilha não encontrada"
            )
        
        # Verifica se a planilha pertence ao usuário
        if spreadsheet.get("user_id") != str(current_user.id) and not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar esta planilha"
            )
        
        # Verifica se a planilha já foi processada
        if spreadsheet.get("processed", False):
            # Se já processada, busca os dados salvos
            return await get_processed_data(db, spreadsheet_id, current_user.id)
        
        # Cria instância do processador
        processor = ExcelProcessor()
        
        # Lê e processa a planilha
        with open(spreadsheet["path"], "rb") as f:
            file_content = f.read()
        
        # Processa os dados da planilha
        process_result = processor.process_excel_data(file_content)
        
        # Verifica categorias obrigatórias
        if required_categories:
            categories_found = [cat.value for cat in processor.metadata.get("categories_found", [])]
            missing_categories = [cat for cat in required_categories if cat not in categories_found]
            if missing_categories:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Categorias obrigatórias não encontradas: {', '.join(missing_categories)}"
                )
        
        # Atualiza o registro no banco de dados
        financial_data_id = ObjectId()
        await db["financial_data"].insert_one({
            "_id": financial_data_id,
            "spreadsheet_id": spreadsheet_id,
            "user_id": str(current_user.id),
            "data": process_result["data"],
            "metadata": processor.metadata,
            "created_at": datetime.utcnow()
        })
        
        await db["spreadsheets"].update_one(
            {"_id": ObjectId(spreadsheet_id)},
            {
                "$set": {
                    "processed": True,
                    "processed_date": datetime.utcnow(),
                    "financial_data_id": str(financial_data_id),
                    "categories": process_result["categories"]
                }
            }
        )
        
        # Prepara resposta
        return {
            "id": spreadsheet_id,
            "filename": spreadsheet["filename"],
            "status": "success",
            "message": "Processamento concluído com sucesso",
            "categories": process_result["categories"],
            "metadata": processor.metadata,
            "user_id": str(current_user.id)
        }
    
    except ExcelValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar planilha: {str(e)}"
        )


async def get_processed_data(db, spreadsheet_id: str, user_id: str) -> Dict[str, Any]:
    """
    Obtém os dados processados de uma planilha.
    
    Args:
        db: Conexão com o banco de dados.
        spreadsheet_id: ID da planilha.
        user_id: ID do usuário atual.
        
    Returns:
        Dados processados da planilha.
        
    Raises:
        HTTPException: Se os dados não forem encontrados.
    """
    spreadsheet = await db["spreadsheets"].find_one({"_id": ObjectId(spreadsheet_id)})
    if not spreadsheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planilha não encontrada"
        )
    
    financial_data = await db["financial_data"].find_one({"spreadsheet_id": spreadsheet_id})
    if not financial_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dados financeiros não encontrados"
        )
    
    return {
        "id": spreadsheet_id,
        "filename": spreadsheet["filename"],
        "status": "success",
        "message": "Dados já processados anteriormente",
        "categories": spreadsheet.get("categories", []),
        "metadata": financial_data["metadata"],
        "user_id": str(user_id)
    }


@router.get("/", response_model=SpreadsheetListResponse)
async def list_spreadsheets(
    skip: int = Query(0, ge=0, description="Itens a pular (paginação)"),
    limit: int = Query(10, ge=1, le=100, description="Limite de itens a retornar"),
    status: Optional[str] = Query(None, description="Filtrar por status (uploaded, processed)"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Lista as planilhas do usuário atual.
    
    Retorna uma lista paginada de planilhas enviadas pelo usuário,
    com opção de filtrar por status.
    
    - **skip**: Número de itens a pular (para paginação)
    - **limit**: Número máximo de itens a retornar
    - **status**: Filtrar por status (uploaded, processed)
    
    Exemplo de chamada:
    ```
    curl -X GET "http://localhost:8000/api/spreadsheets/?skip=0&limit=10&status=processed" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    # Monta a query
    query = {"user_id": str(current_user.id)}
    
    # Adiciona filtro por status
    if status:
        if status == "processed":
            query["processed"] = True
        elif status == "uploaded":
            query["processed"] = False
    
    # Conta o total de documentos
    total = await db["spreadsheets"].count_documents(query)
    
    # Obtém os documentos com paginação
    cursor = db["spreadsheets"].find(query).sort("upload_date", -1).skip(skip).limit(limit)
    spreadsheets = await cursor.to_list(length=limit)
    
    # Formata a resposta
    spreadsheet_list = []
    for sheet in spreadsheets:
        spreadsheet_list.append({
            "id": str(sheet["_id"]),
            "filename": sheet["filename"],
            "upload_date": sheet["upload_date"],
            "size": sheet["size"],
            "status": "processed" if sheet.get("processed", False) else "uploaded",
            "message": "Planilha processada" if sheet.get("processed", False) else "Planilha não processada",
            "user_id": sheet["user_id"],
            "description": sheet.get("description")
        })
    
    return {
        "total": total,
        "spreadsheets": spreadsheet_list
    }


@router.get("/{spreadsheet_id}", response_model=SpreadsheetUploadResponse)
async def get_spreadsheet(
    spreadsheet_id: str = Path(..., description="ID da planilha"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Obtém detalhes de uma planilha específica.
    
    Retorna informações detalhadas sobre uma planilha específica.
    
    - **spreadsheet_id**: ID da planilha a consultar
    
    Exemplo de chamada:
    ```
    curl -X GET "http://localhost:8000/api/spreadsheets/60d9b5e7d2a68c001f45e125" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    spreadsheet = await db["spreadsheets"].find_one({"_id": ObjectId(spreadsheet_id)})
    if not spreadsheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planilha não encontrada"
        )
    
    # Verifica se pertence ao usuário
    if spreadsheet.get("user_id") != str(current_user.id) and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar esta planilha"
        )
    
    return {
        "id": str(spreadsheet["_id"]),
        "filename": spreadsheet["filename"],
        "upload_date": spreadsheet["upload_date"],
        "size": spreadsheet["size"],
        "status": "processed" if spreadsheet.get("processed", False) else "uploaded",
        "message": "Planilha processada" if spreadsheet.get("processed", False) else "Planilha não processada",
        "user_id": spreadsheet["user_id"],
        "description": spreadsheet.get("description")
    }


@router.delete("/{spreadsheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spreadsheet(
    spreadsheet_id: str = Path(..., description="ID da planilha a ser excluída"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Exclui uma planilha e seus dados associados.
    
    Remove permanentemente uma planilha e todos os dados financeiros associados a ela.
    
    - **spreadsheet_id**: ID da planilha a ser excluída
    
    Exemplo de chamada:
    ```
    curl -X DELETE "http://localhost:8000/api/spreadsheets/60d9b5e7d2a68c001f45e125" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    # Busca a planilha
    spreadsheet = await db["spreadsheets"].find_one({"_id": ObjectId(spreadsheet_id)})
    if not spreadsheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planilha não encontrada"
        )
    
    # Verifica se pertence ao usuário
    if spreadsheet.get("user_id") != str(current_user.id) and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para excluir esta planilha"
        )
    
    # Exclui os dados financeiros associados
    await db["financial_data"].delete_many({"spreadsheet_id": spreadsheet_id})
    
    # Exclui cenários associados a esses dados financeiros
    if "financial_data_id" in spreadsheet:
        await db["scenarios"].delete_many({"financial_data_id": spreadsheet["financial_data_id"]})
    
    # Exclui o arquivo físico
    if os.path.exists(spreadsheet["path"]):
        os.remove(spreadsheet["path"])
    
    # Exclui o registro no banco de dados
    await db["spreadsheets"].delete_one({"_id": ObjectId(spreadsheet_id)})
    
    # Não retorna conteúdo (204 No Content)


@router.get("/export/{spreadsheet_id}", status_code=status.HTTP_200_OK)
async def export_processed_spreadsheet(
    spreadsheet_id: str = Path(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(),
) -> FileResponse:
    """
    Exporta os dados processados de uma planilha para um novo arquivo Excel.
    
    Args:
        spreadsheet_id: ID da planilha no banco de dados
        current_user: Usuário autenticado atual
        db: Conexão com o banco de dados
        
    Returns:
        Arquivo Excel processado para download
    """
    try:
        # Busca informações da planilha no banco de dados
        spreadsheet = await db.spreadsheets.find_one({"_id": ObjectId(spreadsheet_id)})
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planilha não encontrada"
            )
        
        # Verifica se a planilha pertence ao usuário
        if spreadsheet.get("user_id") != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar esta planilha"
            )
        
        # Verifica se a planilha foi processada
        if not spreadsheet.get("processed", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta planilha ainda não foi processada"
            )
        
        # Cria instância do processador
        processor = ExcelProcessor(spreadsheet["path"])
        
        # Lê e processa a planilha
        processor.read_excel()
        processor.extract_financial_data()
        
        # Cria um arquivo temporário para a exportação
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            output_path = tmp.name
        
        # Exporta os dados processados
        export_info = processor.export_processed_data(output_path)
        
        # Retorna o arquivo para download
        return FileResponse(
            path=output_path,
            filename=f"processed_{spreadsheet['filename']}",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao exportar a planilha: {str(e)}"
        )


@router.get("/check-integrity", status_code=status.HTTP_200_OK)
async def check_file_integrity(
    file_path: str = Query(...),
    current_user: UserModel = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Verifica a integridade de um arquivo Excel sem processá-lo completamente.
    
    Args:
        file_path: Caminho para o arquivo Excel a ser verificado
        current_user: Usuário autenticado atual
        
    Returns:
        Resultado da verificação de integridade
    """
    try:
        # Garantir que o arquivo está na pasta de uploads do usuário
        user_upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
        file_path_obj = Path(file_path)
        
        # Verificação de segurança para evitar path traversal
        if not str(file_path_obj).startswith(str(user_upload_dir)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado a este arquivo"
            )
        
        # Verifica a integridade
        integrity_result = ExcelProcessor.check_file_integrity(file_path)
        
        return integrity_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar integridade: {str(e)}"
        )