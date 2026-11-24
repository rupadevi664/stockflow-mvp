import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('stockflow_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Format error details & handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        // Clear expired or invalid credentials
        localStorage.removeItem('stockflow_token');
        localStorage.removeItem('stockflow_user');
        if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
          window.location.href = '/login';
        }
      }
      
      // Standardize error message extraction from FastAPI
      const detail = error.response.data?.detail;
      let message = 'An error occurred';
      if (typeof detail === 'string') {
        message = detail;
      } else if (Array.isArray(detail)) {
        // Pydantic validation error array
        message = detail.map((err) => `${err.loc?.slice(1).join('.') || 'field'}: ${err.msg}`).join(', ');
      } else if (error.response.data?.message) {
        message = error.response.data.message;
      }
      error.friendlyMessage = message;
    } else if (error.request) {
      error.friendlyMessage = 'Unable to connect to the backend server. Please verify FastAPI is running at ' + API_BASE_URL;
    } else {
      error.friendlyMessage = error.message || 'Unexpected application error';
    }
    return Promise.reject(error);
  }
);

// 1. Authentication APIs
export const authApi = {
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// 2. Dashboard & Analytics APIs
export const dashboardApi = {
  getSummary: async () => {
    const response = await api.get('/dashboard/summary');
    return response.data;
  },
  getLowStock: async () => {
    const response = await api.get('/dashboard/low-stock');
    return response.data;
  },
  getInventoryValue: async () => {
    const response = await api.get('/dashboard/inventory-value');
    return response.data;
  },
};

// 3. Product Management APIs
export const productsApi = {
  getAll: async ({ skip = 0, limit = 50, search = '' } = {}) => {
    const params = { skip, limit };
    if (search && search.trim() !== '') {
      params.search = search.trim();
    }
    const response = await api.get('/products/', { params });
    return response.data;
  },
  getById: async (id) => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },
  create: async (productData) => {
    const response = await api.post('/products/', productData);
    return response.data;
  },
  update: async (id, productData) => {
    const response = await api.put(`/products/${id}`, productData);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/products/${id}`);
    return response.data;
  },
};

// 4. Stock Management APIs
export const stockApi = {
  increase: async (productId, quantity) => {
    const response = await api.post(`/products/${productId}/stock/increase`, {
      quantity: Number(quantity),
    });
    return response.data;
  },
  decrease: async (productId, quantity) => {
    const response = await api.post(`/products/${productId}/stock/decrease`, {
      quantity: Number(quantity),
    });
    return response.data;
  },
  getLowStock: async () => {
    const response = await api.get('/products/low-stock');
    return response.data;
  },
};

// 5. Organization Settings APIs
export const organizationApi = {
  getSettings: async () => {
    const response = await api.get('/organization/settings');
    return response.data;
  },
  updateSettings: async (settingsData) => {
    const response = await api.put('/organization/settings', settingsData);
    return response.data;
  },
};

export default api;
