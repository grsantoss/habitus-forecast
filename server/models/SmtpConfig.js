const mongoose = require('mongoose');

const SmtpConfigSchema = new mongoose.Schema({
  host: {
    type: String,
    required: [true, 'Por favor, adicione o host SMTP'],
    trim: true
  },
  port: {
    type: Number,
    required: [true, 'Por favor, adicione a porta SMTP'],
    default: 587
  },
  secure: {
    type: Boolean,
    default: false
  },
  user: {
    type: String,
    required: [true, 'Por favor, adicione o usuário SMTP']
  },
  password: {
    type: String,
    required: [true, 'Por favor, adicione a senha SMTP'],
    select: false
  },
  fromEmail: {
    type: String,
    required: [true, 'Por favor, adicione o email de origem'],
    match: [
      /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
      'Por favor, adicione um email válido'
    ]
  },
  fromName: {
    type: String,
    required: [true, 'Por favor, adicione o nome de origem'],
    default: 'Habitus Finance'
  },
  isActive: {
    type: Boolean,
    default: true
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('SmtpConfig', SmtpConfigSchema); 