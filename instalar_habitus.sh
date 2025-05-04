#!/bin/bash

# Script de Instalação Automática - Habitus Finance
# Este script instala todas as dependências e configura a aplicação

# Cores para o terminal
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AZUL='\033[0;34m'
AMARELO='\033[0;33m'
RESET='\033[0m'

echo -e "${AZUL}=== Bem-vindo à instalação do Habitus Finance ===${RESET}"

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
  echo -e "${VERMELHO}Por favor, não execute este script como root ou com sudo${RESET}"
  exit 1
fi

# Função para verificar se o comando foi bem-sucedido
verificar_comando() {
  if [ $? -eq 0 ]; then
    echo -e "${VERDE}✓ $1${RESET}"
  else
    echo -e "${VERMELHO}✗ Erro ao $1${RESET}"
    exit 1
  fi
}

# Perguntar modo de instalação
echo -e "${AZUL}Escolha o modo de instalação:${RESET}"
echo -e "1) Instalação para desenvolvimento (localhost)"
echo -e "2) Instalação para produção (com configuração SMTP e certificado SSL)"
read -p "Opção [1]: " MODO_INSTALACAO
MODO_INSTALACAO=${MODO_INSTALACAO:-1}

if [ "$MODO_INSTALACAO" != "1" ] && [ "$MODO_INSTALACAO" != "2" ]; then
  echo -e "${VERMELHO}Opção inválida. Usando modo de desenvolvimento.${RESET}"
  MODO_INSTALACAO=1
fi

# Verificar requisitos
echo -e "${AZUL}Verificando requisitos...${RESET}"

# Verificar Node.js
if ! command -v node &> /dev/null; then
  echo -e "${VERMELHO}Node.js não encontrado. Instalando...${RESET}"
  
  # Instalar NVM
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
  verificar_comando "instalar NVM"
  
  # Carregar NVM
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  
  # Instalar Node.js
  nvm install 16
  verificar_comando "instalar Node.js"
else
  node_version=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
  if [ "$node_version" -lt 14 ]; then
    echo -e "${VERMELHO}Versão do Node.js muito antiga. Instalando nova versão...${RESET}"
    nvm install 16
    verificar_comando "atualizar Node.js"
  else
    echo -e "${VERDE}✓ Node.js já instalado ($(node -v))${RESET}"
  fi
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
  echo -e "${VERMELHO}Docker não encontrado. Instalando...${RESET}"
  
  # Instalar Docker no Windows usando Chocolatey
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${AZUL}Detectado Windows. Por favor, instale o Docker Desktop manualmente:${RESET}"
    echo -e "https://docs.docker.com/desktop/install/windows-install/"
    read -p "Pressione Enter após instalar o Docker Desktop..."
  else
    # Instalar Docker no Linux
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    verificar_comando "instalar Docker"
    
    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER
    verificar_comando "configurar permissões do Docker"
    echo -e "${AZUL}Reinicie o terminal para aplicar as permissões do Docker${RESET}"
  fi
else
  echo -e "${VERDE}✓ Docker já instalado ($(docker --version))${RESET}"
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
  echo -e "${VERMELHO}Docker Compose não encontrado. Instalando...${RESET}"
  
  # Instalar Docker Compose no Windows (já vem com Docker Desktop)
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${AZUL}Docker Compose deve estar incluso no Docker Desktop${RESET}"
  else
    # Instalar Docker Compose no Linux
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    verificar_comando "instalar Docker Compose"
  fi
else
  echo -e "${VERDE}✓ Docker Compose já instalado ($(docker-compose --version))${RESET}"
fi

# Clonar repositório se não existir
echo -e "${AZUL}Verificando repositório...${RESET}"
if [ ! -d "habitus-finance" ]; then
  echo -e "${AZUL}Clonando repositório...${RESET}"
  git clone https://github.com/seu-usuario/habitus-finance.git
  verificar_comando "clonar repositório"
  cd habitus-finance
else
  echo -e "${VERDE}✓ Repositório já existe${RESET}"
  cd habitus-finance
  echo -e "${AZUL}Atualizando repositório...${RESET}"
  git pull
  verificar_comando "atualizar repositório"
fi

# Instalar dependências
echo -e "${AZUL}Instalando dependências do servidor...${RESET}"
npm install
verificar_comando "instalar dependências do servidor"

echo -e "${AZUL}Instalando dependências do cliente...${RESET}"
cd client
npm install
verificar_comando "instalar dependências do cliente"
cd ..

# Criar diretório de uploads
echo -e "${AZUL}Criando diretório de uploads...${RESET}"
mkdir -p server/uploads
chmod 755 server/uploads
verificar_comando "criar diretório de uploads"

