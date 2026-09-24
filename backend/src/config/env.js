const required = ['MONGO_URI', 'JWT_SECRET', 'AI_SERVICE_URL'];

const validateEnv = () => {
  const missing = required.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    console.error(`Missing env vars: ${missing.join(', ')}`);
    process.exit(1);
  }
  console.log('Environment variables validated');
};

module.exports = validateEnv;
