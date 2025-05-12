# Guia de Instalação do Habitus Forecast

![Habitus Forecast Logo](../image/logo.png)

Este guia fornece instruções passo a passo para instalar e configurar o Habitus Forecast em uma VPS Ubuntu. Foi desenvolvido para usuários com conhecimento básico em Linux, sendo detalhado o suficiente para que mesmo entusiastas iniciantes possam seguir sem problemas.

**Última atualização**: `Data: 01/10/2023`

**Versão do Aplicativo**: `1.0.0`

## Sumário

- [Pré-requisitos e Requisitos Mínimos](#pré-requisitos-e-requisitos-mínimos)
- [Preparação da VPS](#preparação-da-vps)
- [Instalação de Dependências](#instalação-de-dependências)
- [Configuração do Servidor Web](#configuração-do-servidor-web)
- [Clonagem e Configuração do Repositório](#clonagem-e-configuração-do-repositório)
- [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
- [Configuração do Aplicativo](#configuração-do-aplicativo)
- [Configuração para Produção](#configuração-para-produção)
- [Segurança Básica](#segurança-básica)
- [Testando a Instalação](#testando-a-instalação)
- [Manutenção Básica](#manutenção-básica)
- [Solução de Problemas Comuns](#solução-de-problemas-comuns)

## Pré-requisitos e Requisitos Mínimos

### Requisitos de Hardware

Para um ambiente de produção com desempenho adequado, recomendamos:

| Recurso | Mínimo Recomendado | Ideal para Produção |
|---------|--------------------|--------------------|
| CPU     | 2 núcleos          | 4 núcleos          |
| RAM     | 4 GB               | 8 GB               |
| Disco   | 25 GB SSD          | 50 GB SSD          |
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

## Instalação de Dependências

### 1. Python e Ferramentas de Desenvolvimento

O Habitus Forecast utiliza Python 3.11, que precisa ser instalado:

```bash
# Adiciona o repositório para versões mais recentes do Python
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instala o Python 3.11 e ferramentas relacionadas
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verifica a instalação
python3.11 --version
```

### 2. MongoDB

O sistema usa MongoDB como banco de dados. Vamos instalá-lo seguindo a documentação oficial:

```bash
# Importa a chave pública do MongoDB
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor

# Adiciona o repositório do MongoDB
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Atualiza a lista de pacotes
sudo apt update

# Instala o MongoDB
sudo apt install -y mongodb-org

# Inicia o serviço MongoDB e habilita para iniciar automaticamente
sudo systemctl start mongod
sudo systemctl enable mongod

# Verifica se o MongoDB está em execução
sudo systemctl status mongod
```

### 3. Node.js e npm (para o Frontend)

O frontend do Habitus Forecast usa React, portanto, precisamos instalar o Node.js:

```bash
# Adiciona o repositório Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Instala o Node.js
sudo apt install -y nodejs

# Verifica a instalação
node --version
npm --version
```

## Configuração do Servidor Web

Utilizaremos o Nginx como servidor web e proxy reverso para o aplicativo.

### 1. Instalação do Nginx

```bash
# Instala o Nginx
sudo apt install -y nginx

# Inicia o serviço e habilita para iniciar automaticamente
sudo systemctl start nginx
sudo systemctl enable nginx

# Verifica se o Nginx está em execução
sudo systemctl status nginx
```

### 2. Configuração do Firewall

Configuramos o firewall para permitir o tráfego HTTP, HTTPS e SSH:

```bash
# Habilita o UFW (Uncomplicated Firewall)
sudo ufw enable

# Permite o tráfego SSH
sudo ufw allow 22/tcp

# Permite o tráfego HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verifica o status do firewall
sudo ufw status
```

### 3. Configuração do Proxy Reverso

Crie um arquivo de configuração para o Habitus Forecast no Nginx:

```bash
sudo nano /etc/nginx/sites-available/habitus-forecast
```

Adicione a seguinte configuração:

```nginx
server {
    listen 80;
    server_name seu-dominio-ou-ip;

    # Redireciona HTTP para HTTPS
    # Descomente após configurar SSL
    # return 301 https://$host$request_uri;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Configuração para servir arquivos estáticos
    location /static/ {
        alias /home/usuario/habitus-forecast/client/build/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
}
```

Substitua `seu-dominio-ou-ip` pelo seu domínio ou endereço IP.

Ative a configuração criando um link simbólico:

```bash
sudo ln -s /etc/nginx/sites-available/habitus-forecast /etc/nginx/sites-enabled/
sudo nginx -t  # Verifica se a configuração está correta
sudo systemctl reload nginx  # Recarrega o Nginx com a nova configuração
```

## Clonagem e Configuração do Repositório

### 1. Criação de um Usuário para o Aplicativo

É uma boa prática criar um usuário específico para executar o aplicativo:

```bash
# Cria o usuário 'habitus' sem senha (só podemos acessá-lo via sudo)
sudo useradd -m -s /bin/bash habitus

# Adiciona o usuário ao grupo sudo (opcional)
sudo usermod -aG sudo habitus
```

### 2. Clonagem do Repositório

```bash
# Muda para o diretório home do usuário habitus
sudo su - habitus

# Clona o repositório
git clone https://github.com/seu-usuario/habitus-forecast.git
cd habitus-forecast

# Configura o Git para não solicitar credenciais (opcional)
git config --global credential.helper store
```

### 3. Criação do Ambiente Virtual Python

```bash
# Cria um ambiente virtual
python3.11 -m venv venv

# Ativa o ambiente virtual
source venv/bin/activate

# Instala as dependências do Python
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuração do Frontend

```bash
# Navega para o diretório do cliente
cd client

# Instala as dependências do Node.js
npm install

# Constrói o frontend para produção
npm run build

# Retorna ao diretório principal
cd ..
```

## Configuração do Banco de Dados

### 1. Criação de Usuário e Banco no MongoDB

Vamos criar um usuário dedicado para o Habitus Forecast no MongoDB:

```bash
# Inicia o shell do MongoDB
mongosh

# Cria um usuário administrador (se ainda não existir)
use admin
db.createUser({
  user: "mongoAdmin",
  pwd: "senha_admin_segura",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

# Cria o banco de dados e um usuário para o aplicativo
use habitus-prod
db.createUser({
  user: "habitus_user",
  pwd: "senha_segura_app",
  roles: [ { role: "readWrite", db: "habitus-prod" } ]
})

# Sai do shell do MongoDB
exit
```

> **Importante**: Substitua `senha_admin_segura` e `senha_segura_app` por senhas fortes e únicas.

### 2. Habilitação da Autenticação no MongoDB

Edite o arquivo de configuração do MongoDB:

```bash
sudo nano /etc/mongod.conf
```

Adicione ou modifique a seção de segurança:

```yaml
security:
  authorization: enabled
```

Reinicie o MongoDB para aplicar as alterações:

```bash
sudo systemctl restart mongod
```

### 3. Importação de Dados Iniciais (Opcional)

Se você tiver um dump de dados inicial para importar:

```bash
# Navega para o diretório do projeto
cd ~/habitus-forecast

# Restaura o dump do MongoDB
mongorestore --uri="mongodb://habitus_user:senha_segura_app@localhost:27017/habitus-prod" --db=habitus-prod caminho/para/dump
```

## Configuração do Aplicativo

### 1. Criação do Arquivo de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto:

```bash
# Navega para o diretório do projeto
cd ~/habitus-forecast

# Cria o arquivo .env
nano .env.prod
```

Adicione as seguintes variáveis de ambiente:

```
# Configurações gerais
DEBUG=False
ENVIRONMENT=production
API_PREFIX=/api/v1
PORT=8000
WORKERS=4

# URL do MongoDB
MONGODB_URI=mongodb://habitus_user:senha_segura_app@localhost:27017/habitus-prod
MONGODB_DB=habitus-prod
MAX_CONNECTIONS_COUNT=10
MIN_CONNECTIONS_COUNT=1

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
```

> **Importante**: Substitua `sua_chave_secreta_super_segura_com_pelo_menos_32_caracteres` por uma string aleatória segura. Você pode gerar uma com o comando:
> ```bash
> openssl rand -hex 32
> ```

### 2. Teste Inicial do Aplicativo

Vamos testar o aplicativo para garantir que tudo está funcionando:

```bash
# Certifique-se de que o ambiente virtual está ativado
source venv/bin/activate

# Execute o aplicativo
cd ~/habitus-forecast
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env.prod
```

Verifique se o aplicativo está em execução acessando `http://seu-ip:8000` em um navegador. Você deve ver a mensagem de boas-vindas da API.

Pressione `Ctrl+C` para parar o aplicativo após o teste.

## Configuração para Produção

### 1. Configuração do Gunicorn/Uvicorn

Para produção, usaremos Gunicorn com trabalhadores Uvicorn para executar o aplicativo. Crie um script para iniciar o servidor:

```bash
# Crie um arquivo de script de inicialização
nano ~/habitus-forecast/start_server.sh
```

Adicione o seguinte conteúdo:

```bash
#!/bin/bash
cd ~/habitus-forecast
source venv/bin/activate
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --env-file .env.prod --access-logfile logs/access.log --error-logfile logs/error.log
```

Torne o script executável:

```bash
chmod +x ~/habitus-forecast/start_server.sh
```

### 2. Configuração do Serviço Systemd

Crie um arquivo de serviço systemd para gerenciar o aplicativo:

```bash
sudo nano /etc/systemd/system/habitus-api.service
```

Adicione o seguinte conteúdo:

```ini
[Unit]
Description=Habitus Forecast API
After=network.target mongodb.service

[Service]
User=habitus
Group=habitus
WorkingDirectory=/home/habitus/habitus-forecast
ExecStart=/home/habitus/habitus-forecast/start_server.sh
Restart=always
RestartSec=5
StartLimitIntervalSec=0
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=habitus-api

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable habitus-api
sudo systemctl start habitus-api

# Verifique o status do serviço
sudo systemctl status habitus-api
```

### 3. Configuração do Frontend como Serviço (Opcional)

Se você não estiver usando o build estático servido pelo Nginx, crie um serviço para o frontend:

```bash
sudo nano /etc/systemd/system/habitus-frontend.service
```

Adicione o seguinte conteúdo:

```ini
[Unit]
Description=Habitus Forecast Frontend
After=network.target

[Service]
User=habitus
Group=habitus
WorkingDirectory=/home/habitus/habitus-forecast/client
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=habitus-frontend
Environment="PORT=3000"

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable habitus-frontend
sudo systemctl start habitus-frontend

# Verifique o status do serviço
sudo systemctl status habitus-frontend
```

## Segurança Básica

### 1. Configuração de SSL/TLS com Let's Encrypt

Proteja seu site com HTTPS utilizando certificados gratuitos do Let's Encrypt:

```bash
# Instala o Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtém certificados SSL e configura o Nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Responda às perguntas do assistente
```

O Certbot modificará automaticamente sua configuração do Nginx para usar HTTPS.

### 2. Configuração de Segurança Adicional para o Nginx

Edite a configuração do Nginx para adicionar cabeçalhos de segurança:

```bash
sudo nano /etc/nginx/sites-available/habitus-forecast
```

Adicione os seguintes cabeçalhos dentro do bloco `server`:

```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:;" always;
```

Reinicie o Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Configuração de Backup Automático

Configure backups automáticos do banco de dados:

```bash
# Crie um diretório para os backups
sudo mkdir -p /var/backups/mongodb
sudo chown habitus:habitus /var/backups/mongodb

# Crie um script de backup
sudo nano /home/habitus/backup_mongodb.sh
```

Adicione o seguinte conteúdo:

```bash
#!/bin/bash
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="/var/backups/mongodb"
MONGODB_HOST="localhost"
MONGODB_PORT="27017"
MONGODB_USER="habitus_user"
MONGODB_PASSWORD="senha_segura_app"
MONGODB_DATABASE="habitus-prod"

# Cria backup
mongodump --host $MONGODB_HOST --port $MONGODB_PORT --username $MONGODB_USER --password $MONGODB_PASSWORD --db $MONGODB_DATABASE --out $BACKUP_DIR/$DATE

# Remove backups com mais de 30 dias
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} \;
```

Torne o script executável:

```bash
sudo chmod +x /home/habitus/backup_mongodb.sh
```

Configure o cron para executar o backup diariamente:

```bash
sudo crontab -e
```

Adicione a seguinte linha:

```
0 2 * * * /home/habitus/backup_mongodb.sh >> /var/log/mongodb_backup.log 2>&1
```

Isso executará o backup todos os dias às 2h da manhã.

## Testando a Instalação

### 1. Verificação dos Serviços

Verifique se todos os serviços estão em execução:

```bash
# Verifica o status do MongoDB
sudo systemctl status mongod

# Verifica o status do Nginx
sudo systemctl status nginx

# Verifica o status da API
sudo systemctl status habitus-api

# Verifica o status do frontend (se configurado como serviço)
sudo systemctl status habitus-frontend
```

### 2. Teste de Acesso à API

Verifique se a API está respondendo:

```bash
# Teste usando curl
curl http://localhost:8000/api/v1/

# Ou, se tiver configurado SSL:
curl https://seu-dominio.com/api/v1/
```

Você deve receber uma resposta JSON indicando que a API está funcionando.

### 3. Teste do Frontend

Acesse o frontend em um navegador:

```
http://seu-dominio.com
```

Você deve ver a página de login do Habitus Forecast.

## Manutenção Básica

### 1. Atualizações do Sistema

Mantenha seu sistema atualizado:

```bash
# Atualiza os pacotes do sistema
sudo apt update && sudo apt upgrade -y

# Limpa pacotes desnecessários
sudo apt autoremove -y
```

### 2. Atualizações do Aplicativo

Para atualizar o Habitus Forecast:

```bash
# Muda para o usuário do aplicativo
sudo su - habitus

# Navega para o diretório do projeto
cd ~/habitus-forecast

# Atualiza o código do repositório
git pull

# Ativa o ambiente virtual
source venv/bin/activate

# Atualiza as dependências do Python
pip install -r requirements.txt

# Atualiza o frontend
cd client
npm install
npm run build
cd ..

# Reinicia os serviços
exit
sudo systemctl restart habitus-api
sudo systemctl restart habitus-frontend  # Se configurado como serviço
```

### 3. Monitoramento de Logs

Verifique os logs para identificar problemas:

```bash
# Logs do aplicativo
sudo journalctl -u habitus-api -f

# Logs do frontend
sudo journalctl -u habitus-frontend -f

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs do MongoDB
sudo tail -f /var/log/mongodb/mongod.log
```

## Solução de Problemas Comuns

### Problema: A API não inicia

**Verificações**:
1. Verifique se o MongoDB está em execução:
   ```bash
   sudo systemctl status mongod
   ```

2. Verifique os logs do serviço:
   ```bash
   sudo journalctl -u habitus-api -f
   ```

3. Teste manualmente o aplicativo:
   ```bash
   sudo su - habitus
   cd ~/habitus-forecast
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env.prod
   ```

**Soluções possíveis**:
- Verifique as credenciais do MongoDB no arquivo `.env.prod`
- Verifique permissões de arquivos e diretórios
- Certifique-se de que todas as dependências foram instaladas

### Problema: A Interface Web Não Carrega

**Verificações**:
1. Verifique se o Nginx está em execução:
   ```bash
   sudo systemctl status nginx
   ```

2. Teste se o frontend está acessível diretamente:
   ```bash
   curl http://localhost:3000
   ```

3. Verifique os logs do Nginx:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

**Soluções possíveis**:
- Verifique a configuração do Nginx
- Certifique-se de que o build do frontend foi gerado corretamente
- Verifique permissões do diretório `/home/habitus/habitus-forecast/client/build`

### Problema: Erros de Permissão

**Verificações**:
1. Verifique as permissões dos diretórios:
   ```bash
   ls -la /home/habitus/habitus-forecast
   ```

2. Verifique o proprietário dos arquivos:
   ```bash
   sudo stat -c "%U:%G" /home/habitus/habitus-forecast
   ```

**Soluções possíveis**:
- Ajuste as permissões:
   ```bash
   sudo chown -R habitus:habitus /home/habitus/habitus-forecast
   sudo chmod -R 755 /home/habitus/habitus-forecast
   ```

### Problema: MongoDB Não Conecta

**Verificações**:
1. Verifique se o MongoDB está em execução:
   ```bash
   sudo systemctl status mongod
   ```

2. Teste a conexão manualmente:
   ```bash
   mongosh --host localhost --port 27017 -u habitus_user -p senha_segura_app --authenticationDatabase habitus-prod
   ```

**Soluções possíveis**:
- Verifique a configuração do MongoDB (`/etc/mongod.conf`)
- Verifique as credenciais no arquivo `.env.prod`
- Verifique o status do serviço MongoDB

## Conclusão

Parabéns! Você instalou e configurou com sucesso o Habitus Forecast em sua VPS Ubuntu. Este guia cobriu todos os passos essenciais, desde a preparação do servidor até a configuração para produção.

Para obter suporte adicional, visite nossa documentação oficial ou entre em contato com nossa equipe de suporte.

---

**Links Úteis**:
- [Documentação Oficial do FastAPI](https://fastapi.tiangolo.com/)
- [Documentação do MongoDB](https://docs.mongodb.com/)
- [Documentação do Nginx](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)

---

*Este documento é mantido pela equipe Habitus Forecast. Para sugestões ou correções, entre em contato conosco.* 