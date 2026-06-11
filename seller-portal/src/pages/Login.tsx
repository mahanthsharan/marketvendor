import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import useAuthStore from '../store/authStore';
import { Mail, Lock } from 'lucide-react';

function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/v1/auth/login', formData);
      setAuth(response.data.access_token, response.data.seller);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Seller Portal</h1>
          <p className="text-gray-600 mt-2">Login to manage your products</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">Email</label>
            <div className="flex items-center border rounded-lg px-3 py-2">
              <Mail size={20} className="text-gray-400 mr-2" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
                required
                className="w-full outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Password</label>
            <div className="flex items-center border rounded-lg px-3 py-2">
              <Lock size={20} className="text-gray-400 mr-2" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Your password"
                required
                className="w-full outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>

          <p className="text-center text-gray-600">
            Don't have an account?{' '}
            <a href="/register" className="text-blue-600 font-semibold hover:underline">
              Register
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login;
