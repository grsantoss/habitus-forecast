const mongoose = require('mongoose');

const SpreadsheetSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please add a name'],
    trim: true,
    maxlength: [100, 'Name cannot be more than 100 characters']
  },
  originalFilename: {
    type: String,
    required: true
  },
  filePath: {
    type: String,
    required: true
  },
  fileSize: {
    type: Number,
    required: true
  },
  uploadDate: {
    type: Date,
    default: Date.now
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  processedData: {
    type: Object,
    default: {}
  },
  categories: {
    revenues: [{
      name: String,
      values: [Number], // Monthly values
      total: Number
    }],
    variableExpenses: [{
      name: String,
      values: [Number], // Monthly values
      total: Number
    }],
    fixedExpenses: [{
      name: String,
      values: [Number], // Monthly values
      total: Number
    }],
    investments: [{
      name: String,
      values: [Number], // Monthly values
      total: Number
    }]
  },
  status: {
    type: String,
    enum: ['uploaded', 'processing', 'processed', 'error'],
    default: 'uploaded'
  },
  errorMessage: {
    type: String
  }
});

module.exports = mongoose.model('Spreadsheet', SpreadsheetSchema);