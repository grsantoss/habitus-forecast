"""
Módulo de configuração do MongoDB para o Habitus Forecast.

Este módulo contém funções para conexão com MongoDB e configuração
de índices para os modelos da aplicação.
"""

import logging
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

from app.core.config import settings
from app.models.user import user_indexes
from app.models.financial import financial_data_indexes
from app.models.scenario import scenario_indexes


logger = logging.getLogger(__name__)

# Cliente MongoDB global
mongo_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """
    Conecta ao servidor MongoDB.
    
    Raises:
        ConnectionFailure: Se não for possível conectar ao MongoDB.
    """
    global mongo_client, db
    
    if mongo_client is not None:
        return
    
    try:
        mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=settings.MAX_CONNECTIONS_COUNT,
            minPoolSize=settings.MIN_CONNECTIONS_COUNT,
            serverSelectionTimeoutMS=5000
        )
        
        # Verifica a conexão
        await mongo_client.admin.command('ping')
        
        # Configura o banco de dados
        db = mongo_client[settings.MONGODB_DB]
        
        logger.info(f"Conectado ao MongoDB em {settings.MONGODB_URL}")
        
        # Inicializa os índices
        await create_indexes()
        
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        logger.error(f"Falha ao conectar ao MongoDB: {e}")
        raise ConnectionFailure(f"Falha ao conectar ao MongoDB: {e}")


async def close_mongo_connection() -> None:
    """Fecha a conexão com o MongoDB."""
    global mongo_client
    
    if mongo_client is not None:
        mongo_client.close()
        mongo_client = None
        logger.info("Conexão com MongoDB fechada")


async def create_indexes() -> None:
    """
    Cria índices para as coleções no MongoDB.
    
    Esta função deve ser chamada durante a inicialização da aplicação
    para garantir que todos os índices necessários estejam criados.
    """
    if db is None:
        logger.error("Tentativa de criar índices sem conexão ao MongoDB")
        return
    
    # Dicionário de coleções e seus índices
    collections_indexes = {
        "users": user_indexes,
        "financial_data": financial_data_indexes, 
        "scenarios": scenario_indexes
    }
    
    for collection_name, indexes in collections_indexes.items():
        try:
            collection = db[collection_name]
            
            # Cria cada índice definido para a coleção
            for index in indexes:
                await collection.create_index(index.document)
            
            logger.info(f"Índices criados para coleção {collection_name}")
        except Exception as e:
            logger.error(f"Erro ao criar índices para {collection_name}: {e}")


def get_db() -> AsyncIOMotorDatabase:
    """
    Retorna a instância do banco de dados MongoDB.
    
    Returns:
        Instância do banco de dados MongoDB.
        
    Raises:
        ConnectionError: Se a conexão com o MongoDB não foi inicializada.
    """
    if db is None:
        raise ConnectionError("Conexão com MongoDB não inicializada")
    return db 