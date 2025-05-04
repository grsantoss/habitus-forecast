# Build do cliente
FROM node:16-alpine as client-build
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client/ .
RUN npm run build

# Build do servidor
FROM node:16-alpine as server-build
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY server/ ./server/
COPY --from=client-build /app/client/build ./client/build

# Imagem final
FROM node:16-alpine
WORKDIR /app
COPY --from=server-build /app ./

# Criar diretórios necessários
RUN mkdir -p server/uploads logs

# Configurar permissões
RUN chown -R node:node /app
USER node

# Expor porta
EXPOSE 5000

# Iniciar aplicação
CMD ["node", "server/index.js"] 