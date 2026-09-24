require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');

const connectDB = require('./config/db');
const validateEnv = require('./config/env');
const { errorHandler, notFound } = require('./middlewares/error.middleware');

const authRoutes = require('./routes/auth.routes');
const aiRoutes = require('./routes/ai.routes');
const diagnosisRoutes = require('./routes/diagnosis.routes');
const adminRoutes = require('./routes/admin.routes');

validateEnv();
connectDB();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(helmet({ crossOriginResourcePolicy: false }));
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(morgan('dev'));

app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

app.use('/api/auth', authRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/diagnoses', diagnosisRoutes);
app.use('/api/admin', adminRoutes);

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'agrivision-backend', version: '1.0.0' });
});

app.get('/', (req, res) => {
  res.json({
    service: 'AgriVision AI Backend',
    version: '1.0.0',
    endpoints: {
      auth: ['/api/auth/register', '/api/auth/login', '/api/auth/me'],
      ai: ['/api/ai/predict'],
      diagnoses: ['/api/diagnoses', '/api/diagnoses/:id'],
      admin: ['/api/admin/stats'],
    },
  });
});

app.use(notFound);
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
  console.log(`AI service: ${process.env.AI_SERVICE_URL}`);
});
