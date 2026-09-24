import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="agri-navbar">
      <div className="container">
        <div className="d-flex align-items-center justify-content-between">
          {/* Brand */}
          <Link to="/" className="agri-brand">
            <div className="agri-brand-icon">🌱</div>
            <div className="d-none d-sm-block">
              <div className="agri-brand-text">AgriVision</div>
              <div className="agri-brand-sub">AI Crop Diagnostics</div>
            </div>
          </Link>

          {/* Center nav */}
          {user && (
            <div className="d-none d-md-flex align-items-center gap-1">
              <Link to="/diagnose" className={`agri-nav-link ${isActive('/diagnose')}`}>
                <i className="bi bi-search me-1"></i> Diagnose
              </Link>
              <Link to="/history" className={`agri-nav-link ${isActive('/history')}`}>
                <i className="bi bi-clock-history me-1"></i> History
              </Link>
            </div>
          )}

          {/* User section */}
          <div className="d-flex align-items-center gap-2">
            {user ? (
              <>
                <div className="d-none d-sm-flex align-items-center gap-2">
                  <div className="agri-avatar">
                    {user.name?.charAt(0)?.toUpperCase() || '?'}
                  </div>
                  <div className="d-none d-lg-block lh-sm">
                    <div className="fw-medium small text-slate-900">{user.name}</div>
                    <div className="text-slate-500" style={{ fontSize: '0.7rem' }}>
                      {user.role}
                    </div>
                  </div>
                </div>
                <button onClick={handleLogout} className="btn-agri-ghost">
                  <i className="bi bi-box-arrow-right me-1"></i>
                  <span className="d-none d-sm-inline">Logout</span>
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-agri-ghost">Login</Link>
                <Link to="/register" className="btn-agri-primary">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
