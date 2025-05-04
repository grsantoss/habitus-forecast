const Redis = require('ioredis');
const expressRedisCache = require('express-redis-cache');

const redis = new Redis(process.env.REDIS_URL);
const cache = expressRedisCache({
  client: redis,
  prefix: 'habitus:',
  expire: parseInt(process.env.CACHE_TTL)
});

// Middleware para limpar cache
const clearCache = (req, res, next) => {
  const clearCacheKey = req.query.clearCache;
  if (clearCacheKey) {
    cache.del(clearCacheKey, (err) => {
      if (err) {
        console.error('Erro ao limpar cache:', err);
      }
    });
  }
  next();
};

module.exports = {
  cache,
  clearCache
}; 