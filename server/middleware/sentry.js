const Sentry = require('@sentry/node');
const { ProfilingIntegration } = require('@sentry/profiling-node');

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    new ProfilingIntegration(),
  ],
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
});

// Middleware para capturar erros
const errorHandler = (err, req, res, next) => {
  Sentry.captureException(err);
  res.status(500).json({
    error: 'Ocorreu um erro interno no servidor'
  });
};

module.exports = {
  Sentry,
  errorHandler
}; 