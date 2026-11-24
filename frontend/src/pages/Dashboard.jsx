import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Package, 
  Layers, 
  DollarSign, 
  AlertTriangle, 
  AlertOctagon, 
  RefreshCw, 
  Plus, 
  ArrowRight,
  TrendingUp,
  Boxes
} from 'lucide-react';
import { dashboardApi } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Toast from '../components/common/Toast';
import StockModal from '../components/stock/StockModal';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [lowStockList, setLowStockList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedProductForStock, setSelectedProductForStock] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const [summaryData, lowStockData] = await Promise.all([
        dashboardApi.getSummary(),
        dashboardApi.getLowStock(),
      ]);
      setSummary(summaryData);
      setLowStockList(lowStockData || []);
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load dashboard metrics.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const formatCurrency = (val) => {
    const num = Number(val) || 0;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(num);
  };

  if (isLoading && !summary) {
    return <LoadingSpinner size="large" text="Calculating inventory metrics..." />;
  }

  return (
    <div>
      {/* Top Banner & Quick Controls */}
      <div className="dashboard-header-container">
        <div>
          <h2 className="dashboard-main-heading">
            Inventory Overview
          </h2>
          <p className="dashboard-sub-heading">
            Real-time aggregate stock levels and reorder alerts.
          </p>
        </div>

        <div className="dashboard-action-buttons">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={fetchDashboardData}
            title="Refresh metrics"
          >
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
          <Link to="/products" className="btn btn-primary">
            <Plus size={16} />
            <span>Manage Products</span>
          </Link>
        </div>
      </div>

      {error && <Toast type="danger" message={error} onClose={() => setError('')} />}

      {/* KPI Cards Grid */}
      <div className="stats-grid">
        {/* 1. Total Products */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Total Products</span>
            <div className="stat-icon primary">
              <Package size={20} />
            </div>
          </div>
          <div className="stat-value">{summary?.total_products ?? 0}</div>
          <div className="stat-footer">Unique items cataloged</div>
        </div>

        {/* 2. Total Stock Units */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Total Units In Stock</span>
            <div className="stat-icon success">
              <Layers size={20} />
            </div>
          </div>
          <div className="stat-value">{summary?.total_stock_quantity ?? 0}</div>
          <div className="stat-footer">Cumulative warehouse units</div>
        </div>

        {/* 3. Total Inventory Value */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Total Inventory Value</span>
            <div className="stat-icon primary">
              <DollarSign size={20} />
            </div>
          </div>
          <div className="stat-value" style={{ color: 'var(--primary-700)', fontSize: '1.6rem' }}>
            {formatCurrency(summary?.total_inventory_value)}
          </div>
          <div className="stat-footer">Based on price × quantity</div>
        </div>

        {/* 4. Low Stock Products */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Low Stock Items</span>
            <div className="stat-icon warning">
              <AlertTriangle size={20} />
            </div>
          </div>
          <div className="stat-value" style={{ color: summary?.low_stock_products > 0 ? 'var(--amber-600)' : 'var(--slate-800)' }}>
            {summary?.low_stock_products ?? 0}
          </div>
          <div className="stat-footer">At or below threshold</div>
        </div>

        {/* 5. Out of Stock Products */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Out of Stock</span>
            <div className="stat-icon danger">
              <AlertOctagon size={20} />
            </div>
          </div>
          <div className="stat-value" style={{ color: summary?.out_of_stock_products > 0 ? 'var(--rose-600)' : 'var(--slate-800)' }}>
            {summary?.out_of_stock_products ?? 0}
          </div>
          <div className="stat-footer">Quantity equals 0</div>
        </div>
      </div>

      {/* Critical Stock Alerts Table */}
      <div className="content-card">
        <div className="card-header">
          <div className="card-title">
            <AlertTriangle size={20} color="var(--amber-600)" />
            <span>Low-Stock & Out-of-Stock Alerts</span>
            <span className="badge badge-low-stock" style={{ marginLeft: '0.5rem' }}>
              {lowStockList.length} items need attention
            </span>
          </div>

          <Link to="/stock" className="btn btn-secondary btn-sm">
            <span>View All Stock</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        <div className="table-responsive">
          {lowStockList.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon" style={{ backgroundColor: 'var(--emerald-50)', color: 'var(--emerald-600)' }}>
                <TrendingUp size={28} />
              </div>
              <h3 className="empty-state-title">All stock levels healthy!</h3>
              <p className="empty-state-desc">
                None of your products are at or below their low-stock thresholds right now.
              </p>
            </div>
          ) : (
            <>
              {/* Desktop View: Full Table */}
              <div className="desktop-only">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Product Name</th>
                      <th>Current Stock</th>
                      <th>Low-Stock Threshold</th>
                      <th>Unit Price</th>
                      <th>Status</th>
                      <th style={{ textAlign: 'right' }}>Quick Restock</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lowStockList.map((product) => (
                      <tr key={product.id}>
                        <td>
                          <span className="sku-badge">{product.sku}</span>
                        </td>
                        <td>
                          <div style={{ fontWeight: 600, color: 'var(--slate-900)' }}>{product.name}</div>
                          {product.description && (
                            <div style={{ fontSize: '0.775rem', color: 'var(--slate-500)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {product.description}
                            </div>
                          )}
                        </td>
                        <td>
                          <span style={{ fontWeight: 700, fontSize: '0.95rem', color: product.quantity === 0 ? 'var(--rose-600)' : 'var(--amber-600)' }}>
                            {product.quantity} units
                          </span>
                        </td>
                        <td>{product.low_stock_threshold} units</td>
                        <td>{formatCurrency(product.price)}</td>
                        <td>
                          {product.quantity === 0 ? (
                            <span className="badge badge-out-of-stock">Out of Stock</span>
                          ) : (
                            <span className="badge badge-low-stock">Low Stock</span>
                          )}
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <button
                            type="button"
                            className="btn btn-primary btn-sm"
                            onClick={() => setSelectedProductForStock(product)}
                          >
                            <Plus size={14} />
                            <span>Restock</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile View: High-End Restock Cards */}
              <div className="mobile-only mobile-card-list">
                {lowStockList.map((product) => (
                  <div key={product.id} className="mobile-product-card">
                    <div className="mobile-card-header">
                      <div>
                        <span className="sku-badge">{product.sku}</span>
                        <h4 className="mobile-card-name">{product.name}</h4>
                      </div>
                      {product.quantity === 0 ? (
                        <span className="badge badge-out-of-stock">Out of Stock</span>
                      ) : (
                        <span className="badge badge-low-stock">Low Stock</span>
                      )}
                    </div>

                    <div className="mobile-card-stats" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
                      <div className="mobile-stat-col">
                        <span className="mobile-stat-label">In Stock</span>
                        <span
                          className="mobile-stat-value"
                          style={{
                            color: product.quantity === 0 ? 'var(--rose-600)' : 'var(--amber-600)',
                            fontWeight: 800
                          }}
                        >
                          {product.quantity}
                        </span>
                      </div>
                      <div className="mobile-stat-col">
                        <span className="mobile-stat-label">Threshold</span>
                        <span className="mobile-stat-value">{product.low_stock_threshold}</span>
                      </div>
                      <div className="mobile-stat-col">
                        <span className="mobile-stat-label">Price</span>
                        <span className="mobile-stat-value">{formatCurrency(product.price)}</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      className="btn btn-primary"
                      style={{ width: '100%', marginTop: '0.25rem', padding: '0.65rem' }}
                      onClick={() => setSelectedProductForStock(product)}
                    >
                      <Plus size={16} />
                      <span>Restock Item Now</span>
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Stock Increase Modal */}
      {selectedProductForStock && (
        <StockModal
          isOpen={!!selectedProductForStock}
          product={selectedProductForStock}
          onClose={() => setSelectedProductForStock(null)}
          onSuccess={() => {
            fetchDashboardData();
          }}
        />
      )}
    </div>
  );
};

export default Dashboard;
