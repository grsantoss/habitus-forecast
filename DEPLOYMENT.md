# Guia de Deployment do Habitus Forecast

Este documento contém instruções para fazer deploy do Habitus Forecast em diferentes ambientes de produção.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [AWS](#aws)
3. [Digital Ocean](#digital-ocean)
4. [Heroku](#heroku)
5. [Configurações de Segurança](#configurações-de-segurança)
6. [Monitoramento](#monitoramento)
7. [Troubleshooting](#troubleshooting)

## Pré-requisitos

Antes de fazer deploy, você precisa ter:

- Docker e Docker Compose instalados
- Acesso aos repositórios Git do projeto
- Credenciais para os serviços de cloud
- Domínios configurados (opcional, mas recomendado para produção)
- Certificados SSL (ou usar Let's Encrypt)

## AWS

### Opção 1: AWS ECS (Elastic Container Service)

#### Preparação

1. Crie uma conta na AWS se ainda não tiver uma
2. Instale a AWS CLI e configure suas credenciais:

```bash
aws configure
```

3. Crie um repositório ECR para armazenar as imagens Docker:

```bash
aws ecr create-repository --repository-name habitus-forecast-api
aws ecr create-repository --repository-name habitus-forecast-frontend
```

#### Deploy

1. Faça login no ECR:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

2. Construa e faça push das imagens:

```bash
# API
docker build -t habitus-forecast-api .
docker tag habitus-forecast-api:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/habitus-forecast-api:latest
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/habitus-forecast-api:latest

# Frontend
docker build -t habitus-forecast-frontend -f Dockerfile.client ./client
docker tag habitus-forecast-frontend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/habitus-forecast-frontend:latest
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/habitus-forecast-frontend:latest
```

3. Crie um cluster ECS:
   - Vá para o Console AWS > ECS > Clusters > Create Cluster
   - Escolha "EC2 Linux + Networking"
   - Configure o número e tipo de instâncias

4. Crie uma task definition:
   - Vá para ECS > Task Definitions > Create new Task Definition
   - Escolha "EC2"
   - Adicione os containers da API e do Frontend, apontando para as imagens no ECR
   - Configure portas, variáveis de ambiente e volumes conforme necessário

5. Crie um serviço:
   - Vá para seu cluster > Services > Create
   - Escolha sua task definition e configure o número de tarefas
   - Configure load balancing se necessário
   - Configure auto scaling conforme necessário

6. Para o MongoDB, recomendamos usar o AWS DocumentDB ou MongoDB Atlas.

### Opção 2: AWS Elastic Beanstalk

1. Crie um arquivo `Dockerrun.aws.json` na raiz do projeto:

```json
{
  "AWSEBDockerrunVersion": 2,
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/habitus-forecast-api:latest",
      "essential": true,
      "memory": 512,
      "portMappings": [
        {
          "hostPort": 8000,
          "containerPort": 8000
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ]
    },
    {
      "name": "frontend",
      "image": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/habitus-forecast-frontend:latest",
      "essential": true,
      "memory": 256,
      "portMappings": [
        {
          "hostPort": 80,
          "containerPort": 80
        }
      ]
    }
  ]
}
```

2. Instale o EB CLI e inicialize o aplicativo:

```bash
pip install awsebcli
eb init
```

3. Crie o ambiente e faça deploy:

```bash
eb create habitus-forecast-production
```

## Digital Ocean

### Usando Digital Ocean App Platform

1. Crie uma conta na Digital Ocean
2. Vá para Apps > Create App
3. Escolha GitHub como fonte (ou outro provedor Git)
4. Selecione o repositório do Habitus Forecast
5. Configure os componentes:
   - Adicione um componente para a API apontando para a pasta raiz
   - Adicione um componente para o Frontend apontando para a pasta client
6. Configure as variáveis de ambiente
7. Escolha o plano de preços
8. Clique em Launch App

### Usando Digital Ocean Droplets com Docker

1. Crie um Droplet:
   - Escolha uma imagem Ubuntu
   - Selecione o tamanho (recomendamos pelo menos 2GB de RAM)
   - Escolha uma região próxima aos seus usuários
   - Adicione sua chave SSH

2. Acesse o Droplet via SSH e instale o Docker e o Docker Compose:

```bash
ssh root@your-droplet-ip
apt update && apt upgrade -y
apt install -y docker.io docker-compose
systemctl enable --now docker
```

3. Clone o repositório:

```bash
git clone https://github.com/your-username/habitus-forecast.git
cd habitus-forecast
```

4. Crie os arquivos .env necessários:

```bash
cp .env.example .env.prod
# Edite o arquivo .env.prod com suas configurações
nano .env.prod
```

5. Inicie os containers:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

6. Configure o Nginx como proxy reverso:

```bash
apt install -y nginx
```

Crie um arquivo de configuração em `/etc/nginx/sites-available/habitus-forecast`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Ative a configuração:

```bash
ln -s /etc/nginx/sites-available/habitus-forecast /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

7. Configure o SSL com Let's Encrypt:

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

## Heroku

### Preparação

1. Crie uma conta na Heroku
2. Instale o Heroku CLI:

```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

3. Faça login:

```bash
heroku login
```

### Deploy da API

1. Crie um arquivo `heroku.yml` na raiz do projeto:

```yaml
build:
  docker:
    web: Dockerfile
```

2. Crie um app para a API:

```bash
heroku create habitus-forecast-api
```

3. Configure para usar containers:

```bash
heroku stack:set container -a habitus-forecast-api
```

4. Adicione as variáveis de ambiente:

```bash
heroku config:set ENVIRONMENT=production -a habitus-forecast-api
heroku config:set SECRET_KEY=your-secret-key -a habitus-forecast-api
# Adicione outras variáveis de ambiente
```

5. Configure o banco de dados MongoDB:
   - Use o add-on mLab MongoDB:

```bash
heroku addons:create mongolab:sandbox -a habitus-forecast-api
```

6. Faça o deploy:

```bash
git push heroku main
```

### Deploy do Frontend

1. Crie um app para o frontend:

```bash
heroku create habitus-forecast-frontend
```

2. Configure o buildpack Node.js:

```bash
heroku buildpacks:set heroku/nodejs -a habitus-forecast-frontend
```

3. Adicione as variáveis de ambiente:

```bash
heroku config:set REACT_APP_API_URL=https://habitus-forecast-api.herokuapp.com/api/v1 -a habitus-forecast-frontend
```

4. Adicione um arquivo `static.json` na pasta client:

```json
{
  "root": "build/",
  "routes": {
    "/**": "index.html"
  },
  "proxies": {
    "/api/": {
      "origin": "https://habitus-forecast-api.herokuapp.com/api/"
    }
  }
}
```

5. Faça o deploy (assumindo que você tem um subtree para o frontend):

```bash
git subtree push --prefix client heroku-frontend main
```

## Configurações de Segurança

Para garantir a segurança da sua aplicação em produção, siga estas recomendações:

1. **Sempre use HTTPS** - Configure SSL em todos os endpoints públicos
2. **Proteção de Dados**:
   - Nunca armazene senhas ou chaves API no código
   - Use variáveis de ambiente para configurações sensíveis
   - Substitua o valor padrão de SECRET_KEY
3. **MongoDB**:
   - Ative a autenticação
   - Limite o acesso ao MongoDB apenas a IPs confiáveis
   - Use usuários com privilégios mínimos
4. **Backups**:
   - Configure backups automatizados
   - Teste regularmente a restauração dos backups
5. **Logs e Monitoramento**:
   - Configure logs centralizados
   - Implemente monitoramento de erros e performance
6. **Atualizações**:
   - Mantenha as imagens Docker atualizadas
   - Configure CI/CD para testes automáticos antes de deployments

## Monitoramento

Recomendamos as seguintes ferramentas de monitoramento:

1. **Sentry** para monitoramento de erros:
   - Crie uma conta em sentry.io
   - Adicione o SDK ao código Python e JavaScript

2. **Prometheus + Grafana** para métricas:
   - Configure exporters para seu sistema
   - Configure dashboards para visualizar métricas chave

3. **ELK Stack** para logs centralizados:
   - Elasticsearch para armazenamento
   - Logstash para processamento
   - Kibana para visualização

## Troubleshooting

### Problemas comuns e soluções

1. **Aplicação não inicia**:
   - Verifique os logs: `docker logs habitus-forecast-api`
   - Verifique se todas as variáveis de ambiente estão configuradas

2. **Problemas de conexão com MongoDB**:
   - Verifique se o MongoDB está acessível
   - Verifique se as credenciais estão corretas
   - Verifique se o IP está permitido no firewall

3. **Problemas no frontend**:
   - Verifique se a API_URL está configurada corretamente
   - Verifique se a API está respondendo
   - Verifique se o CORS está configurado corretamente

4. **Problemas de performance**:
   - Verifique a utilização de recursos (CPU, memória)
   - Considere escalar horizontalmente (mais instâncias) ou verticalmente (mais recursos)
   - Otimize consultas ao banco de dados 