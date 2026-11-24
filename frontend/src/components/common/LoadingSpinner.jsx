import React from 'react';

const LoadingSpinner = ({ size = 'medium', text = 'Loading...' }) => {
  const sizeMap = {
    small: { width: '20px', height: '20px', border: '2px' },
    medium: { width: '36px', height: '36px', border: '3px' },
    large: { width: '52px', height: '52px', border: '4px' },
  };

  const currentSize = sizeMap[size] || sizeMap.medium;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', padding: '1.5rem' }}>
      <div
        style={{
          width: currentSize.width,
          height: currentSize.height,
          borderRadius: '50%',
          border: `${currentSize.border} solid var(--slate-200)`,
          borderTopColor: 'var(--primary-600)',
          animation: 'spin 0.8s linear infinite',
        }}
      />
      {text && <span style={{ fontSize: '0.85rem', color: 'var(--slate-500)', fontWeight: 500 }}>{text}</span>}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
