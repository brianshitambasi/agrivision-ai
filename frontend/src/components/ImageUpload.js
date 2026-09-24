import React, { useState } from 'react';

function ImageUpload({ onUpload, loading }) {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);

  const handleChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;

    const ext = (selected.name.split('.').pop() || '').toLowerCase();
    const validExts = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'tif', 'heic', 'heif', 'avif'];
    const isImage = selected.type.startsWith('image/') || validExts.includes(ext);

    if (!isImage) {
      alert('Please upload a valid image file (JPEG, PNG, WebP, GIF, BMP, TIFF, HEIC).');
      return;
    }

    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <input
        type="file"
        accept="image/*,.jpg,.jpeg,.png,.webp,.gif,.bmp,.tiff,.heic,.avif"
        onChange={handleChange}
        disabled={loading}
        style={{ marginBottom: '20px' }}
      />

      {preview && (
        <div style={{ marginBottom: '20px' }}>
          <img
            src={preview}
            alt="Preview"
            style={{
              maxWidth: '300px',
              maxHeight: '300px',
              borderRadius: '8px',
              border: '2px solid #4CAF50',
            }}
          />
        </div>
      )}

      {file && (
        <button
          onClick={() => onUpload(file)}
          disabled={loading}
          style={{
            padding: '12px 30px',
            fontSize: '16px',
            backgroundColor: loading ? '#ccc' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Analyzing...' : 'Diagnose'}
        </button>
      )}
    </div>
  );
}

export default ImageUpload;
