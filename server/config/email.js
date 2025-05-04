const nodemailer = require('nodemailer');
const dotenv = require('dotenv');
const SmtpConfig = require('../models/SmtpConfig');

dotenv.config();

const createTransporter = async () => {
  try {
    // Tentar obter configurações do banco de dados
    const dbConfig = await SmtpConfig.findOne({ isActive: true }).select('+password');
    
    if (dbConfig) {
      return nodemailer.createTransport({
        host: dbConfig.host,
        port: dbConfig.port,
        secure: dbConfig.secure,
        auth: {
          user: dbConfig.user,
          pass: dbConfig.password
        }
      });
    }
  } catch (error) {
    console.error('Erro ao obter configuração SMTP do banco de dados:', error);
  }

  // Verificar se as configurações de ambiente estão disponíveis
  if (!process.env.SMTP_HOST || !process.env.SMTP_USER || !process.env.SMTP_PASSWORD) {
    throw new Error('Configuração SMTP não disponível. Configure via painel admin ou variáveis de ambiente.');
  }

  // Fallback para configurações de ambiente
  return nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: process.env.SMTP_PORT || 587,
    secure: process.env.SMTP_SECURE === 'true',
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASSWORD
    }
  });
};

const getFromAddress = async () => {
  try {
    const dbConfig = await SmtpConfig.findOne({ isActive: true });
    if (dbConfig) {
      return {
        name: dbConfig.fromName,
        email: dbConfig.fromEmail
      };
    }
  } catch (error) {
    console.error('Erro ao obter endereço de origem:', error);
  }

  // Fallback para configurações de ambiente
  return {
    name: process.env.FROM_NAME || 'Habitus Finance',
    email: process.env.FROM_EMAIL || 'noreply@habitusfinance.com'
  };
};

const sendEmail = async (options) => {
  try {
    const transporter = await createTransporter();
    const from = await getFromAddress();
    
    const message = {
      from: `${from.name} <${from.email}>`,
      to: options.email,
      subject: options.subject,
      html: options.html
    };

    const info = await transporter.sendMail(message);
    console.log('Email enviado: %s', info.messageId);
    return true;
  } catch (error) {
    console.error('Erro ao enviar email:', error);
    throw error;
  }
};

module.exports = {
  sendEmail
}; 