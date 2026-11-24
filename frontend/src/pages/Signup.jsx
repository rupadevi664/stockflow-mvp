import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Boxes, Building2, User, Mail, Lock, ArrowRight, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Signup = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    organization_name: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (!formData.organization_name.trim()) {
      setError('Organization name is required.');
      return;
    }

    setIsLoading(true);

    try {
      await signup(formData);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.friendlyMessage || 'Registration failed. Please verify your details.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="brand-icon">
            <Boxes size={22} />
          </div>
          <span style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--slate-900)' }}>
            StockFlow
          </span>
        </div>

        <h2 className="auth-title">Create your workspace</h2>
        <p className="auth-subtitle">Get started with multi-tenant inventory control</p>

        {error && (
          <div className="alert alert-danger">
            <AlertCircle size={18} />
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="organization_name">
              Organization Name <span className="required">*</span>
            </label>
            <input
              id="organization_name"
              name="organization_name"
              type="text"
              className="form-control"
              placeholder="e.g. Acme Logistics Corp"
              value={formData.organization_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="name">
              Your Full Name <span className="required">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              className="form-control"
              placeholder="e.g. Jane Doe"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">
              Work Email <span className="required">*</span>
            </label>
            <input
              id="email"
              name="email"
              type="email"
              className="form-control"
              placeholder="jane@acme.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Password (min. 6 chars) <span className="required">*</span>
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-control"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem' }}
            disabled={isLoading}
          >
            {isLoading ? (
              'Creating account...'
            ) : (
              <>
                <span>Complete Registration</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.875rem', color: 'var(--slate-500)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--primary-600)', fontWeight: 600, textDecoration: 'none' }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;
