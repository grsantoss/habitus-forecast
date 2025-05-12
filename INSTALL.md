# Guia de Instalação - Habitus Finance

## Requisitos

- Node.js (versão 14 ou superior)
- MongoDB (versão 4.4 ou superior)
- NPM ou Yarn
- Git

## Instalação Local

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/habitus-finance.git
cd habitus-finance
```

### 2. Instalar Dependências
```bash
# Instalar dependências do servidor
npm install

# Instalar dependências do cliente
cd client
npm install
cd ..
```

### 3. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env com suas configurações
MONGO_URI=mongodb://localhost:27017/habitus-finance
JWT_SECRET=habitus-finance-secret-key
PORT=5000
NODE_ENV=development
```

### 4. Configurar MongoDB
```bash
# Iniciar MongoDB (se não estiver rodando como serviço)
mongod --dbpath /caminho/para/dados

# Criar banco de dados e usuário (opcional)
mongo
> use habitus-finance
> db.createUser({user: "habitus", pwd: "senha", roles: ["readWrite"]})
```

### 5. Criar Diretório de Uploads
```bash
mkdir -p server/uploads
chmod 755 server/uploads
```

### 6. Iniciar a Aplicação
```bash
# Desenvolvimento (servidor e cliente)
npm run dev

# Produção
npm run build
npm start
```

## Instalação em Produção

### 1. Preparar Servidor
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Node.js e NPM
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar MongoDB
sudo apt install -y mongodb
sudo systemctl enable mongodb
sudo systemctl start mongodb
```

### 2. Configurar Firewall
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. Configurar Nginx (opcional)
```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 4. Configurar SSL (opcional)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

### 5. Configurar PM2
```bash
sudo npm install -g pm2
pm2 start npm --name "habitus-finance" -- start
pm2 save
pm2 startup
```

### 6. Configurar Backup
```bash
# Criar script de backup
cat > /usr/local/bin/backup-habitus.sh << 'EOL'
#!/bin/bash
DATE=$(date +%Y%m%d)
mongodump --db habitus-finance --out /backup/habitus-$DATE
tar -czf /backup/habitus-$DATE.tar.gz /backup/habitus-$DATE
rm -rf /backup/habitus-$DATE
EOL

# Tornar script executável
chmod +x /usr/local/bin/backup-habitus.sh

# Adicionar ao crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-habitus.sh") | crontab -
```

## Monitoramento

### 1. Logs
```bash
# Ver logs do PM2
pm2 logs habitus-finance

# Ver logs do Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### 2. Métricas
```bash
# Ver uso de recursos
pm2 monit

# Ver status da aplicação
pm2 status
```

## Manutenção

### 1. Atualização
```bash
# Atualizar código
git pull

# Reinstalar dependências
npm install
cd client && npm install && cd ..

# Reconstruir e reiniciar
npm run build
pm2 restart habitus-finance
```

### 2. Backup e Restauração
```bash
# Backup
mongodump --db habitus-finance --out backup-$(date +%Y%m%d)

# Restauração
mongorestore --db habitus-finance backup-20230101/habitus-finance
```

## Solução de Problemas

### 1. Verificar Status dos Serviços
```bash
# MongoDB
sudo systemctl status mongodb

# Nginx
sudo systemctl status nginx

# PM2
pm2 status
```

### 2. Verificar Logs
```bash
# MongoDB
tail -f /var/log/mongodb/mongod.log

# Nginx
tail -f /var/log/nginx/error.log

# Aplicação
pm2 logs habitus-finance
```

### 3. Verificar Espaço em Disco
```bash
df -h
du -sh /backup/*
```

## Segurança

### 1. Atualizações de Segurança
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Verificar vulnerabilidades
npm audit
```

### 2. Firewall
```bash
# Ver regras
sudo ufw status

# Bloquear IPs suspeitos
sudo ufw deny from IP_ADDRESS
```

### 3. Backup de Segurança
```bash
# Backup diário
0 2 * * * /usr/local/bin/backup-habitus.sh

# Backup semanal
0 2 * * 0 /usr/local/bin/backup-habitus.sh --full
``` 