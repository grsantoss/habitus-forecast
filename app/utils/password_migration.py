#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para migração de senhas entre os sistemas Node.js e Python.
Este utilitário identifica diferentes formatos de hash, converte entre sistemas
e verifica a compatibilidade de senhas.

Funcionalidades:
- Detecta o formato do hash da senha (bcrypt, pbkdf2, etc.)
- Converte hashes entre diferentes formatos
- Verifica a compatibilidade de senhas entre os sistemas
"""

import base64
import binascii
import hashlib
import hmac
import logging
import re
from typing import Dict, Optional, Tuple, Union

import bcrypt

logger = logging.getLogger("password_migration")

# Regex para identificar formatos de hash
HASH_PATTERNS = {
    "bcrypt": r"^\$2[ayb]\$.{56}$",  # Formato do bcrypt
    "pbkdf2": r"^pbkdf2:sha256:\d+\$.*\$.*$",  # Formato do Flask-Security
    "sha256": r"^[a-f0-9]{64}$",  # Formato SHA-256 simples
    "django_pbkdf2_sha256": r"^pbkdf2_sha256\$\d+\$[a-zA-Z0-9]+\$[a-zA-Z0-9+/=]+$",  # Django PBKDF2
    "node_scrypt": r"^scrypt:.*,.*,.*$",  # Node.js scrypt
}

class PasswordFormatError(Exception):
    """Erro ao processar formato de senha."""
    pass

def detect_hash_format(password_hash: str) -> str:
    """
    Detecta o formato do hash da senha.
    
    Args:
        password_hash: Hash da senha a ser analisado
        
    Returns:
        str: Nome do formato detectado
        
    Raises:
        PasswordFormatError: Se o formato não for reconhecido
    """
    for format_name, pattern in HASH_PATTERNS.items():
        if re.match(pattern, password_hash):
            return format_name
    
    # Se não reconhecer o formato, verifica se parece com base64
    try:
        decoded = base64.b64decode(password_hash)
        if len(decoded) >= 20:  # Tamanho mínimo razoável para um hash
            return "base64_unknown"
    except:
        pass
    
    raise PasswordFormatError(f"Formato de hash não reconhecido: {password_hash[:10]}...")

def migrate_password_hash(password_hash: str) -> str:
    """
    Migra um hash de senha do formato Node.js para o formato Python.
    
    Args:
        password_hash: Hash da senha no formato original
        
    Returns:
        str: Hash da senha no formato esperado pelo sistema Python
    """
    # Se a senha já estiver no formato bcrypt, retorna como está
    if re.match(HASH_PATTERNS["bcrypt"], password_hash):
        logger.debug("Hash já está no formato bcrypt, mantendo como está")
        return password_hash

    # Verifica formato de hash
    try:
        hash_format = detect_hash_format(password_hash)
        logger.debug(f"Formato de hash detectado: {hash_format}")
    except PasswordFormatError as e:
        logger.warning(f"Não foi possível detectar formato de hash: {str(e)}")
        # Se não conseguir detectar o formato, retorna um hash temporário
        # que forçará o usuário a redefinir a senha no primeiro login
        temp_hash = bcrypt.hashpw(b"REQUIRE_RESET", bcrypt.gensalt(rounds=10))
        return temp_hash.decode("utf-8")
    
    # Conversão baseada no formato detectado
    try:
        if hash_format == "node_scrypt":
            # Formato scrypt do Node.js (comum em projetos Express/Node.js)
            # Como não podemos converter diretamente para bcrypt, criamos um hash temporário
            logger.info("Convertendo hash scrypt para bcrypt temporário")
            temp_hash = bcrypt.hashpw(b"REQUIRE_RESET", bcrypt.gensalt(rounds=10))
            return temp_hash.decode("utf-8")
        
        elif hash_format == "pbkdf2" or hash_format == "django_pbkdf2_sha256":
            # Para formatos PBKDF2, também criamos um hash temporário
            logger.info("Convertendo hash PBKDF2 para bcrypt temporário")
            temp_hash = bcrypt.hashpw(b"REQUIRE_RESET", bcrypt.gensalt(rounds=12))
            return temp_hash.decode("utf-8")
        
        elif hash_format == "sha256":
            # Mesmo caso para SHA-256 - não é possível converter diretamente
            logger.info("Convertendo hash SHA-256 para bcrypt temporário")
            temp_hash = bcrypt.hashpw(b"REQUIRE_RESET", bcrypt.gensalt(rounds=12))
            return temp_hash.decode("utf-8")
        
        else:
            # Para outros formatos não reconhecidos
            logger.warning(f"Formato de hash não conversível: {hash_format}")
            temp_hash = bcrypt.hashpw(b"REQUIRE_RESET", bcrypt.gensalt(rounds=12))
            return temp_hash.decode("utf-8")
            
    except Exception as e:
        logger.error(f"Erro ao converter hash: {str(e)}")
        # Em caso de erro, retorna um hash temporário
        temp_hash = bcrypt.hashpw(b"REQUIRE_RESET", bcrypt.gensalt(rounds=12))
        return temp_hash.decode("utf-8")

def verify_password_compatibility(password: str, old_hash: str, new_hash: str) -> bool:
    """
    Verifica se a senha é compatível com ambos os hashes (antigo e novo).
    
    Args:
        password: Senha em texto plano
        old_hash: Hash no formato antigo (Node.js)
        new_hash: Hash no formato novo (Python)
        
    Returns:
        bool: True se a senha for compatível com ambos os hashes
    """
    old_format = detect_hash_format(old_hash)
    new_format = detect_hash_format(new_hash)
    
    # Verifica compatibilidade com o hash antigo
    old_compatible = False
    if old_format == "bcrypt":
        old_compatible = bcrypt.checkpw(password.encode("utf-8"), old_hash.encode("utf-8"))
    elif old_format == "node_scrypt":
        # Implementação simplificada - na prática, precisaria implementar a verificação scrypt
        # conforme usado no Node.js
        old_compatible = False
    elif old_format == "pbkdf2":
        # Implementação simplificada para PBKDF2
        old_compatible = False
    
    # Verifica compatibilidade com o hash novo
    new_compatible = bcrypt.checkpw(password.encode("utf-8"), new_hash.encode("utf-8"))
    
    return old_compatible and new_compatible

def needs_password_reset(password_hash: str) -> bool:
    """
    Verifica se um hash de senha indica que o usuário precisa redefinir a senha.
    
    Args:
        password_hash: Hash da senha a ser verificado
        
    Returns:
        bool: True se o usuário precisar redefinir a senha
    """
    # Verifica se é um hash bcrypt de senha temporária
    if re.match(HASH_PATTERNS["bcrypt"], password_hash):
        # Verifica se é o hash da senha temporária "REQUIRE_RESET"
        return bcrypt.checkpw(b"REQUIRE_RESET", password_hash.encode("utf-8"))
    
    # Para outros formatos, assume que precisa de reset
    return True

def generate_password_hash(password: str, rounds: int = 12) -> str:
    """
    Gera um hash bcrypt para a senha fornecida.
    
    Args:
        password: Senha em texto plano
        rounds: Número de rounds para o bcrypt (padrão: 12)
        
    Returns:
        str: Hash bcrypt da senha
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def compare_password_hash(password: str, password_hash: str) -> bool:
    """
    Compara uma senha em texto plano com um hash.
    
    Args:
        password: Senha em texto plano
        password_hash: Hash da senha a ser comparado
        
    Returns:
        bool: True se a senha corresponder ao hash
    """
    try:
        hash_format = detect_hash_format(password_hash)
        
        if hash_format == "bcrypt":
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        else:
            # Para outros formatos, indica que a verificação não é possível
            logger.warning(f"Comparação não implementada para o formato: {hash_format}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao comparar hash: {str(e)}")
        return False 