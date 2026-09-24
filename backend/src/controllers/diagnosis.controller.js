const Diagnosis = require('../models/Diagnosis');

exports.listMyDiagnoses = async (req, res, next) => {
  try {
    const items = await Diagnosis.find({ user: req.user._id }).sort({ createdAt: -1 });
    res.json({ success: true, count: items.length, diagnoses: items });
  } catch (err) {
    next(err);
  }
};

exports.getDiagnosis = async (req, res, next) => {
  try {
    const item = await Diagnosis.findOne({ _id: req.params.id, user: req.user._id });
    if (!item) return res.status(404).json({ success: false, error: 'Not found' });
    res.json({ success: true, diagnosis: item });
  } catch (err) {
    next(err);
  }
};

exports.deleteDiagnosis = async (req, res, next) => {
  try {
    const result = await Diagnosis.deleteOne({ _id: req.params.id, user: req.user._id });
    if (result.deletedCount === 0) {
      return res.status(404).json({ success: false, error: 'Not found' });
    }
    res.json({ success: true, message: 'Deleted' });
  } catch (err) {
    next(err);
  }
};
