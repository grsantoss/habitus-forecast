#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migração de dados do MongoDB (Node.js) para o formato compatível com o sistema Python.
Este script conecta-se aos bancos de dados MongoDB de origem (Node.js) e destino (Python),
migra todos os dados necessários (usuários, dados financeiros, cenários etc.)
e preserva os relacionamentos entre as entidades.

Uso:
    python migrate_data.py --source mongodb://source_connection_string --target mongodb://target_connection_string [--dry-run]

Argumentos:
    --source: String de conexão para o MongoDB de origem (Node.js)
    --target: String de conexão para o MongoDB de destino (Python)
    --dry-run: Executa o script em modo de simulação, sem modificar o banco de destino
    --log-level: Nível de log (DEBUG, INFO, WARNING, ERROR) - padrão: INFO
"""

import argparse
import datetime
import json
import logging
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

import pymongo
from bson import ObjectId
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.database import Database

from app.utils.password_migration import migrate_password_hash
from app.utils.data_validator import validate_data_structure, generate_validation_report

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"migration_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("migration")

# Mapeamento de coleções entre os sistemas
COLLECTION_MAPPING = {
    # Sistema Node.js (origem) -> Sistema Python (destino)
    "users": "users",
    "financialData": "financial_data",
    "scenarios": "scenarios",
    "documents": "documents",
    "transactions": "transactions",
    "settings": "settings",
    "logs": "activity_logs",
}

# Mapeamento de campos entre os sistemas
FIELD_MAPPING = {
    "users": {
        "_id": "_id",  # Mantém o mesmo ID
        "email": "email",
        "password": "password",  # Será migrado com a função migrate_password_hash
        "name": "name",
        "createdAt": "created_at",
        "updatedAt": "updated_at",
        "role": "role",
        "isActive": "is_active",
        "lastLogin": "last_login",
        "settings": "settings",
    },
    "financialData": {
        "_id": "_id",
        "userId": "user_id",
        "title": "title",
        "type": "type",
        "amount": "amount",
        "date": "date",
        "category": "category",
        "description": "description",
        "createdAt": "created_at",
        "updatedAt": "updated_at",
        "tags": "tags",
        "isRecurring": "is_recurring",
        "recurringDetails": "recurring_details",
    },
    "scenarios": {
        "_id": "_id",
        "userId": "user_id",
        "name": "name",
        "description": "description",
        "assumptions": "assumptions",
        "createdAt": "created_at",
        "updatedAt": "updated_at",
        "projections": "projections",
        "isTemplate": "is_template",
        "tags": "tags",
    }
}

# Campos que precisam de transformação especial
TRANSFORM_FIELDS = {
    "users": {
        "password": migrate_password_hash,
        "createdAt": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")),
        "updatedAt": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")),
        "lastLogin": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")) if x else None,
    },
    "financialData": {
        "date": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")),
        "createdAt": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")),
        "updatedAt": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")),
    },
    "scenarios": {
        "createdAt": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")),
        "updatedAt": lambda x: x if isinstance(x, datetime.datetime) else datetime.datetime.fromisoformat(x.replace("Z", "+00:00")),
    }
}

class DataMigration:
    """Classe principal para migração de dados entre os sistemas MongoDB."""

    def __init__(
        self, 
        source_connection_string: str, 
        target_connection_string: str, 
        dry_run: bool = False
    ):
        """
        Inicializa a migração de dados.

        Args:
            source_connection_string: String de conexão para o MongoDB de origem
            target_connection_string: String de conexão para o MongoDB de destino
            dry_run: Se True, executa em modo de simulação sem modificar o banco destino
        """
        self.source_connection_string = source_connection_string
        self.target_connection_string = target_connection_string
        self.dry_run = dry_run
        self.source_client = None
        self.target_client = None
        self.source_db = None
        self.target_db = None
        self.stats = {
            "total_documents": 0,
            "migrated_documents": 0,
            "skipped_documents": 0,
            "error_documents": 0,
            "collections": {}
        }
        
        for collection in COLLECTION_MAPPING:
            self.stats["collections"][collection] = {
                "total": 0,
                "migrated": 0,
                "skipped": 0,
                "errors": 0
            }

    def connect(self) -> bool:
        """
        Estabelece conexões com os bancos de dados de origem e destino.
        
        Returns:
            bool: True se as conexões foram estabelecidas com sucesso, False caso contrário
        """
        try:
            # Conexão com o banco de origem (Node.js)
            self.source_client = pymongo.MongoClient(self.source_connection_string)
            self.source_db = self.source_client.get_database()
            logger.info(f"Conectado ao banco de dados de origem: {self.source_db.name}")
            
            # Conexão com o banco de destino (Python)
            self.target_client = pymongo.MongoClient(self.target_connection_string)
            self.target_db = self.target_client.get_database()
            logger.info(f"Conectado ao banco de dados de destino: {self.target_db.name}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar aos bancos de dados: {str(e)}")
            return False

    def close_connections(self) -> None:
        """Fecha as conexões com os bancos de dados."""
        if self.source_client:
            self.source_client.close()
        if self.target_client:
            self.target_client.close()
        logger.info("Conexões fechadas")

    def transform_document(self, document: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        """
        Transforma um documento do formato Node.js para o formato Python.
        
        Args:
            document: Documento a ser transformado
            collection_name: Nome da coleção do documento
            
        Returns:
            Dict: Documento transformado
        """
        new_doc = {}
        
        # Obtém o mapeamento de campos para esta coleção
        field_map = FIELD_MAPPING.get(collection_name, {})
        transform_map = TRANSFORM_FIELDS.get(collection_name, {})
        
        # Aplica o mapeamento de campos
        for old_field, new_field in field_map.items():
            if old_field in document:
                # Verifica se o campo precisa de transformação especial
                if old_field in transform_map and document[old_field] is not None:
                    try:
                        new_doc[new_field] = transform_map[old_field](document[old_field])
                    except Exception as e:
                        logger.warning(f"Erro ao transformar campo {old_field}: {str(e)}")
                        new_doc[new_field] = document[old_field]
                else:
                    new_doc[new_field] = document[old_field]
        
        # Adiciona campos necessários no novo sistema
        if "updated_at" not in new_doc and "created_at" in new_doc:
            new_doc["updated_at"] = new_doc["created_at"]
            
        # Adiciona versão do documento
        new_doc["version"] = 1
        
        return new_doc

    def migrate_collection(self, source_collection: str, target_collection: str) -> int:
        """
        Migra documentos de uma coleção para outra.
        
        Args:
            source_collection: Nome da coleção de origem
            target_collection: Nome da coleção de destino
            
        Returns:
            int: Número de documentos migrados
        """
        logger.info(f"Migrando coleção: {source_collection} -> {target_collection}")
        
        source_coll = self.source_db[source_collection]
        target_coll = self.target_db[target_collection]
        
        # Conta total de documentos
        total_docs = source_coll.count_documents({})
        self.stats["collections"][source_collection]["total"] = total_docs
        self.stats["total_documents"] += total_docs
        
        logger.info(f"Total de documentos a migrar: {total_docs}")
        
        # Migra os documentos em lotes para melhor performance
        batch_size = 100
        migrated = 0
        errors = 0
        skipped = 0
        
        cursor = source_coll.find({})
        
        # Se não for dry run e a coleção alvo já existe, cria índices
        if not self.dry_run and target_collection in self.target_db.list_collection_names():
            # Cria índices comuns
            if target_collection == "users":
                target_coll.create_index("email", unique=True)
            elif target_collection in ["financial_data", "scenarios"]:
                target_coll.create_index("user_id")
        
        # Processa em lotes
        batch = []
        
        for doc in cursor:
            try:
                # Transforma o documento
                new_doc = self.transform_document(doc, source_collection)
                
                # Adiciona ao lote
                batch.append(new_doc)
                
                # Processa o lote quando atingir o tamanho definido
                if len(batch) >= batch_size:
                    if not self.dry_run:
                        result = target_coll.insert_many(batch, ordered=False)
                        migrated += len(result.inserted_ids)
                    else:
                        migrated += len(batch)
                    batch = []
                    
                    logger.info(f"Progresso: {migrated}/{total_docs} documentos migrados")
            
            except Exception as e:
                logger.error(f"Erro ao migrar documento {doc.get('_id')}: {str(e)}")
                errors += 1
                self.stats["collections"][source_collection]["errors"] += 1
                self.stats["error_documents"] += 1
        
        # Processa o último lote se houver
        if batch and not self.dry_run:
            try:
                result = target_coll.insert_many(batch, ordered=False)
                migrated += len(result.inserted_ids)
            except pymongo.errors.BulkWriteError as bwe:
                # Alguns documentos podem ter falhado
                migrated += bwe.details["nInserted"]
                errors += len(bwe.details["writeErrors"])
                logger.warning(f"Alguns documentos não puderam ser inseridos: {bwe.details['writeErrors']}")
        elif batch and self.dry_run:
            migrated += len(batch)
        
        # Atualiza estatísticas
        self.stats["collections"][source_collection]["migrated"] = migrated
        self.stats["collections"][source_collection]["errors"] = errors
        self.stats["collections"][source_collection]["skipped"] = skipped
        self.stats["migrated_documents"] += migrated
        self.stats["skipped_documents"] += skipped
        
        logger.info(f"Migração da coleção {source_collection} concluída: {migrated} migrados, {errors} erros, {skipped} ignorados")
        
        return migrated

    def validate_migration(self) -> bool:
        """
        Valida se a migração foi bem-sucedida, comparando contagens e estrutura dos dados.
        
        Returns:
            bool: True se a validação for bem-sucedida, False caso contrário
        """
        logger.info("Iniciando validação da migração...")
        
        validation_successful = True
        
        # Verifica contagens de documentos por coleção
        for source_collection, target_collection in COLLECTION_MAPPING.items():
            source_count = self.source_db[source_collection].count_documents({})
            target_count = self.target_db[target_collection].count_documents({})
            
            if source_count != target_count and self.stats["collections"][source_collection]["skipped"] == 0:
                logger.warning(f"Discrepância na contagem de documentos para {source_collection}: origem={source_count}, destino={target_count}")
                validation_successful = False
        
        # Valida estrutura dos dados para coleções importantes
        for collection_name in ["users", "financial_data", "scenarios"]:
            source_name = next((k for k, v in COLLECTION_MAPPING.items() if v == collection_name), None)
            if not source_name:
                continue
                
            # Amostra aleatória de documentos
            sample_size = min(10, self.target_db[collection_name].count_documents({}))
            if sample_size == 0:
                continue
                
            sample_docs = list(self.target_db[collection_name].aggregate([{"$sample": {"size": sample_size}}]))
            
            # Valida estrutura
            for doc in sample_docs:
                is_valid, issues = validate_data_structure(doc, collection_name)
                if not is_valid:
                    logger.warning(f"Problemas encontrados na validação de documento em {collection_name}: {issues}")
                    validation_successful = False
        
        return validation_successful

    def run_migration(self) -> bool:
        """
        Executa o processo completo de migração.
        
        Returns:
            bool: True se a migração for bem-sucedida, False caso contrário
        """
        logger.info(f"Iniciando migração de dados {'(SIMULAÇÃO)' if self.dry_run else ''}")
        start_time = time.time()
        
        # Conecta aos bancos
        if not self.connect():
            return False
        
        try:
            # Migra coleções na ordem correta (respeitando dependências)
            migration_order = [
                "users",             # Primeiro usuários
                "settings",          # Configurações gerais
                "financialData",     # Dados financeiros
                "scenarios",         # Cenários
                "documents",         # Documentos
                "transactions",      # Transações
                "logs"               # Logs por último
            ]
            
            for collection in migration_order:
                if collection in COLLECTION_MAPPING:
                    self.migrate_collection(collection, COLLECTION_MAPPING[collection])
            
            # Valida migração
            if not self.dry_run:
                validation_result = self.validate_migration()
                if not validation_result:
                    logger.warning("Validação da migração encontrou discrepâncias")
            
            # Gera relatório de migração
            self._generate_migration_report()
            
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Migração concluída em {duration:.2f} segundos")
            logger.info(f"Total de documentos: {self.stats['total_documents']}")
            logger.info(f"Documentos migrados: {self.stats['migrated_documents']}")
            logger.info(f"Documentos ignorados: {self.stats['skipped_documents']}")
            logger.info(f"Documentos com erro: {self.stats['error_documents']}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro durante a migração: {str(e)}")
            return False
        
        finally:
            self.close_connections()

    def _generate_migration_report(self) -> None:
        """Gera um relatório detalhado da migração."""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "statistics": self.stats,
            "details": {}
        }
        
        # Adiciona estatísticas por coleção
        for collection, stats in self.stats["collections"].items():
            if stats["total"] > 0:
                report["details"][collection] = {
                    "total_documents": stats["total"],
                    "migrated_documents": stats["migrated"],
                    "success_rate": (stats["migrated"] / stats["total"]) * 100 if stats["total"] > 0 else 0,
                    "error_rate": (stats["errors"] / stats["total"]) * 100 if stats["total"] > 0 else 0
                }
        
        # Escreve relatório em arquivo
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"migration_report_{timestamp}.json"
        
        with open(report_filename, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Relatório de migração salvo em {report_filename}")

def parse_arguments():
    """Processa os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Migração de dados MongoDB entre sistemas Node.js e Python")
    
    parser.add_argument("--source", required=True, help="String de conexão para o MongoDB de origem")
    parser.add_argument("--target", required=True, help="String de conexão para o MongoDB de destino")
    parser.add_argument("--dry-run", action="store_true", help="Executa em modo de simulação, sem modificar o banco destino")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Nível de log")
    
    return parser.parse_args()

def main():
    """Função principal."""
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Processa argumentos
    args = parse_arguments()
    
    # Configura nível de log
    logger.setLevel(getattr(logging, args.log_level))
    
    # Substitui valores de conexão por variáveis de ambiente, se disponíveis
    source_conn = os.getenv("SOURCE_MONGODB_URI", args.source)
    target_conn = os.getenv("TARGET_MONGODB_URI", args.target)
    
    # Inicia migração
    migration = DataMigration(
        source_connection_string=source_conn,
        target_connection_string=target_conn,
        dry_run=args.dry_run
    )
    
    success = migration.run_migration()
    
    # Retorna código de saída
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 