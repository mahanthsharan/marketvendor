import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Home, Package, Zap, ShoppingCart, BarChart3 } from 'lucide-react';
import useAuthStore from '../store/authStore';

function Navbar() {
  const navigate = useNavigate();
  const { seller, logout } = useAuthStore();

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div
            className="text-2xl font-bold cursor-pointer"
            onClick={() => navigate('/')}
          >
            MarketPlace
          </div>

          <div className="flex items-center gap-8">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
            >
              <Home size={20} /> Dashboard
            </button>
            <button
              onClick={() => navigate('/products')}
              className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
            >
              <Package size={20} /> Products
            </button>
            <button
              onClick={() => navigate('/inventory')}
              className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
            >
              <BarChart3 size={20} /> Inventory
            </button>
            <button
              onClick={() => navigate('/pricing')}
              className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
            >
              <Zap size={20} /> Pricing
            </button>
            <button
              onClick={() => navigate('/orders')}
              className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
            >
              <ShoppingCart size={20} /> Orders
            </button>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm">{seller?.business_name}</span>
            <button
              onClick={() => {
                logout();
                navigate('/login');
              }}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition"
            >
              <LogOut size={20} /> Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