# Configurar Nginx
echo -e "${AZUL}Configurando proxy reverso (Nginx)...${RESET}"
mkdir -p nginx/ssl
verificar_comando "criar diretórios para Nginx"

# Criar arquivo de configuração do Nginx
cat > nginx/default.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    # Redirecionar HTTP para HTTPS quando SSL for configurado
    # Descomente as linhas abaixo e ajuste o server_name quando tiver um domínio
    # listen 80;
    # server_name seudominio.com www.seudominio.com;
    # return 301 https://$host$request_uri;

    location / {
        proxy_pass http://app:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Configuração HTTPS (descomente e ajuste quando tiver SSL)
# server {
#     listen 443 ssl http2;
#     server_name seudominio.com www.seudominio.com;
#
#     ssl_certificate /etc/nginx/ssl/fullchain.pem;
#     ssl_certificate_key /etc/nginx/ssl/privkey.pem;
#     ssl_session_timeout 1d;
#     ssl_session_cache shared:SSL:50m;
#     ssl_session_tickets off;
#
#     # Configurações recomendadas de segurança
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
#     ssl_prefer_server_ciphers off;
#
#     # HSTS (descomente quando estiver pronto para produção)
#     # add_header Strict-Transport-Security "max-age=63072000" always;
#
#     location / {
#         proxy_pass http://app:5000;
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade $http_upgrade;
#         proxy_set_header Connection 'upgrade';
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#         proxy_cache_bypass $http_upgrade;
#     }
# }
EOF
verificar_comando "criar configuração do Nginx"

# Atualizar docker-compose.prod.yml se não existir
if [ ! -f "docker-compose.prod.yml" ] || ! grep -q "nginx:" "docker-compose.prod.yml"; then
  cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: habitus-app
    restart: always
    environment:
      - NODE_ENV=production
      - MONGO_URI=${MONGO_URI}
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRE=${JWT_EXPIRE}
      - FRONTEND_URL=${FRONTEND_URL}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
      - REDIS_URL=redis://redis:6379
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_SECURE=${SMTP_SECURE}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FROM_NAME=${FROM_NAME}
      - FROM_EMAIL=${FROM_EMAIL}
    depends_on:
      - mongodb
      - redis
    networks:
      - habitus-network

  nginx:
    image: nginx:alpine
    container_name: habitus-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - habitus-network

  certbot:
    image: certbot/certbot
    container_name: habitus-certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - nginx
    command: renew --dry-run
    entrypoint: "sleep infinity"

  mongodb:
    image: mongo:latest
    container_name: habitus-mongodb
    restart: always
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_USER}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
    networks:
      - habitus-network

  redis:
    image: redis:latest
    container_name: habitus-redis
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - habitus-network

volumes:
  mongodb_data:
  redis_data:

networks:
  habitus-network:
    driver: bridge
EOF
  verificar_comando "atualizar docker-compose.prod.yml com Nginx e Certbot"
else
  echo -e "${VERDE}✓ Docker-compose.prod.yml já configurado${RESET}"
fi

# Criar script para configuração do SSL
cat > configurar-ssl.sh << 'EOF'
#!/bin/bash

# Script para configurar SSL com Let's Encrypt

# Cores para o terminal
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AZUL='\033[0;34m'
AMARELO='\033[0;33m'
RESET='\033[0m'

# Verificar se o domínio foi fornecido
if [ -z "$1" ]; then
  echo -e "${VERMELHO}Erro: Por favor, forneça um domínio como argumento.${RESET}"
  echo -e "Exemplo: ./configurar-ssl.sh meusite.com"
  exit 1
fi

DOMINIO=$1
EMAIL=${2:-"admin@$DOMINIO"}

echo -e "${AZUL}=== Configurando SSL para $DOMINIO ===${RESET}"

# Atualizar a configuração do Nginx para usar o domínio
sed -i "s/server_name localhost;/server_name $DOMINIO www.$DOMINIO;/" nginx/default.conf
sed -i "s/# server_name seudominio.com/server_name $DOMINIO/" nginx/default.conf
sed -i "s/# listen 443 ssl http2;/listen 443 ssl http2;/" nginx/default.conf

# Criar diretórios necessários
mkdir -p certbot/www
mkdir -p nginx/ssl

# Iniciar o Nginx temporariamente para o desafio do Let's Encrypt
docker-compose -f docker-compose.prod.yml up -d nginx

# Executar Certbot para obter o certificado
docker run --rm -v "$(pwd)/nginx/ssl:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" \
  --network habitus-network \
  certbot/certbot certonly --webroot --webroot-path=/var/www/certbot \
  --email $EMAIL --agree-tos --no-eff-email \
  -d $DOMINIO -d www.$DOMINIO

