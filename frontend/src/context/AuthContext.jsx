import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('stockflow_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('stockflow_token'));
  const [isLoading, setIsLoading] = useState(true);

  // Initialize and verify authentication on load
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('stockflow_token');
      if (storedToken) {
        try {
          const profile = await authApi.getMe();
          setUser(profile);
          localStorage.setItem('stockflow_user', JSON.stringify(profile));
        } catch {
          // Token expired or invalid
          localStorage.removeItem('stockflow_token');
          localStorage.removeItem('stockflow_user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await authApi.login({ email, password });
    const accessToken = data.access_token;
    localStorage.setItem('stockflow_token', accessToken);
    setToken(accessToken);

    const profile = await authApi.getMe();
    setUser(profile);
    localStorage.setItem('stockflow_user', JSON.stringify(profile));
    return profile;
  };

  const signup = async (userData) => {
    const data = await authApi.signup(userData);
    // Automatically log in after registration
    await login(userData.email, userData.password);
    return data;
  };

  const logout = () => {
    localStorage.removeItem('stockflow_token');
    localStorage.removeItem('stockflow_user');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const profile = await authApi.getMe();
      setUser(profile);
      localStorage.setItem('stockflow_user', JSON.stringify(profile));
      return profile;
    } catch (err) {
      console.error('Failed to refresh user profile:', err);
    }
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    signup,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
