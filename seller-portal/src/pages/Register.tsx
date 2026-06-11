import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import useAuthStore from '../store/authStore';
import { Mail, Lock, Building2 } from 'lucide-react';

function Register() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    business_name: '',
    contact_person: '',
    phone: '',
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
      const response = await axios.post('/api/v1/auth/register', formData);
      setAuth(response.data.access_token, response.data.seller);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Register as Seller</h1>
          <p className="text-gray-600 mt-2">Start selling on our marketplace</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">Business Name</label>
            <div className="flex items-center border rounded-lg px-3 py-2">
              <Building2 size={20} className="text-gray-400 mr-2" />
              <input
                type="text"
                name="business_name"
                value={formData.business_name}
                onChange={handleChange}
                placeholder="Your business name"
                required
                className="w-full outline-none"
              />
            </div>
          </div>

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
                placeholder="Min 8 characters"
                required
                minLength={8}
                className="w-full outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Contact Person</label>
            <input
              type="text"
              name="contact_person"
              value={formData.contact_person}
              onChange={handleChange}
              placeholder="Your name"
              className="w-full border rounded-lg px-3 py-2 outline-none"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+91 9876543210"
              className="w-full border rounded-lg px-3 py-2 outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            {loading ? 'Registering...' : 'Register'}
          </button>

          <p className="text-center text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="text-blue-600 font-semibold hover:underline">
              Login
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Register;
