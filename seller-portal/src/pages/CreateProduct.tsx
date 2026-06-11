import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Package, DollarSign, Weight } from 'lucide-react';

function CreateProduct() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    category: '',
    base_price: '',
    cost: '',
    weight: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
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
      await axios.post('/api/v1/products/', {
        ...formData,
        base_price: parseFloat(formData.base_price),
        cost: formData.cost ? parseFloat(formData.cost) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
      });
      navigate('/products');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">Create New Product</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-8 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-medium mb-2">SKU (required)</label>
              <div className="flex items-center border rounded-lg px-3 py-2">
                <Package size={20} className="text-gray-400 mr-2" />
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                  placeholder="PROD-001"
                  required
                  className="w-full outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Product Name (required)</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Product name"
                required
                className="w-full border rounded-lg px-3 py-2 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Category</label>
            <input
              type="text"
              name="category"
              value={formData.category}
              onChange={handleChange}
              placeholder="e.g., Electronics, Clothing"
              className="w-full border rounded-lg px-3 py-2 outline-none"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Product description"
              rows={4}
              className="w-full border rounded-lg px-3 py-2 outline-none"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-gray-700 font-medium mb-2">Base Price (required)</label>
              <div className="flex items-center border rounded-lg px-3 py-2">
                <DollarSign size={20} className="text-gray-400 mr-2" />
                <input
                  type="number"
                  name="base_price"
                  value={formData.base_price}
                  onChange={handleChange}
                  placeholder="999.99"
                  step="0.01"
                  min="0"
                  required
                  className="w-full outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Cost Price</label>
              <input
                type="number"
                name="cost"
                value={formData.cost}
                onChange={handleChange}
                placeholder="500.00"
                step="0.01"
                min="0"
                className="w-full border rounded-lg px-3 py-2 outline-none"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Weight (kg)</label>
              <div className="flex items-center border rounded-lg px-3 py-2">
                <Weight size={20} className="text-gray-400 mr-2" />
                <input
                  type="number"
                  name="weight"
                  value={formData.weight}
                  onChange={handleChange}
                  placeholder="1.5"
                  step="0.1"
                  min="0"
                  className="w-full outline-none"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
            >
              {loading ? 'Creating...' : 'Create Product'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/products')}
              className="flex-1 border border-gray-300 text-gray-700 font-semibold py-2 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateProduct;
