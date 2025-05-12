#!/bin/sh

# Script para substituir variáveis de ambiente nos arquivos estáticos
# Isso permite configurar o frontend em tempo de execução através de variáveis de ambiente
# Referência: https://github.com/docker-library/docs/tree/master/nginx#using-environment-variables-in-nginx-configuration

set -e

echo "Configurando variáveis de ambiente do frontend..."

# Lista de variáveis a serem substituídas
JS_FILES=$(find /usr/share/nginx/html -type f -name "*.js")

# Substitui as variáveis em arquivos JS
for JS_FILE in $JS_FILES; do
  # API_URL
  if [ -n "$API_URL" ]; then
    echo "Substituindo API_URL em $JS_FILE"
    sed -i "s|__API_URL__|$API_URL|g" $JS_FILE
  fi
  
  # APP_ENV
  if [ -n "$APP_ENV" ]; then
    echo "Substituindo APP_ENV em $JS_FILE"
    sed -i "s|__APP_ENV__|$APP_ENV|g" $JS_FILE
  fi
  
  # Adicione outras variáveis conforme necessário
done

# Configura as variáveis de ambiente no nginx.conf também
if [ -n "$API_URL" ]; then
  echo "Configurando API_URL no nginx.conf"
  sed -i "s|\${API_URL}|$API_URL|g" /etc/nginx/conf.d/default.conf
fi

echo "Configuração de variáveis de ambiente concluída." 