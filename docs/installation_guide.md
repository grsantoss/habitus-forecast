# Guia de Instalação do Habitus Forecast com Docker

![Habitus Forecast Logo](../image/logo.png)

Este guia fornece instruções passo a passo para instalar e configurar o Habitus Forecast em uma VPS Ubuntu utilizando Docker e docker-compose. Foi desenvolvido para usuários com conhecimento básico em Linux, sendo detalhado o suficiente para que mesmo entusiastas iniciantes possam seguir sem problemas.

**Última atualização**: `Data: 01/11/2023`

**Versão do Aplicativo**: `1.0.0`

## Sumário

- [Pré-requisitos e Requisitos Mínimos](#pré-requisitos-e-requisitos-mínimos)
- [Preparação da VPS](#preparação-da-vps)
- [Instalação do Docker e Docker Compose](#instalação-do-docker-e-docker-compose)
- [Obtenção do Código da Aplicação](#obtenção-do-código-da-aplicação)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Construção e Inicialização dos Containers](#construção-e-inicialização-dos-containers)
- [Configuração do Servidor Web e SSL](#configuração-do-servidor-web-e-ssl)
- [Verificação e Teste da Instalação](#verificação-e-teste-da-instalação)
- [Manutenção Básica](#manutenção-básica)
- [Solução de Problemas Comuns](#solução-de-problemas-comuns)
- [Segurança Básica](#segurança-básica)

## Pré-requisitos e Requisitos Mínimos

### Requisitos de Hardware

Para um ambiente de produção com desempenho adequado usando Docker, recomendamos:

| Recurso | Mínimo Recomendado | Ideal para Produção |
|---------|--------------------|--------------------|
| CPU     | 2 núcleos          | 4 núcleos          |
| RAM     | 4 GB               | 8 GB               |
| Disco   | 30 GB SSD          | 60 GB SSD          |
| Rede    | 1 Gbps             | 1 Gbps             |

### Sistema Operacional

Este guia foi testado com:
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS

> **Nota**: Embora o sistema possa funcionar em outras versões ou distribuições, recomendamos usar o Ubuntu LTS para melhor compatibilidade e suporte.

## Preparação da VPS

### 1. Acesso via SSH

Primeiro, conecte-se à sua VPS usando SSH. Você precisará do endereço IP e das credenciais fornecidas pelo seu provedor de VPS.

```bash
ssh usuario@seu-ip-da-vps
```

Substitua `usuario` e `seu-ip-da-vps` pelas suas informações reais.

> **Dica de Segurança**: É recomendável configurar a autenticação por chave SSH em vez de senha. Seu provedor de VPS geralmente oferece esta opção durante a criação do servidor.

### 2. Atualização Inicial do Sistema

Após conectar-se, atualize o sistema operacional:

```bash
# Atualiza a lista de pacotes
sudo apt update

# Instala as atualizações disponíveis
sudo apt upgrade -y

# Instala alguns pacotes essenciais
sudo apt install -y curl wget vim git software-properties-common apt-transport-https ca-certificates gnupg
```

### 3. Configuração do Fuso Horário

Configure o fuso horário correto para evitar problemas com logs e agendamento:

```bash
# Lista os fusos horários disponíveis
timedatectl list-timezones | grep America/Sao_Paulo

# Define o fuso horário (exemplo: Brasil/São Paulo)
sudo timedatectl set-timezone America/Sao_Paulo

# Verifica se a configuração foi aplicada
date
```

## Instalação do Docker e Docker Compose

### 1. Instalação do Docker

O Docker é a plataforma de containerização que usaremos para executar o Habitus Forecast:

```bash
# Remove versões antigas do Docker (caso existam)
sudo apt remove docker docker-engine docker.io containerd runc

# Instala os pacotes necessários
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Adiciona a chave GPG oficial do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adiciona o repositório do Docker às fontes do APT
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualiza o índice de pacotes
sudo apt update

# Instala a versão mais recente do Docker Engine e do containerd
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Inicia e habilita o Docker para iniciar na inicialização do sistema
sudo systemctl start docker
sudo systemctl enable docker

# Verifica se o Docker foi instalado corretamente
sudo docker run hello-world
```

### 2. Configuração de Permissões do Docker

Para evitar a necessidade de usar `sudo` com comandos Docker, adicione seu usuário ao grupo `docker`:

```bash
# Adiciona o usuário atual ao grupo docker
sudo usermod -aG docker $USER

# Aplica as alterações de grupo
newgrp docker

# Verifica se você pode executar comandos Docker sem sudo
docker run hello-world
```

### 3. Instalação do Docker Compose

O Docker Compose é usado para definir e executar aplicativos Docker multi-container:

```bash
# Baixa a versão mais recente do Docker Compose
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Aplica permissões de execução
sudo chmod +x /usr/local/bin/docker-compose

# Cria um link simbólico (opcional)
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verifica a instalação
docker-compose --version
```

## Obtenção do Código da Aplicação

### 1. Clonagem do Repositório

Baixe o código-fonte do Habitus Forecast do repositório Git:

```bash
# Navegue para o diretório onde deseja armazenar o projeto
cd /opt

# Clone o repositório (substitua pelo URL correto do seu repositório)
sudo git clone https://github.com/seu-usuario/habitus-forecast.git

# Defina as permissões corretas
sudo chown -R $USER:$USER /opt/habitus-forecast
cd habitus-forecast
```

### 2. Verificação da Estrutura do Projeto

Verifique se o repositório foi clonado corretamente e se todos os arquivos necessários estão presentes:

```bash
# Lista os arquivos no diretório raiz do projeto
ls -la

# Verifica se os arquivos Docker essenciais existem
ls -la Dockerfile docker-compose*.yml
```

Você deve ver a seguinte estrutura básica:
- `Dockerfile`: Define como construir a imagem Docker da API
- `docker-compose.yml`: Configuração Docker Compose para desenvolvimento
- `docker-compose.prod.yml`: Configuração Docker Compose para produção
- `app/`: Diretório contendo o código da API Python
- `client/`: Diretório contendo o código do frontend React
- `nginx/`: Configurações do servidor Nginx
- `scripts/`: Scripts de utilidade, como backup

## Configuração do Ambiente

### 1. Criação do Arquivo .env para Produção

Crie um arquivo `.env.prod` para configurar as variáveis de ambiente necessárias:

```bash
# Navegue para o diretório do projeto
cd /opt/habitus-forecast

# Crie o arquivo .env.prod
touch .env.prod

# Abra o arquivo para edição
nano .env.prod
```

Adicione as seguintes variáveis ao arquivo `.env.prod`:

```env
# Configurações gerais
ENVIRONMENT=production
DEBUG=False
API_PREFIX=/api/v1
PORT=8000
WORKERS=4

# Configurações do MongoDB
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=sua_senha_segura_aqui
MONGODB_DB=habitus-prod

# Configuração de segurança
SECRET_KEY=sua_chave_secreta_super_segura_com_pelo_menos_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Configurações CORS
CORS_ORIGINS=http://localhost,http://localhost:3000,https://seu-dominio.com

# Configurações do sistema
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=10485760

# Configurações de domínio
DOMAIN=seu-dominio.com
```

> **IMPORTANTE**: Substitua `sua_senha_segura_aqui`, `sua_chave_secreta_super_segura_com_pelo_menos_32_caracteres` e `seu-dominio.com` por valores reais. Para gerar uma chave secreta segura, você pode usar:
> ```bash
> openssl rand -hex 32
> ```

### 2. Geração de Certificado SSL Temporário (Opcional)

Se você ainda não tem um certificado SSL, pode criar um certificado autoassinado temporário:

```bash
# Crie um diretório para armazenar certificados SSL
mkdir -p /opt/habitus-forecast/ssl

# Gere um certificado SSL autoassinado
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/habitus-forecast/ssl/privkey.pem \
  -out /opt/habitus-forecast/ssl/fullchain.pem \
  -subj "/C=BR/ST=Estado/L=Cidade/O=Organização/CN=seu-dominio.com"
  
# Defina as permissões corretas
sudo chown -R $USER:$USER /opt/habitus-forecast/ssl
```

> **Nota**: Este certificado autoassinado é apenas para teste. Para produção, você deve usar um certificado válido, como os fornecidos pelo Let's Encrypt (instruções mais adiante).

## Construção e Inicialização dos Containers

### 1. Construção das Imagens Docker

Construa as imagens Docker para a API e o frontend:

```bash
# Navegue para o diretório do projeto
cd /opt/habitus-forecast

# Construa as imagens usando docker-compose
sudo docker-compose -f docker-compose.prod.yml build
```

Este processo pode levar alguns minutos, pois ele baixa todas as dependências necessárias e compila as imagens.

### 2. Inicialização dos Containers

Inicie os containers usando o Docker Compose:

```bash
# Inicie os containers em modo detached (background)
sudo docker-compose -f docker-compose.prod.yml up -d
```

O Docker Compose irá iniciar todos os serviços definidos no arquivo `docker-compose.prod.yml`:
- API (Python/FastAPI)
- Frontend (React/Nginx)
- MongoDB
- Serviço de backup

### 3. Verificação dos Containers em Execução

Verifique se todos os containers estão em execução:

```bash
# Lista todos os containers em execução
docker ps

# Verifica os logs da API
docker logs habitus-forecast-api-prod

# Verifica os logs do frontend
docker logs habitus-forecast-frontend-prod

# Verifica os logs do MongoDB
docker logs habitus-forecast-mongo-prod
```

## Configuração do Servidor Web e SSL

### 1. Configuração do Let's Encrypt com Certbot

Para obter um certificado SSL válido para seu domínio, você pode usar o Let's Encrypt com o Certbot:

```bash
# Pare os containers temporariamente
docker-compose -f docker-compose.prod.yml down

# Instale o Certbot
sudo apt install -y certbot

# Obtenha um certificado SSL
sudo certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com

# Copie os certificados para o diretório do projeto
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /opt/habitus-forecast/ssl/
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /opt/habitus-forecast/ssl/

# Ajuste as permissões
sudo chown -R $USER:$USER /opt/habitus-forecast/ssl
```

> **Nota**: Substitua `seu-dominio.com` pelo seu nome de domínio real. Certifique-se de que seu domínio está configurado para apontar para o IP da sua VPS e que as portas 80 e 443 estão abertas.

### 2. Configuração do Nginx para HTTPS

Edite o arquivo de configuração do Nginx para habilitar HTTPS:

```bash
# Abra o arquivo de configuração do Nginx
nano /opt/habitus-forecast/nginx/nginx.conf
```

Atualize a configuração para suportar HTTPS:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Redireciona para HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Configurações SSL
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # Adiciona HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Configurações de segurança
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Frame-Options SAMEORIGIN;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' https://api.seu-dominio.com/api/v1";
    add_header Referrer-Policy strict-origin-when-cross-origin;

    # Diretório raiz
    root /usr/share/nginx/html;
    index index.html;

    # Rota para a API
    location /api/ {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_redirect off;
    }

    # Rota para o aplicativo React
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }
    
    # Configurações adicionais (como as existentes)
    ...
}
```

> **Nota**: Substitua `seu-dominio.com` pelo seu domínio real. Inclua quaisquer configurações adicionais específicas que você precise.

### 3. Reinicialização dos Containers

Após configurar o SSL, reinicie os containers para aplicar as alterações:

```bash
# Reinicie todos os containers
docker-compose -f docker-compose.prod.yml up -d
```

## Verificação e Teste da Instalação

### 1. Verificação dos Serviços

Verifique se todos os serviços estão em execução:

```bash
# Verifica o status de todos os containers
docker-compose -f docker-compose.prod.yml ps

# Verifica a saúde dos containers (se algum estiver com problemas)
docker ps --format "{{.Names}}: {{.Status}}"
```

### 2. Teste de Acesso à API

Verifique se a API está respondendo:

```bash
# Teste usando curl
curl -k https://seu-dominio.com/api/v1/

# Para testar o endpoint de saúde
curl -k https://seu-dominio.com/api/v1/health
```

Você deve receber uma resposta JSON indicando que a API está funcionando.

### 3. Teste do Frontend

Acesse o frontend em um navegador web:

```
https://seu-dominio.com
```

Você deve ver a página de login do Habitus Forecast.

### 4. Verificação dos Logs

Verifique os logs para identificar possíveis problemas:

```bash
# Logs da API
docker logs habitus-forecast-api-prod

# Logs do frontend
docker logs habitus-forecast-frontend-prod

# Logs do MongoDB
docker logs habitus-forecast-mongo-prod
```

## Manutenção Básica

### 1. Atualização da Aplicação

Para atualizar a aplicação quando novas versões forem lançadas:

```bash
# Navegue para o diretório do projeto
cd /opt/habitus-forecast

# Busque as alterações mais recentes do repositório
git pull

# Reconstrua as imagens
docker-compose -f docker-compose.prod.yml build

# Reinicie os containers
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Backup dos Dados

O serviço de backup está configurado para executar automaticamente, mas você também pode fazer backups manuais:

```bash
# Executar backup manual
docker exec habitus-forecast-backup /usr/local/bin/backup.sh

# Verificar backups existentes
ls -la /opt/habitus-forecast/backups
```

Para restaurar um backup:

```bash
# Navegue para o diretório de backups
cd /opt/habitus-forecast/backups

# Liste os backups disponíveis
ls -la

# Restaure um backup específico (substitua pelo nome do seu arquivo de backup)
docker exec -it habitus-forecast-mongo-prod mongorestore --gzip --archive=/backups/seu-arquivo-de-backup.gz --username admin --password sua_senha_admin --authenticationDatabase admin
```

### 3. Reinicialização dos Serviços

Se precisar reiniciar serviços específicos:

```bash
# Reiniciar apenas a API
docker restart habitus-forecast-api-prod

# Reiniciar apenas o frontend
docker restart habitus-forecast-frontend-prod

# Reiniciar apenas o MongoDB
docker restart habitus-forecast-mongo-prod

# Reiniciar todos os serviços
docker-compose -f docker-compose.prod.yml restart
```

### 4. Visualização de Logs

Para acompanhar os logs em tempo real:

```bash
# Logs da API
docker logs -f habitus-forecast-api-prod

# Logs do frontend
docker logs -f habitus-forecast-frontend-prod

# Logs do MongoDB
docker logs -f habitus-forecast-mongo-prod

# Todos os logs do docker-compose
docker-compose -f docker-compose.prod.yml logs -f
```

## Solução de Problemas Comuns

### Problema: Containers não iniciam

**Verificações**:
1. Verifique os logs do container:
   ```bash
   docker logs nome-do-container
   ```

2. Verifique se o arquivo `.env.prod` existe e contém todas as variáveis necessárias:
   ```bash
   cat /opt/habitus-forecast/.env.prod
   ```

3. Verifique se há erros na configuração do Docker Compose:
   ```bash
   docker-compose -f docker-compose.prod.yml config
   ```

**Soluções possíveis**:
- Verifique se todas as variáveis de ambiente estão definidas corretamente
- Verifique se as portas necessárias não estão sendo usadas por outros serviços
- Certifique-se de que o Docker tem permissões para acessar os volumes mapeados

### Problema: Não é possível acessar a aplicação via navegador

**Verificações**:
1. Verifique se os containers estão em execução:
   ```bash
   docker ps
   ```

2. Teste a conexão localmente:
   ```bash
   curl -k https://localhost
   ```

3. Verifique a configuração do Nginx:
   ```bash
   docker exec habitus-forecast-frontend-prod nginx -t
   ```

**Soluções possíveis**:
- Verifique se as portas 80 e 443 estão abertas no firewall
- Certifique-se de que o domínio está configurado para apontar para o IP correto
- Verifique se o certificado SSL está válido e configurado corretamente

### Problema: Erros de Conexão com o MongoDB

**Verificações**:
1. Verifique os logs do MongoDB:
   ```bash
   docker logs habitus-forecast-mongo-prod
   ```

2. Verifique se o MongoDB está acessível pela API:
   ```bash
   docker exec habitus-forecast-api-prod curl -s mongo:27017
   ```

**Soluções possíveis**:
- Verifique se as credenciais do MongoDB estão corretas no arquivo `.env.prod`
- Certifique-se de que o volume do MongoDB está configurado corretamente
- Reinicie o container do MongoDB para resolver problemas de conexão

### Problema: Problemas de Desempenho

**Verificações**:
1. Verifique a utilização de recursos:
   ```bash
   docker stats
   ```

2. Verifique a utilização do disco:
   ```bash
   df -h
   ```

**Soluções possíveis**:
- Aumente os limites de recursos para os containers no arquivo `docker-compose.prod.yml`
- Verifique se há espaço suficiente em disco
- Considere escalar horizontalmente adicionando mais réplicas da API

## Segurança Básica

### 1. Configuração do Firewall (UFW)

Configure o firewall para permitir apenas o tráfego necessário:

```bash
# Instale o UFW se ainda não estiver instalado
sudo apt install -y ufw

# Configure as regras padrão
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permita SSH
sudo ufw allow ssh

# Permita HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilite o firewall
sudo ufw enable

# Verifique o status
sudo ufw status
```

### 2. Boas Práticas de Segurança com Docker

#### Limitar recursos dos containers

Edite o arquivo `docker-compose.prod.yml` para limitar recursos:

```yaml
services:
  api:
    # ... outras configurações ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

#### Usar imagens oficiais e manter atualizadas

Sempre use imagens oficiais do Docker Hub e mantenha-as atualizadas:

```bash
# Puxe as imagens mais recentes
docker-compose -f docker-compose.prod.yml pull

# Reconstrua as imagens
docker-compose -f docker-compose.prod.yml build --no-cache
```

#### Proteger os segredos

Nunca armazene segredos diretamente no código ou em imagens Docker:

```bash
# Verifique as permissões do arquivo .env.prod
sudo chmod 600 /opt/habitus-forecast/.env.prod
sudo chown $USER:$USER /opt/habitus-forecast/.env.prod
```

### 3. Atualizações de Segurança Regulares

Mantenha o sistema operacional e os containers atualizados:

```bash
# Atualize o sistema
sudo apt update && sudo apt upgrade -y

# Atualize as imagens Docker
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Renovação Automática do Certificado SSL

Configure a renovação automática do certificado Let's Encrypt:

```bash
# Teste a renovação
sudo certbot renew --dry-run

# Crie um script para atualizar os certificados no diretório do projeto
cat > /opt/habitus-forecast/scripts/renew-ssl.sh << 'EOF'
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /opt/habitus-forecast/ssl/
cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /opt/habitus-forecast/ssl/
chown -R $(whoami):$(whoami) /opt/habitus-forecast/ssl
docker restart habitus-forecast-frontend-prod
EOF

# Torne o script executável
chmod +x /opt/habitus-forecast/scripts/renew-ssl.sh

# Adicione ao crontab para execução automática (duas vezes por dia)
(crontab -l 2>/dev/null; echo "0 0,12 * * * /opt/habitus-forecast/scripts/renew-ssl.sh") | crontab -
```

## Conclusão

Parabéns! Você instalou e configurou com sucesso o Habitus Forecast usando Docker e docker-compose. Este guia cobriu todos os passos essenciais, desde a preparação do servidor até a configuração para produção e manutenção.

Para obter suporte adicional, visite nossa documentação oficial ou entre em contato com nossa equipe de suporte.

---

**Links Úteis**:
- [Documentação Oficial do Docker](https://docs.docker.com/)
- [Documentação do Docker Compose](https://docs.docker.com/compose/)
- [Documentação do Nginx](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)
- [Documentação do MongoDB](https://docs.mongodb.com/)

---

*Este documento é mantido pela equipe Habitus Forecast. Para sugestões ou correções, entre em contato conosco.* 