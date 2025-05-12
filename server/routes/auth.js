const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const auth = require('../middleware/auth');
const crypto = require('crypto');

const User = require('../models/User');
const { sendEmail } = require('../config/email');

// @route   POST api/auth/register
// @desc    Register a user
// @access  Public
router.post(
  '/register',
  [
    check('name', 'Name is required').not().isEmpty(),
    check('email', 'Please include a valid email').isEmail(),
    check('password', 'Please enter a password with 6 or more characters').isLength({ min: 6 })
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { name, email, password } = req.body;

    try {
      // Check if user exists
      let user = await User.findOne({ email });

      if (user) {
        return res.status(400).json({ msg: 'User already exists' });
      }

      user = new User({
        name,
        email,
        password
      });

      await user.save();

      const token = user.getSignedJwtToken();

      res.json({ token });
    } catch (err) {
      console.error(err.message);
      res.status(500).send('Server error');
    }
  }
);

// @route   POST api/auth/login
// @desc    Authenticate user & get token
// @access  Public
router.post(
  '/login',
  [
    check('email', 'Please include a valid email').isEmail(),
    check('password', 'Password is required').exists()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password } = req.body;

    try {
      // Check if user exists
      let user = await User.findOne({ email }).select('+password');

      if (!user) {
        return res.status(400).json({ msg: 'Invalid Credentials' });
      }

      // Check if password matches
      const isMatch = await user.matchPassword(password);

      if (!isMatch) {
        return res.status(400).json({ msg: 'Invalid Credentials' });
      }

      const token = user.getSignedJwtToken();

      res.json({ token });
    } catch (err) {
      console.error(err.message);
      res.status(500).send('Server error');
    }
  }
);

// @route   GET api/auth/me
// @desc    Get current user
// @access  Private
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    res.json(user);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route   POST api/auth/forgot-password
// @desc    Forgot password route, sends password reset email
// @access  Public
router.post('/forgot-password', 
  [
    check('email', 'Por favor, forneça um email válido').isEmail()
  ], 
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const user = await User.findOne({ email: req.body.email });

      if (!user) {
        return res.status(404).json({ msg: 'Usuário com este email não existe' });
      }

      // Gera token de reset
      const resetToken = user.getResetPasswordToken();
      await user.save({ validateBeforeSave: false });

      // Cria URL de reset
      const resetUrl = `${process.env.NODE_ENV === 'production' ? 'https' : 'http'}://${process.env.FRONTEND_URL || req.get('host').replace(/:\d+$/, '')}/reset-password/${resetToken}`;

      // Conteúdo do email
      const message = `
        <h1>Solicitação de redefinição de senha</h1>
        <p>Você recebeu este email porque você (ou alguém) solicitou a redefinição da senha da sua conta.</p>
        <p>Por favor, clique no link abaixo para redefinir sua senha:</p>
        <a href="${resetUrl}" target="_blank">Redefinir Senha</a>
        <p>Se você não solicitou esta redefinição, por favor ignore este email e sua senha permanecerá inalterada.</p>
      `;

      try {
        await sendEmail({
          email: user.email,
          subject: 'Redefinição de senha - Habitus Finance',
          html: message
        });

        res.status(200).json({ success: true, data: 'Email enviado' });
      } catch (err) {
        console.error('Erro ao enviar email:', err);
        
        user.resetPasswordToken = undefined;
        user.resetPasswordExpire = undefined;
        await user.save({ validateBeforeSave: false });

        const errorMessage = err.message && err.message.includes('Configuração SMTP não disponível') 
          ? 'Configuração SMTP não disponível. Entre em contato com o administrador.'
          : 'Email não pode ser enviado. Verifique a configuração SMTP.';

        return res.status(500).json({ msg: errorMessage });
      }
    } catch (err) {
      console.error(err);
      res.status(500).json({ msg: 'Erro no servidor' });
    }
  }
);

// @route   POST api/auth/reset-password/:resettoken
// @desc    Reset password
// @access  Public
router.post('/reset-password/:resettoken', 
  [
    check('password', 'A senha deve ter no mínimo 6 caracteres').isLength({ min: 6 })
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Obter token hash
    const resetPasswordToken = crypto
      .createHash('sha256')
      .update(req.params.resettoken)
      .digest('hex');

    try {
      // Encontrar usuário com token válido
      const user = await User.findOne({
        resetPasswordToken,
        resetPasswordExpire: { $gt: Date.now() }
      });

      if (!user) {
        return res.status(400).json({ msg: 'Token inválido ou expirado' });
      }

      // Definir nova senha
      user.password = req.body.password;
      user.resetPasswordToken = undefined;
      user.resetPasswordExpire = undefined;
      await user.save();

      // Enviar email confirmando alteração de senha
      try {
        await sendEmail({
          email: user.email,
          subject: 'Senha alterada com sucesso - Habitus Finance',
          html: `
            <h1>Senha Alterada</h1>
            <p>Sua senha foi alterada com sucesso.</p>
            <p>Se você não realizou esta alteração, por favor entre em contato conosco imediatamente.</p>
          `
        });
      } catch (err) {
        console.error('Erro ao enviar email de confirmação:', err);
        // Não impede o fluxo se o email de confirmação falhar
      }

      res.status(200).json({ success: true, msg: 'Senha alterada com sucesso' });
    } catch (err) {
      console.error(err);
      res.status(500).json({ msg: 'Erro no servidor' });
    }
  }
);

module.exports = router;