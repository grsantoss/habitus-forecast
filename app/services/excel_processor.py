import pandas as pd
import numpy as np
import io
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from enum import Enum
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)


class ExcelValidationError(Exception):
    """Exceção para erro de validação em arquivos Excel."""
    pass


class FinancialCategory(Enum):
    """Categorias financeiras para classificação dos dados."""
    REVENUE = "receitas"
    VARIABLE_COSTS = "custos_variaveis"
    PERSONNEL_EXPENSES = "despesas_pessoal"
    COMMERCIAL_EXPENSES = "despesas_comerciais"
    ADMIN_EXPENSES = "despesas_administrativas"
    INVESTMENTS = "investimentos"
    CONTRIBUTION_MARGIN = "margem_contribuicao"
    CASH_FLOW = "fluxo_de_caixa"
    FINAL_BALANCE = "saldo_final"


class ExcelProcessor:
    """
    Processador de arquivos Excel para dados financeiros.
    
    Esta classe é responsável por ler, validar e processar dados financeiros
    de arquivos Excel, extraindo categorias específicas como receitas, custos
    e despesas.
    
    Attributes:
        financial_data (Dict[str, pd.DataFrame]): Dados financeiros extraídos.
        metadata (Dict[str, Any]): Metadados do arquivo processado.
    """
    
    # Mapeamento de palavras-chave para identificar categorias
    CATEGORY_KEYWORDS = {
        FinancialCategory.REVENUE: ["receita", "faturamento", "vendas", "entrada"],
        FinancialCategory.VARIABLE_COSTS: ["custo variável", "custo operacional", "matéria prima"],
        FinancialCategory.PERSONNEL_EXPENSES: ["despesa pessoal", "salário", "remuneração", "benefício"],
        FinancialCategory.COMMERCIAL_EXPENSES: ["despesa comercial", "marketing", "vendas", "comissão"],
        FinancialCategory.ADMIN_EXPENSES: ["despesa administrativa", "escritório", "aluguel", "utilidade"],
        FinancialCategory.INVESTMENTS: ["investimento", "aquisição", "ativo", "imobilizado"]
    }
    
    def __init__(self):
        """Inicializa o processador de Excel."""
        self.financial_data: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, Any] = {
            "processing_date": datetime.now(),
            "sheet_names": [],
            "categories_found": []
        }
    
    def process_excel_data(self, content: bytes) -> Dict[str, Any]:
        """
        Processa um arquivo Excel contendo dados financeiros.
        
        Args:
            content: Conteúdo do arquivo Excel em bytes.
            
        Returns:
            Dicionário com dados financeiros processados e metadados.
            
        Raises:
            ExcelValidationError: Se o arquivo não atender os requisitos.
        """
        # Ler o arquivo Excel em memória
        try:
            excel_file = io.BytesIO(content)
            # Ler todas as planilhas
            excel_data = pd.read_excel(excel_file, sheet_name=None)
        except Exception as e:
            logger.error(f"Erro ao ler arquivo Excel: {str(e)}")
            raise ExcelValidationError(f"Erro ao ler arquivo Excel: {str(e)}")
        
        # Atualizar metadados
        self.metadata["sheet_names"] = list(excel_data.keys())
        self.metadata["total_sheets"] = len(excel_data)
        
        # Validar a estrutura do arquivo
        self._validate_excel_structure(excel_data)
        
        # Extrair dados financeiros
        self._extract_financial_data(excel_data)
        
        # Validar os dados extraídos
        self._validate_financial_data()
        
        # Preparar a resposta
        response = {
            "status": "success",
            "message": "Dados financeiros processados com sucesso",
            "categories": [
                {"id": cat.value, "name": self._format_category_name(cat.value), 
                 "description": self._get_category_description(cat)}
                for cat in self.metadata.get("categories_found", [])
            ],
            "data": self.financial_data,
            "metadata": self.metadata
        }
        
        return response
    
    def _validate_excel_structure(self, excel_data: Dict[str, pd.DataFrame]) -> None:
        """
        Valida a estrutura do arquivo Excel.
        
        Args:
            excel_data: Dicionário com os dados das planilhas.
            
        Raises:
            ExcelValidationError: Se a estrutura não for válida.
        """
        if not excel_data:
            raise ExcelValidationError("O arquivo Excel não contém planilhas.")
        
        # Verifica se pelo menos uma planilha tem dados suficientes
        has_valid_data = False
        for sheet_name, df in excel_data.items():
            if not df.empty and df.shape[0] > 0 and df.shape[1] > 0:
                has_valid_data = True
                break
        
        if not has_valid_data:
            raise ExcelValidationError("O arquivo Excel não contém dados válidos em nenhuma planilha.")
    
    def _extract_financial_data(self, excel_data: Dict[str, pd.DataFrame]) -> None:
        """
        Extrai dados financeiros do arquivo Excel.
        
        Args:
            excel_data: Dicionário com os dados das planilhas.
        """
        # Inicializar contador de categorias encontradas
        categories_found = set()
        
        # Processar cada planilha
        for sheet_name, df in excel_data.items():
            if df.empty:
                continue
            
            # Tenta identificar a categoria da planilha
            category = self._identify_sheet_category(sheet_name, df)
            
            if category:
                # Processar dados conforme a categoria
                processed_df = self._process_dataframe_by_category(df, category)
                
                # Armazenar dados processados
                self.financial_data[category.value] = processed_df
                categories_found.add(category)
                
                # Registrar no log
                logger.info(f"Planilha '{sheet_name}' processada como '{category.value}'")
        
        # Atualizar metadados
        self.metadata["categories_found"] = list(categories_found)
        self.metadata["total_categories"] = len(categories_found)
    
    def _identify_sheet_category(
        self, 
        sheet_name: str, 
        df: pd.DataFrame
    ) -> Optional[FinancialCategory]:
        """
        Identifica a categoria financeira de uma planilha.
        
        Args:
            sheet_name: Nome da planilha.
            df: DataFrame da planilha.
            
        Returns:
            Categoria financeira identificada ou None.
        """
        # Converter para minúsculas para facilitar as comparações
        sheet_name_lower = sheet_name.lower()
        
        # Verificar se o nome da planilha contém uma palavra-chave de categoria
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in sheet_name_lower for keyword in keywords):
                return category
        
        # Se não encontrou pelo nome da planilha, tenta pelo conteúdo da planilha
        # Converte todas as colunas de texto para string e concatena
        text_content = ""
        for col in df.columns:
            if df[col].dtype == 'object':
                text_content += " ".join(df[col].astype(str).tolist())
                text_content = text_content.lower()
        
        # Verifica se o conteúdo contém palavras-chave
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in text_content for keyword in keywords):
                return category
        
        # Tenta inferir pelo nome das colunas
        columns_text = " ".join(df.columns.astype(str)).lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in columns_text for keyword in keywords):
                return category
        
        return None
    
    def _process_dataframe_by_category(
        self, 
        df: pd.DataFrame, 
        category: FinancialCategory
    ) -> pd.DataFrame:
        """
        Processa um DataFrame conforme sua categoria.
        
        Args:
            df: DataFrame a ser processado.
            category: Categoria financeira.
            
        Returns:
            DataFrame processado.
        """
        # Cópia para evitar modificações no original
        processed_df = df.copy()
        
        # Remove linhas totalmente vazias
        processed_df = processed_df.dropna(how='all')
        
        # Tenta identificar e padronizar colunas de data/período
        date_columns = [col for col in processed_df.columns if 
                         'data' in str(col).lower() or 
                         'período' in str(col).lower() or 
                         'mes' in str(col).lower() or
                         'mês' in str(col).lower()]
        
        if date_columns:
            # Padronizar como datetime se possível
            for col in date_columns:
                try:
                    processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
                except:
                    pass  # Mantém como está se não for possível converter
        
        # Padronizar colunas numéricas (converte para float)
        numeric_columns = processed_df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            processed_df[col] = processed_df[col].astype(float)
        
        return processed_df
    
    def _validate_financial_data(self) -> None:
        """
        Valida os dados financeiros extraídos.
        
        Raises:
            ExcelValidationError: Se os dados não forem válidos.
        """
        if not self.financial_data:
            raise ExcelValidationError(
                "Não foi possível extrair dados financeiros. "
                "Verifique se o arquivo contém categorias reconhecíveis."
            )
        
        # Verificações adicionais para garantir dados coerentes
        for category, df in self.financial_data.items():
            # Verificar se há colunas numéricas
            numeric_columns = df.select_dtypes(include=['number']).columns
            if len(numeric_columns) == 0:
                raise ExcelValidationError(
                    f"A categoria '{category}' não contém colunas numéricas para análise."
                )
    
    def _format_category_name(self, category_name: str) -> str:
        """
        Formata o nome da categoria para apresentação.
        
        Args:
            category_name: Nome da categoria.
            
        Returns:
            Nome formatado.
        """
        return " ".join(word.capitalize() for word in category_name.replace("_", " ").split())
    
    def _get_category_description(self, category: FinancialCategory) -> str:
        """
        Retorna uma descrição para a categoria.
        
        Args:
            category: Categoria financeira.
            
        Returns:
            Descrição da categoria.
        """
        descriptions = {
            FinancialCategory.REVENUE: "Entradas de recursos financeiros",
            FinancialCategory.VARIABLE_COSTS: "Custos diretos relacionados à operação",
            FinancialCategory.PERSONNEL_EXPENSES: "Despesas com pessoal e folha de pagamento",
            FinancialCategory.COMMERCIAL_EXPENSES: "Despesas comerciais e de marketing",
            FinancialCategory.ADMIN_EXPENSES: "Despesas administrativas e gerais",
            FinancialCategory.INVESTMENTS: "Aplicações de capital",
            FinancialCategory.CONTRIBUTION_MARGIN: "Margem de contribuição financeira",
            FinancialCategory.CASH_FLOW: "Fluxo de caixa operacional",
            FinancialCategory.FINAL_BALANCE: "Saldo final acumulado"
        }
        
        return descriptions.get(category, "Categoria financeira")
    
    def analyze_trends(self) -> Dict[str, Any]:
        """
        Analisa tendências nos dados financeiros.
        
        Returns:
            Dicionário com análises de tendências.
        """
        if not self.financial_data:
            return {"status": "error", "message": "Sem dados para análise"}
        
        trends = {}
        
        # Para cada categoria, calcula tendências básicas
        for category, df in self.financial_data.items():
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) < 2:
                continue
            
            # Calcular estatísticas básicas
            category_trends = {
                "media": df[numeric_cols].mean().to_dict(),
                "mediana": df[numeric_cols].median().to_dict(),
                "tendencia": {},
                "crescimento": {}
            }
            
            # Calcular tendência (crescente, decrescente ou estável)
            for col in numeric_cols:
                values = df[col].dropna().values
                if len(values) < 2:
                    continue
                
                # Calcular taxa de crescimento
                growth_rate = (values[-1] / values[0]) - 1 if values[0] != 0 else 0
                category_trends["crescimento"][col] = growth_rate
                
                # Determinar tendência
                if growth_rate > 0.05:  # Crescimento de mais de 5%
                    trend = "crescente"
                elif growth_rate < -0.05:  # Queda de mais de 5%
                    trend = "decrescente"
                else:
                    trend = "estável"
                
                category_trends["tendencia"][col] = trend
            
            trends[category] = category_trends
        
        return {
            "status": "success",
            "message": "Análise de tendências concluída",
            "trends": trends
        } 