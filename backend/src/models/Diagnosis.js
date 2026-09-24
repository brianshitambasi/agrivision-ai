const mongoose = require('mongoose');

const diagnosisSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    imageFilename: { type: String, required: true },
    disease: { type: String, required: true },
    confidence: { type: Number, required: true },
    topPredictions: [
      {
        label: String,
        confidence: Number,
      },
    ],
    recommendation: { type: String, default: '' },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Diagnosis', diagnosisSchema);
