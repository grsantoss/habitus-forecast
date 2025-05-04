#!/bin/bash

# Configurações
BACKUP_DIR="./backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="habitus-forecast"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Executar backup
mongodump --db $DB_NAME --out $BACKUP_DIR/$TIMESTAMP

# Compactar backup
tar -czf $BACKUP_DIR/$TIMESTAMP.tar.gz $BACKUP_DIR/$TIMESTAMP

# Remover diretório temporário
rm -rf $BACKUP_DIR/$TIMESTAMP

echo "Backup criado em: $BACKUP_DIR/$TIMESTAMP.tar.gz" 