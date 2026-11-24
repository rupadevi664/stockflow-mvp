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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--slate-900)' }}>
            Inventory Overview
          </h2>
          <p style={{ color: 'var(--slate-500)', fontSize: '0.875rem' }}>
            Real-time aggregate stock levels, value analysis, and critical low-stock alerts.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
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
