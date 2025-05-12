#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para validação de dados durante e após a migração.
Este utilitário valida a estrutura de dados de usuários, dados financeiros e cenários,
verifica relacionamentos entre entidades e fornece estatísticas detalhadas de validação.
"""

import datetime
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import bson
from bson import ObjectId

logger = logging.getLogger("data_validator")

# Esquemas de validação para cada tipo de coleção
SCHEMAS = {
    "users": {
        "required_fields": [
            "_id", "email", "password", "name", "created_at", "updated_at", "is_active"
        ],
        "field_types": {
            "_id": (ObjectId, str),
            "email": str,
            "password": str,
            "name": str,
            "created_at": datetime.datetime,
            "updated_at": datetime.datetime,
            "is_active": bool,
            "role": str,
            "settings": dict,
            "last_login": (datetime.datetime, type(None))
        },
        "string_patterns": {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        }
    },
    "financial_data": {
        "required_fields": [
            "_id", "user_id", "title", "amount", "date", "created_at", "updated_at"
        ],
        "field_types": {
            "_id": (ObjectId, str),
            "user_id": (ObjectId, str),
            "title": str,
            "type": str,
            "amount": (float, int),
            "date": datetime.datetime,
            "category": str,
            "description": (str, type(None)),
            "created_at": datetime.datetime,
            "updated_at": datetime.datetime,
            "tags": (list, type(None)),
            "is_recurring": bool,
            "recurring_details": (dict, type(None))
        }
    },
    "scenarios": {
        "required_fields": [
            "_id", "user_id", "name", "created_at", "updated_at"
        ],
        "field_types": {
            "_id": (ObjectId, str),
            "user_id": (ObjectId, str),
            "name": str,
            "description": (str, type(None)),
            "assumptions": (dict, type(None)),
            "created_at": datetime.datetime,
            "updated_at": datetime.datetime,
            "projections": (list, type(None)),
            "is_template": bool,
            "tags": (list, type(None))
        }
    }
}

def validate_data_structure(
    document: Dict[str, Any], 
    collection_name: str
) -> Tuple[bool, List[str]]:
    """
    Valida a estrutura de um documento de acordo com o esquema definido.
    
    Args:
        document: Documento a ser validado
        collection_name: Nome da coleção a que o documento pertence
        
    Returns:
        Tuple[bool, List[str]]: (é_válido, lista_de_problemas)
    """
    issues = []
    
    # Verifica se o esquema existe para esta coleção
    if collection_name not in SCHEMAS:
        issues.append(f"Esquema de validação não definido para a coleção {collection_name}")
        return False, issues
    
    schema = SCHEMAS[collection_name]
    
    # Valida campos obrigatórios
    for field in schema["required_fields"]:
        if field not in document:
            issues.append(f"Campo obrigatório ausente: {field}")
    
    # Valida tipos de campos
    for field, expected_type in schema["field_types"].items():
        if field in document and document[field] is not None:
            if isinstance(expected_type, tuple):
                # Múltiplos tipos possíveis
                if not any(isinstance(document[field], t) for t in expected_type):
                    actual_type = type(document[field]).__name__
                    expected_types = [t.__name__ for t in expected_type]
                    issues.append(f"Tipo inválido para {field}: esperado {expected_types}, recebido {actual_type}")
            else:
                # Tipo único esperado
                if not isinstance(document[field], expected_type):
                    actual_type = type(document[field]).__name__
                    issues.append(f"Tipo inválido para {field}: esperado {expected_type.__name__}, recebido {actual_type}")
    
    # Valida padrões de string
    if "string_patterns" in schema:
        for field, pattern in schema["string_patterns"].items():
            if field in document and isinstance(document[field], str):
                if not re.match(pattern, document[field]):
                    issues.append(f"Padrão inválido para {field}: '{document[field]}' não corresponde a '{pattern}'")
    
    # Validações específicas por coleção
    if collection_name == "financial_data":
        # Verificações específicas para dados financeiros
        if "amount" in document and document["amount"] < 0 and document.get("type") != "expense":
            issues.append(f"Valor negativo ({document['amount']}) para tipo diferente de despesa: {document.get('type')}")
    
    # Retorna resultado da validação
    return len(issues) == 0, issues

def validate_relationships(
    db: Any, 
    sample_size: int = 100
) -> Dict[str, Any]:
    """
    Valida os relacionamentos entre entidades.
    
    Args:
        db: Conexão com o banco de dados
        sample_size: Tamanho da amostra para validação
        
    Returns:
        Dict: Relatório de validação
    """
    report = {
        "orphaned_data": {
            "financial_data": 0,
            "scenarios": 0
        },
        "invalid_references": {
            "financial_data_user": 0,
            "scenarios_user": 0
        },
        "sample_size": sample_size,
        "errors": []
    }
    
    # Valida relacionamento entre dados financeiros e usuários
    financial_sample = list(db.financial_data.aggregate([
        {"$sample": {"size": sample_size}}
    ]))
    
    for data in financial_sample:
        user_id = data.get("user_id")
        if not user_id:
            report["orphaned_data"]["financial_data"] += 1
            report["errors"].append(f"Dados financeiros órfãos: ID {data['_id']}")
            continue
        
        # Verifica se o usuário existe
        user = db.users.find_one({"_id": user_id})
        if not user:
            report["invalid_references"]["financial_data_user"] += 1
            report["errors"].append(f"Referência inválida: dados financeiros {data['_id']} -> usuário {user_id}")
    
    # Valida relacionamento entre cenários e usuários
    scenarios_sample = list(db.scenarios.aggregate([
        {"$sample": {"size": sample_size}}
    ]))
    
    for scenario in scenarios_sample:
        user_id = scenario.get("user_id")
        if not user_id:
            report["orphaned_data"]["scenarios"] += 1
            report["errors"].append(f"Cenário órfão: ID {scenario['_id']}")
            continue
        
        # Verifica se o usuário existe
        user = db.users.find_one({"_id": user_id})
        if not user:
            report["invalid_references"]["scenarios_user"] += 1
            report["errors"].append(f"Referência inválida: cenário {scenario['_id']} -> usuário {user_id}")
    
    return report

def validate_users(
    db: Any, 
    validate_all: bool = False
) -> Dict[str, Any]:
    """
    Valida a integridade dos dados de usuários.
    
    Args:
        db: Conexão com o banco de dados
        validate_all: Se True, valida todos os usuários; caso contrário, amostra aleatória
        
    Returns:
        Dict: Relatório de validação
    """
    report = {
        "total_users": db.users.count_documents({}),
        "valid_users": 0,
        "invalid_users": 0,
        "issues": {
            "missing_fields": 0,
            "invalid_types": 0,
            "invalid_email": 0,
            "other_issues": 0
        },
        "samples": []
    }
    
    # Define o pipeline de agregação
    pipeline = []
    if not validate_all:
        # Limita a 100 usuários aleatórios se não validar todos
        pipeline.append({"$sample": {"size": 100}})
    
    users = db.users.aggregate(pipeline)
    
    for user in users:
        is_valid, issues = validate_data_structure(user, "users")
        
        if is_valid:
            report["valid_users"] += 1
        else:
            report["invalid_users"] += 1
            
            # Categoriza os problemas
            for issue in issues:
                if "obrigatório ausente" in issue:
                    report["issues"]["missing_fields"] += 1
                elif "Tipo inválido" in issue:
                    report["issues"]["invalid_types"] += 1
                elif "email" in issue.lower():
                    report["issues"]["invalid_email"] += 1
                else:
                    report["issues"]["other_issues"] += 1
            
            # Adiciona amostra de problemas (limitada a 10)
            if len(report["samples"]) < 10:
                report["samples"].append({
                    "user_id": str(user["_id"]),
                    "issues": issues
                })
    
    return report

def validate_financial_data(
    db: Any, 
    validate_all: bool = False
) -> Dict[str, Any]:
    """
    Valida a integridade dos dados financeiros.
    
    Args:
        db: Conexão com o banco de dados
        validate_all: Se True, valida todos os dados; caso contrário, amostra aleatória
        
    Returns:
        Dict: Relatório de validação
    """
    report = {
        "total_records": db.financial_data.count_documents({}),
        "valid_records": 0,
        "invalid_records": 0,
        "issues": {
            "missing_fields": 0,
            "invalid_types": 0,
            "invalid_values": 0,
            "orphaned_records": 0,
            "other_issues": 0
        },
        "samples": []
    }
    
    # Define o pipeline de agregação
    pipeline = []
    if not validate_all:
        # Limita a 100 registros aleatórios se não validar todos
        pipeline.append({"$sample": {"size": 100}})
    
    records = db.financial_data.aggregate(pipeline)
    
    for record in records:
        is_valid, issues = validate_data_structure(record, "financial_data")
        
        # Verifica se o registro está órfão (sem usuário correspondente)
        has_user = db.users.find_one({"_id": record.get("user_id")}) is not None
        
        if is_valid and has_user:
            report["valid_records"] += 1
        else:
            report["invalid_records"] += 1
            
            # Categoriza os problemas
            if not has_user:
                report["issues"]["orphaned_records"] += 1
                issues.append(f"Registro órfão: usuário {record.get('user_id')} não encontrado")
            
            for issue in issues:
                if "obrigatório ausente" in issue:
                    report["issues"]["missing_fields"] += 1
                elif "Tipo inválido" in issue:
                    report["issues"]["invalid_types"] += 1
                elif "Valor" in issue or "valor" in issue:
                    report["issues"]["invalid_values"] += 1
                elif "órfão" not in issue:  # Já contabilizado
                    report["issues"]["other_issues"] += 1
            
            # Adiciona amostra de problemas (limitada a 10)
            if len(report["samples"]) < 10:
                report["samples"].append({
                    "record_id": str(record["_id"]),
                    "issues": issues
                })
    
    return report

def validate_scenarios(
    db: Any, 
    validate_all: bool = False
) -> Dict[str, Any]:
    """
    Valida a integridade dos cenários financeiros.
    
    Args:
        db: Conexão com o banco de dados
        validate_all: Se True, valida todos os cenários; caso contrário, amostra aleatória
        
    Returns:
        Dict: Relatório de validação
    """
    report = {
        "total_scenarios": db.scenarios.count_documents({}),
        "valid_scenarios": 0,
        "invalid_scenarios": 0,
        "issues": {
            "missing_fields": 0,
            "invalid_types": 0,
            "orphaned_scenarios": 0,
            "other_issues": 0
        },
        "samples": []
    }
    
    # Define o pipeline de agregação
    pipeline = []
    if not validate_all:
        # Limita a 100 cenários aleatórios se não validar todos
        pipeline.append({"$sample": {"size": 100}})
    
    scenarios = db.scenarios.aggregate(pipeline)
    
    for scenario in scenarios:
        is_valid, issues = validate_data_structure(scenario, "scenarios")
        
        # Verifica se o cenário está órfão (sem usuário correspondente)
        has_user = db.users.find_one({"_id": scenario.get("user_id")}) is not None
        
        if is_valid and has_user:
            report["valid_scenarios"] += 1
        else:
            report["invalid_scenarios"] += 1
            
            # Categoriza os problemas
            if not has_user:
                report["issues"]["orphaned_scenarios"] += 1
                issues.append(f"Cenário órfão: usuário {scenario.get('user_id')} não encontrado")
            
            for issue in issues:
                if "obrigatório ausente" in issue:
                    report["issues"]["missing_fields"] += 1
                elif "Tipo inválido" in issue:
                    report["issues"]["invalid_types"] += 1
                elif "órfão" not in issue:  # Já contabilizado
                    report["issues"]["other_issues"] += 1
            
            # Adiciona amostra de problemas (limitada a 10)
            if len(report["samples"]) < 10:
                report["samples"].append({
                    "scenario_id": str(scenario["_id"]),
                    "issues": issues
                })
    
    return report

def generate_validation_report(db: Any) -> Dict[str, Any]:
    """
    Gera um relatório completo de validação dos dados.
    
    Args:
        db: Conexão com o banco de dados
        
    Returns:
        Dict: Relatório completo de validação
    """
    logger.info("Gerando relatório de validação...")
    
    # Inicia relatório completo
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "database": db.name,
        "collections": {
            "users": db.users.count_documents({}),
            "financial_data": db.financial_data.count_documents({}),
            "scenarios": db.scenarios.count_documents({})
        },
        "validation": {
            "users": validate_users(db, validate_all=False),
            "financial_data": validate_financial_data(db, validate_all=False),
            "scenarios": validate_scenarios(db, validate_all=False)
        },
        "relationships": validate_relationships(db, sample_size=100)
    }
    
    # Calcula estatísticas gerais
    total_records = sum(report["collections"].values())
    total_valid = (report["validation"]["users"]["valid_users"] +
                  report["validation"]["financial_data"]["valid_records"] +
                  report["validation"]["scenarios"]["valid_scenarios"])
    total_invalid = (report["validation"]["users"]["invalid_users"] +
                    report["validation"]["financial_data"]["invalid_records"] +
                    report["validation"]["scenarios"]["invalid_scenarios"])
    
    report["summary"] = {
        "total_records": total_records,
        "valid_records_pct": (total_valid / (total_valid + total_invalid)) * 100 if (total_valid + total_invalid) > 0 else 0,
        "invalid_records": total_invalid,
        "orphaned_data": sum(report["relationships"]["orphaned_data"].values()),
        "invalid_references": sum(report["relationships"]["invalid_references"].values())
    }
    
    logger.info(f"Relatório de validação concluído. Taxa de validação: {report['summary']['valid_records_pct']:.2f}%")
    
    return report

def save_validation_report(report: Dict[str, Any], filename: str = None) -> str:
    """
    Salva o relatório de validação em um arquivo JSON.
    
    Args:
        report: Relatório de validação
        filename: Nome do arquivo (opcional)
        
    Returns:
        str: Caminho do arquivo de relatório
    """
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_report_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"Relatório de validação salvo em {filename}")
    return filename 