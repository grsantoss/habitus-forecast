#!/bin/bash

# Script de backup para MongoDB do Habitus Forecast
# Uso: backup.sh
# Dependências: mongodump

# Variáveis de configuração
MONGO_HOST=${MONGO_HOST:-mongo}
MONGO_PORT=${MONGO_PORT:-27017}
MONGO_DATABASE=${MONGO_DATABASE:-habitus-prod}
MONGO_USER=${MONGO_USER:-admin}
MONGO_PASSWORD=${MONGO_PASSWORD:-password}
BACKUP_DIR=${BACKUP_DIR:-/backups}
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_NAME="${MONGO_DATABASE}_${DATE}"
DAYS_TO_KEEP=7

# Função para log de atividades
log() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $1"
}

# Verifica se o diretório de backup existe
if [ ! -d "$BACKUP_DIR" ]; then
    log "Criando diretório de backup: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# Realiza o backup
log "Iniciando backup do banco de dados $MONGO_DATABASE..."
mongodump \
    --host="$MONGO_HOST" \
    --port="$MONGO_PORT" \
    --username="$MONGO_USER" \
    --password="$MONGO_PASSWORD" \
    --db="$MONGO_DATABASE" \
    --authenticationDatabase=admin \
    --gzip \
    --archive="$BACKUP_DIR/$BACKUP_NAME.gz"

# Verifica se o backup foi bem-sucedido
if [ $? -eq 0 ]; then
    log "Backup concluído com sucesso: $BACKUP_DIR/$BACKUP_NAME.gz"
    
    # Cria arquivo de metadados
    cat > "$BACKUP_DIR/$BACKUP_NAME.meta" << EOF
Backup: $BACKUP_NAME
Data: $(date)
Banco: $MONGO_DATABASE
Tamanho: $(du -h "$BACKUP_DIR/$BACKUP_NAME.gz" | cut -f1)
EOF
    
    # Remove backups antigos
    log "Removendo backups com mais de $DAYS_TO_KEEP dias..."
    find "$BACKUP_DIR" -name "*.gz" -type f -mtime +$DAYS_TO_KEEP -delete
    find "$BACKUP_DIR" -name "*.meta" -type f -mtime +$DAYS_TO_KEEP -delete
else
    log "ERRO: Falha ao realizar backup"
    exit 1
fi

log "Processo de backup concluído"
exit 0 