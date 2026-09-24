const express = require('express');
const { listMyDiagnoses, getDiagnosis, deleteDiagnosis } = require('../controllers/diagnosis.controller');
const { protect } = require('../middlewares/auth.middleware');

const router = express.Router();
router.use(protect);

router.get('/', listMyDiagnoses);
router.get('/:id', getDiagnosis);
router.delete('/:id', deleteDiagnosis);

module.exports = router;
