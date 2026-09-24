import React from 'react';

function DiagnosisCard({ result }) {
  if (!result) return null;

  const confidence = (result.confidence * 100).toFixed(1);
  const isLow = !result.is_confident;
  const isUnknown = result.disease === 'Unknown / Low Confidence';

  return (
    <div className={`agri-card mt-4 overflow-hidden border-2 ${isLow ? 'border-warning' : 'border-success'}`}>
      {/* Header */}
      <div className={`agri-result-header ${isLow ? 'low' : 'high'}`}>
        <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
          <div className="d-flex align-items-center gap-3">
            <div
              className={`rounded-3 d-flex align-items-center justify-content-center ${
                isLow ? 'bg-warning-subtle' : 'bg-success-subtle'
              }`}
              style={{ width: 52, height: 52, fontSize: '1.5rem' }}
            >
              {isLow ? '⚠️' : '🔬'}
            </div>
            <div>
              <div
                className={`text-uppercase fw-bold small ${
                  isLow ? 'text-warning-emphasis' : 'text-success-emphasis'
                }`}
                style={{ letterSpacing: '0.05em' }}
              >
                {isLow ? 'Low Confidence' : 'Diagnosis Result'}
              </div>
              <div className="fw-bold fs-5">
                {isUnknown ? 'Not Identified' : result.disease}
              </div>
            </div>
          </div>
          <div className="text-end">
            <div
              className={`agri-confidence-badge ${
                isLow ? 'text-warning-emphasis' : 'text-success-emphasis'
              }`}
            >
              {confidence}%
            </div>
            <div className="small text-slate-500">model confidence</div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-4">
        {/* Crop */}
        {!isUnknown && result.crop && result.crop !== 'Unknown' && (
          <div className="mb-3 small">
            <span className="text-slate-500">Crop: </span>
            <span className="fw-semibold">{result.crop}</span>
          </div>
        )}

        {/* Top predictions */}
        {result.top_predictions && result.top_predictions.length > 0 && (
          <div className="mb-4">
            <div className="fw-semibold small mb-3">Top 3 Candidates</div>
            {result.top_predictions.map((p, i) => {
              const pct = (p.confidence * 100).toFixed(1);
              const name = p.label.replace(/___/g, ' ').replace(/_/g, ' ');
              return (
                <div key={i} className="mb-2">
                  <div className="d-flex justify-content-between small mb-1">
                    <span className={i === 0 ? 'fw-semibold' : 'text-slate-600'}>{name}</span>
                    <span className={i === 0 ? 'fw-bold text-agri-primary' : 'text-slate-500'}>
                      {pct}%
                    </span>
                  </div>
                  <div className="agri-progress">
                    <div
                      className={`agri-progress-bar ${
                        i === 0 ? 'bg-success' : 'bg-secondary'
                      }`}
                      style={{ width: `${p.confidence * 100}%`, opacity: i === 0 ? 1 : 0.4 }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Symptoms */}
        {result.symptoms && result.symptoms.length > 0 && (
          <div className="rounded-3 bg-light p-3 mb-3 border">
            <div className="fw-semibold small mb-2">
              <i className="bi bi-search text-agri-primary me-1"></i> Observed Symptoms
            </div>
            <ul className="list-unstyled mb-0 small">
              {result.symptoms.map((s, i) => (
                <li key={i} className="d-flex gap-2 mb-1">
                  <i className="bi bi-dot text-agri-primary"></i>
                  <span className="text-slate-600">{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommendation */}
        <div className={`rounded-3 p-3 mb-3 ${isLow ? 'bg-warning-subtle' : 'bg-success-subtle'}`}>
          <div className={`fw-semibold small mb-2 ${isLow ? 'text-warning-emphasis' : 'text-success-emphasis'}`}>
            <i className="bi bi-lightbulb me-1"></i>
            {isLow ? 'What to do' : 'Recommended Action'}
          </div>
          <p className="small mb-0 text-slate-600">{result.recommendation}</p>
        </div>

        {/* Disclaimer */}
        <div className="border-start border-4 border-secondary-subtle ps-3 py-2">
          <p className="small text-slate-500 mb-0">
            <strong className="text-slate-700">
              <i className="bi bi-exclamation-triangle me-1"></i>Disclaimer:
            </strong>{' '}
            {result.disclaimer}
          </p>
        </div>
      </div>
    </div>
  );
}

export default DiagnosisCard;
