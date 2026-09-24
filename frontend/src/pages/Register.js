import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', location: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { registerUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await registerUser(form);
      navigate('/diagnose');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light py-5 px-3">
      <div style={{ width: '100%', maxWidth: 440 }}>
        <div className="text-center mb-4">
          <div
            className="mx-auto rounded-3 mb-3 d-flex align-items-center justify-content-center"
            style={{
              width: 64,
              height: 64,
              background: 'linear-gradient(135deg, #22c55e, #15803d)',
              fontSize: '1.75rem',
              boxShadow: '0 4px 12px rgba(34, 197, 94, 0.25)',
            }}
          >
            🌱
          </div>
          <h1 className="h3 fw-bold mb-1">Create your account</h1>
          <p className="text-slate-500 small">Start diagnosing crops in seconds</p>
        </div>

        <form onSubmit={handleSubmit} className="agri-card p-4">
          {error && (
            <div className="alert alert-danger small py-2">
              <i className="bi bi-exclamation-circle me-1"></i>
              {error}
            </div>
          )}

          <div className="mb-3">
            <label className="form-label-agri">Full name</label>
            <input
              className="form-control form-control-agri"
              placeholder="John Doe"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label-agri">Email</label>
            <input
              className="form-control form-control-agri"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label-agri">Password</label>
            <input
              className="form-control form-control-agri"
              type="password"
              placeholder="At least 6 characters"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={6}
            />
          </div>

          <div className="mb-4">
            <label className="form-label-agri">
              Location <span className="text-slate-500 fw-normal">(optional)</span>
            </label>
            <input
              className="form-control form-control-agri"
              placeholder="Nairobi, Kenya"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
            />
          </div>

          <button type="submit" disabled={loading} className="btn-agri-primary w-100 mb-3">
            {loading ? (
              <>
                <span className="agri-spinner me-2"></span>
                Creating account...
              </>
            ) : (
              'Create account'
            )}
          </button>

          <p className="text-center small text-slate-600 mb-0">
            Already have an account?{' '}
            <Link to="/login" className="text-agri-primary fw-semibold">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Register;
