import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowRight, ShoppingCart } from 'lucide-react';
import useCartStore from '../store/cartStore';

function Home() {
  const navigate = useNavigate();
  const addToCart = useCartStore((state) => state.addToCart);
  const [recommended, setRecommended] = useState<any[]>([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoadingRecommendations(true);
      const response = await axios.get('/api/v1/recommendations', {
        params: { limit: 6 },
      });
      setRecommended(response.data);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  return (
    <div>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 gap-8 items-center">
            <div>
              <h1 className="text-5xl font-bold mb-4">Welcome to Our Marketplace</h1>
              <p className="text-xl mb-8 opacity-90">
                Discover thousands of products from trusted sellers at competitive prices. 
                Real-time inventory updates and dynamic pricing for the best deals.
              </p>
              <button
                onClick={() => navigate('/products')}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition flex items-center gap-2"
              >
                Start Shopping <ArrowRight size={20} />
              </button>
            </div>
            <div className="text-center">
              <div className="text-8xl">🛍️</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 px-6 max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold mb-12 text-center text-gray-800">Why Shop With Us?</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-lg shadow hover:shadow-lg transition">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-2 text-gray-800">Real-time Inventory</h3>
            <p className="text-gray-600">
              Products are synced across multiple channels instantly. No more out-of-stock surprises!
            </p>
          </div>

          <div className="bg-white p-8 rounded-lg shadow hover:shadow-lg transition">
            <div className="text-4xl mb-4">💰</div>
            <h3 className="text-xl font-bold mb-2 text-gray-800">Dynamic Pricing</h3>
            <p className="text-gray-600">
              Prices adjust based on demand. High-demand items may increase, low-demand items decrease!
            </p>
          </div>

          <div className="bg-white p-8 rounded-lg shadow hover:shadow-lg transition">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-xl font-bold mb-2 text-gray-800">Secure Payments</h3>
            <p className="text-gray-600">
              All transactions are processed securely through Stripe. Your data is always protected.
            </p>
          </div>
        </div>
      </div>

      {/* Recommended Products Section */}
      <div className="py-16 px-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-gray-800">Recommended for You</h2>
          <button
            onClick={() => navigate('/products')}
            className="text-blue-600 font-semibold hover:text-blue-800"
          >
            See all products
          </button>
        </div>

        {loadingRecommendations ? (
          <div className="text-center py-12">Loading recommendations...</div>
        ) : recommended.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600">No recommendations available yet. Start browsing products to generate recommendations.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommended.map((product) => (
              <div key={product.id} className="bg-white rounded-lg shadow p-6">
                <div className="h-40 bg-gradient-to-br from-blue-200 to-blue-300 rounded-lg flex items-center justify-center mb-4">
                  <div className="text-5xl">📦</div>
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">{product.name}</h3>
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">{product.description}</p>
                <p className="text-2xl font-bold text-gray-800 mb-4">₹{product.current_price}</p>
                <button
                  onClick={() => navigate(`/products/${product.id}`)}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition mb-3"
                >
                  View Product
                </button>
                <button
                  onClick={() => addToCart(product)}
                  className="w-full bg-gray-100 text-gray-800 py-2 rounded-lg hover:bg-gray-200 transition"
                >
                  <ShoppingCart size={16} className="inline-block align-middle mr-2" /> Add to Cart
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 text-white py-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8">Ready to Start Shopping?</h2>
          <button
            onClick={() => navigate('/products')}
            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition"
          >
            Browse Our Catalog
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
