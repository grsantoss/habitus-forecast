"""
Testes unitários para o ExcelProcessor.

Este módulo contém testes para validar o funcionamento do processador de planilhas Excel,
verificando a leitura de arquivos, validação de estrutura e tratamento de erros.
"""

import pytest
import pandas as pd
import os
import io
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.utils.excel_processor import ExcelProcessor, ExcelValidationError, FinancialCategory


@pytest.fixture
def valid_excel_data():
    """Fixture que cria dados de Excel válidos em formato de bytes."""
    # Cria DataFrames para cada categoria financeira
    revenue_df = pd.DataFrame({
        'Descrição': ['Venda Produto A', 'Venda Produto B', 'Serviço X'],
        'Janeiro': [10000, 15000, 5000],
        'Fevereiro': [12000, 16000, 5500],
        'Março': [13000, 17000, 6000]
    })
    
    costs_df = pd.DataFrame({
        'Descrição': ['Matéria Prima A', 'Matéria Prima B', 'Embalagem'],
        'Janeiro': [3000, 4000, 1000],
        'Fevereiro': [3200, 4200, 1100],
        'Março': [3500, 4500, 1200]
    })
    
    expenses_df = pd.DataFrame({
        'Descrição': ['Salários', 'Aluguel', 'Marketing'],
        'Janeiro': [7000, 3000, 2000],
        'Fevereiro': [7000, 3000, 2500],
        'Março': [7000, 3000, 3000]
    })
    
    # Cria um arquivo Excel em memória com múltiplas planilhas
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        revenue_df.to_excel(writer, sheet_name='Receitas', index=False)
        costs_df.to_excel(writer, sheet_name='Custos Variáveis', index=False)
        expenses_df.to_excel(writer, sheet_name='Despesas', index=False)
    
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def invalid_excel_data():
    """Fixture que cria dados de Excel inválidos (sem estrutura adequada)."""
    # Cria um DataFrame sem dados financeiros
    invalid_df = pd.DataFrame({
        'Coluna A': ['Dado 1', 'Dado 2', 'Dado 3'],
        'Coluna B': ['Valor 1', 'Valor 2', 'Valor 3'],
    })
    
    # Cria um arquivo Excel em memória
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        invalid_df.to_excel(writer, sheet_name='Planilha Inválida', index=False)
    
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def empty_excel_data():
    """Fixture que cria dados de Excel vazios."""
    # Cria um DataFrame vazio
    empty_df = pd.DataFrame()
    
    # Cria um arquivo Excel em memória
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        empty_df.to_excel(writer, sheet_name='Planilha Vazia')
    
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def excel_processor():
    """Fixture que cria uma instância do ExcelProcessor."""
    return ExcelProcessor()


def test_process_valid_excel_data(excel_processor, valid_excel_data):
    """Testa o processamento de um arquivo Excel válido."""
    # Processa os dados
    result = excel_processor.process_excel_data(valid_excel_data)
    
    # Verifica se o resultado tem status de sucesso
    assert result["status"] == "success"
    assert "Dados financeiros processados com sucesso" in result["message"]
    
    # Verifica se as categorias foram encontradas
    assert len(result["categories"]) > 0
    
    # Verifica se os dados foram extraídos
    assert len(excel_processor.financial_data) > 0
    
    # Verifica se os metadados foram atualizados
    assert len(excel_processor.metadata["sheet_names"]) == 3
    assert len(excel_processor.metadata["categories_found"]) > 0


def test_validate_excel_structure(excel_processor, valid_excel_data, invalid_excel_data):
    """Testa a validação da estrutura do arquivo Excel."""
    # Testa com dados válidos
    excel_processor.process_excel_data(valid_excel_data)
    assert len(excel_processor.metadata["categories_found"]) > 0
    
    # Reinicia o processador
    excel_processor = ExcelProcessor()
    
    # Testa com dados inválidos
    with pytest.raises(ExcelValidationError):
        # Este deve falhar na validação de dados financeiros
        excel_processor.process_excel_data(invalid_excel_data)


