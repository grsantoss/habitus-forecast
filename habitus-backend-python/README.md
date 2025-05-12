# Habitus Forecast API

API backend em FastAPI para o aplicativo Habitus Forecast, um SaaS para simulação e análise financeira.

## Estrutura do Projeto

```
habitus-backend-python/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── scenarios.py
│   │   │   ├── spreadsheets.py
│   │   │   ├── smtp_config.py
│   │   │   └── users.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── scenario.py
│   │   ├── spreadsheet.py
│   │   └── smtp_config.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── scenario.py
│   │   ├── spreadsheet.py
│   │   └── smtp_config.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── spreadsheet_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file_utils.py
│   ├── __init__.py
│   └── main.py
├── tests/
├── uploads/
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.10+
- MongoDB 5.0+

## Configuração

1. Clone o repositório:

```bash
git clone https://github.com/seu-username/habitus-forecast-api.git
cd habitus-forecast-api
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Crie a pasta de uploads:

```bash
mkdir -p uploads
```

## Execução

```bash
# Desenvolvimento
uvicorn app.main:app --reload

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

A documentação da API estará disponível em: http://localhost:8000/docs

## Docker

Para executar com Docker:

```bash
# Construir a imagem
docker build -t habitus-forecast-api .

# Executar o container
docker run -p 8000:8000 --env-file .env habitus-forecast-api
```

## Testes

```bash
pytest
```

## Recursos da API

- Autenticação (JWT)
- Gerenciamento de usuários
- Upload e processamento de planilhas
- Criação de cenários financeiros
- Configuração SMTP para envio de emails

## Licença

Este projeto está licenciado sob a licença ISC.
