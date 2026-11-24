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
          id="mobile-menu-btn"
          aria-label="Toggle menu"
        >
          <Menu size={20} />
        </button>
        <h2 className="page-heading" title={title}>{title}</h2>
      </div>

      <div className="top-nav-right">
        <div className="org-badge">
          <Building2 size={15} color="var(--primary-600)" />
          <span>Org #{user?.organization_id || '1'}</span>
        </div>

        <div className="user-nav-info">
          <UserIcon size={15} />
          <span className="user-email-text">{user?.email}</span>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
