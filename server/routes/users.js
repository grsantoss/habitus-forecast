const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { check, validationResult } = require('express-validator');
const auth = require('../middleware/auth');
const adminAuth = require('../middleware/adminAuth');
const User = require('../models/User');
const Spreadsheet = require('../models/Spreadsheet');
const Scenario = require('../models/Scenario');

// @route   GET api/users/me
// @desc    Get current user profile
// @access  Private
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ msg: 'Usuário não encontrado' });
    }
    
    res.json(user);
  } catch (err) {
    console.error('Error in /users/me:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   PUT api/users/me
// @desc    Update current user profile
// @access  Private
router.put('/me', [
  auth,
  [
    check('name', 'Nome é obrigatório').not().isEmpty(),
    check('email', 'Por favor, inclua um email válido').isEmail()
  ]
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  
  const { name, email, password } = req.body;
  
  try {
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return res.status(404).json({ msg: 'Usuário não encontrado' });
    }
    
    // Check if email is already in use by another user
    if (email !== user.email) {
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(400).json({ msg: 'Este email já está em uso' });
      }
    }
    
    // Update user fields
    user.name = name;
    user.email = email;
    
    // Update password if provided
    if (password) {
      const salt = await bcrypt.genSalt(10);
      user.password = await bcrypt.hash(password, salt);
    }
    
    await user.save();
    
    // Return updated user without password
    const updatedUser = await User.findById(req.user.id).select('-password');
    res.json(updatedUser);
  } catch (err) {
    console.error('Error updating user profile:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   GET api/users/admin/users
// @desc    Get all users (admin only)
// @access  Admin
router.get('/admin/users', adminAuth, async (req, res) => {
  try {
    const users = await User.find().select('-password').sort({ createdAt: -1 });
    res.json(users);
  } catch (err) {
    console.error('Error getting users:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   POST api/users/admin/users
// @desc    Create a new user (admin only)
// @access  Admin
router.post('/admin/users', [
  adminAuth,
  [
    check('name', 'Nome é obrigatório').not().isEmpty(),
    check('email', 'Por favor, inclua um email válido').isEmail(),
    check('password', 'Por favor, digite uma senha com 6 ou mais caracteres').isLength({ min: 6 }),
    check('role', 'Perfil deve ser user ou admin').isIn(['user', 'admin'])
  ]
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  
  const { name, email, password, role } = req.body;
  
  try {
    // Check if user already exists
    let user = await User.findOne({ email });
    
    if (user) {
      return res.status(400).json({ msg: 'Usuário já existe' });
    }
    
    user = new User({
      name,
      email,
      password,
      role
    });
    
    // Hash password
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(password, salt);
    
    await user.save();
    
    // Return created user without password
    const newUser = await User.findById(user.id).select('-password');
    res.status(201).json(newUser);
  } catch (err) {
    console.error('Error creating user:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   PUT api/users/admin/users/:id
// @desc    Update a user (admin only)
// @access  Admin
router.put('/admin/users/:id', [
  adminAuth,
  [
    check('name', 'Nome é obrigatório').not().isEmpty(),
    check('email', 'Por favor, inclua um email válido').isEmail(),
    check('role', 'Perfil deve ser user ou admin').isIn(['user', 'admin'])
  ]
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  
  const { name, email, password, role } = req.body;
  
  try {
    let user = await User.findById(req.params.id);
    
    if (!user) {
      return res.status(404).json({ msg: 'Usuário não encontrado' });
    }
    
    // Check if email is already in use by another user
    if (email !== user.email) {
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(400).json({ msg: 'Este email já está em uso' });
      }
    }
    
    // Update user fields
    user.name = name;
    user.email = email;
    user.role = role;
    
    // Update password if provided
    if (password) {
      const salt = await bcrypt.genSalt(10);
      user.password = await bcrypt.hash(password, salt);
    }
    
    await user.save();
    
    // Return updated user without password
    const updatedUser = await User.findById(req.params.id).select('-password');
    res.json(updatedUser);
  } catch (err) {
    console.error('Error updating user:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   DELETE api/users/admin/users/:id
// @desc    Delete a user (admin only)
// @access  Admin
router.delete('/admin/users/:id', adminAuth, async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    
    if (!user) {
      return res.status(404).json({ msg: 'Usuário não encontrado' });
    }
    
    // Don't allow deleting the last admin user
    if (user.role === 'admin') {
      const adminCount = await User.countDocuments({ role: 'admin' });
      if (adminCount <= 1) {
        return res.status(400).json({ msg: 'Não é possível excluir o último usuário administrador' });
      }
    }
    
    await user.remove();
    
    res.json({ msg: 'Usuário excluído com sucesso' });
  } catch (err) {
    console.error('Error deleting user:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   GET api/users/admin/stats
// @desc    Get admin dashboard statistics
// @access  Admin
router.get('/admin/stats', adminAuth, async (req, res) => {
  try {
    // Get total counts
    const totalUsers = await User.countDocuments();
    const totalScenarios = await Scenario.countDocuments();
    const totalSpreadsheets = await Spreadsheet.countDocuments();
    
    // Get counts for current month
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    
    const usersThisMonth = await User.countDocuments({
      createdAt: { $gte: startOfMonth }
    });
    
    const scenariosThisMonth = await Scenario.countDocuments({
      createdAt: { $gte: startOfMonth }
    });
    
    res.json({
      totalUsers,
      totalScenarios,
      totalSpreadsheets,
      usersThisMonth,
      scenariosThisMonth
    });
  } catch (err) {
    console.error('Error getting admin stats:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

// @route   GET api/users/admin/logs
// @desc    Get system activity logs
// @access  Admin
router.get('/admin/logs', adminAuth, async (req, res) => {
  try {
    // This would typically come from a Log model
    // For now, we'll return a simulated response
    const logs = [
      {
        _id: '1',
        user: {
          _id: req.user.id,
          email: req.user.email
        },
        action: 'LOGIN',
        resource: 'System',
        timestamp: new Date()
      },
      {
        _id: '2',
        user: {
          _id: req.user.id,
          email: req.user.email
        },
        action: 'VIEW_STATS',
        resource: 'Admin Dashboard',
        timestamp: new Date(Date.now() - 1000 * 60 * 10) // 10 minutes ago
      }
    ];
    
    res.json(logs);
  } catch (err) {
    console.error('Error getting activity logs:', err.message);
    res.status(500).json({ msg: 'Erro no servidor' });
  }
});

module.exports = router;