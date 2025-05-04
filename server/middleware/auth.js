const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Protect routes
module.exports = async function(req, res, next) {
  let token;

  // Check if auth header exists and starts with Bearer
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith('Bearer')
  ) {
    // Set token from Bearer token in header
    token = req.headers.authorization.split(' ')[1];
  }

  // Check if token exists
  if (!token) {
    return res.status(401).json({ msg: 'No token, authorization denied' });
  }

  try {
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Set user from payload
    req.user = await User.findById(decoded.id);

    next();
  } catch (err) {
    res.status(401).json({ msg: 'Token is not valid' });
  }
};