const mongoose = require('mongoose');

const ScenarioSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please add a name'],
    trim: true,
    maxlength: [100, 'Name cannot be more than 100 characters']
  },
  description: {
    type: String,
    maxlength: [500, 'Description cannot be more than 500 characters']
  },
  spreadsheet: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Spreadsheet',
    required: true
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  modifiedAt: {
    type: Date,
    default: Date.now
  },
  isFrozen: {
    type: Boolean,
    default: false
  },
  frozenDate: {
    type: Date
  },
  data: {
    revenues: [{
      name: String,
      values: [Number], // Monthly values
      total: Number,
      isModified: Boolean,
      originalValues: [Number] // Original values from spreadsheet
    }],
    variableExpenses: [{
      name: String,
      values: [Number], // Monthly values
      total: Number,
      isModified: Boolean,
      originalValues: [Number] // Original values from spreadsheet
    }],
    fixedExpenses: [{
      name: String,
      values: [Number], // Monthly values
      total: Number,
      isModified: Boolean,
      originalValues: [Number] // Original values from spreadsheet
    }],
    investments: [{
      name: String,
      values: [Number], // Monthly values
      total: Number,
      isModified: Boolean,
      originalValues: [Number] // Original values from spreadsheet
    }]
  },
  summary: {
    monthlyNetIncome: [Number], // Monthly net income
    annualNetIncome: Number, // Annual net income
    monthlyRevenues: [Number], // Monthly total revenues
    annualRevenues: Number, // Annual total revenues
    monthlyExpenses: [Number], // Monthly total expenses
    annualExpenses: Number, // Annual total expenses
    monthlyInvestments: [Number], // Monthly total investments
    annualInvestments: Number // Annual total investments
  }
});

// Update the modifiedAt field before saving
ScenarioSchema.pre('save', function(next) {
  if (!this.isFrozen) {
    this.modifiedAt = Date.now();
  }
  next();
});

module.exports = mongoose.model('Scenario', ScenarioSchema);