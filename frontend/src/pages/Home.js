import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Home() {
  const { user } = useAuth();

  const features = [
    {
      icon: 'bi-cpu',
      title: 'Real ML inference',
      text: 'ResNet18 trained on 14,440 images. Not a mock — real PyTorch predictions.',
    },
    {
      icon: 'bi-diagram-3',
      title: '15 disease classes',
      text: 'Pepper, Potato, and Tomato. Bacterial spots, blights, molds, and viruses.',
    },
    {
      icon: 'bi-lightbulb',
      title: 'Actionable guidance',
      text: 'Symptoms, treatment recommendations, and disclaimers for every diagnosis.',
    },
  ];

  const stats = [
    { value: '88.65%', label: 'Test accuracy' },
    { value: '97.0%', label: 'Acc. when confident' },
    { value: '3,109', label: 'Test images' },
    { value: '15', label: 'Disease classes' },
  ];

  return (
    <>
      {/* Hero */}
      <section className="agri-hero">
        <div className="container">
          <div className="text-center mx-auto" style={{ maxWidth: 720 }}>
            <div className="agri-badge-pill mb-4">
              <span className="agri-badge-dot"></span>
              Real AI · 88.65% test accuracy
            </div>

            <h1 className="display-3 fw-bold text-slate-900 mb-3 lh-1">
              Diagnose crop diseases
              <span className="d-block text-agri-primary">in seconds</span>
            </h1>

            <p className="lead text-slate-600 mb-4">
              Upload a leaf image and get an instant AI-powered diagnosis with treatment
              recommendations. Built for smallholder farmers.
            </p>

            <div className="d-flex flex-column flex-sm-row gap-2 justify-content-center">
              {user ? (
                <Link to="/diagnose" className="btn-agri-primary btn-lg px-4">
                  Start Diagnosing <i className="bi bi-arrow-right ms-1"></i>
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn-agri-primary btn-lg px-4">
                    Get Started Free
                  </Link>
                  <Link to="/login" className="btn-agri-outline btn-lg px-4">
                    Sign In
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container py-5">
        <div className="row g-4">
          {features.map((f, i) => (
            <div key={i} className="col-md-4">
              <div className="agri-card p-4 h-100">
                <div className="agri-feature-icon">
                  <i className={`bi ${f.icon} text-agri-primary`}></i>
                </div>
                <h5 className="fw-bold mb-2">{f.title}</h5>
                <p className="text-slate-600 mb-0 small">{f.text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="container pb-5">
        <div className="agri-card p-4 bg-agri-primary-soft border-0">
          <div className="row text-center g-4">
            {stats.map((s, i) => (
              <div key={i} className="col-6 col-md-3">
                <div className="display-6 fw-bold text-agri-primary mb-1">{s.value}</div>
                <div className="small text-slate-600">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-top py-4 mt-5">
        <div className="container text-center small text-slate-500">
          🌱 AgriVision AI · Empowering smallholder farmers with honest AI diagnostics
        </div>
      </footer>
    </>
  );
}

export default Home;
