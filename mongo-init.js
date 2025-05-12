// Script de inicialização do MongoDB para Habitus Forecast
// Este script será executado uma vez quando o container MongoDB for iniciado pela primeira vez

// Conecta ao banco de dados admin para autenticação
db = db.getSiblingDB('admin');

// Define variáveis para os usuários
const appDbName = process.env.MONGO_INITDB_DATABASE || 'habitus';
const rootUser = process.env.MONGO_INITDB_ROOT_USERNAME;
const rootPassword = process.env.MONGO_INITDB_ROOT_PASSWORD;
const appUser = process.env.MONGO_APP_USERNAME || 'habitus_app';
const appPassword = process.env.MONGO_APP_PASSWORD || 'habitus_app_password';
const readOnlyUser = process.env.MONGO_READONLY_USERNAME || 'habitus_readonly';
const readOnlyPassword = process.env.MONGO_READONLY_PASSWORD || 'habitus_readonly_password';

// Autentica como admin (apenas necessário se --auth estiver habilitado)
// db.auth(rootUser, rootPassword);

// Criar usuário de aplicação com permissões somente no banco de dados da aplicação
print('Criando usuário de aplicação...');
db.getSiblingDB(appDbName).createUser({
  user: appUser,
  pwd: appPassword,
  roles: [
    { role: 'readWrite', db: appDbName },
    { role: 'dbAdmin', db: appDbName }
  ]
});

// Criar usuário somente leitura para backups e monitoramento
print('Criando usuário somente leitura...');
db.getSiblingDB(appDbName).createUser({
  user: readOnlyUser,
  pwd: readOnlyPassword,
  roles: [
    { role: 'read', db: appDbName }
  ]
});

// Prepara as coleções principais
const db = db.getSiblingDB(appDbName);

// Cria as coleções principais
print('Criando coleções...');
db.createCollection('users');
db.createCollection('financial_data');
db.createCollection('scenarios');
db.createCollection('password_resets');

// Cria índices para melhorar a performance
print('Criando índices...');
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.financial_data.createIndex({ user_id: 1, created_at: -1 });
db.scenarios.createIndex({ user_id: 1, scenario_type: 1, created_at: -1 });
db.password_resets.createIndex({ token: 1 });
db.password_resets.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });

// Cria um TTL (time-to-live) índice para expiração automática de tokens
print('Criando índice TTL para tokens...');
db.password_resets.createIndex(
  { "expires_at": 1 },
  { expireAfterSeconds: 0 }
);

print('Inicialização do MongoDB concluída com sucesso!'); 