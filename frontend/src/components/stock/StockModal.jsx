import React, { useState } from 'react';
import { ArrowUpCircle, ArrowDownCircle, AlertCircle } from 'lucide-react';
import Modal from '../common/Modal';
import { stockApi } from '../../services/api';

const StockModal = ({ isOpen, onClose, product, onSuccess }) => {
  const [mode, setMode] = useState('increase'); // 'increase' or 'decrease'
  const [quantity, setQuantity] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!product) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const qtyNumber = parseInt(quantity, 10);
    if (isNaN(qtyNumber) || qtyNumber <= 0) {
      setError('Quantity must be an integer greater than zero.');
      return;
    }

    if (mode === 'decrease' && qtyNumber > product.quantity) {
      setError(`Cannot decrease by ${qtyNumber}. Available stock is only ${product.quantity}.`);
      return;
    }

    setIsSubmitting(true);
    try {
      if (mode === 'increase') {
        await stockApi.increase(product.id, qtyNumber);
      } else {
        await stockApi.decrease(product.id, qtyNumber);
      }
      setQuantity('');
      onSuccess?.();
      onClose();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to update stock. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const calculatedNewQuantity = () => {
    const qty = parseInt(quantity, 10);
    if (isNaN(qty) || qty <= 0) return product.quantity;
    return mode === 'increase'
      ? product.quantity + qty
      : Math.max(0, product.quantity - qty);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Adjust Stock – ${product.name}`}
      footer={
        <>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="button"
            className={`btn ${mode === 'increase' ? 'btn-primary' : 'btn-danger'}`}
            onClick={handleSubmit}
            disabled={isSubmitting || !quantity}
          >
            {isSubmitting
              ? 'Processing...'
              : mode === 'increase'
              ? 'Confirm Stock Increase'
              : 'Confirm Stock Decrease'}
          </button>
        </>
      }
    >
      {error && (
        <div className="alert alert-danger">
          <AlertCircle size={18} />
          <div>{error}</div>
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <button
          type="button"
          className={`btn ${mode === 'increase' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ flex: 1 }}
          onClick={() => {
            setMode('increase');
            setError('');
          }}
        >
          <ArrowUpCircle size={18} />
          <span>Increase Stock</span>
        </button>

        <button
          type="button"
          className={`btn ${mode === 'decrease' ? 'btn-danger' : 'btn-secondary'}`}
          style={{ flex: 1 }}
          onClick={() => {
            setMode('decrease');
            setError('');
          }}
        >
          <ArrowDownCircle size={18} />
          <span>Decrease Stock</span>
        </button>
      </div>

      <div
        style={{
          backgroundColor: 'var(--slate-50)',
          border: '1px solid var(--slate-200)',
          borderRadius: 'var(--radius-md)',
          padding: '1rem',
          marginBottom: '1.25rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '0.5rem',
          textAlign: 'center',
        }}
      >
        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--slate-500)', fontWeight: 600 }}>CURRENT</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--slate-800)' }}>
            {product.quantity}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--slate-500)', fontWeight: 600 }}>CHANGE</div>
          <div
            style={{
              fontSize: '1.25rem',
              fontWeight: 800,
              color: mode === 'increase' ? 'var(--emerald-600)' : 'var(--rose-600)',
            }}
          >
            {quantity ? (mode === 'increase' ? `+${quantity}` : `-${quantity}`) : '0'}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--slate-500)', fontWeight: 600 }}>NEW TOTAL</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary-600)' }}>
            {calculatedNewQuantity()}
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="stockQuantity">
            Quantity to {mode === 'increase' ? 'Add' : 'Deduct'} <span className="required">*</span>
          </label>
          <input
            id="stockQuantity"
            type="number"
            min="1"
            className="form-control"
            placeholder="e.g. 10"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
            autoFocus
          />
          <div className="form-help">
            {mode === 'increase'
              ? 'Units will be immediately added to inventory.'
              : `Safe decrease with concurrency protection. Maximum: ${product.quantity} units.`}
          </div>
        </div>

        {/* Quick add/subtract helper pills */}
        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
          {[5, 10, 25, 50].map((preset) => (
            <button
              key={preset}
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => setQuantity(preset.toString())}
            >
              +{preset}
            </button>
          ))}
        </div>
      </form>
    </Modal>
  );
};

export default StockModal;
