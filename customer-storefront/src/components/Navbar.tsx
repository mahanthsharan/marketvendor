import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingCart, Home } from 'lucide-react';
import useCartStore from '../store/cartStore';

function Navbar() {
  const navigate = useNavigate();
  const cartCount = useCartStore((state) => state.items.length);

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <button
            onClick={() => navigate('/')}
            className="text-2xl font-bold cursor-pointer flex items-center gap-2 hover:text-blue-100"
          >
            <Home size={24} /> MarketPlace
          </button>

          <div className="flex items-center gap-8">
            <button
              onClick={() => navigate('/')}
              className="hover:text-blue-100 transition font-medium"
            >
              Home
            </button>
            <button
              onClick={() => navigate('/products')}
              className="hover:text-blue-100 transition font-medium"
            >
              Shop
            </button>
            <button
              onClick={() => navigate('/cart')}
              className="flex items-center gap-2 hover:text-blue-100 transition font-medium relative"
            >
              <ShoppingCart size={24} />
              <span>Cart</span>
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
