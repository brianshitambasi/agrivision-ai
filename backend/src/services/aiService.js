const axios = require('axios');
const FormData = require('form-data');

const predict = async (fileBuffer, filename, mimetype) => {
  const form = new FormData();
  form.append('file', fileBuffer, { filename, contentType: mimetype });

  const response = await axios.post(
    `${process.env.AI_SERVICE_URL}/api/predict`,
    form,
    { headers: form.getHeaders(), timeout: 30000 }
  );
  return response.data;
};

module.exports = { predict };
