import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  ArrowUpCircle, 
  ArrowDownCircle, 
  AlertTriangle, 
  Search, 
  RefreshCw,
  TrendingDown,
  Package
} from 'lucide-react';
import { productsApi, stockApi } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Toast from '../components/common/Toast';
import StockModal from '../components/stock/StockModal';

const Stock = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all'); // 'all', 'low', 'out'
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [adjustingProduct, setAdjustingProduct] = useState(null);

  const fetchStockData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await productsApi.getAll({ skip: 0, limit: 100 });
      setProducts(data);
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load stock data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStockData();
  }, []);

  // Filter products by tab and search
  useEffect(() => {
    let result = products;

    if (activeFilter === 'low') {
      result = result.filter(
        (p) => p.quantity <= p.low_stock_threshold && p.quantity > 0
      );
    } else if (activeFilter === 'out') {
      result = result.filter((p) => p.quantity === 0);
    }

    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (p) => p.name.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q)
      );
    }

    setFilteredProducts(result);
  }, [products, activeFilter, searchQuery]);

  const lowCount = products.filter(
    (p) => p.quantity <= p.low_stock_threshold && p.quantity > 0
  ).length;
  const outCount = products.filter((p) => p.quantity === 0).length;

  return (
    <div>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--slate-900)' }}>
            Stock Operations & Adjustments
          </h2>
          <p style={{ color: 'var(--slate-500)', fontSize: '0.875rem' }}>
            Safely increase or deduct inventory levels with concurrency safeguards and low-stock tracking.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={fetchStockData}
          title="Reload stock"
        >
          <RefreshCw size={16} />
          <span>Refresh Levels</span>
        </button>
      </div>

      {successMsg && <Toast type="success" message={successMsg} onClose={() => setSuccessMsg('')} />}
      {error && <Toast type="danger" message={error} onClose={() => setError('')} />}

      {/* Filter Tabs and Search Bar */}
      <div className="content-card" style={{ marginBottom: '1.25rem' }}>
        <div
          style={{
            padding: '1rem 1.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          {/* Tabs */}
          <div className="tabs-scroll-container">
            <button
              type="button"
              className={`btn btn-sm ${activeFilter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveFilter('all')}
            >
              All Items ({products.length})
            </button>
            <button
              type="button"
              className={`btn btn-sm ${activeFilter === 'low' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveFilter('low')}
            >
              Low Stock ({lowCount})
            </button>
            <button
              type="button"
              className={`btn btn-sm ${activeFilter === 'out' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveFilter('out')}
            >
              Out of Stock ({outCount})
            </button>
          </div>

          {/* Search */}
          <div className="stock-search-wrapper" style={{ position: 'relative' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Filter by name or SKU..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '2.5rem' }}
            />
            <Search
              size={18}
              color="var(--slate-400)"
              style={{
                position: 'absolute',
                left: '0.85rem',
                top: '50%',
                transform: 'translateY(-50%)',
              }}
            />
          </div>
        </div>
      </div>

      {/* Stock Table */}
      <div className="content-card">
        <div className="table-responsive">
          {isLoading ? (
            <LoadingSpinner size="medium" text="Syncing stock levels..." />
          ) : filteredProducts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">
                <Package size={28} />
              </div>
              <h3 className="empty-state-title">No matching stock records</h3>
              <p className="empty-state-desc">
                {activeFilter === 'low'
                  ? 'No products are currently running low.'
                  : activeFilter === 'out'
                  ? 'No products are completely out of stock.'
                  : 'No inventory items match your current filter.'}
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
                      <th>Threshold</th>
                      <th>Current Stock</th>
                      <th>Status</th>
                      <th style={{ textAlign: 'right' }}>Quick Adjust</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.map((p) => {
                      const isLow = p.quantity <= p.low_stock_threshold && p.quantity > 0;
                      const isOut = p.quantity === 0;

                      return (
                        <tr key={p.id}>
                          <td>
                            <span className="sku-badge">{p.sku}</span>
                          </td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'var(--slate-900)' }}>{p.name}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--slate-500)' }}>
                              ID #{p.id}
                            </div>
                          </td>
                          <td>
                            <span style={{ color: 'var(--slate-600)', fontWeight: 500 }}>
                              {p.low_stock_threshold} units
                            </span>
                          </td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <span
                                style={{
                                  fontSize: '1.1rem',
                                  fontWeight: 800,
                                  color: isOut
                                    ? 'var(--rose-600)'
                                    : isLow
                                    ? 'var(--amber-600)'
                                    : 'var(--emerald-600)',
                                }}
                              >
                                {p.quantity}
                              </span>
                              <span style={{ fontSize: '0.8rem', color: 'var(--slate-500)' }}>units</span>
                            </div>
                          </td>
                          <td>
                            {isOut ? (
                              <span className="badge badge-out-of-stock">Out of Stock</span>
                            ) : isLow ? (
                              <span className="badge badge-low-stock">Low Stock</span>
                            ) : (
                              <span className="badge badge-in-stock">In Stock</span>
                            )}
                          </td>
                          <td style={{ textAlign: 'right' }}>
                            <button
                              type="button"
                              className="btn btn-primary btn-sm"
                              onClick={() => setAdjustingProduct(p)}
                            >
                              <Layers size={14} />
                              <span>Adjust Stock</span>
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Mobile View: High-End Stock Cards */}
              <div className="mobile-only mobile-card-list">
                {filteredProducts.map((p) => {
                  const isLow = p.quantity <= p.low_stock_threshold && p.quantity > 0;
                  const isOut = p.quantity === 0;

                  return (
                    <div key={p.id} className="mobile-product-card">
                      <div className="mobile-card-header">
                        <div>
                          <span className="sku-badge">{p.sku}</span>
                          <h4 className="mobile-card-name">{p.name}</h4>
                        </div>
                        {isOut ? (
                          <span className="badge badge-out-of-stock">Out of Stock</span>
                        ) : isLow ? (
                          <span className="badge badge-low-stock">Low Stock</span>
                        ) : (
                          <span className="badge badge-in-stock">In Stock</span>
                        )}
                      </div>

                      <div className="mobile-card-stats" style={{ gridTemplateColumns: '1fr 1fr' }}>
                        <div className="mobile-stat-col">
                          <span className="mobile-stat-label">Current Stock</span>
                          <span
                            className="mobile-stat-value"
                            style={{
                              fontSize: '1.25rem',
                              color: isOut ? 'var(--rose-600)' : isLow ? 'var(--amber-600)' : 'var(--emerald-600)',
                            }}
                          >
                            {p.quantity} units
                          </span>
                        </div>
                        <div className="mobile-stat-col">
                          <span className="mobile-stat-label">Threshold</span>
                          <span className="mobile-stat-value" style={{ fontSize: '1.1rem' }}>
                            {p.low_stock_threshold} units
                          </span>
                        </div>
                      </div>

                      <button
                        type="button"
                        className="btn btn-primary"
                        style={{ width: '100%', marginTop: '0.25rem', padding: '0.65rem' }}
                        onClick={() => setAdjustingProduct(p)}
                      >
                        <Layers size={16} />
                        <span>Adjust Stock (+ / -)</span>
                      </button>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Stock Adjustment Modal */}
      {adjustingProduct && (
        <StockModal
          isOpen={!!adjustingProduct}
          product={adjustingProduct}
          onClose={() => setAdjustingProduct(null)}
          onSuccess={() => {
            setSuccessMsg(`Stock levels updated successfully for ${adjustingProduct.name}.`);
            fetchStockData();
          }}
        />
      )}
    </div>
  );
};

export default Stock;