def test_empty_excel_file(excel_processor, empty_excel_data):
    """Testa o comportamento com um arquivo Excel vazio."""
    with pytest.raises(ExcelValidationError) as excinfo:
        excel_processor.process_excel_data(empty_excel_data)
    
    # Verifica a mensagem de erro
    assert "não contém dados válidos" in str(excinfo.value)


def test_invalid_file_format(excel_processor):
    """Testa o comportamento com um arquivo que não é Excel."""
    # Cria dados inválidos (não é um arquivo Excel)
    invalid_data = b"Este não é um arquivo Excel"
    
    with pytest.raises(ExcelValidationError) as excinfo:
        excel_processor.process_excel_data(invalid_data)
    
    # Verifica a mensagem de erro
    assert "Erro ao ler arquivo Excel" in str(excinfo.value)


def test_category_identification(excel_processor, valid_excel_data):
    """Testa a identificação correta das categorias financeiras."""
    # Processa os dados
    excel_processor.process_excel_data(valid_excel_data)
    
    # Verifica se as categorias foram identificadas corretamente
    categories_found = [cat.value for cat in excel_processor.metadata["categories_found"]]
    
    # Deve encontrar pelo menos receitas e custos
    assert FinancialCategory.REVENUE.value in categories_found
    assert FinancialCategory.VARIABLE_COSTS.value in categories_found


def test_financial_data_extraction(excel_processor, valid_excel_data):
    """Testa a extração correta dos dados financeiros."""
    # Processa os dados
    excel_processor.process_excel_data(valid_excel_data)
    
    # Verifica se os dados financeiros foram extraídos
    assert FinancialCategory.REVENUE.value in excel_processor.financial_data
    assert FinancialCategory.VARIABLE_COSTS.value in excel_processor.financial_data
    
    # Verifica os dados de receita
    revenue_data = excel_processor.financial_data[FinancialCategory.REVENUE.value]
    assert isinstance(revenue_data, pd.DataFrame)
    assert "Janeiro" in revenue_data.columns
    assert "Fevereiro" in revenue_data.columns
    assert "Março" in revenue_data.columns
    
    # Verifica se os valores são numéricos
    assert pd.api.types.is_numeric_dtype(revenue_data["Janeiro"])
    
    # Verifica se os totais foram calculados corretamente
    total_revenue_jan = revenue_data["Janeiro"].sum()
    assert total_revenue_jan == 30000  # 10000 + 15000 + 5000


@patch('app.utils.excel_processor.pd.read_excel')
def test_excel_reading_error(mock_read_excel, excel_processor):
    """Testa o tratamento de erros na leitura do Excel."""
    # Configura o mock para lançar uma exceção
    mock_read_excel.side_effect = Exception("Erro simulado na leitura do Excel")
    
    # Tenta processar os dados
    with pytest.raises(ExcelValidationError) as excinfo:
        excel_processor.process_excel_data(b"dummy data")
    
    # Verifica a mensagem de erro
    assert "Erro ao ler arquivo Excel" in str(excinfo.value)


def test_excel_format_category_name(excel_processor):
    """Testa a formatação de nomes de categorias."""
    # Testa várias categorias
    assert excel_processor._format_category_name("receitas") == "Receitas"
    assert excel_processor._format_category_name("custos_variaveis") == "Custos Variaveis"
    assert excel_processor._format_category_name("despesas_pessoal") == "Despesas Pessoal"


@pytest.mark.integration
def test_full_process_workflow(excel_processor, valid_excel_data):
    """Teste de integração para verificar o fluxo completo de processamento."""
    # Processa os dados
    result = excel_processor.process_excel_data(valid_excel_data)
    
    # Verifica metadados
    assert excel_processor.metadata["total_sheets"] == 3
    assert "processing_date" in excel_processor.metadata
    
    # Verifica categorias
    categories = [cat["id"] for cat in result["categories"]]
    assert "receitas" in categories
    assert "custos_variaveis" in categories
    
    # Verifica dados
    assert "receitas" in result["data"]
    assert "custos_variaveis" in result["data"]


if __name__ == "__main__":
    pytest.main(["-v"])