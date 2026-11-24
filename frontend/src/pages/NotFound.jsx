import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

const NotFound = () => {
  return (
    <div
      style={{
        minHeight: '70vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '2rem',
      }}
    >
      <h1 style={{ fontSize: '4rem', fontWeight: 900, color: 'var(--primary-600)', lineHeight: 1 }}>
        404
      </h1>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--slate-800)', marginTop: '0.5rem' }}>
        Page Not Found
      </h2>
      <p style={{ color: 'var(--slate-500)', maxWidth: '420px', margin: '0.75rem 0 1.5rem' }}>
        The page you are looking for does not exist or may have been moved.
      </p>
      <Link to="/dashboard" className="btn btn-primary">
        <Home size={16} />
        <span>Return to Dashboard</span>
      </Link>
    </div>
  );
};

export default NotFound;
