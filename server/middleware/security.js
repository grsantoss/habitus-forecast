const rateLimit = require('express-rate-limit');
const multer = require('multer');
const path = require('path');

// Rate Limiting
const apiLimiter = rateLimit({
  windowMs: process.env.RATE_LIMIT_WINDOW * 60 * 1000, // minutos para milissegundos
  max: process.env.RATE_LIMIT_MAX,
  message: 'Muitas requisições deste IP, tente novamente mais tarde'
});

// Configuração do Multer para uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'server/uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

const fileFilter = (req, file, cb) => {
  const allowedTypes = process.env.ALLOWED_FILE_TYPES.split(',');
  const fileExt = path.extname(file.originalname).toLowerCase().substring(1);
  
  if (allowedTypes.includes(fileExt)) {
    cb(null, true);
  } else {
    cb(new Error('Tipo de arquivo não permitido'), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE)
  }
});

// Validação de senha
const validatePassword = (password) => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (password.length < minLength) {
    throw new Error('A senha deve ter pelo menos 8 caracteres');
  }
  if (!hasUpperCase) {
    throw new Error('A senha deve conter pelo menos uma letra maiúscula');
  }
  if (!hasLowerCase) {
    throw new Error('A senha deve conter pelo menos uma letra minúscula');
  }
  if (!hasNumbers) {
    throw new Error('A senha deve conter pelo menos um número');
  }
  if (!hasSpecialChar) {
    throw new Error('A senha deve conter pelo menos um caractere especial');
  }

  return true;
};

module.exports = {
  apiLimiter,
  upload,
  validatePassword
}; 