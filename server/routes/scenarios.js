const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const auth = require('../middleware/auth');

const Scenario = require('../models/Scenario');
const Spreadsheet = require('../models/Spreadsheet');

// @route   POST api/scenarios
// @desc    Create a new scenario
// @access  Private
router.post(
  '/',
  [
    auth,
    [
      check('name', 'Name is required').not().isEmpty(),
      check('spreadsheet', 'Spreadsheet ID is required').not().isEmpty()
    ]
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { name, description, spreadsheet } = req.body;

      // Check if spreadsheet exists and belongs to user
      const spreadsheetDoc = await Spreadsheet.findById(spreadsheet);

      if (!spreadsheetDoc) {
        return res.status(404).json({ msg: 'Spreadsheet not found' });
      }

      if (spreadsheetDoc.user.toString() !== req.user.id && req.user.role !== 'admin') {
        return res.status(401).json({ msg: 'Not authorized' });
      }

      // Create scenario with data from spreadsheet
      const scenarioData = {
        name,
        description,
        spreadsheet,
        user: req.user.id,
        data: {
          revenues: spreadsheetDoc.categories.revenues.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          })),
          variableExpenses: spreadsheetDoc.categories.variableExpenses.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          })),
          fixedExpenses: spreadsheetDoc.categories.fixedExpenses.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          })),
          investments: spreadsheetDoc.categories.investments.map(item => ({
            name: item.name,
            values: [...item.values],
            total: item.total,
            isModified: false,
            originalValues: [...item.values]
          }))
        }
      };

      // Calculate summary
      const summary = calculateSummary(scenarioData.data);
      scenarioData.summary = summary;

      const scenario = new Scenario(scenarioData);
      await scenario.save();

      res.json(scenario);
    } catch (err) {
      console.error(err.message);
      res.status(500).send('Server Error');
    }
  }
);

// Helper function to calculate summary
const calculateSummary = (data) => {
  const summary = {
    monthlyNetIncome: Array(12).fill(0),
    annualNetIncome: 0,
    monthlyRevenues: Array(12).fill(0),
    annualRevenues: 0,
    monthlyExpenses: Array(12).fill(0),
    annualExpenses: 0,
    monthlyInvestments: Array(12).fill(0),
    annualInvestments: 0
  };

  // Calculate monthly and annual revenues
  data.revenues.forEach(item => {
    item.values.forEach((value, index) => {
      summary.monthlyRevenues[index] += value;
    });
    summary.annualRevenues += item.total;
  });

  // Calculate monthly and annual expenses (variable + fixed)
  const calculateExpenses = (expenseType) => {
    data[expenseType].forEach(item => {
      item.values.forEach((value, index) => {
        summary.monthlyExpenses[index] += value;
      });
      summary.annualExpenses += item.total;
    });
  };

  calculateExpenses('variableExpenses');
  calculateExpenses('fixedExpenses');

  // Calculate monthly and annual investments
  data.investments.forEach(item => {
    item.values.forEach((value, index) => {
      summary.monthlyInvestments[index] += value;
    });
    summary.annualInvestments += item.total;
  });

  // Calculate monthly and annual net income
  for (let i = 0; i < 12; i++) {
    summary.monthlyNetIncome[i] = summary.monthlyRevenues[i] - summary.monthlyExpenses[i] - summary.monthlyInvestments[i];
  }
  summary.annualNetIncome = summary.annualRevenues - summary.annualExpenses - summary.annualInvestments;

  return summary;
};

// @route   GET api/scenarios
// @desc    Get all scenarios for a user
// @access  Private
router.get('/', auth, async (req, res) => {
  try {
    const scenarios = await Scenario.find({ user: req.user.id }).sort({
      createdAt: -1,
    });
    res.json(scenarios);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route   GET api/scenarios/:id
// @desc    Get scenario by ID
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const scenario = await Scenario.findById(req.params.id);

    if (!scenario) {
      return res.status(404).json({ msg: 'Scenario not found' });
    }

    // Check user
    if (scenario.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(401).json({ msg: 'Not authorized' });
    }

    res.json(scenario);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Scenario not found' });
    }
    res.status(500).send('Server Error');
  }
});

// @route   PUT api/scenarios/:id
// @desc    Update a scenario
// @access  Private
router.put('/:id', auth, async (req, res) => {
  try {
    let scenario = await Scenario.findById(req.params.id);

    if (!scenario) {
      return res.status(404).json({ msg: 'Scenario not found' });
    }

    // Check user
    if (scenario.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(401).json({ msg: 'Not authorized' });
    }

    // Check if scenario is frozen
    if (scenario.isFrozen) {
      return res.status(400).json({ msg: 'Cannot update a frozen scenario' });
    }

    const { name, description, data } = req.body;

    // Update fields
    if (name) scenario.name = name;
    if (description) scenario.description = description;
    if (data) {
      scenario.data = data;
      // Recalculate summary
      scenario.summary = calculateSummary(data);
    }

    await scenario.save();

    res.json(scenario);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Scenario not found' });
    }
    res.status(500).send('Server Error');
  }
});

// @route   PUT api/scenarios/:id/freeze
// @desc    Freeze a scenario
// @access  Private
router.put('/:id/freeze', auth, async (req, res) => {
  try {
    let scenario = await Scenario.findById(req.params.id);

    if (!scenario) {
      return res.status(404).json({ msg: 'Scenario not found' });
    }

    // Check user
    if (scenario.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(401).json({ msg: 'Not authorized' });
    }

    // Freeze scenario
    scenario.isFrozen = true;
    scenario.frozenDate = Date.now();

    await scenario.save();

    res.json(scenario);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Scenario not found' });
    }
    res.status(500).send('Server Error');
  }
});

// @route   DELETE api/scenarios/:id
// @desc    Delete a scenario
// @access  Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const scenario = await Scenario.findById(req.params.id);

    if (!scenario) {
      return res.status(404).json({ msg: 'Scenario not found' });
    }

    // Check user
    if (scenario.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(401).json({ msg: 'Not authorized' });
    }

    await scenario.remove();

    res.json({ msg: 'Scenario removed' });
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Scenario not found' });
    }
    res.status(500).send('Server Error');
  }
});

module.exports = router;