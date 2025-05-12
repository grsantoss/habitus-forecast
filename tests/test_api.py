import pytest
from fastapi.testclient import TestClient
import io
import pandas as pd
import json

from app.main import app
from tests.test_excel_processor import create_test_excel


client = TestClient(app)


def test_root_endpoint():
    """
    Testa o endpoint raiz da API.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()


def test_get_financial_categories():
    """
    Testa o endpoint de obtenção de categorias financeiras.
    """
    response = client.get("/api/v1/financial/categories")
    assert response.status_code == 200
    
    # Verifica se a resposta contém categorias
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    
    # Verifica a estrutura de cada categoria
    for category in categories:
        assert "id" in category
        assert "name" in category
        assert "description" in category


def test_get_scenario_types():
    """
    Testa o endpoint de obtenção de tipos de cenários.
    """
    response = client.get("/api/v1/scenarios/types")
    assert response.status_code == 200
    
    # Verifica se a resposta contém tipos de cenários
    scenario_types = response.json()
    assert isinstance(scenario_types, list)
    assert len(scenario_types) > 0
    
    # Verifica a estrutura de cada tipo de cenário
    for scenario_type in scenario_types:
        assert "id" in scenario_type
        assert "name" in scenario_type
        assert "description" in scenario_type
    
    # Verifica se existem os quatro tipos de cenários
    scenario_ids = [s["id"] for s in scenario_types]
    assert "realistic" in scenario_ids
    assert "pessimistic" in scenario_ids
    assert "optimistic" in scenario_ids
    assert "aggressive" in scenario_ids


def test_upload_financial_data():
    """
    Testa o endpoint de upload de dados financeiros.
    """
    # Cria um arquivo Excel fictício
    excel_data = create_test_excel()
    
    # Faz o upload do arquivo
    response = client.post(
        "/api/v1/financial/upload",
        files={"file": ("test.xlsx", excel_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 201
    
    # Verifica a estrutura da resposta
    response_data = response.json()
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert "categories" in response_data
    assert "metadata" in response_data


def test_generate_scenario():
    """
    Testa o endpoint de geração de cenários.
    """
    # Primeiro, faz upload de dados financeiros para ter algo para gerar cenários
    excel_data = create_test_excel()
    upload_response = client.post(
        "/api/v1/financial/upload",
        files={"file": ("test.xlsx", excel_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    financial_data = upload_response.json()["data"]
    
    # Requisição para gerar um cenário realista
    scenario_request = {
        "financial_data": financial_data,
        "scenario_type": "realista",
        "parameters": None
    }
    
    response = client.post(
        "/api/v1/scenarios/generate",
        json=scenario_request
    )
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 200
    
    # Verifica a estrutura da resposta
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["scenario_type"] == "realista"
    assert "data" in response_data
    assert "metrics" in response_data 