"""
Testes unitários para o ScenarioGenerator.

Este módulo contém testes para validar o funcionamento do gerador de cenários financeiros,
verificando a geração de diferentes tipos de cenários e os cálculos correspondentes.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, PropertyMock
from copy import deepcopy

from app.services.scenario_generator import ScenarioGenerator, ScenarioType
from app.utils.excel_processor import ExcelProcessor, FinancialCategory


@pytest.fixture
def sample_financial_data():
    """Fixture que cria dados financeiros de exemplo para os testes."""
    # Dados financeiros em formato de dicionário com DataFrames
    financial_data = {}
    
    # DataFrame de receitas
    financial_data[FinancialCategory.REVENUE.value] = pd.DataFrame({
        'Descrição': ['Produto A', 'Produto B', 'Serviço X'],
        'Jan': [100000, 150000, 50000],
        'Fev': [105000, 155000, 52000],
        'Mar': [110000, 160000, 55000]
    })
    
    # DataFrame de custos variáveis
    financial_data[FinancialCategory.VARIABLE_COSTS.value] = pd.DataFrame({
        'Descrição': ['Custo A', 'Custo B', 'Custo C'],
        'Jan': [40000, 30000, 20000],
        'Fev': [42000, 31000, 21000],
        'Mar': [44000, 32000, 22000]
    })
    
    # DataFrame de despesas de pessoal
    financial_data[FinancialCategory.PERSONNEL_EXPENSES.value] = pd.DataFrame({
        'Descrição': ['Salários', 'Benefícios', 'Encargos'],
        'Jan': [50000, 15000, 20000],
        'Fev': [50000, 15000, 20000],
        'Mar': [50000, 15000, 20000]
    })
    
    # DataFrame de despesas administrativas
    financial_data[FinancialCategory.ADMIN_EXPENSES.value] = pd.DataFrame({
        'Descrição': ['Aluguel', 'Utilities', 'Materiais'],
        'Jan': [15000, 5000, 2000],
        'Fev': [15000, 5500, 2100],
        'Mar': [15000, 6000, 2200]
    })
    
    # DataFrame de investimentos
    financial_data[FinancialCategory.INVESTMENTS.value] = pd.DataFrame({
        'Descrição': ['Equipamentos', 'Marketing', 'P&D'],
        'Jan': [20000, 10000, 5000],
        'Fev': [5000, 12000, 5000],
        'Mar': [10000, 15000, 5000]
    })
    
    return financial_data


@pytest.fixture
def excel_processor_mock(sample_financial_data):
    """Fixture que cria um mock do ExcelProcessor."""
    mock = MagicMock(spec=ExcelProcessor)
    # Define o retorno da propriedade financial_data
    type(mock).financial_data = PropertyMock(return_value=sample_financial_data)
    
    # Define os valores de metadados
    mock.metadata = {
        "processing_date": "2023-05-15T10:00:00",
        "categories_found": [
            FinancialCategory.REVENUE,
            FinancialCategory.VARIABLE_COSTS,
            FinancialCategory.PERSONNEL_EXPENSES,
            FinancialCategory.ADMIN_EXPENSES,
            FinancialCategory.INVESTMENTS
        ]
    }
    
    return mock


@pytest.fixture
def scenario_generator(excel_processor_mock):
    """Fixture que cria uma instância do ScenarioGenerator com um ExcelProcessor mockado."""
    return ScenarioGenerator(excel_processor_mock)


def test_initialize_scenario_generator(excel_processor_mock):
    """Testa a inicialização correta do ScenarioGenerator."""
    generator = ScenarioGenerator(excel_processor_mock)
    
    # Verifica se os dados financeiros foram recebidos corretamente
    assert generator.financial_data is not None
    assert len(generator.financial_data) > 0
    
    # Verifica se os cenários estão vazios inicialmente
    assert generator.scenarios == {}
    
    # Verifica se os metadados foram inicializados corretamente
    assert "generation_date" in generator.metadata
    assert "scenarios_generated" in generator.metadata
    assert "base_metadata" in generator.metadata


def test_generate_realistic_scenario(scenario_generator):
    """Testa a geração de um cenário realista."""
    # Gera o cenário
    scenario_data = scenario_generator.generate_realistic_scenario()
    
    # Verifica se o cenário foi gerado e armazenado
    assert ScenarioType.REALISTIC in scenario_generator.scenarios
    assert scenario_data is not None
    
    # Verifica se todas as categorias do dataset original estão presentes
    original_categories = set(scenario_generator.financial_data.keys())
    scenario_categories = set(scenario_data.keys())
    assert original_categories.issubset(scenario_categories)
    
    # Verifica se os valores continuam os mesmos (cenário realista não altera valores)
    for category in original_categories:
        orig_df = scenario_generator.financial_data[category]
        scen_df = scenario_data[category]
        
        # Verifica se as colunas numéricas têm os mesmos valores
        for col in orig_df.select_dtypes(include=[np.number]).columns:
            np.testing.assert_array_almost_equal(
                orig_df[col].values, 
                scen_df[col].values
            )


def test_generate_pessimistic_scenario(scenario_generator):
    """Testa a geração de um cenário pessimista."""
    # Gera o cenário
    scenario_data = scenario_generator.generate_pessimistic_scenario()
    
    # Verifica se o cenário foi gerado e armazenado
    assert ScenarioType.PESSIMISTIC in scenario_generator.scenarios
    assert scenario_data is not None
    
    # No cenário pessimista:
    # - Receitas devem diminuir
    # - Custos e despesas devem aumentar
    
    # Verifica receitas
    original_revenue = scenario_generator.financial_data[FinancialCategory.REVENUE.value]
    pessimistic_revenue = scenario_data[FinancialCategory.REVENUE.value]
    
    numeric_cols = original_revenue.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Receitas devem ser menores no cenário pessimista
        assert pessimistic_revenue[col].sum() < original_revenue[col].sum()
    
    # Verifica custos e despesas
    for category in [FinancialCategory.VARIABLE_COSTS.value, FinancialCategory.ADMIN_EXPENSES.value]:
        if category in scenario_generator.financial_data:
            original_df = scenario_generator.financial_data[category]
            pessimistic_df = scenario_data[category]
            
            numeric_cols = original_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                # Custos e despesas devem ser maiores no cenário pessimista
                assert pessimistic_df[col].sum() > original_df[col].sum()


def test_generate_optimistic_scenario(scenario_generator):
    """Testa a geração de um cenário otimista."""
    # Gera o cenário
    scenario_data = scenario_generator.generate_optimistic_scenario()
    
    # Verifica se o cenário foi gerado e armazenado
    assert ScenarioType.OPTIMISTIC in scenario_generator.scenarios
    assert scenario_data is not None
    
    # No cenário otimista:
    # - Receitas devem aumentar
    # - Custos e despesas devem diminuir
    
    # Verifica receitas
    original_revenue = scenario_generator.financial_data[FinancialCategory.REVENUE.value]
    optimistic_revenue = scenario_data[FinancialCategory.REVENUE.value]
    
    numeric_cols = original_revenue.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Receitas devem ser maiores no cenário otimista
        assert optimistic_revenue[col].sum() > original_revenue[col].sum()
    
    # Verifica custos e despesas
    for category in [FinancialCategory.VARIABLE_COSTS.value, FinancialCategory.ADMIN_EXPENSES.value]:
        if category in scenario_generator.financial_data:
            original_df = scenario_generator.financial_data[category]
            optimistic_df = scenario_data[category]
            
            numeric_cols = original_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                # Custos e despesas devem ser menores no cenário otimista
                assert optimistic_df[col].sum() < original_df[col].sum()


def test_generate_aggressive_scenario(scenario_generator):
    """Testa a geração de um cenário agressivo."""
    # Gera o cenário
    scenario_data = scenario_generator.generate_aggressive_scenario()
    
    # Verifica se o cenário foi gerado e armazenado
    assert ScenarioType.AGGRESSIVE in scenario_generator.scenarios
    assert scenario_data is not None
    
    # No cenário agressivo:
    # - Receitas devem aumentar significativamente
    # - Investimentos devem aumentar
    
    # Verifica receitas
    original_revenue = scenario_generator.financial_data[FinancialCategory.REVENUE.value]
    aggressive_revenue = scenario_data[FinancialCategory.REVENUE.value]
    
    numeric_cols = original_revenue.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Receitas devem ser significativamente maiores no cenário agressivo (pelo menos 15% maior)
        assert aggressive_revenue[col].sum() >= original_revenue[col].sum() * 1.15
    
    # Verifica investimentos
    if FinancialCategory.INVESTMENTS.value in scenario_generator.financial_data:
        original_investments = scenario_generator.financial_data[FinancialCategory.INVESTMENTS.value]
        aggressive_investments = scenario_data[FinancialCategory.INVESTMENTS.value]
        
        numeric_cols = original_investments.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            # Investimentos devem ser maiores no cenário agressivo
            assert aggressive_investments[col].sum() > original_investments[col].sum()


def test_generate_all_scenarios(scenario_generator):
    """Testa a geração de todos os cenários."""
    # Gera todos os cenários
    scenarios = scenario_generator.generate_all_scenarios()
    
    # Verifica se todos os tipos de cenários foram gerados
    assert ScenarioType.REALISTIC in scenarios
    assert ScenarioType.PESSIMISTIC in scenarios
    assert ScenarioType.OPTIMISTIC in scenarios
    assert ScenarioType.AGGRESSIVE in scenarios
    
    # Verifica se os metadados foram atualizados
    assert len(scenario_generator.metadata["scenarios_generated"]) == 4
    assert ScenarioType.REALISTIC in scenario_generator.metadata["scenarios_generated"]
    assert ScenarioType.PESSIMISTIC in scenario_generator.metadata["scenarios_generated"]
    assert ScenarioType.OPTIMISTIC in scenario_generator.metadata["scenarios_generated"]
    assert ScenarioType.AGGRESSIVE in scenario_generator.metadata["scenarios_generated"]


def test_recalculate_derived_values(scenario_generator):
    """Testa o recálculo de valores derivados."""
    # Obtém os dados financeiros originais
    scenario_data = deepcopy(scenario_generator.financial_data)
    
    # Recalcula os valores derivados
    recalculated_data = scenario_generator._recalculate_derived_values(scenario_data)
    
    # Verifica se os valores derivados foram calculados corretamente
    assert FinancialCategory.CONTRIBUTION_MARGIN.value in recalculated_data
    assert FinancialCategory.CASH_FLOW.value in recalculated_data
    assert FinancialCategory.FINAL_BALANCE.value in recalculated_data
    
    # Verifica a margem de contribuição (receitas - custos variáveis)
    revenue = scenario_data[FinancialCategory.REVENUE.value]
    costs = scenario_data[FinancialCategory.VARIABLE_COSTS.value]
    margin = recalculated_data[FinancialCategory.CONTRIBUTION_MARGIN.value]
    
    numeric_cols = revenue.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        expected_margin = revenue[col].sum() - costs[col].sum()
        assert margin[col].sum() == pytest.approx(expected_margin)


def test_sum_category_values(scenario_generator):
    """Testa o cálculo da soma de valores por categoria."""
    # Dados para testar
    test_data = {
        FinancialCategory.REVENUE.value: pd.DataFrame({
            'Jan': [100, 200],
            'Fev': [150, 250]
        }),
        FinancialCategory.VARIABLE_COSTS.value: pd.DataFrame({
            'Jan': [50, 75],
            'Fev': [60, 80]
        })
    }
    
    # Categorias a somar
    categories = [FinancialCategory.REVENUE, FinancialCategory.VARIABLE_COSTS]
    
    # Colunas a somar
    columns = ['Jan', 'Fev']
    
    # Calcula a soma
    result = scenario_generator._sum_category_values(test_data, categories, columns)
    
    # Verifica se o resultado é um array do numpy
    assert isinstance(result, np.ndarray)
    
    # Verifica os valores
    expected = np.array([425, 540])  # Jan: 100+200+50+75, Fev: 150+250+60+80
    np.testing.assert_array_equal(result, expected)


def test_edge_cases(scenario_generator):
    """Testa o comportamento do gerador com casos de borda."""
    # Caso 1: Dados financeiros vazios
    empty_data = {}
    
    # Tenta recalcular valores derivados
    result = scenario_generator._recalculate_derived_values(empty_data)
    
    # Verifica se não houve erro e o resultado está vazio
    assert result == empty_data
    
    # Caso 2: Dados financeiros sem receitas
    no_revenue_data = {
        FinancialCategory.VARIABLE_COSTS.value: pd.DataFrame({
            'Jan': [50, 75],
            'Fev': [60, 80]
        })
    }
    
    # Tenta recalcular valores derivados
    result = scenario_generator._recalculate_derived_values(no_revenue_data)
    
    # Verifica se as categorias derivadas foram criadas mesmo sem receitas
    assert FinancialCategory.CONTRIBUTION_MARGIN.value in result
    assert FinancialCategory.CASH_FLOW.value in result
    assert FinancialCategory.FINAL_BALANCE.value in result


def test_update_dataframe_with_values(scenario_generator):
    """Testa a atualização de um DataFrame com valores calculados."""
    # Cria um DataFrame de teste
    df = pd.DataFrame(index=range(1))
    
    # Colunas e valores para atualizar
    columns = ['Jan', 'Fev', 'Mar']
    values = np.array([100, 200, 300])
    
    # Atualiza o DataFrame
    scenario_generator._update_dataframe_with_values(df, columns, values)
    
    # Verifica se as colunas foram adicionadas
    for col in columns:
        assert col in df.columns
    
    # Verifica se os valores foram definidos corretamente
    assert df['Jan'].iloc[0] == 100
    assert df['Fev'].iloc[0] == 200
    assert df['Mar'].iloc[0] == 300


def test_create_or_get_dataframe(scenario_generator):
    """Testa a criação ou obtenção de um DataFrame."""
    # Cria dados de teste
    test_data = {
        'existing_category': pd.DataFrame({
            'Descrição': ['Item 1', 'Item 2'],
            'Jan': [100, 200],
            'Fev': [150, 250]
        })
    }
    
    # Caso 1: Obter um DataFrame existente
    df1 = scenario_generator._create_or_get_dataframe(test_data, 'existing_category')
    assert df1 is test_data['existing_category']
    
    # Caso 2: Criar um novo DataFrame
    df2 = scenario_generator._create_or_get_dataframe(test_data, 'new_category')
    assert isinstance(df2, pd.DataFrame)
    assert df2.empty  # DataFrame deve estar vazio


def test_get_scenario_data(scenario_generator):
    """Testa a obtenção de dados de um cenário específico."""
    # Gera um cenário realista
    scenario_generator.generate_realistic_scenario()
    
    # Obtém os dados do cenário
    scenario_data = scenario_generator.get_scenario_data(ScenarioType.REALISTIC)
    
    # Verifica se os dados foram retornados corretamente
    assert scenario_data is not None
    assert isinstance(scenario_data, dict)
    assert len(scenario_data) > 0
    
    # Tenta obter dados de um cenário inexistente
    non_existent = scenario_generator.get_scenario_data("cenário_inexistente")
    assert non_existent is None


if __name__ == "__main__":
    pytest.main(["-v"]) 