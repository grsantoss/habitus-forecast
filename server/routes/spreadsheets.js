const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const XLSX = require('xlsx');
const auth = require('../middleware/auth');

const Spreadsheet = require('../models/Spreadsheet');

// Set up multer storage
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = path.join(__dirname, '../uploads');
    // Create directory if it doesn't exist
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(
      null,
      `${req.user.id}-${Date.now()}${path.extname(file.originalname)}`
    );
  },
});

// Check file type
const fileFilter = (req, file, cb) => {
  const filetypes = /xlsx|xls/;
  const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
  const mimetype = filetypes.test(file.mimetype);

  if (mimetype && extname) {
    return cb(null, true);
  } else {
    cb('Error: Excel files only!');
  }
};

// Initialize upload
const upload = multer({
  storage,
  fileFilter,
  limits: { fileSize: 10000000 }, // 10MB limit
});

// Process Excel file
const processExcelFile = (filePath) => {
  try {
    const workbook = XLSX.readFile(filePath);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

    // Initialize categories
    const categories = {
      revenues: [],
      variableExpenses: [],
      fixedExpenses: [],
      investments: [],
    };

    // Process data based on expected format
    // This is a simplified example - adjust based on your actual Excel format
    let currentCategory = null;

    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      
      // Skip empty rows
      if (!row || row.length === 0) continue;
      
      // Check if this is a category header row
      const firstCell = row[0]?.toString().toLowerCase();
      
      if (firstCell?.includes('receita') || firstCell?.includes('entrada')) {
        currentCategory = 'revenues';
        continue;
      } else if (firstCell?.includes('variável') || firstCell?.includes('variavel')) {
        currentCategory = 'variableExpenses';
        continue;
      } else if (firstCell?.includes('fixo')) {
        currentCategory = 'fixedExpenses';
        continue;
      } else if (firstCell?.includes('investimento') || firstCell?.includes('financiamento')) {
        currentCategory = 'investments';
        continue;
      }
      
      // If we have a category and this is a data row
      if (currentCategory && row[0] && typeof row[0] === 'string') {
        const name = row[0];
        const values = [];
        let total = 0;
        
        // Extract monthly values (assuming columns 1-12 are months)
        for (let j = 1; j <= 12; j++) {
          const value = parseFloat(row[j]) || 0;
          values.push(value);
          total += value;
        }
        
        if (values.some(v => v !== 0)) {
          categories[currentCategory].push({
            name,
            values,
            total
          });
        }
      }
    }

    return categories;
  } catch (error) {
    console.error('Error processing Excel file:', error);
    throw new Error('Failed to process Excel file');
  }
};

// @route   POST api/spreadsheets
// @desc    Upload a spreadsheet
// @access  Private
router.post('/', auth, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ msg: 'Please upload a file' });
    }

    // Create new spreadsheet record
    const spreadsheet = new Spreadsheet({
      name: req.body.name || path.parse(req.file.originalname).name,
      originalFilename: req.file.originalname,
      filePath: req.file.path,
      fileSize: req.file.size,
      user: req.user.id,
      status: 'processing'
    });

    await spreadsheet.save();

    // Process the file asynchronously
    try {
      const categories = processExcelFile(req.file.path);
      
      // Update spreadsheet with processed data
      spreadsheet.categories = categories;
      spreadsheet.status = 'processed';
      await spreadsheet.save();
    } catch (error) {
      spreadsheet.status = 'error';
      spreadsheet.errorMessage = error.message;
      await spreadsheet.save();
    }

    res.json(spreadsheet);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route   GET api/spreadsheets
// @desc    Get all spreadsheets for a user
// @access  Private
router.get('/', auth, async (req, res) => {
  try {
    const spreadsheets = await Spreadsheet.find({ user: req.user.id }).sort({
      uploadDate: -1,
    });
    res.json(spreadsheets);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route   GET api/spreadsheets/:id
// @desc    Get spreadsheet by ID
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const spreadsheet = await Spreadsheet.findById(req.params.id);

    if (!spreadsheet) {
      return res.status(404).json({ msg: 'Spreadsheet not found' });
    }

    // Check user
    if (spreadsheet.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(401).json({ msg: 'Not authorized' });
    }

    res.json(spreadsheet);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Spreadsheet not found' });
    }
    res.status(500).send('Server Error');
  }
});

// @route   DELETE api/spreadsheets/:id
// @desc    Delete a spreadsheet
// @access  Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const spreadsheet = await Spreadsheet.findById(req.params.id);

    if (!spreadsheet) {
      return res.status(404).json({ msg: 'Spreadsheet not found' });
    }

    // Check user
    if (spreadsheet.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(401).json({ msg: 'Not authorized' });
    }

    // Delete file from filesystem
    if (fs.existsSync(spreadsheet.filePath)) {
      fs.unlinkSync(spreadsheet.filePath);
    }

    await spreadsheet.remove();

    res.json({ msg: 'Spreadsheet removed' });
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Spreadsheet not found' });
    }
    res.status(500).send('Server Error');
  }
});

module.exports = router;