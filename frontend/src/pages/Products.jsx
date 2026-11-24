import React, { useState, useEffect, useCallback } from 'react';
import { 
  Package, 
  Plus, 
  Search, 
  Edit2, 
  Trash2, 
  Layers, 
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Filter
} from 'lucide-react';
import { productsApi } from '../services/api';
import Modal from '../components/common/Modal';
import Toast from '../components/common/Toast';
import LoadingSpinner from '../components/common/LoadingSpinner';
import StockModal from '../components/stock/StockModal';

const ITEMS_PER_PAGE = 10;

const Products = () => {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Search & Pagination
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0); // skip = page * ITEMS_PER_PAGE
  const [hasMore, setHasMore] = useState(false);

  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [deletingProduct, setDeletingProduct] = useState(null);
  const [adjustingStockProduct, setAdjustingStockProduct] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    description: '',
    price: '',
    quantity: '0',
    low_stock_threshold: '5',
  });
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchProducts = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const skip = page * ITEMS_PER_PAGE;
      const data = await productsApi.getAll({
        skip,
        limit: ITEMS_PER_PAGE + 1, // Fetch 1 extra to check if next page exists
        search: searchTerm,
      });

      if (data.length > ITEMS_PER_PAGE) {
        setHasMore(true);
        setProducts(data.slice(0, ITEMS_PER_PAGE));
      } else {
        setHasMore(false);
        setProducts(data);
      }
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to fetch products.');
    } finally {
      setIsLoading(false);
    }
  }, [page, searchTerm]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchProducts();
  };

  const resetForm = () => {
    setFormData({
      name: '',
      sku: '',
      description: '',
      price: '',
      quantity: '0',
      low_stock_threshold: '5',
    });
    setFormError('');
  };

  const openAddModal = () => {
    resetForm();
    setIsAddModalOpen(true);
  };

  const openEditModal = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      sku: product.sku,
      description: product.description || '',
      price: product.price.toString(),
      quantity: product.quantity.toString(),
      low_stock_threshold: product.low_stock_threshold.toString(),
    });
    setFormError('');
  };

  const handleSaveProduct = async (e) => {
    e.preventDefault();
    setFormError('');

    // Validation
    if (!formData.name.trim()) {
      setFormError('Product name is required.');
      return;
    }
    if (!formData.sku.trim()) {
      setFormError('SKU is required.');
      return;
    }
    const priceNum = parseFloat(formData.price);
    if (isNaN(priceNum) || priceNum <= 0) {
      setFormError('Price must be a number strictly greater than 0.');
      return;
    }
    const qtyNum = parseInt(formData.quantity, 10);
    if (isNaN(qtyNum) || qtyNum < 0) {
      setFormError('Quantity must be an integer >= 0.');
      return;
    }
    const thresholdNum = parseInt(formData.low_stock_threshold, 10);
    if (isNaN(thresholdNum) || thresholdNum < 0) {
      setFormError('Low-stock threshold must be an integer >= 0.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        name: formData.name.trim(),
        sku: formData.sku.trim(),
        description: formData.description.trim() || null,
        price: priceNum,
        quantity: qtyNum,
        low_stock_threshold: thresholdNum,
      };

      if (editingProduct) {
        await productsApi.update(editingProduct.id, payload);
        setSuccessMsg(`Product "${payload.name}" updated successfully.`);
        setEditingProduct(null);
      } else {
        await productsApi.create(payload);
        setSuccessMsg(`Product "${payload.name}" created successfully.`);
        setIsAddModalOpen(false);
      }
      resetForm();
      fetchProducts();
    } catch (err) {
      setFormError(err.friendlyMessage || 'Failed to save product. Please check your inputs.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteProduct = async () => {
    if (!deletingProduct) return;
    setIsSubmitting(true);
    try {
      await productsApi.delete(deletingProduct.id);
      setSuccessMsg(`Product "${deletingProduct.name}" deleted successfully.`);
      setDeletingProduct(null);
      fetchProducts();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to delete product.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatPrice = (p) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(Number(p) || 0);
  };

  return (
    <div>
      {/* Page Title & Add Button */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--slate-900)' }}>
            Products Catalog
          </h2>
          <p style={{ color: 'var(--slate-500)', fontSize: '0.875rem' }}>
            Create, update, manage prices, and track stock counts for your organization.
          </p>
        </div>

        <button type="button" className="btn btn-primary" onClick={openAddModal}>
          <Plus size={18} />
          <span>Add New Product</span>
        </button>
      </div>

      {successMsg && <Toast type="success" message={successMsg} onClose={() => setSuccessMsg('')} />}
      {error && <Toast type="danger" message={error} onClose={() => setError('')} />}

      {/* Filter and Search Bar */}
      <div className="content-card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ padding: '1rem 1.5rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flex: 1, gap: '0.5rem', minWidth: '260px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                type="text"
                className="form-control"
                placeholder="Search by product name or SKU..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ paddingLeft: '2.5rem' }}
              />
              <Search
                size={18}
                color="var(--slate-400)"
                style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }}
              />
            </div>
            <button type="submit" className="btn btn-secondary">
              Search
            </button>
            {searchTerm && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setSearchTerm('');
                  setPage(0);
                }}
              >
                Clear
              </button>
            )}
          </form>
        </div>
      </div>

      {/* Products Table */}
      <div className="content-card">
        <div className="table-responsive">
          {isLoading ? (
            <LoadingSpinner size="medium" text="Loading product inventory..." />
          ) : products.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">
                <Package size={28} />
              </div>
              <h3 className="empty-state-title">No products found</h3>
              <p className="empty-state-desc">
                {searchTerm
                  ? `No products match your search query "${searchTerm}".`
                  : 'Start cataloging your inventory by adding your first product.'}
              </p>
              {!searchTerm && (
                <button type="button" className="btn btn-primary" onClick={openAddModal}>
                  <Plus size={16} />
                  <span>Add First Product</span>
                </button>
              )}
            </div>
          ) : (
            <>
              {/* Desktop View: Full Data Table */}
              <div className="desktop-only">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Product Details</th>
                      <th>Unit Price</th>
                      <th>Quantity</th>
                      <th>Threshold</th>
                      <th>Status</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p) => {
                      const isLow = p.quantity <= p.low_stock_threshold && p.quantity > 0;
                      const isOut = p.quantity === 0;

                      return (
                        <tr key={p.id}>
                          <td>
                            <span className="sku-badge">{p.sku}</span>
                          </td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'var(--slate-900)' }}>{p.name}</div>
                            {p.description && (
                              <div
                                style={{
                                  fontSize: '0.775rem',
                                  color: 'var(--slate-500)',
                                  maxWidth: '280px',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap',
                                }}
                              >
                                {p.description}
                              </div>
                            )}
                          </td>
                          <td style={{ fontWeight: 600 }}>{formatPrice(p.price)}</td>
                          <td>
                            <span
                              style={{
                                fontWeight: 700,
                                fontSize: '0.95rem',
                                color: isOut ? 'var(--rose-600)' : isLow ? 'var(--amber-600)' : 'var(--slate-800)',
                              }}
                            >
                              {p.quantity} units
                            </span>
                          </td>
                          <td style={{ color: 'var(--slate-500)' }}>{p.low_stock_threshold}</td>
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
                            <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                              <button
                                type="button"
                                className="btn btn-secondary btn-sm"
                                onClick={() => setAdjustingStockProduct(p)}
                                title="Adjust Stock"
                              >
                                <Layers size={14} />
                                <span>Stock</span>
                              </button>
                              <button
                                type="button"
                                className="btn btn-secondary btn-icon-only btn-sm"
                                onClick={() => openEditModal(p)}
                                title="Edit Product"
                              >
                                <Edit2 size={14} />
                              </button>
                              <button
                                type="button"
                                className="btn btn-secondary btn-icon-only btn-sm"
                                style={{ color: 'var(--rose-600)' }}
                                onClick={() => setDeletingProduct(p)}
                                title="Delete Product"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Mobile View: High-End Responsive Cards */}
              <div className="mobile-only mobile-card-list">
                {products.map((p) => {
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

                      {p.description && (
                        <p className="mobile-card-desc">{p.description}</p>
                      )}

                      <div className="mobile-card-stats">
                        <div className="mobile-stat-col">
                          <span className="mobile-stat-label">Price</span>
                          <span className="mobile-stat-value">{formatPrice(p.price)}</span>
                        </div>
                        <div className="mobile-stat-col">
                          <span className="mobile-stat-label">Quantity</span>
                          <span
                            className="mobile-stat-value"
                            style={{
                              color: isOut ? 'var(--rose-600)' : isLow ? 'var(--amber-600)' : 'var(--emerald-600)',
                            }}
                          >
                            {p.quantity} units
                          </span>
                        </div>
                        <div className="mobile-stat-col">
                          <span className="mobile-stat-label">Threshold</span>
                          <span className="mobile-stat-value">{p.low_stock_threshold}</span>
                        </div>
                      </div>

                      <div className="mobile-card-actions">
                        <button
                          type="button"
                          className="btn btn-primary btn-sm"
                          onClick={() => setAdjustingStockProduct(p)}
                        >
                          <Layers size={14} />
                          <span>Adjust Stock</span>
                        </button>
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => openEditModal(p)}
                        >
                          <Edit2 size={14} />
                          <span>Edit</span>
                        </button>
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          style={{ color: 'var(--rose-600)' }}
                          onClick={() => setDeletingProduct(p)}
                        >
                          <Trash2 size={14} />
                          <span>Delete</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Pagination Bar */}
        <div
          style={{
            padding: '1rem 1.5rem',
            borderTop: '1px solid var(--slate-100)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ fontSize: '0.85rem', color: 'var(--slate-500)' }}>
            Showing page {page + 1}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={page === 0 || isLoading}
              onClick={() => setPage((prev) => Math.max(0, prev - 1))}
            >
              <ChevronLeft size={16} />
              <span>Previous</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={!hasMore || isLoading}
              onClick={() => setPage((prev) => prev + 1)}
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Add / Edit Product Modal */}
      <Modal
        isOpen={isAddModalOpen || !!editingProduct}
        onClose={() => {
          setIsAddModalOpen(false);
          setEditingProduct(null);
        }}
        title={editingProduct ? `Edit Product: ${editingProduct.name}` : 'Add New Product'}
        footer={
          <>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setIsAddModalOpen(false);
                setEditingProduct(null);
              }}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSaveProduct}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : editingProduct ? 'Save Changes' : 'Create Product'}
            </button>
          </>
        }
      >
        {formError && (
          <div className="alert alert-danger">
            <AlertCircle size={18} />
            <div>{formError}</div>
          </div>
        )}

        <form onSubmit={handleSaveProduct}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="prod_name">
                Product Name <span className="required">*</span>
              </label>
              <input
                id="prod_name"
                type="text"
                className="form-control"
                placeholder="e.g. Ergonomic Office Chair"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="prod_sku">
                SKU (Stock Keeping Unit) <span className="required">*</span>
              </label>
              <input
                id="prod_sku"
                type="text"
                className="form-control"
                placeholder="e.g. CHAIR-001"
                value={formData.sku}
                onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="prod_desc">
              Description (Optional)
            </label>
            <textarea
              id="prod_desc"
              rows="2"
              className="form-control"
              placeholder="High-density foam, adjustable armrests..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="prod_price">
                Unit Price ($) <span className="required">*</span>
              </label>
              <input
                id="prod_price"
                type="number"
                step="0.01"
                min="0.01"
                className="form-control"
                placeholder="99.99"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="prod_qty">
                Initial Quantity <span className="required">*</span>
              </label>
              <input
                id="prod_qty"
                type="number"
                min="0"
                className="form-control"
                placeholder="25"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="prod_threshold">
                Low-Stock Threshold <span className="required">*</span>
              </label>
              <input
                id="prod_threshold"
                type="number"
                min="0"
                className="form-control"
                placeholder="5"
                value={formData.low_stock_threshold}
                onChange={(e) => setFormData({ ...formData, low_stock_threshold: e.target.value })}
                required
              />
            </div>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deletingProduct}
        onClose={() => setDeletingProduct(null)}
        title="Confirm Product Deletion"
        footer={
          <>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setDeletingProduct(null)}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-danger"
              onClick={handleDeleteProduct}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Deleting...' : 'Delete Permanently'}
            </button>
          </>
        }
      >
        <p style={{ color: 'var(--slate-700)', fontSize: '0.95rem' }}>
          Are you sure you want to delete{' '}
          <strong>{deletingProduct?.name}</strong> (SKU: {deletingProduct?.sku})?
        </p>
        <p style={{ color: 'var(--rose-600)', fontSize: '0.825rem', marginTop: '0.5rem' }}>
          This will permanently remove this item and its inventory records from your organization.
        </p>
      </Modal>

      {/* Adjust Stock Modal */}
      {adjustingStockProduct && (
        <StockModal
          isOpen={!!adjustingStockProduct}
          product={adjustingStockProduct}
          onClose={() => setAdjustingStockProduct(null)}
          onSuccess={() => {
            setSuccessMsg(`Stock updated for ${adjustingStockProduct.name}.`);
            fetchProducts();
          }}
        />
      )}
    </div>
  );
};

export default Products;
