import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Trash2 } from 'lucide-react';

function ProductsList() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);

  useEffect(() => {
    fetchProducts();
  }, [page]);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`/api/v1/products/seller/products?skip=${page * 20}&limit=20`);
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteProduct = async (productId: string) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await axios.delete(`/api/v1/products/${productId}`);
        setProducts(products.filter(p => p.id !== productId));
      } catch (error) {
        console.error('Failed to delete product:', error);
      }
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">My Products</h1>
        <button
          onClick={() => navigate('/products/create')}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus size={20} /> Add Product
        </button>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : products.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">No products yet</p>
          <button
            onClick={() => navigate('/products/create')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Create Your First Product
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">SKU</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Product Name</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Price</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Status</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product: any) => (
                <tr key={product.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-gray-600">{product.sku}</td>
                  <td className="px-6 py-4">
                    <p className="font-medium text-gray-800">{product.name}</p>
                    <p className="text-sm text-gray-600">{product.category}</p>
                  </td>
                  <td className="px-6 py-4 font-semibold text-gray-800">₹{product.current_price}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      product.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {product.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 flex gap-2">
                    <button
                      onClick={() => navigate(`/products/${product.id}`)}
                      className="text-blue-600 hover:text-blue-800 p-2"
                    >
                      <Edit size={18} />
                    </button>
                    <button
                      onClick={() => deleteProduct(product.id)}
                      className="text-red-600 hover:text-red-800 p-2"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ProductsList;
