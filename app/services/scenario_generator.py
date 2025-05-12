"""
Serviço de geração de cenários financeiros para o Habitus Forecast.

Este módulo contém funcionalidades para criar diferentes cenários financeiros
baseados em dados extraídos de planilhas Excel, incluindo projeções realistas,
pessimistas, otimistas e agressivas.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from copy import deepcopy

from app.services.excel_processor import ExcelProcessor, FinancialCategory

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
        financial_data (Dict[str, pd.DataFrame]): Dados financeiros de entrada.
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
    
    def __init__(self):
        """Inicializa o gerador de cenários."""
        self.financial_data = {}
        self.scenarios = {}
        self.metadata = {
            "generation_date": datetime.now(),
            "scenarios_generated": []
        }
    
    def generate_scenario(
        self,
        financial_data: Dict[str, Any],
        scenario_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera um cenário financeiro com base nos dados e parâmetros fornecidos.
        
        Args:
            financial_data: Dados financeiros a serem analisados.
            scenario_type: Tipo de cenário a ser gerado (realista, pessimista, otimista, agressivo).
            parameters: Parâmetros adicionais para personalizar o cenário.
            
        Returns:
            Dicionário contendo o cenário gerado.
            
        Raises:
            ValueError: Se o tipo de cenário não for reconhecido.
        """
        # Inicializa dados financeiros
        self.financial_data = financial_data
        
        # Normaliza e converte dados para DataFrames se necessário
        self._normalize_financial_data()
        
        # Gera o cenário conforme o tipo
        if scenario_type == ScenarioType.REALISTIC:
            scenario_data = self._generate_realistic_scenario(parameters)
        elif scenario_type == ScenarioType.PESSIMISTIC:
            scenario_data = self._generate_pessimistic_scenario(parameters)
        elif scenario_type == ScenarioType.OPTIMISTIC:
            scenario_data = self._generate_optimistic_scenario(parameters)
        elif scenario_type == ScenarioType.AGGRESSIVE:
            scenario_data = self._generate_aggressive_scenario(parameters)
        else:
            raise ValueError(f"Tipo de cenário desconhecido: {scenario_type}")
        
        # Armazena o cenário gerado
        self.scenarios[scenario_type] = scenario_data
        
        # Atualiza metadados
        if scenario_type not in self.metadata["scenarios_generated"]:
            self.metadata["scenarios_generated"].append(scenario_type)
        
        # Calcula métricas relevantes para o cenário
        metrics = self._calculate_scenario_metrics(scenario_data)
        
        # Monta a resposta
        response = {
            "status": "success",
            "message": f"Cenário {scenario_type} gerado com sucesso",
            "scenario_type": scenario_type,
            "data": scenario_data,
            "metrics": metrics
        }
        
        return response
    
    def _normalize_financial_data(self) -> None:
        """
        Normaliza os dados financeiros, garantindo que estejam em formato de DataFrame.
        """
        normalized_data = {}
        
        for category, data in self.financial_data.items():
            if isinstance(data, list):
                # Converte lista para DataFrame
                normalized_data[category] = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Converte dicionário para DataFrame
                normalized_data[category] = pd.DataFrame([data])
            elif isinstance(data, pd.DataFrame):
                # Mantém DataFrame como está
                normalized_data[category] = data
            else:
                logger.warning(f"Tipo de dados desconhecido para categoria {category}: {type(data)}")
                continue
        
        self.financial_data = normalized_data
    
    def _generate_realistic_scenario(
        self, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário realista baseado nos dados atuais.
        
        Args:
            parameters: Parâmetros adicionais (não utilizados neste cenário).
            
        Returns:
            Dicionário com dados do cenário realista.
        """
        # Copia os dados originais
        scenario_data = deepcopy(self.financial_data)
        
        # Recalcula valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        return scenario_data
    
    def _generate_pessimistic_scenario(
        self, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário pessimista com redução de receitas e aumento de despesas.
        
        Args:
            parameters: Parâmetros adicionais para ajuste do cenário.
            
        Returns:
            Dicionário com dados do cenário pessimista.
        """
        # Pega parâmetros ou usa valores padrão
        revenue_adjustment = parameters.get("revenue_adjustment", -0.15) if parameters else -0.15
        cost_adjustment = parameters.get("cost_adjustment", 0.10) if parameters else 0.10
        expense_adjustment = parameters.get("expense_adjustment", 0.10) if parameters else 0.10
        
        # Copia os dados originais
        scenario_data = deepcopy(self.financial_data)
        
        # Ajusta receitas (redução)
        for category in self.REVENUE_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * (1 + revenue_adjustment)
        
        # Ajusta custos variáveis (aumento)
        for category in self.VARIABLE_COST_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * (1 + cost_adjustment)
        
        # Ajusta despesas fixas (aumento)
        for category in self.FIXED_EXPENSE_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * (1 + expense_adjustment)
        
        # Recalcula valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        return scenario_data
    
    def _generate_optimistic_scenario(
        self, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário otimista com aumento de receitas e redução de despesas.
        
        Args:
            parameters: Parâmetros adicionais para ajuste do cenário.
            
        Returns:
            Dicionário com dados do cenário otimista.
        """
        # Pega parâmetros ou usa valores padrão
        revenue_adjustment = parameters.get("revenue_adjustment", 0.20) if parameters else 0.20
        cost_adjustment = parameters.get("cost_adjustment", -0.05) if parameters else -0.05
        expense_adjustment = parameters.get("expense_adjustment", -0.05) if parameters else -0.05
        
        # Copia os dados originais
        scenario_data = deepcopy(self.financial_data)
        
        # Ajusta receitas (aumento)
        for category in self.REVENUE_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * (1 + revenue_adjustment)
        
        # Ajusta custos variáveis (redução)
        for category in self.VARIABLE_COST_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * (1 + cost_adjustment)
        
        # Ajusta despesas fixas (redução)
        for category in self.FIXED_EXPENSE_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * (1 + expense_adjustment)
        
        # Recalcula valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        return scenario_data
    
    def _generate_aggressive_scenario(
        self, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Gera um cenário agressivo com crescimento exponencial de receitas.
        
        Args:
            parameters: Parâmetros adicionais para ajuste do cenário.
            
        Returns:
            Dicionário com dados do cenário agressivo.
        """
        # Pega parâmetros ou usa valores padrão
        initial_growth = parameters.get("initial_growth", 0.30) if parameters else 0.30
        growth_rate = parameters.get("growth_rate", 0.05) if parameters else 0.05
        investment_adjustment = parameters.get("investment_adjustment", 0.25) if parameters else 0.25
        
        # Copia os dados originais
        scenario_data = deepcopy(self.financial_data)
        
        # Ajusta receitas (crescimento exponencial)
        for category in self.REVENUE_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                # Aplica crescimento diferente para cada período
                for i, col in enumerate(numeric_cols):
                    growth_factor = 1 + initial_growth + (i * growth_rate)
                    df[col] = df[col] * growth_factor
        
        # Aumenta investimentos
        for category in self.INVESTMENT_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols] * (1 + investment_adjustment)
        
        # Ajusta custos variáveis (proporcional às receitas, mas com eficiência)
        original_revenue = self._sum_category_values(self.financial_data, self.REVENUE_CATEGORIES)
        new_revenue = self._sum_category_values(scenario_data, self.REVENUE_CATEGORIES)
        
        if original_revenue.size > 0 and new_revenue.size > 0:
            revenue_growth = new_revenue / original_revenue
            revenue_growth[~np.isfinite(revenue_growth)] = 1.0  # Lidar com divisão por zero
            
            # Custos crescem 80% do que as receitas crescem
            for category in self.VARIABLE_COST_CATEGORIES:
                category_key = category.value
                if category_key in scenario_data and category_key in self.financial_data:
                    df = scenario_data[category_key]
                    df_orig = self.financial_data[category_key]
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    
                    for i, col in enumerate(numeric_cols):
                        if i < len(revenue_growth):
                            # Eficiência: apenas 80% do crescimento das receitas
                            cost_growth = 1 + ((revenue_growth[i] - 1) * 0.8)
                            df[col] = df_orig[col] * cost_growth
            
            # Despesas fixas crescem 50% do que as receitas crescem
            for category in self.FIXED_EXPENSE_CATEGORIES:
                category_key = category.value
                if category_key in scenario_data and category_key in self.financial_data:
                    df = scenario_data[category_key]
                    df_orig = self.financial_data[category_key]
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    
                    for i, col in enumerate(numeric_cols):
                        if i < len(revenue_growth):
                            # Apenas 50% do crescimento das receitas
                            expense_growth = 1 + ((revenue_growth[i] - 1) * 0.5)
                            df[col] = df_orig[col] * expense_growth
        
        # Recalcula valores derivados
        scenario_data = self._recalculate_derived_values(scenario_data)
        
        return scenario_data
    
    def _sum_category_values(
        self, 
        data: Dict[str, pd.DataFrame],
        categories: List[FinancialCategory]
    ) -> np.ndarray:
        """
        Soma os valores numéricos de uma lista de categorias.
        
        Args:
            data: Dados financeiros.
            categories: Lista de categorias a somar.
            
        Returns:
            Array com a soma por coluna numérica.
        """
        # Identifica todas as colunas numéricas em todas as categorias
        numeric_columns = set()
        for category in categories:
            category_key = category.value
            if category_key in data:
                df = data[category_key]
                numeric_columns.update(df.select_dtypes(include=['number']).columns)
        
        numeric_columns = list(numeric_columns)
        result = np.zeros(len(numeric_columns))
        
        # Soma os valores de cada categoria
        for category in categories:
            category_key = category.value
            if category_key in data:
                df = data[category_key]
                for i, col in enumerate(numeric_columns):
                    if col in df.columns:
                        result[i] += df[col].sum()
        
        return result
    
    def _recalculate_derived_values(
        self, 
        scenario_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Recalcula todos os valores derivados em um cenário.
        
        Args:
            scenario_data: Dados do cenário.
            
        Returns:
            Dados do cenário com valores derivados recalculados.
        """
        # Identifica as colunas numéricas em comum
        common_columns = self._find_common_numeric_columns(scenario_data)
        
        # Cria ou obtém DataFrames para valores calculados
        margin_df = self._create_or_get_dataframe(
            scenario_data,
            FinancialCategory.CONTRIBUTION_MARGIN.value
        )
        
        cashflow_df = self._create_or_get_dataframe(
            scenario_data,
            FinancialCategory.CASH_FLOW.value
        )
        
        balance_df = self._create_or_get_dataframe(
            scenario_data,
            FinancialCategory.FINAL_BALANCE.value
        )
        
        # Calcula a soma das receitas
        revenue_sum = self._sum_category_values(scenario_data, self.REVENUE_CATEGORIES)
        
        # Calcula a soma dos custos variáveis
        variable_costs_sum = self._sum_category_values(scenario_data, self.VARIABLE_COST_CATEGORIES)
        
        # Calcula a soma das despesas fixas
        fixed_expenses_sum = self._sum_category_values(scenario_data, self.FIXED_EXPENSE_CATEGORIES)
        
        # Calcula a margem de contribuição (receitas - custos variáveis)
        contribution_margin = revenue_sum - variable_costs_sum
        
        # Calcula o fluxo de caixa (margem - despesas fixas)
        cashflow = contribution_margin - fixed_expenses_sum
        
        # Calcula o saldo final (acumulado do fluxo de caixa)
        balance = np.cumsum(cashflow)
        
        # Atualiza os DataFrames calculados
        self._update_dataframe_with_values(margin_df, common_columns, contribution_margin)
        self._update_dataframe_with_values(cashflow_df, common_columns, cashflow)
        self._update_dataframe_with_values(balance_df, common_columns, balance)
        
        # Atualiza os dados do cenário
        scenario_data[FinancialCategory.CONTRIBUTION_MARGIN.value] = margin_df
        scenario_data[FinancialCategory.CASH_FLOW.value] = cashflow_df
        scenario_data[FinancialCategory.FINAL_BALANCE.value] = balance_df
        
        return scenario_data
    
    def _find_common_numeric_columns(
        self, 
        scenario_data: Dict[str, pd.DataFrame]
    ) -> List[str]:
        """
        Encontra colunas numéricas comuns a todas as categorias.
        
        Args:
            scenario_data: Dados do cenário.
            
        Returns:
            Lista de nomes de colunas numéricas comuns.
        """
        all_numeric_columns = {}
        
        # Coleta todas as colunas numéricas de todas as categorias
        for category, df in scenario_data.items():
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
                
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            all_numeric_columns[category] = set(numeric_cols)
        
        # Se não tiver categorias, retorna lista vazia
        if not all_numeric_columns:
            return []
        
        # Encontra colunas em comum
        common_columns = set.intersection(*all_numeric_columns.values()) if all_numeric_columns else set()
        
        return list(common_columns)
    
    def _create_or_get_dataframe(
        self, 
        scenario_data: Dict[str, pd.DataFrame],
        category: str
    ) -> pd.DataFrame:
        """
        Cria um novo DataFrame ou obtém um existente para uma categoria.
        
        Args:
            scenario_data: Dados do cenário.
            category: Nome da categoria.
            
        Returns:
            DataFrame para a categoria.
        """
        if category in scenario_data and isinstance(scenario_data[category], pd.DataFrame):
            return scenario_data[category]
        
        # Busca um DataFrame existente para usar como modelo
        template_df = None
        for df in scenario_data.values():
            if isinstance(df, pd.DataFrame) and not df.empty:
                template_df = df
                break
        
        if template_df is None:
            # Sem modelo, cria DataFrame vazio
            return pd.DataFrame()
        
        # Cria DataFrame com a mesma estrutura
        df = pd.DataFrame(index=template_df.index)
        
        # Copia colunas não numéricas
        for col in template_df.columns:
            if not pd.api.types.is_numeric_dtype(template_df[col]):
                df[col] = template_df[col]
        
        return df
    
    def _update_dataframe_with_values(
        self, 
        df: pd.DataFrame,
        columns: List[str],
        values: np.ndarray
    ) -> None:
        """
        Atualiza um DataFrame com valores calculados.
        
        Args:
            df: DataFrame a atualizar.
            columns: Lista de colunas a atualizar.
            values: Valores calculados.
        """
        if not columns or len(values) == 0:
            return
            
        # Ajusta o tamanho dos valores se necessário
        if len(values) > len(columns):
            values = values[:len(columns)]
        elif len(values) < len(columns):
            values = np.pad(values, (0, len(columns) - len(values)))
        
        # Atualiza as colunas
        for i, col in enumerate(columns):
            if i < len(values):
                # Se for uma série temporal, distribui o valor
                if len(df) > 1 and values.ndim == 1:
                    # Distribui o valor igualmente para cada linha
                    df[col] = values[i] / len(df)
                else:
                    # Atribui o valor diretamente
                    df[col] = values[i]
    
    def _calculate_scenario_metrics(
        self, 
        scenario_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """
        Calcula métricas importantes do cenário.
        
        Args:
            scenario_data: Dados do cenário.
            
        Returns:
            Dicionário com métricas calculadas.
        """
        metrics = {
            "total_revenue": 0,
            "total_costs": 0,
            "total_expenses": 0,
            "total_margin": 0,
            "total_cashflow": 0,
            "final_balance": 0,
            "margin_percentage": 0,
            "roi": 0
        }
        
        # Calcula métricas de receita
        for category in self.REVENUE_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                metrics["total_revenue"] += df[numeric_cols].sum().sum()
        
        # Calcula métricas de custos
        for category in self.VARIABLE_COST_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                metrics["total_costs"] += df[numeric_cols].sum().sum()
        
        # Calcula métricas de despesas
        for category in self.FIXED_EXPENSE_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                metrics["total_expenses"] += df[numeric_cols].sum().sum()
        
        # Margem de contribuição
        category_key = FinancialCategory.CONTRIBUTION_MARGIN.value
        if category_key in scenario_data:
            df = scenario_data[category_key]
            numeric_cols = df.select_dtypes(include=['number']).columns
            metrics["total_margin"] = df[numeric_cols].sum().sum()
        
        # Fluxo de caixa
        category_key = FinancialCategory.CASH_FLOW.value
        if category_key in scenario_data:
            df = scenario_data[category_key]
            numeric_cols = df.select_dtypes(include=['number']).columns
            metrics["total_cashflow"] = df[numeric_cols].sum().sum()
        
        # Saldo final
        category_key = FinancialCategory.FINAL_BALANCE.value
        if category_key in scenario_data:
            df = scenario_data[category_key]
            numeric_cols = df.select_dtypes(include=['number']).columns
            # Pega o último valor não nulo
            for col in numeric_cols:
                last_values = df[col].dropna()
                if not last_values.empty:
                    metrics["final_balance"] += last_values.iloc[-1]
        
        # Calcula percentuais
        if metrics["total_revenue"] > 0:
            metrics["margin_percentage"] = (metrics["total_margin"] / metrics["total_revenue"]) * 100
        
        # Calcula ROI
        total_investment = 0
        for category in self.INVESTMENT_CATEGORIES:
            category_key = category.value
            if category_key in scenario_data:
                df = scenario_data[category_key]
                numeric_cols = df.select_dtypes(include=['number']).columns
                total_investment += df[numeric_cols].sum().sum()
        
        if total_investment > 0:
            metrics["roi"] = (metrics["total_cashflow"] / total_investment) * 100
        
        return metrics 