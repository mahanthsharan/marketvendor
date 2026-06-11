import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Package } from 'lucide-react';

function InventoryManagement() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/api/v1/products/seller/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800 flex items-center gap-2">
        <Package size={32} /> Inventory Management
      </h1>

      {loading ? (
        <div>Loading...</div>
      ) : products.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-600">No products to manage inventory for.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {products.map((product: any) => (
            <div key={product.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-800">{product.name}</h3>
                  <p className="text-sm text-gray-600">SKU: {product.sku}</p>
                </div>
                <span className="text-lg font-bold text-blue-600">₹{product.current_price}</span>
              </div>
              <button
                onClick={() => window.location.href = `/products/${product.id}`}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Manage Inventory
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default InventoryManagement;
