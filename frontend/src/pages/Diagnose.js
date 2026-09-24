import React, { useState, useRef } from 'react';
import DiagnosisCard from '../components/DiagnosisCard';
import { predictImage } from '../services/api';

function Diagnose() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleFile = (selected) => {
    if (!selected) return;
    const ext = (selected.name.split('.').pop() || '').toLowerCase();
    const validExts = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'tif', 'heic', 'heif', 'avif'];
    const isImage = selected.type.startsWith('image/') || validExts.includes(ext);

    if (!isImage) {
      setError('Please upload a valid image file (JPEG, PNG, WebP, GIF, BMP, TIFF).');
      return;
    }

    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError(null);
    setResult(null);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await predictImage(file);
      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to analyze image. Is the backend running?'
      );
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="container py-5" style={{ maxWidth: 900 }}>
      <div className="text-center mb-5">
        <h1 className="fw-bold text-slate-900 mb-2">Diagnose Your Crop</h1>
        <p className="text-slate-600">Upload a leaf image and get an instant AI diagnosis.</p>
      </div>

      {/* Upload Zone */}
      {!file && (
        <div
          className={`agri-upload-zone ${dragOver ? 'dragover' : ''}`}
          onClick={() => inputRef.current?.click()}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFile(e.dataTransfer.files[0]);
          }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*,.jpg,.jpeg,.png,.webp,.gif,.bmp,.tiff,.heic,.avif"
            onChange={(e) => handleFile(e.target.files[0])}
            hidden
          />
          <div className="agri-upload-icon">
            <i className="bi bi-cloud-arrow-up text-agri-primary"></i>
          </div>
          <h5 className="fw-bold mb-1">
            {dragOver ? 'Drop image here' : 'Click or drag image to upload'}
          </h5>
          <p className="text-slate-500 small mb-0">
            JPEG, PNG, WebP, GIF, BMP, TIFF · Max 10 MB
          </p>
        </div>
      )}

      {/* Preview + Submit */}
      {file && (
        <div className="agri-card p-4">
          <div className="row g-4 align-items-center">
            <div className="col-md-4">
              <img
                src={preview}
                alt="Preview"
                className="img-fluid rounded-3 border"
                style={{ aspectRatio: '1 / 1', objectFit: 'cover' }}
              />
            </div>
            <div className="col-md-8">
              <div className="mb-3">
                <div className="text-slate-500 small mb-1">Selected file</div>
                <div className="fw-medium text-break">{file.name}</div>
                <div className="text-slate-500 small mt-1">
                  {(file.size / 1024).toFixed(1)} KB
                </div>
              </div>

              <div className="d-flex gap-2">
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="btn-agri-primary flex-grow-1"
                >
                  {loading ? (
                    <>
                      <span className="agri-spinner me-2"></span>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-search me-1"></i> Diagnose
                    </>
                  )}
                </button>
                <button onClick={reset} disabled={loading} className="btn-agri-outline">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="alert alert-danger mt-4 d-flex align-items-center">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
        </div>
      )}

      {/* Result */}
      {result && <DiagnosisCard result={result} />}
    </div>
  );
}

export default Diagnose;
