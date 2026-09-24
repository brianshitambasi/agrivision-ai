import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginUser(form);
      navigate('/diagnose');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
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
          <h1 className="h3 fw-bold mb-1">Welcome back</h1>
          <p className="text-slate-500 small">Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="agri-card p-4">
          {error && (
            <div className="alert alert-danger small py-2">
              <i className="bi bi-exclamation-circle me-1"></i>
              {error}
            </div>
          )}

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

          <div className="mb-4">
            <label className="form-label-agri">Password</label>
            <input
              className="form-control form-control-agri"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <button type="submit" disabled={loading} className="btn-agri-primary w-100 mb-3">
            {loading ? (
              <>
                <span className="agri-spinner me-2"></span>
                Signing in...
              </>
            ) : (
              'Sign in'
            )}
          </button>

          <p className="text-center small text-slate-600 mb-0">
            No account?{' '}
            <Link to="/register" className="text-agri-primary fw-semibold">
              Create one
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login;
