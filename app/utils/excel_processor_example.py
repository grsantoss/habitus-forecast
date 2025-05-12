"""
Exemplo de uso da classe ExcelProcessor para o Habitus Forecast.

Este script demonstra como utilizar a classe ExcelProcessor para processar
uma planilha financeira, extrair os dados relevantes e exportar o resultado.
"""

import sys
import os
from pathlib import Path
import json
import argparse
from datetime import datetime

# Adiciona o diretório raiz ao path para importar módulos da aplicação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.utils.excel_processor import ExcelProcessor, FinancialCategory, ExcelValidationError


def process_financial_spreadsheet(excel_path: str, output_path: str = None, verbose: bool = False) -> None:
    """
    Processa uma planilha financeira e opcionalmente exporta os resultados.
    
    Args:
        excel_path: Caminho para o arquivo Excel.
        output_path: Caminho para salvar o arquivo processado (opcional).
        verbose: Se True, imprime informações detalhadas durante o processamento.
    """
    try:
        print(f"Iniciando processamento do arquivo: {excel_path}")
        start_time = datetime.now()
        
        # Verifica a integridade do arquivo
        integrity = ExcelProcessor.check_file_integrity(excel_path)
        if not integrity["can_open"] or integrity["is_corrupt"]:
            print(f"ERRO: Arquivo corrompido ou inválido: {integrity['error_message']}")
            return
        
        print(f"Arquivo válido com {integrity['sheet_count']} abas.")
        
        # Cria o processador
        processor = ExcelProcessor(excel_path)
        
        # Lê as planilhas
        sheets = processor.read_excel()
        print(f"Leitura concluída. {len(sheets)} abas processadas.")
        
        if verbose:
            print("\nAbas encontradas:")
            for sheet_name in processor.metadata["sheet_names"]:
                print(f"  - {sheet_name}")
        
        # Valida a estrutura
        valid = processor.validate_structure()
        if valid:
            print("Planilha com estrutura válida: todas as categorias financeiras foram encontradas.")
        else:
            print("AVISO: Estrutura incompleta. Categorias ausentes:")
            for cat in processor.metadata.get("missing_categories", []):
                print(f"  - {cat}")
        
        # Extrai os dados financeiros
        financial_data = processor.extract_financial_data()
        print(f"\nDados financeiros extraídos para {len(financial_data)} categorias:")
        for category, df in financial_data.items():
            print(f"  - {category}: {df.shape[0]} linhas, {df.shape[1]} colunas")
        
        # Analisa tendências
        trends = processor.analyze_financial_trends()
        
        if verbose:
            print("\nResumo de dados:")
            for category, summary in processor.metadata["data_summary"].items():
                print(f"\n  {category}:")
                print(f"    - Linhas: {summary['row_count']}")
                print(f"    - Colunas: {summary['column_count']}")
                print(f"    - Dados ausentes: {summary['missing_data_percentage']:.2f}%")
                
                if 'column_sums' in summary:
                    print("    - Totais:")
                    for col, value in summary['column_sums'].items():
                        print(f"      * {col}: {value:,.2f}")
        
        # Exporta os dados processados se um caminho de saída for fornecido
        if output_path:
            export_info = processor.export_processed_data(output_path)
            print(f"\nDados exportados para: {export_info['output_path']}")
            print(f"Tamanho do arquivo: {export_info['file_size'] / 1024:.2f} KB")
            print(f"Categorias exportadas: {', '.join(export_info['categories_exported'])}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        print(f"\nProcessamento concluído em {processing_time:.2f} segundos.")
        
        # Exibe erros de validação se existirem
        if processor.metadata["validation_errors"]:
            print("\nErros encontrados durante o processamento:")
            for error in processor.metadata["validation_errors"]:
                print(f"  - Tipo: {error['type']}")
                if 'category' in error:
                    print(f"    Categoria: {error['category']}")
                if 'error' in error:
                    print(f"    Erro: {error['error']}")
        
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo não encontrado: {str(e)}")
    except ExcelValidationError as e:
        print(f"ERRO de validação: {e.message}")
        if e.details:
            print(f"Detalhes: {json.dumps(e.details, indent=2)}")
    except Exception as e:
        print(f"ERRO inesperado: {str(e)}")


if __name__ == "__main__":
    # Configura argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Processar planilha financeira para o Habitus Forecast")
    parser.add_argument("excel_path", help="Caminho para o arquivo Excel a ser processado")
    parser.add_argument("-o", "--output", help="Caminho para salvar o arquivo processado", required=False)
    parser.add_argument("-v", "--verbose", help="Exibir informações detalhadas", action="store_true")
    
    args = parser.parse_args()
    
    # Executa o processamento
    process_financial_spreadsheet(args.excel_path, args.output, args.verbose)