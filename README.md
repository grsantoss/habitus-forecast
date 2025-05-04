# Habitus Finance - Financial Simulation SaaS

A comprehensive SaaS platform for financial simulation and analysis with an interactive dashboard, scenario creation, and reporting features.

## Features

- User authentication with role-based access (user/admin)
- Excel spreadsheet upload for data input
- Manual data entry interface
- Interactive financial dashboard with visualizations
- Scenario creation and comparison
- PDF report generation
- Admin panel with user management and action logs

## Technology Stack

- **Frontend**: React with Tailwind CSS
- **Backend**: Node.js/Express
- **Database**: MongoDB
- **Authentication**: JWT
- **File Processing**: SheetJS for Excel files
- **Visualization**: Chart.js

## Installation

### Prerequisites

- Node.js (v14+)
- MongoDB (local or Atlas)
- Git

### Setup Instructions

1. Clone the repository
```
git clone <repository-url>
cd Habitus_Forecast
```

2. Create environment file
```
cp .env.example .env
```

3. Configure your .env file with appropriate values:
```
MONGO_URI=mongodb://localhost:27017/habitus-forecast
JWT_SECRET=your-secret-key
PORT=5000
NODE_ENV=development
```

4. Install dependencies
```
npm install
npm run install-client
```

5. Start development server
```
npm run dev
```

This will start both the backend server (on port 5000) and frontend client (on port 3000).

### Alternative: Run Server and Client Separately

Backend:
```
npm run server
```

Frontend:
```
npm run client
```

## Testing Guide

1. **Register a new user**
   - Navigate to `/register`
   - Create an account with email and password

2. **Login**
   - Navigate to `/login`
   - Use your registered credentials

3. **Upload Financial Data**
   - Navigate to Spreadsheet Upload page
   - Use the sample Excel template in `/samples` directory or create your own
   - Upload the file

4. **Manual Data Entry**
   - Navigate to the data entry form
   - Input financial data across all categories
   - Save the data

5. **Create Scenarios**
   - Navigate to scenario creation
   - Adjust parameters to create different financial scenarios
   - Save scenarios with descriptive names

6. **Dashboard Analysis**
   - Navigate to the dashboard
   - Compare different scenarios
   - Analyze charts and financial metrics

7. **Generate Reports**
   - Select a scenario
   - Generate PDF report
   - Verify all data is correctly displayed

8. **Admin Features** (requires admin account)
   - Login with admin credentials
   - Navigate to `/admin`
   - Test user management features
   - Review action logs

## API Documentation

The API documentation is available at `/api-docs.md` with detailed information about all endpoints.

## Sample Data

Sample spreadsheet templates are available in the `/samples` directory.

## Troubleshooting

- If database connection fails, ensure MongoDB is running and your connection string is correct
- For JWT errors, try clearing local storage and logging in again
- For Excel upload issues, ensure your file follows the required template structure

## License

[MIT](LICENSE)

## Configuração do Ambiente

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` com suas configurações:
- `MONGO_URI`: URL de conexão com o MongoDB
- `JWT_SECRET`: Chave secreta para tokens JWT
- `PORT`: Porta do servidor (padrão: 5000)
- `NODE_ENV`: Ambiente (development/production)

3. Instale as dependências:
```bash
npm install
cd client && npm install && cd ..
```

4. Inicie o MongoDB:
```bash
docker-compose up -d mongodb
```

5. Execute os seeds do banco:
```bash
npm run db:seed
```

6. Inicie a aplicação:
```bash
npm run dev
```

## Configuração SMTP para Recuperação de Senha

O sistema agora suporta recuperação de senha via email. Para configurar o serviço SMTP, você tem duas opções:

### 1. Configuração via Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```
# SMTP (opcional, pode usar configuração via painel admin)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=seu-usuario@example.com
SMTP_PASSWORD=suasenha
FROM_NAME=Habitus Finance
FROM_EMAIL=noreply@example.com
```

### 2. Configuração via Painel Administrativo

1. Acesse o sistema com uma conta de administrador
2. Navegue até "Configuração SMTP" no menu da área administrativa
3. Preencha os dados do servidor SMTP
4. Salve as configurações
5. Você pode enviar um email de teste para verificar se a configuração está funcionando corretamente

O sistema usará preferencialmente as configurações salvas no banco de dados. Se não encontrar, recorrerá às variáveis de ambiente. 

## Configuração com Domínio Real

A aplicação já inclui um proxy reverso Nginx que facilita a configuração com um domínio real. Siga os passos abaixo:

### 1. Configuração Inicial

Execute o script para criar a configuração do Nginx:

```bash
chmod +x setup-nginx.sh
./setup-nginx.sh
```

### 2. Configuração de Domínio

Edite o arquivo `nginx/default.conf` e substitua `localhost` pelo seu domínio real:

```nginx
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;
    
    # ... restante da configuração
}
```

### 3. Configuração HTTPS (recomendado)

1. Obtenha certificados SSL (Let's Encrypt é uma opção gratuita)
2. Coloque os certificados na pasta `nginx/ssl/`:
   - `fullchain.pem` - Certificado completo
   - `privkey.pem` - Chave privada
3. Descomente a seção HTTPS no arquivo `nginx/default.conf`

### 4. Inicie a Aplicação

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Configuração DNS

Configure o registro A ou CNAME do seu domínio para apontar para o IP do servidor onde a aplicação está hospedada. 

## Configuração com Domínio e HTTPS

Para configurar a aplicação com um domínio real e HTTPS, siga os passos abaixo:

### 1. Prepare o ambiente

```bash
# Crie a estrutura para o Nginx
chmod +x setup-nginx.sh
./setup-nginx.sh
```

### 2. Configure seu domínio

Edite o arquivo `nginx/default.conf` e atualize a diretiva `server_name` com seu domínio:

```nginx
server_name seudominio.com www.seudominio.com;
```

### 3. Obtenha certificados SSL com Let's Encrypt

```bash
# Instale o certbot (exemplo para Ubuntu/Debian)
apt-get update
apt-get install -y certbot

# Obtenha o certificado
certbot certonly --standalone -d seudominio.com -d www.seudominio.com

# Copie os certificados para a pasta correta
cp /etc/letsencrypt/live/seudominio.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/seudominio.com/privkey.pem nginx/ssl/
```

### 4. Ative a configuração HTTPS

Edite o arquivo `nginx/default.conf` e descomente a seção do servidor HTTPS.

### 5. Inicie a aplicação

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 6. Renovação automática de certificados

Configure um cron job para renovar automaticamente seus certificados:

```bash
# Adicione ao crontab
echo "0 3 * * * certbot renew --quiet && cp /etc/letsencrypt/live/seudominio.com/fullchain.pem /caminho/para/app/nginx/ssl/ && cp /etc/letsencrypt/live/seudominio.com/privkey.pem /caminho/para/app/nginx/ssl/ && docker restart habitus-nginx" | crontab -
```