# Verificar se o certificado foi obtido com sucesso
if [ $? -eq 0 ]; then
  echo -e "${VERDE}✓ Certificado SSL obtido com sucesso!${RESET}"
  
  # Ativar a configuração HTTPS no Nginx
  sed -i "s/# return 301 https:\/\/\$host\$request_uri;/return 301 https:\/\/\$host\$request_uri;/" nginx/default.conf
  
  # Substituir o comentário do bloco HTTPS
  sed -i "s/# server {/server {/" nginx/default.conf
  sed -i "s/#     listen 443 ssl http2;/    listen 443 ssl http2;/" nginx/default.conf
  
  # Atualizar as linhas dos certificados
  CERT_PATH="/etc/letsencrypt/live/$DOMINIO"
  sed -i "s|#     ssl_certificate /etc/nginx/ssl/fullchain.pem;|    ssl_certificate $CERT_PATH/fullchain.pem;|" nginx/default.conf
  sed -i "s|#     ssl_certificate_key /etc/nginx/ssl/privkey.pem;|    ssl_certificate_key $CERT_PATH/privkey.pem;|" nginx/default.conf
  
  # Reiniciar o Nginx para aplicar as alterações
  docker-compose -f docker-compose.prod.yml restart nginx
  
  # Configurar renovação automática do certificado
  cat > renovar-certificado.sh << 'CERTEOF'
#!/bin/bash
docker run --rm -v "$(pwd)/nginx/ssl:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot renew --webroot --webroot-path=/var/www/certbot
docker-compose -f docker-compose.prod.yml restart nginx
CERTEOF
  
  chmod +x renovar-certificado.sh
  
  # Adicionar ao crontab
  (crontab -l 2>/dev/null; echo "0 3 * * * $(pwd)/renovar-certificado.sh > /dev/null 2>&1") | crontab -
  
  echo -e "${VERDE}✓ Renovação automática configurada! O certificado será renovado automaticamente.${RESET}"
  echo -e "${VERDE}✓ Sua aplicação está agora disponível em https://$DOMINIO${RESET}"
else
  echo -e "${VERMELHO}✗ Falha ao obter o certificado SSL.${RESET}"
  echo -e "${AMARELO}Verifique se o domínio $DOMINIO está corretamente apontado para este servidor.${RESET}"
fi
EOF

chmod +x configurar-ssl.sh
verificar_comando "criar script de configuração SSL"

# Configuração de acordo com o modo escolhido
if [ "$MODO_INSTALACAO" = "1" ]; then
  # Modo desenvolvimento
  echo -e "${AZUL}Configurando ambiente de desenvolvimento...${RESET}"
  
  # Criar arquivo .env para desenvolvimento
  if [ ! -f ".env" ]; then
    cat > .env << EOF
MONGO_URI=mongodb://habitus:habitus123@localhost:27017/habitus-finance?authSource=admin
JWT_SECRET=habitus-secure-jwt-secret-key-change-in-production
JWT_EXPIRE=30d
PORT=5000
NODE_ENV=development
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100
ALLOWED_FILE_TYPES=xlsx,xls,csv
MAX_FILE_SIZE=10485760
CACHE_TTL=3600
LOG_LEVEL=info
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost
SMTP_HOST=
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=
SMTP_PASSWORD=
FROM_NAME=Habitus Finance
FROM_EMAIL=noreply@habitusfinance.com
EOF
    verificar_comando "criar arquivo .env para desenvolvimento"
  else
    echo -e "${VERDE}✓ Arquivo .env já existe${RESET}"
  fi
  
  # Iniciar containers Docker
  echo -e "${AZUL}Iniciando containers Docker (MongoDB e Redis)...${RESET}"
  docker-compose up -d mongodb redis
  verificar_comando "iniciar containers Docker"
  
  # Aguardar MongoDB iniciar
  echo -e "${AZUL}Aguardando MongoDB inicializar...${RESET}"
  sleep 10
  
  # Executar seed do banco de dados
  echo -e "${AZUL}Populando banco de dados...${RESET}"
  npm run db:seed
  verificar_comando "popular banco de dados"
  
  # Mostrar credenciais padrão
  echo -e "${AZUL}=== Instalação de desenvolvimento concluída com sucesso ===${RESET}"
  echo -e "${VERDE}Credenciais de acesso:${RESET}"
  echo -e "Admin: admin@habitus.com / Admin123!"
  echo -e "Teste: teste@habitus.com / Teste123!"
  
  echo -e "${AZUL}Para iniciar a aplicação em modo desenvolvimento, execute:${RESET}"
  echo -e "cd habitus-finance && npm run dev"
  
  echo -e "${AZUL}A aplicação estará disponível em:${RESET}"
  echo -e "http://localhost:3000"

