"""
Serviço de geração de cenários financeiros para o Habitus Forecast.

Este módulo contém funcionalidades para criar diferentes cenários financeiros
baseados em dados extraídos de planilhas Excel, incluindo projeções realistas,
pessimistas, otimistas e agressivas.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import logging
from copy import deepcopy

from app.utils.excel_processor import ExcelProcessor, FinancialCategory

# Configurar logger
logger = logging.getLogger(__name__)


class ScenarioType:
    """Tipos de cenários disponíveis."""
    REALISTIC = "realista"
    PESSIMISTIC = "pessimista"
    OPTIMISTIC = "otimista"
    AGGRESSIVE = "agressivo"


class ScenarioGenerator:
    """
    Gerador de cenários financeiros para o Habitus Forecast.
    
    Esta classe utiliza os dados financeiros processados pelo ExcelProcessor
    para gerar diferentes cenários de análise financeira, incluindo:
    - Realista: baseado nos dados atuais
    - Pessimista: redução de receitas e aumento de despesas
    - Otimista: aumento de receitas e redução de despesas
    - Agressivo: crescimento exponencial de receitas e aumento de investimentos
    
    Attributes:
        excel_processor (ExcelProcessor): Instância do processador de planilhas Excel.
        financial_data (Dict[str, pd.DataFrame]): Dados financeiros extraídos.
        scenarios (Dict[str, Dict[str, pd.DataFrame]]): Cenários gerados.
        metadata (Dict[str, Any]): Metadados dos cenários gerados.
    """
    
    # Categorias que representam receitas/entradas
    REVENUE_CATEGORIES = [FinancialCategory.REVENUE]
    
    # Categorias que representam custos variáveis
    VARIABLE_COST_CATEGORIES = [FinancialCategory.VARIABLE_COSTS]
    
    # Categorias que representam despesas fixas
    FIXED_EXPENSE_CATEGORIES = [
        FinancialCategory.PERSONNEL_EXPENSES,
        FinancialCategory.COMMERCIAL_EXPENSES,
        FinancialCategory.ADMIN_EXPENSES
    ]
    
    # Categorias que representam investimentos
    INVESTMENT_CATEGORIES = [FinancialCategory.INVESTMENTS]
    
    # Categorias calculadas
    CALCULATED_CATEGORIES = [
        FinancialCategory.CONTRIBUTION_MARGIN,
        FinancialCategory.CASH_FLOW,
        FinancialCategory.FINAL_BALANCE
    ]
    
    def __init__(self, excel_processor: ExcelProcessor):
        """
        Inicializa o gerador de cenários.
        
        Args:
            excel_processor: Instância processada do ExcelProcessor contendo dados.
            
        Raises:
            ValueError: Se os dados financeiros não foram extraídos.
        """
        self.excel_processor = excel_processor
        self.financial_data = excel_processor.financial_data
        
        if not self.financial_data:
            raise ValueError("Dados financeiros não extraídos. Execute extract_financial_data() primeiro.")
        
        self.scenarios: Dict[str, Dict[str, pd.DataFrame]] = {}
        self.metadata: Dict[str, Any] = {
            "generation_date": datetime.now(),
            "scenarios_generated": [],
            "base_metadata": excel_processor.metadata,
        }
    
    def generate_all_scenarios(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Gera todos os tipos de cenários disponíveis.
        
        Returns:
            Dicionário contendo todos os cenários gerados.
        """
        self.generate_realistic_scenario()
        self.generate_pessimistic_scenario()
        self.generate_optimistic_scenario()
        self.generate_aggressive_scenario()
        
        self.metadata["scenarios_generated"] = list(self.scenarios.keys())
        
        return self.scenarios
    
    def generate_realistic_scenario(self) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário realista baseado nos dados atuais.
        
        O cenário realista usa os valores originais dos dados, mas garante
        que todos os cálculos derivados estejam corretos e consistentes.
        
        Returns:
            Dicionário contendo as categorias financeiras do cenário realista.
        """
        # Inicia um novo dicionário para o cenário
        scenario_data = {}
        
        # Copia todas as categorias originais
        for category, df in self.financial_data.items():
            scenario_data[category] = df.copy(deep=True)
        
        # Recalcula os valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        # Adiciona aos cenários
        self.scenarios[ScenarioType.REALISTIC] = scenario_data
        
        return scenario_data
    
    def generate_pessimistic_scenario(self) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário pessimista.
        
        Neste cenário:
        - Redução de 15% nas receitas
        - Aumento de 10% nas despesas
        
        Returns:
            Dicionário contendo as categorias financeiras do cenário pessimista.
        """
        # Inicia com uma cópia do cenário realista
        if ScenarioType.REALISTIC not in self.scenarios:
            self.generate_realistic_scenario()
        
        scenario_data = deepcopy(self.scenarios[ScenarioType.REALISTIC])
        
        # Reduz receitas em 15%
        for category in self.REVENUE_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * 0.85  # redução de 15%
        
        # Aumenta custos variáveis em 10%
        for category in self.VARIABLE_COST_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * 1.10  # aumento de 10%
        
        # Aumenta despesas fixas em 10%
        for category in self.FIXED_EXPENSE_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * 1.10  # aumento de 10%
        
        # Recalcula os valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        # Adiciona aos cenários
        self.scenarios[ScenarioType.PESSIMISTIC] = scenario_data
        
        return scenario_data
    
    def generate_optimistic_scenario(self) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário otimista.
        
        Neste cenário:
        - Aumento de 20% nas receitas
        - Redução de 5% nas despesas
        
        Returns:
            Dicionário contendo as categorias financeiras do cenário otimista.
        """
        # Inicia com uma cópia do cenário realista
        if ScenarioType.REALISTIC not in self.scenarios:
            self.generate_realistic_scenario()
        
        scenario_data = deepcopy(self.scenarios[ScenarioType.REALISTIC])
        
        # Aumenta receitas em 20%
        for category in self.REVENUE_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * 1.20  # aumento de 20%
        
        # Reduz custos variáveis em 5%
        for category in self.VARIABLE_COST_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * 0.95  # redução de 5%
        
        # Reduz despesas fixas em 5%
        for category in self.FIXED_EXPENSE_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * 0.95  # redução de 5%
        
        # Recalcula os valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        # Adiciona aos cenários
        self.scenarios[ScenarioType.OPTIMISTIC] = scenario_data
        
        return scenario_data
    
    def generate_aggressive_scenario(self) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário agressivo com crescimento exponencial.
        
        Neste cenário:
        - Crescimento exponencial das receitas (30% inicial + 5% a cada período)
        - Aumento de investimentos (25%)
        - Aumento de custos variáveis proporcional às receitas, mas com eficiência (80% do crescimento)
        - Despesas fixas crescem mais lentamente (50% do crescimento das receitas)
        
        Returns:
            Dicionário contendo as categorias financeiras do cenário agressivo.
        """
        # Inicia com uma cópia do cenário realista
        if ScenarioType.REALISTIC not in self.scenarios:
            self.generate_realistic_scenario()
        
        scenario_data = deepcopy(self.scenarios[ScenarioType.REALISTIC])
        
        # Crescimento exponencial das receitas
        for category in self.REVENUE_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                # Aplica crescimento exponencial
                for i, col in enumerate(numeric_cols):
                    # Começa com 30% e adiciona 5% a cada período
                    growth_factor = 1.30 + (i * 0.05)
                    df[col] = df[col] * growth_factor
        
        # Aumenta investimentos em 25%
        for category in self.INVESTMENT_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * 1.25  # aumento de 25%
        
        # Ajusta custos variáveis para crescer proporcionalmente às receitas, mas com eficiência
        revenue_growth = self._calculate_category_growth(
            original_data=self.scenarios[ScenarioType.REALISTIC],
            modified_data=scenario_data,
            categories=self.REVENUE_CATEGORIES
        )
        
        for category in self.VARIABLE_COST_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                # Aplica 80% do crescimento das receitas aos custos variáveis
                for i, col in enumerate(numeric_cols):
                    if i < len(revenue_growth):
                        # Eficiência: apenas 80% do crescimento das receitas impacta os custos
                        cost_growth = 1 + ((revenue_growth[i] - 1) * 0.8)
                        df[col] = self.scenarios[ScenarioType.REALISTIC][category.value][col] * cost_growth
        
        # Despesas fixas crescem mais lentamente (50% do crescimento das receitas)
        for category in self.FIXED_EXPENSE_CATEGORIES:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                # Aplica 50% do crescimento das receitas às despesas fixas
                for i, col in enumerate(numeric_cols):
                    if i < len(revenue_growth):
                        # Apenas 50% do crescimento das receitas impacta as despesas fixas
                        expense_growth = 1 + ((revenue_growth[i] - 1) * 0.5)
                        df[col] = self.scenarios[ScenarioType.REALISTIC][category.value][col] * expense_growth
        
        # Recalcula os valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        # Adiciona aos cenários
        self.scenarios[ScenarioType.AGGRESSIVE] = scenario_data
        
        return scenario_data
    
    def _calculate_category_growth(
        self,
        original_data: Dict[str, pd.DataFrame],
        modified_data: Dict[str, pd.DataFrame],
        categories: List[FinancialCategory]
    ) -> List[float]:
        """
        Calcula o fator de crescimento entre os dados originais e modificados para uma categoria.
        
        Args:
            original_data: Dados originais
            modified_data: Dados modificados
            categories: Lista de categorias a considerar
            
        Returns:
            Lista de fatores de crescimento por coluna numérica
        """
        growth_factors = []
        
        for category in categories:
            if category.value in original_data and category.value in modified_data:
                orig_df = original_data[category.value]
                mod_df = modified_data[category.value]
                
                numeric_cols = orig_df.select_dtypes(include=['number']).columns
                
                for col in numeric_cols:
                    orig_sum = orig_df[col].sum()
                    mod_sum = mod_df[col].sum()
                    
                    if orig_sum > 0:
                        growth_factor = mod_sum / orig_sum
                    else:
                        growth_factor = 1.0
                    
                    growth_factors.append(growth_factor)
        
        return growth_factors if growth_factors else [1.0]
    
    def _recalculate_derived_values(
        self, 
        scenario_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Recalcula todos os valores derivados em um cenário.
        
        Isso inclui:
        - ENTRADAS [OPERACIONAIS] = soma das receitas
        - SAÍDAS [GASTOS VARIÁVEIS] = soma dos custos variáveis
        - SAÍDAS [GASTOS FIXOS] = soma das despesas fixas
        - MARGEM CONTRIBUIÇÃO FINANCEIRA = ENTRADAS - SAÍDAS VARIÁVEIS
        - FDC DAS ATIVIDADES OPERACIONAIS = MARGEM - SAÍDAS FIXAS
        - SALDO FINAL = valor acumulado dos fluxos de caixa
        
        Args:
            scenario_data: Dados do cenário a serem recalculados
            
        Returns:
            Cenário com valores derivados recalculados
        """
        # 1. Identifica as colunas numéricas em comum entre todas as categorias
        common_columns = self._find_common_numeric_columns(scenario_data)
        
        # 2. Cria ou atualiza o DataFrame de Margem de Contribuição
        margin_df = self._create_or_get_dataframe(
            scenario_data, 
            FinancialCategory.CONTRIBUTION_MARGIN.value
        )
        
        # 3. Calcula a ENTRADA OPERACIONAL (soma das receitas)
        revenue_sum = self._sum_category_values(
            scenario_data, 
            self.REVENUE_CATEGORIES, 
            common_columns
        )
        
        # 4. Calcula as SAÍDAS VARIÁVEIS (soma dos custos variáveis)
        variable_costs_sum = self._sum_category_values(
            scenario_data, 
            self.VARIABLE_COST_CATEGORIES, 
            common_columns
        )
        
        # 5. Calcula as SAÍDAS FIXAS (soma das despesas fixas)
        fixed_expenses_sum = self._sum_category_values(
            scenario_data, 
            self.FIXED_EXPENSE_CATEGORIES, 
            common_columns
        )
        
        # 6. Calcula MARGEM DE CONTRIBUIÇÃO (ENTRADAS - SAÍDAS VARIÁVEIS)
        contribution_margin = revenue_sum - variable_costs_sum
        
        # Atualiza o DataFrame de Margem
        self._update_dataframe_with_values(
            margin_df, 
            common_columns, 
            contribution_margin
        )
        
        # 7. Cria ou atualiza o DataFrame de Fluxo de Caixa (FDC)
        cashflow_df = self._create_or_get_dataframe(
            scenario_data, 
            FinancialCategory.CASH_FLOW.value
        )
        
        # 8. Calcula FDC (MARGEM - SAÍDAS FIXAS)
        cashflow = contribution_margin - fixed_expenses_sum
        
        # Atualiza o DataFrame de Fluxo de Caixa
        self._update_dataframe_with_values(
            cashflow_df, 
            common_columns, 
            cashflow
        )
        
        # 9. Cria ou atualiza o DataFrame de Saldo Final
        balance_df = self._create_or_get_dataframe(
            scenario_data, 
            FinancialCategory.FINAL_BALANCE.value
        )
        
        # 10. Calcula o SALDO FINAL (acumulado dos fluxos de caixa)
        balance = np.cumsum(cashflow)
        
        # Atualiza o DataFrame de Saldo Final
        self._update_dataframe_with_values(
            balance_df, 
            common_columns, 
            balance
        )
        
        # Atualiza os DataFrames no cenário
        scenario_data[FinancialCategory.CONTRIBUTION_MARGIN.value] = margin_df
        scenario_data[FinancialCategory.CASH_FLOW.value] = cashflow_df
        scenario_data[FinancialCategory.FINAL_BALANCE.value] = balance_df
        
        return scenario_data
    
    def _find_common_numeric_columns(
        self, 
        scenario_data: Dict[str, pd.DataFrame]
    ) -> List[str]:
        """
        Identifica colunas numéricas comuns em todas as categorias relevantes.
        
        Args:
            scenario_data: Dados do cenário
            
        Returns:
            Lista de nomes de colunas numéricas comuns
        """
        # Colete todas as categorias não derivadas
        non_derived_categories = []
        for cat_list in [self.REVENUE_CATEGORIES, self.VARIABLE_COST_CATEGORIES, 
                        self.FIXED_EXPENSE_CATEGORIES, self.INVESTMENT_CATEGORIES]:
            for category in cat_list:
                if category.value in scenario_data:
                    non_derived_categories.append(category.value)
        
        if not non_derived_categories:
            return []
        
        # Identifique colunas numéricas na primeira categoria
        first_category = non_derived_categories[0]
        numeric_columns = scenario_data[first_category].select_dtypes(include=['number']).columns.tolist()
        
        # Verifique quais dessas colunas estão presentes em todas as outras categorias
        common_columns = []
        for col in numeric_columns:
            is_common = True
            for category in non_derived_categories[1:]:
                if col not in scenario_data[category].columns or not pd.api.types.is_numeric_dtype(scenario_data[category][col]):
                    is_common = False
                    break
            
            if is_common:
                common_columns.append(col)
        
        return common_columns
    
    def _create_or_get_dataframe(
        self, 
        scenario_data: Dict[str, pd.DataFrame],
        category: str
    ) -> pd.DataFrame:
        """
        Cria um novo DataFrame ou retorna um existente para uma categoria.
        
        Args:
            scenario_data: Dados do cenário
            category: Nome da categoria
            
        Returns:
            DataFrame para a categoria especificada
        """
        if category in scenario_data:
            return scenario_data[category]
        
        # Busque um DataFrame existente para usar como modelo
        template_df = None
        for cat_list in [self.REVENUE_CATEGORIES, self.VARIABLE_COST_CATEGORIES, 
                         self.FIXED_EXPENSE_CATEGORIES, self.INVESTMENT_CATEGORIES]:
            for cat in cat_list:
                if cat.value in scenario_data:
                    template_df = scenario_data[cat.value]
                    break
            if template_df is not None:
                break
        
        if template_df is None:
            # Se não houver template, crie um DataFrame básico
            return pd.DataFrame()
        
        # Crie um DataFrame com a mesma estrutura, mas sem os dados numéricos
        df = pd.DataFrame(index=template_df.index)
        
        # Copie as colunas não numéricas
        for col in template_df.columns:
            if not pd.api.types.is_numeric_dtype(template_df[col]):
                df[col] = template_df[col]
        
        return df
    
    def _sum_category_values(
        self, 
        scenario_data: Dict[str, pd.DataFrame],
        categories: List[FinancialCategory],
        columns: List[str]
    ) -> np.ndarray:
        """
        Soma os valores numéricos de uma lista de categorias.
        
        Args:
            scenario_data: Dados do cenário
            categories: Lista de categorias a serem somadas
            columns: Lista de colunas a serem somadas
            
        Returns:
            Array NumPy com as somas
        """
        # Inicializa array de zeros com o tamanho das colunas
        result = np.zeros(len(columns))
        
        for category in categories:
            if category.value in scenario_data:
                df = scenario_data[category.value]
                for i, col in enumerate(columns):
                    if col in df.columns:
                        # Soma os valores da coluna (ignora NaN)
                        result[i] += df[col].sum(skipna=True)
        
        return result
    
    def _update_dataframe_with_values(
        self, 
        df: pd.DataFrame,
        columns: List[str],
        values: np.ndarray
    ) -> None:
        """
        Atualiza um DataFrame com valores calculados.
        
        Args:
            df: DataFrame a ser atualizado
            columns: Lista de colunas a serem atualizadas
            values: Array de valores calculados
        """
        # Adiciona ou atualiza colunas numéricas
        for i, col in enumerate(columns):
            df[col] = values[i]
    
    def export_scenarios_summary(self) -> pd.DataFrame:
        """
        Exporta um resumo comparativo de todos os cenários.
        
        Returns:
            DataFrame com o resumo comparativo dos cenários.
        """
        if not self.scenarios:
            raise ValueError("Nenhum cenário foi gerado. Execute generate_all_scenarios() primeiro.")
        
        # Cria um DataFrame vazio para o resumo
        summary = pd.DataFrame()
        
        # Adiciona entradas para cada cenário
        for scenario_name, scenario_data in self.scenarios.items():
            # Somente adiciona se houver dados de margem, fluxo de caixa e saldo final
            if (FinancialCategory.CONTRIBUTION_MARGIN.value in scenario_data and
                FinancialCategory.CASH_FLOW.value in scenario_data and
                FinancialCategory.FINAL_BALANCE.value in scenario_data):
                
                margin_df = scenario_data[FinancialCategory.CONTRIBUTION_MARGIN.value]
                cashflow_df = scenario_data[FinancialCategory.CASH_FLOW.value]
                balance_df = scenario_data[FinancialCategory.FINAL_BALANCE.value]
                
                # Calcula totais
                numeric_cols = margin_df.select_dtypes(include=['number']).columns
                
                for col in numeric_cols:
                    summary.loc['Margem Contribuição', f"{scenario_name}_{col}"] = margin_df[col].sum()
                    summary.loc['Fluxo de Caixa', f"{scenario_name}_{col}"] = cashflow_df[col].sum()
                    summary.loc['Saldo Final', f"{scenario_name}_{col}"] = balance_df[col].iloc[-1] if len(balance_df) > 0 else 0
        
        return summary
    
    def get_scenario_data(self, scenario_type: str) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Retorna os dados de um cenário específico.
        
        Args:
            scenario_type: Tipo de cenário (realista, pessimista, otimista, agressivo)
            
        Returns:
            Dados do cenário ou None se o cenário não existir
        """
        return self.scenarios.get(scenario_type) 