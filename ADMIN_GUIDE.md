# Guia de Administração - Habitus Forecast

Este guia fornece informações detalhadas para administradores do Habitus Forecast, incluindo tarefas administrativas comuns, gerenciamento de usuários, monitoramento do sistema e resolução de problemas.

## Sumário

- [Visão Geral do Papel de Administrador](#visão-geral-do-papel-de-administrador)
- [Acessando o Dashboard Administrativo](#acessando-o-dashboard-administrativo)
- [Gerenciamento de Usuários](#gerenciamento-de-usuários)
  - [Criação de Usuários](#criação-de-usuários)
  - [Edição de Perfis](#edição-de-perfis)
  - [Gerenciamento de Permissões](#gerenciamento-de-permissões)
  - [Desativação de Contas](#desativação-de-contas)
- [Monitoramento do Sistema](#monitoramento-do-sistema)
  - [Métricas do Sistema](#métricas-do-sistema)
  - [Logs de Atividade](#logs-de-atividade)
  - [Notificações e Alertas](#notificações-e-alertas)
- [Configuração do Sistema](#configuração-do-sistema)
  - [Definições Globais](#definições-globais)
  - [Modelos de Cenários](#modelos-de-cenários)
  - [Configurações de Email](#configurações-de-email)
- [Tarefas Administrativas Comuns](#tarefas-administrativas-comuns)
  - [Backup de Dados](#backup-de-dados)
  - [Manutenção do Banco de Dados](#manutenção-do-banco-de-dados)
  - [Atualização do Sistema](#atualização-do-sistema)
- [Resolução de Problemas](#resolução-de-problemas)
  - [Problemas de Autenticação](#problemas-de-autenticação)
  - [Problemas de Desempenho](#problemas-de-desempenho)
  - [Problemas de Dados](#problemas-de-dados)
- [Melhores Práticas](#melhores-práticas)
  - [Segurança](#segurança)
  - [Desempenho](#desempenho)
  - [Suporte aos Usuários](#suporte-aos-usuários)

## Visão Geral do Papel de Administrador

Como administrador do Habitus Forecast, você tem acesso a funcionalidades e ferramentas que permitem gerenciar todos os aspectos do sistema, incluindo:

- Gerenciamento completo de usuários e suas permissões
- Acesso a dados e métricas de uso do sistema
- Configuração de parâmetros globais e padrões do sistema
- Monitoramento de desempenho e logs
- Administração do banco de dados e backups
- Resolução de problemas e suporte técnico

Cada administrador deve usar estas capacidades de forma responsável, seguindo as políticas de segurança e privacidade da organização.

## Acessando o Dashboard Administrativo

O dashboard administrativo é o ponto central para todas as tarefas de administração:

1. Faça login no sistema com suas credenciais de administrador
2. Acesse `/admin` ou clique no ícone "Admin" no menu principal
3. O dashboard administrativo é dividido em seções:
   - **Visão Geral**: Estatísticas e métricas principais
   - **Usuários**: Gerenciamento de contas
   - **Sistema**: Configurações e logs
   - **Dados**: Backups e manutenção
   - **Suporte**: Ferramentas de suporte ao usuário

## Gerenciamento de Usuários

### Criação de Usuários

Para criar um novo usuário:

1. No dashboard administrativo, navegue até "Usuários" > "Novo Usuário"
2. Preencha os campos obrigatórios:
   - Email (deve ser único)
   - Nome
   - Papel (Usuário ou Administrador)
   - Senha inicial (ou habilite envio automático)
3. Configure opções adicionais:
   - Status da conta (Ativo/Inativo)
   - Requer alteração de senha no primeiro login
   - Limite de cenários (se aplicável)
4. Clique em "Criar Usuário"

O sistema enviará automaticamente um email com as instruções de acesso se a opção estiver habilitada.

### Edição de Perfis

Para editar um perfil de usuário existente:

1. No dashboard administrativo, navegue até "Usuários" > "Lista de Usuários"
2. Localize o usuário através da busca ou filtros
3. Clique no ícone de edição
4. Modifique os campos necessários
5. Clique em "Salvar Alterações"

**Nota**: A alteração do email de um usuário requer confirmação adicional e pode exigir verificação do novo endereço.

### Gerenciamento de Permissões

O Habitus Forecast utiliza um sistema de controle de acesso baseado em papéis (RBAC):

1. **Usuário Regular**: Acesso apenas aos seus próprios dados e cenários
2. **Administrador**: Acesso completo a todas as funcionalidades e dados

Para modificar o papel de um usuário:

1. No dashboard administrativo, navegue até "Usuários" > "Lista de Usuários"
2. Localize o usuário desejado
3. Clique no ícone de edição
4. Altere o campo "Papel"
5. Clique em "Salvar Alterações"

**Importante**: A alteração de um usuário para administrador concede acesso total ao sistema. Atribua este papel com cautela.

### Desativação de Contas

Quando um usuário não deve mais ter acesso, em vez de excluir a conta (o que poderia afetar a integridade dos dados), desative-a:

1. No dashboard administrativo, navegue até "Usuários" > "Lista de Usuários"
2. Localize o usuário desejado
3. Clique no ícone de edição
4. Altere o campo "Status" para "Inativo"
5. Opcionalmente, adicione uma nota sobre o motivo da desativação
6. Clique em "Salvar Alterações"

Um usuário desativado:
- Não pode fazer login no sistema
- Tem seus dados preservados
- Pode ser reativado posteriormente se necessário

Para reativar uma conta, siga o mesmo processo e defina o status como "Ativo".

## Monitoramento do Sistema

### Métricas do Sistema

O dashboard administrativo fornece métricas importantes do sistema:

1. **Métricas de Usuários**:
   - Total de usuários
   - Usuários ativos nos últimos 7/30 dias
   - Taxa de crescimento
   - Distribuição geográfica (se disponível)

2. **Métricas de Uso**:
   - Número de cenários criados
   - Operações de projeção realizadas
   - Importações e exportações
   - Utilização de recursos

3. **Métricas de Sistema**:
   - Utilização de CPU/Memória
   - Tempo de resposta da API
   - Taxa de erros
   - Espaço em disco

Para acessar métricas históricas:
1. No dashboard administrativo, navegue até "Sistema" > "Métricas"
2. Selecione o período desejado
3. Utilize os filtros para refinar os dados
4. Exporte relatórios se necessário (CSV, PDF)

### Logs de Atividade

Os logs são essenciais para monitoramento, auditoria e resolução de problemas:

1. **Logs de Usuário**:
   - Logins/Logouts
   - Alterações de senha
   - Criação/Edição de cenários
   - Exportações de dados

2. **Logs do Sistema**:
   - Inicialização/Desligamento
   - Atualizações
   - Backups
   - Erros e alertas

Para acessar os logs:
1. No dashboard administrativo, navegue até "Sistema" > "Logs"
2. Utilize filtros para pesquisar por:
   - Período
   - Tipo de log
   - Usuário
   - Nível (INFO, WARNING, ERROR)
   - Termos específicos
3. Clique em um item para ver detalhes completos
4. Exporte logs filtrados para análise externa

Os logs são retidos por 90 dias por padrão. Períodos mais longos estão disponíveis através da exportação e arquivamento.

### Notificações e Alertas

Configure alertas para ser notificado sobre eventos importantes:

1. No dashboard administrativo, navegue até "Sistema" > "Alertas"
2. Configure alertas para:
   - Falhas de autenticação múltiplas
   - Uso elevado de recursos
   - Erros críticos do sistema
   - Tentativas de acesso não autorizadas
   - Backups falhos
3. Defina limites e condições para cada alerta
4. Configure o método de notificação (email, SMS, webhook)

## Configuração do Sistema

### Definições Globais

As definições globais afetam todo o funcionamento do sistema:

1. No dashboard administrativo, navegue até "Sistema" > "Configurações"
2. Configure parâmetros como:
   - **Limites de usuário**: Número máximo de cenários por usuário, tamanho de importação
   - **Políticas de senha**: Complexidade, duração, histórico
   - **Sessões**: Duração dos tokens, número máximo de sessões simultâneas
   - **Intervalos de backup**: Frequência dos backups automáticos
   - **Recursos computacionais**: Alocação para análises e projeções

**Importante**: Alterações nas definições globais podem afetar significativamente o desempenho e o comportamento do sistema. Teste em ambiente de staging antes de aplicar em produção.

### Modelos de Cenários

Administradores podem criar modelos de cenários que servem como ponto de partida para os usuários:

1. No dashboard administrativo, navegue até "Conteúdo" > "Modelos de Cenários"
2. Clique em "Novo Modelo"
3. Configure o cenário modelo:
   - Nome e descrição
   - Estrutura de dados
   - Parâmetros padrão
   - Projeções pré-configuradas
4. Defina visibilidade e permissões:
   - Disponível para todos os usuários
   - Restrito a grupos específicos
   - Editável ou somente leitura
5. Salve o modelo

### Configurações de Email

Configure o sistema de email para notificações e comunicações:

1. No dashboard administrativo, navegue até "Sistema" > "Email"
2. Configure o provedor SMTP:
   - Servidor, porta, autenticação
   - Email de remetente
   - Limite de envios
3. Gerencie templates de email para:
   - Boas-vindas
   - Recuperação de senha
   - Notificações
   - Alertas
4. Verifique o log de envios e falhas

## Tarefas Administrativas Comuns

### Backup de Dados

O Habitus Forecast suporta backups automáticos e manuais:

**Backups Automáticos**:
- Configurados nas definições globais
- Executados em horários de baixo uso
- Armazenados localmente e/ou na nuvem
- Rotação automática (períodos configuráveis)

**Backups Manuais**:
1. No dashboard administrativo, navegue até "Dados" > "Backup"
2. Clique em "Backup Manual"
3. Selecione o escopo:
   - Completo (todo o banco de dados)
   - Parcial (configurações, usuários, dados)
4. Aguarde a conclusão
5. Baixe o arquivo ou confirme o armazenamento remoto

**Restauração de Backup**:
1. No dashboard administrativo, navegue até "Dados" > "Restauração"
2. Selecione o arquivo de backup ou fonte remota
3. Escolha o modo de restauração:
   - Completa (substitui todos os dados)
   - Seletiva (apenas componentes específicos)
4. Confirme a operação

**Importante**: A restauração completa é uma operação irreversível que substitui todos os dados atuais. Use com extrema cautela e considere criar um backup antes de restaurar.

### Manutenção do Banco de Dados

Tarefas periódicas para manter o desempenho e integridade do banco de dados:

1. **Otimização**:
   - No dashboard administrativo, navegue até "Dados" > "Manutenção"
   - Clique em "Otimizar Banco de Dados"
   - Selecione as coleções a otimizar ou escolha "Todas"
   - Programe para horários de baixo uso

2. **Validação**:
   - No mesmo painel, clique em "Validar Integridade"
   - Verifique os relatórios de consistência
   - Corrija problemas identificados

3. **Limpeza**:
   - Remova dados temporários e logs antigos
   - Arquive dados históricos raramente acessados
   - Programe limpezas automáticas

### Atualização do Sistema

Quando novas versões do Habitus Forecast estiverem disponíveis:

1. Revise as notas da versão para mudanças importantes
2. Teste a atualização em ambiente de staging primeiro
3. Programe um período de manutenção e notifique os usuários
4. Crie um backup completo antes de atualizar
5. Siga as instruções específicas da versão para atualização
6. Após a atualização, verifique:
   - Funcionalidades críticas
   - Desempenho do sistema
   - Integridade dos dados
   - Logs de erros

## Resolução de Problemas

### Problemas de Autenticação

**Usuário não consegue fazer login**:
1. Verifique se a conta está ativa
2. Confirme que o email está correto
3. Verifique se a conta está bloqueada por tentativas falhas
4. Redefina a senha do usuário:
   - No dashboard administrativo, navegue até "Usuários" > "Lista"
   - Localize o usuário e clique em "Redefinir Senha"
   - Escolha enviar link de redefinição ou definir senha temporária

**Tokens expirados ou inválidos**:
1. Verifique a configuração de duração dos tokens
2. Confirme que o horário do servidor está sincronizado
3. Limpe tokens expirados:
   - No dashboard administrativo, navegue até "Sistema" > "Sessões"
   - Clique em "Limpar Sessões Expiradas"

### Problemas de Desempenho

**Lentidão geral do sistema**:
1. Verifique as métricas de utilização de recursos
2. Identifique picos de uso e correlacione com atividades
3. Verifique processos de análise e projeção executando
4. Otimize o banco de dados se necessário
5. Considere limitar operações pesadas durante horários de pico

**Consultas lentas**:
1. No dashboard administrativo, navegue até "Sistema" > "Desempenho"
2. Revise o log de consultas lentas
3. Otimize índices para consultas frequentes

### Problemas de Dados

**Inconsistência de dados**:
1. Execute a validação de integridade do banco de dados
2. Identifique relações quebradas ou dados corrompidos
3. Restaure a partir de backup se necessário
4. Para problemas específicos de um usuário, considere exportar seus dados, corrigir e reimportar

**Dados ausentes**:
1. Verifique logs de operações para identificar quando os dados foram removidos
2. Determine se foi uma operação de usuário ou uma falha do sistema
3. Restaure dados específicos a partir do backup mais recente

## Melhores Práticas

### Segurança

- **Rotação de senhas**: Exija que administradores alterem suas senhas a cada 60-90 dias
- **Autenticação de dois fatores (2FA)**: Ative para todas as contas administrativas
- **Princípio do menor privilégio**: Conceda apenas as permissões necessárias para cada função
- **Auditoria regular**: Revise logs de atividade administrativa periodicamente
- **Acesso administrativo**: Restrinja a redes confiáveis quando possível

### Desempenho

- **Manutenção preventiva**: Agende otimizações regulares do banco de dados
- **Monitoramento contínuo**: Configure alertas para métricas críticas
- **Escalabilidade**: Monitore o crescimento e planeje capacidade adicional
- **Janelas de manutenção**: Agende atualizações e tarefas pesadas fora do horário comercial
- **Arquivamento**: Mova dados históricos raramente acessados para armazenamento secundário

### Suporte aos Usuários

- **Documentação**: Mantenha guias e tutoriais atualizados
- **Comunicação proativa**: Notifique sobre manutenções e atualizações com antecedência
- **Treinamento**: Ofereça sessões regulares para novos recursos
- **Feedback**: Colete e analise opiniões dos usuários para melhorias
- **Base de conhecimento**: Documente problemas comuns e suas soluções

---

Para questões não cobertas neste guia, entre em contato com o suporte técnico avançado em `support@habitus-forecast.com`. 