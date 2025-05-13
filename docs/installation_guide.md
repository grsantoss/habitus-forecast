# Guia de Instalação Atualizado do Habitus Forecast com Docker

![Habitus Forecast Logo](../image/logo.png)

Este guia fornece instruções detalhadas para instalar e configurar o Habitus Forecast em uma VPS Ubuntu (20.04 LTS ou 22.04 LTS) utilizando Docker e Docker Compose. Ele aborda problemas comuns de implantação e oferece soluções para uma configuração robusta e segura.

**Última atualização**: `Data da Atualização (ex: 15/07/2024)`

**Versão do Aplicativo**: `1.0.0`

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [Preparação da VPS](#preparação-da-vps)
- [Instalação do Docker e Docker Compose](#instalação-do-docker-e-docker-compose)
- [Obtenção do Código da Aplicação](#obtenção-do-código-da-aplicação)
- [Configuração do Ambiente (.env.prod)](#configuração-do-ambiente-envprod)
- **Etapa 1: Implantação do Backend (API) e Banco de Dados (MongoDB)**
  - [Ajustes no Código da API (Pydantic e MongoDB)](#ajustes-no-código-da-api-pydantic-e-mongodb)
  - [Construção e Inicialização (API e MongoDB)](#construção-e-inicialização-api-e-mongodb)
  - [Verificação (API e MongoDB)](#verificação-api-e-mongodb)
- **Etapa 2: Implantação do Frontend (React/Nginx)**
  - [Configuração do Nginx](#configuração-do-nginx)
  - [Geração de Certificado SSL (Let's Encrypt)](#geração-de-certificado-ssl-lets-encrypt)
  - [Construção e Inicialização (Frontend)](#construção-e-inicialização-frontend)
  - [Verificação Final](#verificação-final)
- [Manutenção e Operações](#manutenção-e-operações)
  - [Visualização de Logs](#visualização-de-logs)
  - [Backup e Restauração do MongoDB](#backup-e-restauração-do-mongodb)
  - [Atualização da Aplicação](#atualização-da-aplicação)
  - [Verificação de Integridade dos Containers](#verificação-de-integridade-dos-containers)
- [Solução de Problemas Comuns (Troubleshooting)](#solução-de-problemas-comuns-troubleshooting)
- [Considerações de Segurança](#considerações-de-segurança)

## Pré-requisitos

- VPS com Ubuntu 20.04 LTS ou 22.04 LTS.
- Requisitos de Hardware: Mínimo 2 CPU, 4GB RAM, 30GB SSD. Recomendado 4 CPU, 8GB RAM, 60GB SSD.
- Acesso root ou um usuário com privilégios sudo.
- Um nome de domínio apontando para o IP da sua VPS (para HTTPS).
- Conhecimento básico de linha de comando Linux.

## Preparação da VPS

1.  **Acesso via SSH:**
    ```bash
    ssh seu_usuario@seu_ip_da_vps
    ```

2.  **Atualização do Sistema:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget vim git software-properties-common apt-transport-https ca-certificates gnupg
    ```

3.  **Configuração do Fuso Horário (Exemplo: São Paulo):**
    ```bash
    sudo timedatectl set-timezone America/Sao_Paulo
    date
    ```

## Instalação do Docker e Docker Compose

1.  **Instalação do Docker Engine:**
    ```bash
    sudo apt remove docker docker-engine docker.io containerd runc # Remove versões antigas
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo systemctl start docker
    sudo systemctl enable docker
    ```

2.  **Permissões do Docker (Opcional, para evitar `sudo`):**
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker # Aplica as alterações de grupo, pode ser necessário sair e logar novamente
    docker run hello-world # Teste
    ```
    > **Nota:** Se `newgrp docker` não funcionar ou se você preferir, continue usando `sudo docker ...` para os comandos Docker.

3.  **Verificar Docker Compose (plugin):**
    O Docker Compose V2 agora é um plugin do Docker CLI.
    ```bash
    docker compose version
    ```
    Se você precisar do `docker-compose` standalone (V1, legado), as instruções de instalação são diferentes. Este guia assume o uso do plugin `docker compose`.

## Obtenção do Código da Aplicação

1.  **Clonagem do Repositório:**
    ```bash
    cd /opt # Ou outro diretório de sua preferência
    sudo git clone https://github.com/seu-usuario/habitus-forecast.git # Substitua pelo URL correto
    sudo chown -R $USER:$USER /opt/habitus-forecast
    cd /opt/habitus-forecast
    ```
    > **Nota de Permissão:** O `chown` acima define o usuário atual como proprietário. Se você planeja usar `user: "${UID_GID}"` no `docker-compose.prod.yml`, certifique-se de que o `UID` e `GID` correspondam a este usuário.

2.  **Estrutura Esperada do Projeto:**
    Verifique a presença de `Dockerfile`, `docker-compose.prod.yml`, `client/Dockerfile.client`, `nginx/nginx.conf`, `app/`, etc.

## Configuração do Ambiente (`.env.prod`)

Crie e configure o arquivo `.env.prod` na raiz do projeto (`/opt/habitus-forecast/.env.prod`):

```bash
nano .env.prod
```

Conteúdo exemplo para `.env.prod`:

```env
# Configurações Gerais
ENVIRONMENT=production
DEBUG=False
API_PREFIX=/api/v1
PORT=8000 # Porta interna da API
WORKERS=4 # Número de workers Uvicorn

# Configurações do MongoDB
MONGO_INITDB_ROOT_USERNAME=admin_habitus
MONGO_INITDB_ROOT_PASSWORD=coloque_uma_senha_muito_segura_aqui
MONGODB_DB=habitus-prod

# Segurança da API
SECRET_KEY=gere_uma_chave_secreta_forte_com_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Configure seus domínios permitidos
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Uploads (se aplicável)
# UPLOAD_FOLDER=./uploads
# MAX_UPLOAD_SIZE=10485760 # 10MB

# Domínio (usado em configurações, ex: Nginx, CORS)
DOMAIN=seu-dominio.com

# UID/GID para permissões de volume (opcional, mas recomendado)
# Execute `id -u` e `id -g` no terminal do host para obter os valores
# UID_GID=1000:1000 # Exemplo: UID:GID

# Variáveis específicas do Frontend (se o Dockerfile.client precisar)
# REACT_APP_API_URL=https://api.seu-dominio.com/api/v1 # Já definido como arg no docker-compose
```

> **IMPORTANTE:**
> - Substitua os valores de exemplo (senhas, chaves, domínio).
> - Gere `SECRET_KEY` com: `openssl rand -hex 32`.
> - Se for usar `user: "${UID_GID}"` no `docker-compose.prod.yml` para os serviços `api` ou `frontend` para evitar problemas de permissão com volumes montados (como `./logs`), descomente e defina `UID_GID` com o ID do seu usuário e grupo no host (ex: `1000:1000`).

## Etapa 1: Implantação do Backend (API) e Banco de Dados (MongoDB)

### Ajustes no Código da API (Pydantic e MongoDB)

Antes de construir a imagem da API, verifique e corrija os seguintes pontos no código-fonte da API:

1.  **Pydantic `BaseSettings`:**
    Se sua API usa Pydantic para configurações, a importação de `BaseSettings` mudou.
    - Adicione `pydantic-settings` ao seu arquivo `requirements.txt` (ou similar) da API.
    - No arquivo de configuração da API (ex: `app/core/config.py`):
      ```python
      # Altere de:
      # from pydantic import BaseSettings
      # Para:
      from pydantic_settings import BaseSettings
      ```

2.  **Conexão com MongoDB (`get_db` vs `get_database`):**
    Verifique o módulo de conexão com o MongoDB (ex: `app/db/mongodb.py` ou `app/database.py`). Certifique-se de que o nome da função usada para obter a instância do banco de dados é consistente com o que é chamado em outras partes da API.
    Exemplo (`app/db/mongodb.py`):
    ```python
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings # Supondo que suas settings estão aqui

    client = AsyncIOMotorClient(settings.MONGODB_URI)
    # O nome do banco de dados é geralmente pego das settings
    database = client[settings.MONGODB_DB]

    async def get_db(): # Ou get_database(), padronize o nome
        return database
    ```
    Adapte conforme a estrutura do seu projeto.

3.  **Permissões de Scripts em `docker-entrypoint.d`:**
    Se você tiver scripts em um diretório como `/docker-entrypoint.d/` (comum em algumas imagens base) que precisam ser executados (ex: `40-env.sh`), garanta que eles tenham permissão de execução no `Dockerfile` da API.
    Exemplo no `Dockerfile` da API:
    ```dockerfile
    # ... outras instruções ...
    COPY ./docker-entrypoint.d/ /docker-entrypoint.d/
    RUN chmod +x /docker-entrypoint.d/*.sh
    # ... ou use COPY --chmod=0755 se sua versão do Docker suportar
    # COPY --chmod=0755 ./docker-entrypoint.d/ /docker-entrypoint.d/
    # ... outras instruções ...
    ```

### Construção e Inicialização (API e MongoDB)

1.  **Criar diretórios necessários (se não existirem):**
    ```bash
    mkdir -p /opt/habitus-forecast/logs
    mkdir -p /opt/habitus-forecast/backups
    mkdir -p /opt/habitus-forecast/ssl
    mkdir -p /opt/habitus-forecast/nginx # Para nginx.conf
    # mkdir -p /opt/habitus-forecast/uploads # Se usar uploads
    
    # Crie um mongo-init.prod.js se necessário para inicializar usuários/índices
    # Exemplo básico (adapte conforme sua necessidade):
    cat << EOF > /opt/habitus-forecast/mongo-init.prod.js
    db = db.getSiblingDB(\'${MONGO_INITDB_DATABASE}\');
    db.createUser({
      user: \'${MONGO_INITDB_ROOT_USERNAME}\',
      pwd: \'${MONGO_INITDB_ROOT_PASSWORD}\',
      roles: [{ role: \'readWrite\', db: \'${MONGO_INITDB_DATABASE}\' }]
    });
    // Você pode adicionar a criação de coleções ou índices aqui
    // db.createCollection(\'nome_da_colecao\');
    EOF
    ```
    > **Nota:** O script `mongo-init.prod.js` será executado apenas na primeira vez que o volume do MongoDB for criado. As variáveis de ambiente como `${MONGO_INITDB_DATABASE}` são substituídas pelo Docker Compose no ambiente do container `mongo` e usadas pelo entrypoint do MongoDB.

2.  **Construir as imagens e iniciar os serviços (API e MongoDB):**
    Usaremos `docker compose` (com espaço) que é o comando para o plugin Docker Compose V2.
    ```bash
    cd /opt/habitus-forecast
    sudo docker compose -f docker-compose.prod.yml pull # Baixa imagens base mais recentes
    sudo docker compose -f docker-compose.prod.yml build --no-cache api mongo # Constrói apenas api e mongo (mongo usa imagem pronta)
    sudo docker compose -f docker-compose.prod.yml up -d api mongo # Inicia apenas api e mongo
    ```

### Verificação (API e MongoDB)

1.  **Verificar containers em execução:**
    ```bash
    sudo docker compose -f docker-compose.prod.yml ps
    ```
    Você deve ver os containers `api` (possivelmente 2 réplicas) e `mongo` com status `Up` ou `running`.

2.  **Verificar logs:**
    ```bash
    sudo docker compose -f docker-compose.prod.yml logs -f api
    sudo docker compose -f docker-compose.prod.yml logs -f mongo
    ```
    Procure por mensagens de erro. Para a API, você deve ver o Uvicorn iniciando. Para o MongoDB, procure por mensagens indicando que está pronto para conexões.

3.  **Testar o endpoint de saúde da API (do host da VPS):**
    Como a porta 8000 da API está mapeada, você pode testar localmente.
    ```bash
    curl http://localhost:8000/api/v1/health # Substitua pelo seu API_PREFIX se diferente
    ```
    Você deve receber uma resposta JSON de sucesso (ex: `{"status":"healthy"}`).

## Etapa 2: Implantação do Frontend (React/Nginx)

### Configuração do Nginx

1.  **Crie/Verifique `nginx/nginx.conf`:**
    O arquivo `nginx/nginx.conf` (caminho definido no `docker-compose.prod.yml`) deve ser configurado corretamente. O conteúdo foi fornecido em uma etapa anterior. Certifique-se que:
    - `limit_req_zone` está no contexto `http {}`.
    - `server_name` está definido com seu domínio.
    - Os caminhos para os certificados SSL (`/etc/nginx/ssl/fullchain.pem` e `/etc/nginx/ssl/privkey.pem`) estão corretos (estes são os caminhos DENTRO do container do frontend).
    - `proxy_pass http://api:8000;` aponta para o serviço da API.

### Geração de Certificado SSL (Let's Encrypt)

1.  **Instale o Certbot:**
    ```bash
    sudo apt install -y certbot python3-certbot-nginx
    ```

2.  **Obtenha o Certificado:**
    Certifique-se que seu domínio (`seu-dominio.com`) já está apontando para o IP da sua VPS e que as portas 80 e 443 não estão bloqueadas pelo firewall e não estão sendo usadas por outros serviços no host.
    ```bash
    # Pare temporariamente qualquer serviço que possa estar usando a porta 80 no host
    # Se o Nginx do frontend já estiver rodando via Docker na porta 80, pare-o:
    # sudo docker compose -f docker-compose.prod.yml stop frontend
    
    sudo certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com --agree-tos -m seu_email@example.com --no-eff-email
    ```
    > **Nota:** Se a porta 80 estiver em uso pelo container do Nginx, você pode precisar pará-lo (`sudo docker compose -f docker-compose.prod.yml stop frontend`) ou usar o método `webroot` do Certbot se o Nginx já estiver servindo algum conteúdo.

3.  **Copie os Certificados para o Diretório SSL do Projeto:**
    O Nginx dentro do container do frontend espera os certificados no caminho especificado no volume (`./ssl:/etc/nginx/ssl:ro`).
    ```bash
    sudo mkdir -p /opt/habitus-forecast/ssl
    sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /opt/habitus-forecast/ssl/fullchain.pem
    sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /opt/habitus-forecast/ssl/privkey.pem
    sudo chown -R $USER:$USER /opt/habitus-forecast/ssl # Garante permissões para o Docker montar
    ```

4.  **Configure a Renovação Automática:**
    ```bash
    echo "0 3 * * * root certbot renew --quiet && sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /opt/habitus-forecast/ssl/fullchain.pem && sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /opt/habitus-forecast/ssl/privkey.pem && sudo docker compose -f /opt/habitus-forecast/docker-compose.prod.yml restart frontend" | sudo tee -a /etc/crontab
    ```
    Ou use `sudo certbot renew --dry-run` para testar a renovação.

### Construção e Inicialização (Frontend)

1.  **Construa a imagem do frontend e inicie o serviço:**
    ```bash
    cd /opt/habitus-forecast
    sudo docker compose -f docker-compose.prod.yml build --no-cache frontend
    sudo docker compose -f docker-compose.prod.yml up -d frontend
    ```
    Pode ser necessário iniciar todos os serviços se eles não estiverem rodando:
    ```bash
    sudo docker compose -f docker-compose.prod.yml up -d # Inicia todos os serviços definidos
    ```

### Verificação Final

1.  **Verificar todos os containers:**
    ```bash
    sudo docker compose -f docker-compose.prod.yml ps
    ```
    Todos os serviços (api, mongo, frontend, backup) devem estar `Up`.

2.  **Testar o Frontend no Navegador:**
    Acesse `https://seu-dominio.com` no seu navegador. Você deve ver a aplicação Habitus Forecast.

3.  **Testar a API através do domínio:**
    Acesse `https://seu-dominio.com/api/v1/health` (ou o endpoint de saúde da sua API).

4.  **Verificar Logs do Frontend:**
    ```bash
    sudo docker compose -f docker-compose.prod.yml logs -f frontend
    ```
    Procure por erros do Nginx.

## Manutenção e Operações

### Visualização de Logs

```bash
# Logs de um serviço específico (ex: api)
sudo docker compose -f docker-compose.prod.yml logs -f api

# Logs de todos os serviços
sudo docker compose -f docker-compose.prod.yml logs -f
```

### Backup e Restauração do MongoDB

O serviço `backup` no `docker-compose.prod.yml` está configurado para backups automáticos via cron dentro do container.

1.  **Executar Backup Manual:**
    O script `scripts/backup.sh` deve conter a lógica de backup (ex: `mongodump`).
    Exemplo de `scripts/backup.sh` (crie este arquivo):
    ```bash
    #!/bin/bash
    set -e # Sair imediatamente se um comando falhar
    
    BACKUP_DIR="/backups"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_NAME="${MONGO_DATABASE}_${TIMESTAMP}.gz"
    LOG_FILE="${BACKUP_DIR}/backup_log.txt"

    echo "Starting backup of ${MONGO_DATABASE} to ${BACKUP_NAME} at $(date)" >> "${LOG_FILE}"
    
    mongodump --host="${MONGO_HOST}" --port="${MONGO_PORT}" \
              --username="${MONGO_USER}" --password="${MONGO_PASSWORD}" \
              --authenticationDatabase=admin --db="${MONGO_DATABASE}" \
              --archive="${BACKUP_DIR}/${BACKUP_NAME}" --gzip >> "${LOG_FILE}" 2>&1
              
    if [ $? -eq 0 ]; then
      echo "Backup successful: ${BACKUP_NAME}" >> "${LOG_FILE}"
      # Opcional: Remover backups antigos (ex: manter os últimos 7)
      find "${BACKUP_DIR}" -name "${MONGO_DATABASE}_*.gz" -type f -mtime +7 -delete
      echo "Old backups removed." >> "${LOG_FILE}"
    else
      echo "Backup failed for ${MONGO_DATABASE}" >> "${LOG_FILE}"
      exit 1
    fi
    echo "----------------------------------------" >> "${LOG_FILE}"
    ```
    Torne-o executável: `chmod +x scripts/backup.sh`.

    Para executar manualmente:
    ```bash
    sudo docker compose -f docker-compose.prod.yml exec backup /usr/local/bin/backup.sh
    ```
    Os backups estarão em `/opt/habitus-forecast/backups` no host.

2.  **Restaurar Backup:**
    ```bash
    # Exemplo com um arquivo de backup chamado meu_backup.gz
    sudo docker compose -f docker-compose.prod.yml exec -T mongo mongorestore \
        --username="${MONGO_INITDB_ROOT_USERNAME}" \
        --password="${MONGO_INITDB_ROOT_PASSWORD}" \
        --authenticationDatabase=admin \
        --nsInclude="${MONGODB_DB}.*" \
        --archive --gzip < /opt/habitus-forecast/backups/meu_backup.gz
    ```
    > **Nota:** Ajuste `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` e `MONGODB_DB` conforme seu `.env.prod` ou use as variáveis de ambiente diretamente se o comando for executado de um contexto que as tenha. O comando `-T` desabilita a alocação de pseudo-TTY, útil para piping.

### Atualização da Aplicação

1.  **Baixar Alterações:**
    ```bash
    cd /opt/habitus-forecast
    git pull origin main # Ou a branch relevante
    ```
2.  **Reconstruir Imagens (se houver mudanças no código ou Dockerfiles):**
    ```bash
    sudo docker compose -f docker-compose.prod.yml build --no-cache
    ```
3.  **Reiniciar Serviços:**
    ```bash
    sudo docker compose -f docker-compose.prod.yml up -d
    ```
4.  **Remover Imagens Antigas (Opcional):**
    ```bash
    sudo docker image prune -f
    ```

### Verificação de Integridade dos Containers

- **Healthchecks:** O serviço `api` tem um healthcheck. Verifique o status:
  ```bash
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
  ```
  Procure por `(healthy)` no status.
- **`docker stats`:** Para monitorar o uso de recursos em tempo real:
  ```bash
  sudo docker stats
  ```

## Solução de Problemas Comuns (Troubleshooting)

-   **`container_name` vs `deploy.replicas`:** Resolvido removendo `container_name` de serviços com `replicas` > 1.
-   **Erro de importação Pydantic/MongoDB:** Siga as instruções na Etapa 1.
-   **Nginx `limit_req_zone`:** Certifique-se que está no contexto `http{}` do `nginx.conf`.
-   **Scripts não executáveis (ex: `/docker-entrypoint.d/`):** Verifique permissões no `Dockerfile` (use `RUN chmod +x` ou `COPY --chmod=0755`).
-   **Erros de Permissão em Volumes Montados (Read-only filesystem):**
    -   Verifique se o volume não está montado com `:ro` se escrita for necessária.
    -   Use `user: "${UID_GID}"` no `docker-compose.prod.yml` para o serviço problemático (ex: `api`, `frontend` se Nginx precisar escrever logs em volumes montados do host que não sejam `/var/log/nginx`). Defina `UID_GID` no `.env.prod` com `id -u`:`id -g` do seu usuário no host.
    -   Garanta que os diretórios no host (ex: `./logs`, `./uploads`) tenham permissões de escrita para o UID/GID especificado ou para o usuário padrão dentro do container.
-   **Variáveis de Ambiente Não Carregadas:**
    -   Verifique a sintaxe do `.env.prod` (sem espaços extras, sem aspas a menos que necessário).
    -   Certifique-se que `env_file: - .env.prod` está no `docker-compose.prod.yml`.
    -   Dentro do container, use `echo $NOME_DA_VARIAVEL` para testar.
-   **Falha ao iniciar container:** `sudo docker compose -f docker-compose.prod.yml logs <nome_do_servico>` para ver a causa.
-   **Problemas de rede entre containers:** Verifique se todos os containers estão na mesma `network` (`habitus-network-prod`). Use `docker network inspect habitus-network-prod`.
-   **Frontend não carrega (erro 404/50x):** Verifique os logs do Nginx (`frontend` service). Problemas comuns incluem `proxy_pass` incorreto, build do React falho, ou configuração do `root` e `try_files` no Nginx.

## Considerações de Segurança

-   **Firewall (UFW):** Configure o firewall no host da VPS:
    ```bash
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow http # Porta 80/tcp
    sudo ufw allow https # Porta 443/tcp
    sudo ufw enable
    sudo ufw status
    ```
-   **Segredos:** Use o arquivo `.env.prod` (com permissões restritas: `sudo chmod 600 .env.prod`) e não exponha segredos no código ou em Dockerfiles.
-   **Atualizações Regulares:** Mantenha o Ubuntu, Docker, e as imagens base dos seus containers atualizadas.
-   **Nginx Headers de Segurança:** Configure headers como `Strict-Transport-Security`, `Content-Security-Policy` no `nginx.conf` conforme suas necessidades.
-   **Limitar Recursos:** O `docker-compose.prod.yml` já define limites de CPU/memória. Ajuste conforme necessário.
-   **Permissões de Arquivos no Host:** Garanta que diretórios montados como volumes (ex: `logs`, `ssl`, `backups`) tenham permissões apropriadas no host.

--- 
*Este documento é mantido pela equipe Habitus Forecast. Para sugestões ou correções, entre em contato conosco.* 