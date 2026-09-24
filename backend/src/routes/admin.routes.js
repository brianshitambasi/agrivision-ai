const express = require('express');
const User = require('../models/User');
const Diagnosis = require('../models/Diagnosis');
const { protect, adminOnly } = require('../middlewares/auth.middleware');

const router = express.Router();
router.use(protect, adminOnly);

router.get('/stats', async (req, res, next) => {
  try {
    const [users, diagnoses] = await Promise.all([
      User.countDocuments(),
      Diagnosis.countDocuments(),
    ]);

    const topDiseases = await Diagnosis.aggregate([
      { $group: { _id: '$disease', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 5 },
    ]);

    res.json({ success: true, users, diagnoses, topDiseases });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
