import React from 'react';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';

const Toast = ({ type = 'info', message, onClose }) => {
  if (!message) return null;

  const iconMap = {
    danger: <AlertCircle size={18} />,
    success: <CheckCircle size={18} />,
    warning: <AlertCircle size={18} />,
    info: <Info size={18} />,
  };

  return (
    <div className={`alert alert-${type}`}>
      <span style={{ display: 'flex', alignItems: 'center', marginTop: '2px' }}>
        {iconMap[type] || iconMap.info}
      </span>
      <div style={{ flex: 1, fontWeight: 500 }}>{message}</div>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'inherit',
            cursor: 'pointer',
            padding: '2px',
            opacity: 0.8,
          }}
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
};

export default Toast;
