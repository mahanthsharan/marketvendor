import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import useAuthStore from './store/authStore';

import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ProductsList from './pages/ProductsList';
import CreateProduct from './pages/CreateProduct';
import ProductDetail from './pages/ProductDetail';
import InventoryManagement from './pages/InventoryManagement';
import OrderManagement from './pages/OrderManagement';
import PricingRules from './pages/PricingRules';
import Login from './pages/Login';
import Register from './pages/Register';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Configure axios
axios.defaults.baseURL = API_BASE_URL;
axios.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function App() {
  const { isAuthenticated, token } = useAuthStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verify token on app load
    if (token) {
      verifyToken();
    } else {
      setLoading(false);
    }
  }, [token]);

  const verifyToken = async () => {
    try {
      await axios.get('/api/v1/auth/me');
    } catch (error) {
      useAuthStore.setState({ token: null, isAuthenticated: false });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        {isAuthenticated && <Navbar />}
        <Routes>
          {!isAuthenticated ? (
            <>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="*" element={<Login />} />
            </>
          ) : (
            <>
              <Route path="/" element={<Dashboard />} />
              <Route path="/products" element={<ProductsList />} />
              <Route path="/products/create" element={<CreateProduct />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/inventory" element={<InventoryManagement />} />
              <Route path="/orders" element={<OrderManagement />} />
              <Route path="/pricing" element={<PricingRules />} />
            </>
          )}
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
