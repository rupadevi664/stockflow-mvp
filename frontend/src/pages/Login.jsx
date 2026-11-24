import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Boxes, Lock, Mail, ArrowRight, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.friendlyMessage || 'Invalid email or password. Please try again.');
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

        <h2 className="auth-title">Welcome back</h2>
        <p className="auth-subtitle">Sign in to manage your inventory and orders</p>

        {error && (
          <div className="alert alert-danger">
            <AlertCircle size={18} />
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="email">
              Email Address <span className="required">*</span>
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="email"
                type="email"
                className="form-control"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Password <span className="required">*</span>
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="password"
                type="password"
                className="form-control"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem' }}
            disabled={isLoading}
          >
            {isLoading ? (
              'Signing in...'
            ) : (
              <>
                <span>Sign In to Dashboard</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.875rem', color: 'var(--slate-500)' }}>
          Don't have an account?{' '}
          <Link to="/signup" style={{ color: 'var(--primary-600)', fontWeight: 600, textDecoration: 'none' }}>
            Register Organization
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
