import React from 'react';
import { Menu, Building2, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const TopNav = ({ onToggleSidebar, title }) => {
  const { user } = useAuth();

  return (
    <header className="top-nav">
      <div className="top-nav-left">
        <button
          type="button"
          className="btn btn-secondary btn-icon-only"
          onClick={onToggleSidebar}
          style={{ display: 'none' }}
          id="mobile-menu-btn"
          aria-label="Toggle menu"
        >
          <Menu size={20} />
        </button>
        <h2 className="page-heading">{title}</h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            backgroundColor: 'var(--slate-100)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.825rem',
            fontWeight: 600,
            color: 'var(--slate-700)',
          }}
        >
          <Building2 size={16} color="var(--primary-600)" />
          <span>Organization #{user?.organization_id || '1'}</span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.85rem',
            color: 'var(--slate-600)',
            fontWeight: 500,
          }}
        >
          <UserIcon size={16} />
          <span>{user?.email}</span>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          #mobile-menu-btn {
            display: inline-flex !important;
          }
        }
      `}</style>
    </header>
  );
};

export default TopNav;
