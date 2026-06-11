import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Star, ShoppingCart } from 'lucide-react';
import useCartStore from '../store/cartStore';

function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const addToCart = useCartStore((state) => state.addToCart);
  const [product, setProduct] = useState<any>(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [similarProducts, setSimilarProducts] = useState<any[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(true);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`/api/v1/products/${id}`);
      setProduct(response.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSimilarProducts = async () => {
    if (!id) {
      setSimilarProducts([]);
      setLoadingSimilar(false);
      return;
    }

    try {
      setLoadingSimilar(true);
      const response = await axios.get('/api/v1/recommendations', {
        params: {
          product_id: id,
          limit: 4,
        },
      });
      setSimilarProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoadingSimilar(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchSimilarProducts();
    }
  }, [id]);

  const handleAddToCart = () => {
    for (let i = 0; i < quantity; i++) {
      addToCart(product);
    }
    setQuantity(1);
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!product) return <div className="p-6">Product not found</div>;

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-2 gap-8">
          {/* Product Image */}
          <div className="h-96 bg-gradient-to-br from-blue-200 to-blue-300 rounded-lg flex items-center justify-center">
            <div className="text-9xl">📦</div>
          </div>

          {/* Product Details */}
          <div>
            <h1 className="text-4xl font-bold mb-2 text-gray-800">{product.name}</h1>
            
            <div className="flex items-center gap-2 mb-4">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  size={20}
                  className={i < 4 ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                />
              ))}
              <span className="text-gray-600">(128 reviews)</span>
            </div>

            <p className="text-gray-600 mb-4">{product.category}</p>

            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-sm mb-2">Current Price</p>
              <div className="flex items-center gap-4">
                <p className="text-4xl font-bold text-gray-800">₹{product.current_price}</p>
                {product.base_price !== product.current_price && (
                  <div>
                    <p className="text-lg text-gray-500 line-through">₹{product.base_price}</p>
                    <p className="text-sm font-bold text-green-600">
                      Save ₹{(product.base_price - product.current_price).toFixed(2)}
                    </p>
                  </div>
                )}
              </div>
            </div>

            <p className="text-gray-700 mb-6 leading-relaxed">{product.description}</p>

            <div className="mb-6">
              <label className="block text-gray-700 font-medium mb-2">Quantity</label>
              <div className="flex items-center gap-3 border rounded-lg p-2 w-fit">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="w-8 h-8 flex items-center justify-center bg-gray-200 hover:bg-gray-300 rounded"
                >
                  −
                </button>
                <span className="w-8 text-center font-bold">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="w-8 h-8 flex items-center justify-center bg-gray-200 hover:bg-gray-300 rounded"
                >
                  +
                </button>
              </div>
            </div>

            <button
              onClick={handleAddToCart}
              className="w-full bg-blue-600 text-white py-4 rounded-lg font-bold text-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
            >
              <ShoppingCart size={24} /> Add to Cart
            </button>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-gray-600">
                <strong>✓ Real-time Inventory:</strong> This product is synced across all sales channels. Prices adjust dynamically based on demand.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">You May Also Like</h2>
          {loadingSimilar ? (
            <div className="text-center py-6">Loading similar products...</div>
          ) : similarProducts.length === 0 ? (
            <div className="text-gray-600">No similar products are available right now.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {similarProducts.map((item) => (
                <div key={item.id} className="bg-white rounded-lg shadow p-4">
                  <div className="h-32 bg-gradient-to-br from-blue-200 to-blue-300 rounded-lg flex items-center justify-center mb-4">
                    <div className="text-4xl">📦</div>
                  </div>
                  <h3 className="text-lg font-bold text-gray-800 mb-2">{item.name}</h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{item.description}</p>
                  <p className="text-xl font-bold text-gray-900">₹{item.current_price}</p>
                  <button
                    onClick={() => addToCart(item)}
                    className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                  >
                    Add to Cart
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProductDetail;
