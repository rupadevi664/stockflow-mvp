import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopNav from './TopNav';

const pageTitles = {
  '/dashboard': 'Dashboard & Analytics',
  '/products': 'Product Catalog',
  '/stock': 'Stock Operations & Thresholds',
  '/settings': 'Organization Settings',
};

const AppLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const title = pageTitles[location.pathname] || 'Inventory Management';

  return (
    <div className="app-container">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.4)',
            zIndex: 35,
          }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="main-wrapper">
        <TopNav
          title={title}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
        <main className="content-viewport">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
