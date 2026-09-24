import React, { useState, useEffect } from 'react';
import { getDiagnoses, deleteDiagnosis } from '../services/api';

function History() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const res = await getDiagnoses();
      setItems(res.data.diagnoses || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this diagnosis?')) return;
    await deleteDiagnosis(id);
    load();
  };

  const filtered = items.filter((item) =>
    item.disease.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="container py-5" style={{ maxWidth: 1000 }}>
      <div className="d-flex justify-content-between align-items-end flex-wrap gap-3 mb-4">
        <div>
          <h1 className="fw-bold mb-1">Diagnosis History</h1>
          <p className="text-slate-600 mb-0">
            {items.length} {items.length === 1 ? 'record' : 'records'} saved
          </p>
        </div>
        {items.length > 0 && (
          <div style={{ minWidth: 240 }}>
            <input
              className="form-control form-control-agri"
              placeholder="🔍 Search diseases..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        )}
      </div>

      {loading ? (
        <div className="agri-card p-5 text-center">
          <div className="agri-spinner text-agri-primary mb-3" style={{ width: 32, height: 32, borderWidth: 3 }}></div>
          <p className="text-slate-600 mb-0">Loading history...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="agri-card p-5 text-center">
          <div style={{ fontSize: '3rem' }} className="mb-3">📋</div>
          <h5 className="fw-bold mb-2">No diagnoses yet</h5>
          <p className="text-slate-500 mb-0 small">
            Upload a leaf image in the Diagnose tab to get started.
          </p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="agri-card p-5 text-center">
          <p className="text-slate-600 mb-0">No results for "{filter}"</p>
        </div>
      ) : (
        <div className="d-flex flex-column gap-3">
          {filtered.map((item) => {
            const conf = (item.confidence * 100).toFixed(1);
            const low = item.confidence < 0.7;
            return (
              <div key={item._id} className="agri-card p-4">
                <div className="d-flex justify-content-between align-items-start gap-3">
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-center gap-2 mb-2 flex-wrap">
                      <h6 className="fw-bold mb-0">{item.disease}</h6>
                      <span className={`badge ${low ? 'bg-warning-subtle text-warning-emphasis' : 'bg-success-subtle text-success-emphasis'}`}>
                        {conf}% confidence
                      </span>
                    </div>
                    <div className="small text-slate-500">
                      <i className="bi bi-clock me-1"></i>
                      {new Date(item.createdAt).toLocaleString()}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(item._id)}
                    className="btn btn-sm btn-outline-danger"
                    title="Delete"
                  >
                    <i className="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default History;
