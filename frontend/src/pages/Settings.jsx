import React, { useState, useEffect } from 'react';
import { Building2, Mail, Phone, Sliders, Check, AlertCircle } from 'lucide-react';
import { organizationApi } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Toast from '../components/common/Toast';

const Settings = () => {
  const [formData, setFormData] = useState({
    name: '',
    contact_email: '',
    contact_phone: '',
    default_low_stock_threshold: '5',
  });
  const [orgData, setOrgData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const fetchSettings = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await organizationApi.getSettings();
      setOrgData(data);
      setFormData({
        name: data.name || '',
        contact_email: data.contact_email || '',
        contact_phone: data.contact_phone || '',
        default_low_stock_threshold: (data.default_low_stock_threshold ?? 5).toString(),
      });
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to fetch organization settings.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    if (!formData.name.trim()) {
      setError('Organization name cannot be empty.');
      return;
    }

    const thresholdNum = parseInt(formData.default_low_stock_threshold, 10);
    if (isNaN(thresholdNum) || thresholdNum < 0) {
      setError('Default low-stock threshold must be zero or greater.');
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        name: formData.name.trim(),
        contact_email: formData.contact_email.trim() || null,
        contact_phone: formData.contact_phone.trim() || null,
        default_low_stock_threshold: thresholdNum,
      };

      const updated = await organizationApi.updateSettings(payload);
      setOrgData(updated);
      setSuccessMsg('Organization settings updated successfully.');
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to update organization settings.');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner size="large" text="Loading organization profile..." />;
  }

  return (
    <div style={{ maxWidth: '800px' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--slate-900)' }}>
          Organization Settings
        </h2>
        <p style={{ color: 'var(--slate-500)', fontSize: '0.875rem' }}>
          Manage your company profile, primary contact info, and default inventory thresholds.
        </p>
      </div>

      {successMsg && <Toast type="success" message={successMsg} onClose={() => setSuccessMsg('')} />}
      {error && <Toast type="danger" message={error} onClose={() => setError('')} />}

      <div className="content-card">
        <div className="card-header">
          <div className="card-title">
            <Building2 size={20} color="var(--primary-600)" />
            <span>Profile & Threshold Configuration</span>
          </div>
          {orgData?.id && (
            <span className="sku-badge" style={{ fontSize: '0.75rem' }}>
              Org ID #{orgData.id}
            </span>
          )}
        </div>

        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="orgName">
                Organization Name <span className="required">*</span>
              </label>
              <input
                id="orgName"
                name="name"
                type="text"
                className="form-control"
                placeholder="e.g. Acme Corporation"
                value={formData.name}
                onChange={handleChange}
                required
              />
              <div className="form-help">The official registered company or tenant name.</div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="contactEmail">
                  Contact Email
                </label>
                <input
                  id="contactEmail"
                  name="contact_email"
                  type="email"
                  className="form-control"
                  placeholder="contact@company.com"
                  value={formData.contact_email}
                  onChange={handleChange}
                />
                <div className="form-help">Primary support or billing contact email.</div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="contactPhone">
                  Contact Phone
                </label>
                <input
                  id="contactPhone"
                  name="contact_phone"
                  type="text"
                  className="form-control"
                  placeholder="+1 (800) 555-0199"
                  value={formData.contact_phone}
                  onChange={handleChange}
                />
                <div className="form-help">Standard 7–15 digit phone number with area code.</div>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="threshold">
                Default Low-Stock Threshold <span className="required">*</span>
              </label>
              <input
                id="threshold"
                name="default_low_stock_threshold"
                type="number"
                min="0"
                className="form-control"
                placeholder="5"
                value={formData.default_low_stock_threshold}
                onChange={handleChange}
                required
              />
              <div className="form-help">
                Default minimum threshold value applied when configuring new inventory items.
              </div>
            </div>

            <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSaving}
              >
                {isSaving ? (
                  'Saving Changes...'
                ) : (
                  <>
                    <Check size={16} />
                    <span>Save Settings</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Settings;
