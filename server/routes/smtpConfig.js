const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const adminAuth = require('../middleware/adminAuth');
const nodemailer = require('nodemailer');

const SmtpConfig = require('../models/SmtpConfig');

// @route   GET api/smtp-config
// @desc    Get SMTP configuration
// @access  Admin
router.get('/', adminAuth, async (req, res) => {
  try {
    const config = await SmtpConfig.findOne().sort({ updatedAt: -1 });
    
    if (!config) {
      return res.status(404).json({ msg: 'Configuração SMTP não encontrada' });
    }
    
    // Não envie a senha de volta
    const safeConfig = {
      host: config.host,
      port: config.port,
      secure: config.secure,
      user: config.user,
      fromEmail: config.fromEmail,
      fromName: config.fromName,
      isActive: config.isActive,
      updatedAt: config.updatedAt,
      _id: config._id
    };
    
    res.json(safeConfig);
  } catch (err) {
    console.error('Erro ao obter configuração SMTP:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   POST api/smtp-config
// @desc    Create or update SMTP configuration
// @access  Admin
router.post('/', [
  adminAuth,
  [
    check('host', 'Host é obrigatório').not().isEmpty(),
    check('port', 'Porta é obrigatória').isNumeric(),
    check('user', 'Usuário é obrigatório').not().isEmpty(),
    check('password', 'Senha é obrigatória').not().isEmpty(),
    check('fromEmail', 'Email de origem é obrigatório').isEmail(),
    check('fromName', 'Nome de origem é obrigatório').not().isEmpty()
  ]
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  
  const { host, port, secure, user, password, fromEmail, fromName, isActive } = req.body;
  
  try {
    // Criar ou atualizar configuração
    let config = await SmtpConfig.findOne();
    
    if (config) {
      // Atualizar configuração existente
      config.host = host;
      config.port = port;
      config.secure = secure || false;
      config.user = user;
      if (password) {
        config.password = password;
      }
      config.fromEmail = fromEmail;
      config.fromName = fromName;
      config.isActive = isActive !== undefined ? isActive : true;
      config.updatedAt = Date.now();
    } else {
      // Criar nova configuração
      config = new SmtpConfig({
        host,
        port,
        secure: secure || false,
        user,
        password,
        fromEmail,
        fromName,
        isActive: isActive !== undefined ? isActive : true
      });
    }
    
    await config.save();
    
    // Retornar configuração sem senha
    const safeConfig = {
      host: config.host,
      port: config.port,
      secure: config.secure,
      user: config.user,
      fromEmail: config.fromEmail,
      fromName: config.fromName,
      isActive: config.isActive,
      updatedAt: config.updatedAt,
      _id: config._id
    };
    
    res.json(safeConfig);
  } catch (err) {
    console.error('Erro ao salvar configuração SMTP:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   POST api/smtp-config/test
// @desc    Test SMTP configuration
// @access  Admin
router.post('/test', [
  adminAuth,
  [
    check('email', 'Email para teste é obrigatório').isEmail()
  ]
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  
  try {
    const config = await SmtpConfig.findOne().select('+password');
    
    if (!config) {
      return res.status(404).json({ msg: 'Configuração SMTP não encontrada' });
    }
    
    // Configurar nodemailer com as configurações do banco de dados
    const transporter = nodemailer.createTransport({
      host: config.host,
      port: config.port,
      secure: config.secure,
      auth: {
        user: config.user,
        pass: config.password
      }
    });
    
    // Enviar email de teste
    const info = await transporter.sendMail({
      from: `"${config.fromName}" <${config.fromEmail}>`,
      to: req.body.email,
      subject: 'Teste de Configuração SMTP - Habitus Finance',
      html: `
        <h1>Teste de Configuração SMTP</h1>
        <p>Este é um email de teste para verificar a configuração SMTP do Habitus Finance.</p>
        <p>Se você recebeu este email, a configuração foi bem-sucedida!</p>
      `
    });
    
    res.json({ 
      success: true, 
      msg: 'Email de teste enviado com sucesso',
      messageId: info.messageId
    });
  } catch (err) {
    console.error('Erro ao testar configuração SMTP:', err.message);
    res.status(500).json({ 
      success: false,
      msg: `Erro ao enviar email de teste: ${err.message}` 
    });
  }
});

module.exports = router; 