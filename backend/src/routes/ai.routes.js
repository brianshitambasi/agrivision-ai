const express = require('express');
const multer = require('multer');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');
const { predict } = require('../services/aiService');
const { protect } = require('../middlewares/auth.middleware');
const Diagnosis = require('../models/Diagnosis');

const router = express.Router();

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE) || 5 * 1024 * 1024 },
});

// Optional auth: attach user if token present
const optionalAuth = async (req, res, next) => {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) return next();
  return protect(req, res, next);
};

router.post('/predict', optionalAuth, upload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, error: 'No file uploaded' });
    }

    const result = await predict(
      req.file.buffer,
      req.file.originalname,
      req.file.mimetype
    );

    if (req.user) {
      const filename = `${crypto.randomUUID()}${path.extname(req.file.originalname)}`;
      const uploadPath = path.join(__dirname, '../../uploads', filename);
      fs.writeFileSync(uploadPath, req.file.buffer);

      await Diagnosis.create({
        user: req.user._id,
        imageFilename: filename,
        disease: result.disease,
        confidence: result.confidence,
        topPredictions: result.top_predictions,
        recommendation: result.recommendation,
      });
    }

    res.json(result);
  } catch (err) {
    if (err.response) {
      return res.status(err.response.status).json(err.response.data);
    }
    next(err);
  }
});

module.exports = router;