else
  # Modo produção
  echo -e "${AZUL}=== Configuração de Produção - Habitus Finance ===${RESET}"
  
  # Gerar chave JWT aleatória
  JWT_SECRET=$(openssl rand -hex 32)
  
  # Solicitar informações de produção
  read -p "Digite o domínio frontend (ex: app.habitusfinance.com): " FRONTEND_URL
  read -p "Digite a senha para o MongoDB [habitus123]: " MONGO_PASSWORD
  MONGO_PASSWORD=${MONGO_PASSWORD:-"habitus123"}
  MONGO_USER="habitus"
  MONGO_URI="mongodb://${MONGO_USER}:${MONGO_PASSWORD}@mongodb:27017/habitus-finance?authSource=admin"
  
  read -p "Porta da aplicação [5000]: " PORT
  PORT=${PORT:-5000}
  
  # Configurações SMTP
  echo -e "${AZUL}Configuração SMTP para recuperação de senha${RESET}"
  read -p "Host SMTP: " SMTP_HOST
  read -p "Porta SMTP [587]: " SMTP_PORT
  SMTP_PORT=${SMTP_PORT:-587}
  read -p "Usar conexão segura (SSL/TLS)? [s/N]: " SMTP_SECURE_CHOICE
  SMTP_SECURE=$(echo "$SMTP_SECURE_CHOICE" | grep -i "^s" > /dev/null && echo "true" || echo "false")
  read -p "Usuário SMTP: " SMTP_USER
  read -sp "Senha SMTP: " SMTP_PASSWORD
  echo
  read -p "Nome do remetente [Habitus Finance]: " FROM_NAME
  FROM_NAME=${FROM_NAME:-"Habitus Finance"}
  read -p "Email do remetente [noreply@habitusfinance.com]: " FROM_EMAIL
  FROM_EMAIL=${FROM_EMAIL:-"noreply@habitusfinance.com"}
  
  # Definir variáveis de ambiente
  JWT_EXPIRE="7d"
  ALLOWED_ORIGINS="https://${FRONTEND_URL},http://${FRONTEND_URL}"
  
  # Criar arquivo .env de produção
  cat > .env << EOF
NODE_ENV=production
MONGO_URI=${MONGO_URI}
MONGO_USER=${MONGO_USER}
MONGO_PASSWORD=${MONGO_PASSWORD}
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRE=${JWT_EXPIRE}
PORT=${PORT}
FRONTEND_URL=${FRONTEND_URL}
ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
SMTP_SECURE=${SMTP_SECURE}
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
FROM_NAME=${FROM_NAME}
FROM_EMAIL=${FROM_EMAIL}
EOF
  verificar_comando "criar arquivo .env para produção"
  
  # Perguntar se quer configurar HTTPS com Let's Encrypt
  read -p "Configurar HTTPS com Let's Encrypt? [s/N]: " SSL_CHOICE
  if [[ "$SSL_CHOICE" =~ ^[Ss] ]]; then
    read -p "Email para certificado Let's Encrypt [${FROM_EMAIL}]: " SSL_EMAIL
    SSL_EMAIL=${SSL_EMAIL:-${FROM_EMAIL}}
    ./configurar-ssl.sh $FRONTEND_URL $SSL_EMAIL
  fi
  
  # Iniciar em modo produção
  echo -e "${AZUL}Iniciando aplicação em modo produção...${RESET}"
  docker-compose -f docker-compose.prod.yml up -d
  verificar_comando "iniciar containers em modo produção"
  
  # Mostrar credenciais padrão
  echo -e "${AZUL}=== Instalação de produção concluída com sucesso ===${RESET}"
  echo -e "${VERDE}Credenciais de acesso:${RESET}"
  echo -e "Admin: admin@habitus.com / Admin123!"
  echo -e "Teste: teste@habitus.com / Teste123!"
  
  if [[ "$SSL_CHOICE" =~ ^[Ss] ]]; then
    echo -e "${VERDE}Habitus Finance está rodando em produção em https://${FRONTEND_URL}${RESET}"
  else
    echo -e "${VERDE}Habitus Finance está rodando em produção em http://${FRONTEND_URL}${RESET}"
    echo -e "${AMARELO}ATENÇÃO: Para habilitar HTTPS posteriormente, execute:${RESET}"
    echo -e "./configurar-ssl.sh ${FRONTEND_URL}"
  fi
fi