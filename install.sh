#!/bin/bash

# ================================================================
# Script de Instalação Automatizada do Habitus Forecast
# ================================================================

# Cores para melhor legibilidade
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de utilidade
print_section() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Verifica se o script está sendo executado como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script precisa ser executado como root (sudo)."
    print_info "Por favor, execute: sudo bash install.sh"
    exit 1
fi

# Verifica o sistema operacional
if ! grep -q "Ubuntu" /etc/os-release; then
    print_warning "Este script foi testado apenas no Ubuntu 20.04 e 22.04 LTS."
    read -p "Continuar mesmo assim? (s/n): " continue_anyway
    if [[ ! $continue_anyway =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Bem-vindo
clear
cat << "EOF"
  _   _      _     _ _              ______                               _   
 | | | |    | |   (_) |             |  ___|                             | |  
 | |_| | ___| |__  _| |_ _   _ ___  | |_ ___  _ __ ___  ___ __ _ ___ ___| |_ 
 |  _  |/ _ \ '_ \| | __| | | / __| |  _/ _ \| '__/ _ \/ __/ _` / __/ __| __|
 | | | |  __/ |_) | | |_| |_| \__ \ | || (_) | | |  __/ (_| (_| \__ \__ \ |_ 
 \_| |_/\___|_.__/|_|\__|\__,_|___/ \_| \___/|_|  \___|\___\__,_|___/___/\__|
                                                                             
EOF
echo -e "${GREEN}Script de Instalação Automatizada${NC}"
echo -e "Este script irá configurar o Habitus Forecast em seu servidor.\n"

# ================================================================
# Coleta de informações
# ================================================================
print_section "Informações Necessárias"

# Domínio
read -p "Digite o domínio para a aplicação (ex: exemplo.com): " DOMAIN
while [[ -z "$DOMAIN" ]]; do
    print_error "O domínio não pode estar vazio."
    read -p "Digite o domínio para a aplicação (ex: exemplo.com): " DOMAIN
done

# Diretório de instalação
read -p "Diretório de instalação [/opt/habitus-forecast]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-/opt/habitus-forecast}

# MongoDB
read -p "Nome de usuário para MongoDB [admin]: " MONGO_USER
MONGO_USER=${MONGO_USER:-admin}

# Gera senha aleatória ou aceita entrada do usuário
read -p "Senha para o MongoDB [gerar senha aleatória]: " MONGO_PASSWORD
if [[ -z "$MONGO_PASSWORD" ]]; then
    MONGO_PASSWORD=$(openssl rand -base64 12)
    print_info "Senha gerada para MongoDB: $MONGO_PASSWORD"
fi

# Chave secreta para JWT
read -p "Chave secreta para JWT [gerar chave aleatória]: " SECRET_KEY
if [[ -z "$SECRET_KEY" ]]; then
    SECRET_KEY=$(openssl rand -hex 32)
    print_info "Chave secreta gerada: $SECRET_KEY"
fi

# Fuso horário
read -p "Fuso horário [America/Sao_Paulo]: " TIMEZONE
TIMEZONE=${TIMEZONE:-America/Sao_Paulo}

# Configurar SSL
read -p "Configurar SSL com Let's Encrypt? (s/n) [s]: " SETUP_SSL
SETUP_SSL=${SETUP_SSL:-s}

# Confirmar informações
echo -e "\n${YELLOW}Resumo da instalação:${NC}"
echo -e "Domínio: ${DOMAIN}"
echo -e "Diretório de instalação: ${INSTALL_DIR}"
echo -e "Usuário MongoDB: ${MONGO_USER}"
echo -e "Fuso horário: ${TIMEZONE}"
echo -e "Configurar SSL: ${SETUP_SSL}"

read -p "As informações estão corretas? Continuar com a instalação? (s/n) [s]: " CONFIRM
CONFIRM=${CONFIRM:-s}
if [[ ! $CONFIRM =~ ^[Ss]$ ]]; then
    print_info "Instalação cancelada pelo usuário."
    exit 0
fi

# ================================================================
# Preparação do sistema
# ================================================================
print_section "Atualizando o Sistema"

# Atualiza o sistema
apt update
if [ $? -ne 0 ]; then
    print_error "Falha ao atualizar a lista de pacotes."
    exit 1
fi
print_success "Lista de pacotes atualizada."

apt upgrade -y
if [ $? -ne 0 ]; then
    print_error "Falha ao atualizar os pacotes do sistema."
    exit 1
fi
print_success "Sistema atualizado."

# Instala pacotes essenciais
print_info "Instalando pacotes essenciais..."
apt install -y curl wget vim git software-properties-common apt-transport-https ca-certificates gnupg
if [ $? -ne 0 ]; then
    print_error "Falha ao instalar pacotes essenciais."
    exit 1
fi
print_success "Pacotes essenciais instalados."

# Configura o fuso horário
print_info "Configurando fuso horário para $TIMEZONE..."
timedatectl set-timezone $TIMEZONE
if [ $? -ne 0 ]; then
    print_error "Falha ao configurar o fuso horário."
    exit 1
fi
print_success "Fuso horário configurado como $TIMEZONE."

# ================================================================
# Instalação do Docker e Docker Compose
# ================================================================
print_section "Instalando Docker e Docker Compose"

# Remove versões antigas do Docker
apt remove --purge -y docker docker-engine docker.io containerd runc || true
print_success "Versões antigas do Docker removidas (se existiam)."

# Instala os pacotes necessários para o Docker
print_info "Instalando dependências do Docker..."
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Adiciona a chave GPG oficial do Docker
print_info "Adicionando repositório do Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adiciona o repositório do Docker às fontes do APT
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualiza o índice de pacotes
apt update

# Instala Docker Engine
print_info "Instalando Docker Engine..."
apt install -y docker-ce docker-ce-cli containerd.io

# Verifica se o Docker foi instalado corretamente
if ! command -v docker &> /dev/null; then
    print_error "A instalação do Docker falhou."
    exit 1
fi

# Inicia e habilita o Docker
systemctl start docker
systemctl enable docker
print_success "Docker instalado e habilitado."

# Instalação do Docker Compose
print_info "Instalando Docker Compose..."
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verifica se o Docker Compose foi instalado corretamente
if ! command -v docker-compose &> /dev/null; then
    print_error "A instalação do Docker Compose falhou."
    exit 1
fi
print_success "Docker Compose instalado: $(docker-compose --version)"

# ================================================================
# Configuração do Firewall
# ================================================================
print_section "Configurando Firewall (UFW)"

# Instala UFW se não estiver instalado
apt install -y ufw

# Configura as regras do firewall
print_info "Configurando regras do firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Habilita o firewall apenas se não estiver habilitado
if ! ufw status | grep -q "Status: active"; then
    print_info "Habilitando firewall..."
    echo "y" | ufw enable
fi
print_success "Firewall configurado."

# ================================================================
# Obtenção e configuração do código
# ================================================================
print_section "Configurando o Habitus Forecast"

# Cria diretório de instalação
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR || exit 1

# Clona o repositório
print_info "Obtendo o código-fonte..."
if [ -d ".git" ]; then
    print_info "Repositório já existe. Atualizando..."
    git pull
else
    # Substitua pela URL real do seu repositório
    print_warning "Este script assume que você está executando-o do diretório raiz do projeto."
    print_info "Copiando arquivos locais para $INSTALL_DIR..."
    
    # Se o script estiver sendo executado de dentro do repositório, copie os arquivos
    SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
    cp -R $SCRIPT_DIR/* $INSTALL_DIR
fi

# Verifica se os arquivos essenciais existem
if [ ! -f "docker-compose.prod.yml" ] || [ ! -f "Dockerfile" ]; then
    print_error "Arquivos essenciais do Docker não encontrados. Verifique se você está no diretório correto."
    exit 1
fi
print_success "Código-fonte obtido com sucesso."

# ================================================================
# Configuração do Ambiente
# ================================================================
print_section "Configurando o Ambiente"

# Cria o diretório SSL e scripts
mkdir -p $INSTALL_DIR/ssl
mkdir -p $INSTALL_DIR/scripts

# Cria o arquivo .env.prod
cat > $INSTALL_DIR/.env.prod << EOF
# Configurações gerais
ENVIRONMENT=production
DEBUG=False
API_PREFIX=/api/v1
PORT=8000
WORKERS=4

# Configurações do MongoDB
MONGO_INITDB_ROOT_USERNAME=$MONGO_USER
MONGO_INITDB_ROOT_PASSWORD=$MONGO_PASSWORD
MONGODB_DB=habitus-prod

# Configuração de segurança
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Configurações CORS
CORS_ORIGINS=http://localhost,http://localhost:3000,https://$DOMAIN

# Configurações do sistema
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=10485760

# Configurações de domínio
DOMAIN=$DOMAIN
EOF

# Define permissões adequadas para o arquivo .env.prod
chmod 600 $INSTALL_DIR/.env.prod
print_success "Arquivo de ambiente .env.prod criado."

# ================================================================
# Configuração SSL
# ================================================================
if [[ $SETUP_SSL =~ ^[Ss]$ ]]; then
    print_section "Configurando SSL com Let's Encrypt"
    
    # Instala Certbot
    print_info "Instalando Certbot..."
    apt install -y certbot
    
    print_info "Obtendo certificado SSL para $DOMAIN..."
    # Verifica se os serviços estão rodando nas portas 80/443
    if lsof -Pi :80 -sTCP:LISTEN -t &>/dev/null; then
        print_warning "Porta 80 está em uso. Parando serviços temporariamente..."
        docker-compose -f docker-compose.prod.yml down || true
    fi
    
    # Obtém certificado SSL
    certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN
    
    if [ $? -ne 0 ]; then
        print_error "Falha ao obter certificado SSL. Continuando com certificado auto-assinado."
        # Gera um certificado autoassinado
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
          -keyout $INSTALL_DIR/ssl/privkey.pem \
          -out $INSTALL_DIR/ssl/fullchain.pem \
          -subj "/C=BR/ST=Estado/L=Cidade/O=Organização/CN=$DOMAIN"
    else
        # Copia certificados para o diretório do projeto
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $INSTALL_DIR/ssl/
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $INSTALL_DIR/ssl/
        print_success "Certificado SSL obtido com sucesso."
        
        # Configura renovação automática
        cat > $INSTALL_DIR/scripts/renew-ssl.sh << 'EOF'
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/DOMAIN/fullchain.pem INSTALL_DIR/ssl/
cp /etc/letsencrypt/live/DOMAIN/privkey.pem INSTALL_DIR/ssl/
docker restart habitus-forecast-frontend-prod
EOF
        
        # Substitui variáveis no script
        sed -i "s|DOMAIN|$DOMAIN|g" $INSTALL_DIR/scripts/renew-ssl.sh
        sed -i "s|INSTALL_DIR|$INSTALL_DIR|g" $INSTALL_DIR/scripts/renew-ssl.sh
        
        chmod +x $INSTALL_DIR/scripts/renew-ssl.sh
        
        # Adiciona ao crontab para execução automática
        (crontab -l 2>/dev/null; echo "0 0,12 * * * $INSTALL_DIR/scripts/renew-ssl.sh") | crontab -
        print_success "Renovação automática de SSL configurada."
    fi
else
    print_info "Gerando certificado SSL autoassinado..."
    # Gera um certificado autoassinado
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout $INSTALL_DIR/ssl/privkey.pem \
      -out $INSTALL_DIR/ssl/fullchain.pem \
      -subj "/C=BR/ST=Estado/L=Cidade/O=Organização/CN=$DOMAIN"
    print_success "Certificado SSL autoassinado gerado."
fi

# Ajusta as permissões
chown -R $SUDO_USER:$SUDO_USER $INSTALL_DIR/ssl

# ================================================================
# Construção e inicialização dos containers
# ================================================================
print_section "Construindo e Iniciando os Containers"

# Muda permissões para o usuário
chown -R $SUDO_USER:$SUDO_USER $INSTALL_DIR

# Constrói as imagens Docker
print_info "Construindo imagens Docker (pode levar alguns minutos)..."
cd $INSTALL_DIR
su - $SUDO_USER -c "cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml build"

if [ $? -ne 0 ]; then
    print_error "Falha ao construir as imagens Docker."
    exit 1
fi
print_success "Imagens Docker construídas com sucesso."

# Inicia os containers
print_info "Iniciando containers..."
su - $SUDO_USER -c "cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml up -d"

if [ $? -ne 0 ]; then
    print_error "Falha ao iniciar os containers."
    exit 1
fi
print_success "Containers iniciados com sucesso."

# ================================================================
# Conclusão
# ================================================================
print_section "Instalação Concluída!"

echo -e "${GREEN}O Habitus Forecast foi instalado com sucesso!${NC}"
echo ""
echo -e "📋 Resumo da Instalação:"
echo -e "   🌐 Aplicação: https://$DOMAIN"
echo -e "   📁 Diretório de instalação: $INSTALL_DIR"
echo -e "   🔑 Usuário MongoDB: $MONGO_USER"
echo -e "   🔑 Senha MongoDB: $MONGO_PASSWORD"
echo ""
echo -e "📝 Comandos úteis:"
echo -e "   ▶️ Iniciar containers:    cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml up -d"
echo -e "   ⏹️ Parar containers:      cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml down"
echo -e "   🔄 Reiniciar containers:  cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml restart"
echo -e "   📊 Verificar status:      cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml ps"
echo -e "   📋 Ver logs:              cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${YELLOW}IMPORTANTE: Guarde as credenciais geradas em um local seguro!${NC}"
echo -e "Para mais informações, consulte o arquivo de documentação em docs/installation_guide.md"
echo ""
echo -e "${BLUE}Obrigado por escolher o Habitus Forecast!${NC}" 