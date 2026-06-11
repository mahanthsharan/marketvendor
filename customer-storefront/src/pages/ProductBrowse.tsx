import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Search, Star, ShoppingCart } from 'lucide-react';
import useCartStore from '../store/cartStore';

function ProductBrowse() {
  const navigate = useNavigate();
  const addToCart = useCartStore((state) => state.addToCart);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [priceRange, setPriceRange] = useState([0, 100000]);

  useEffect(() => {
    searchProducts();
  }, [searchQuery, selectedCategory, priceRange]);

  const searchProducts = async () => {
    if (!searchQuery && !selectedCategory) {
      setProducts([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get('/api/v1/products/search', {
        params: {
          q: searchQuery,
          category: selectedCategory,
          min_price: priceRange[0],
          max_price: priceRange[1],
        },
      });
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to search products:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">Browse Products</h1>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-gray-700 font-medium mb-2">Search</label>
              <div className="flex items-center border rounded-lg px-3 py-2">
                <Search size={20} className="text-gray-400 mr-2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search products..."
                  className="w-full outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 outline-none"
              >
                <option value="">All Categories</option>
                <option value="Electronics">Electronics</option>
                <option value="Clothing">Clothing</option>
                <option value="Books">Books</option>
                <option value="Home">Home & Garden</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Min Price (₹)</label>
              <input
                type="number"
                value={priceRange[0]}
                onChange={(e) => setPriceRange([parseInt(e.target.value), priceRange[1]])}
                min="0"
                className="w-full border rounded-lg px-3 py-2 outline-none"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Max Price (₹)</label>
              <input
                type="number"
                value={priceRange[1]}
                onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                min="0"
                className="w-full border rounded-lg px-3 py-2 outline-none"
              />
            </div>
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : products.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600 mb-4">No products found. Try adjusting your search.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map((product: any) => (
              <div
                key={product.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer overflow-hidden group"
              >
                <div className="h-48 bg-gradient-to-br from-blue-200 to-blue-300 flex items-center justify-center overflow-hidden">
                  <div className="text-4xl text-white">📦</div>
                </div>

                <div className="p-4">
                  <h3 className="text-lg font-bold text-gray-800 truncate">{product.name}</h3>
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">{product.description}</p>

                  <div className="flex items-center gap-1 mb-3">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        size={16}
                        className={i < 4 ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                      />
                    ))}
                  </div>

                  <div className="mb-4">
                    <p className="text-2xl font-bold text-gray-800">₹{product.current_price}</p>
                    {product.base_price !== product.current_price && (
                      <p className="text-sm text-gray-500 line-through">₹{product.base_price}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <button
                      onClick={() => navigate(`/products/${product.id}`)}
                      className="w-full bg-blue-100 text-blue-600 py-2 rounded-lg hover:bg-blue-200 transition"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => addToCart(product)}
                      className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
                    >
                      <ShoppingCart size={18} /> Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductBrowse;
