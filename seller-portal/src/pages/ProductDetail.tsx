import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Package, Zap } from 'lucide-react';

function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<any>(null);
  const [inventory, setInventory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedChannel, setSelectedChannel] = useState('');
  const [stockInput, setStockInput] = useState('');

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const [productRes, inventoryRes] = await Promise.all([
        axios.get(`/api/v1/products/${id}`),
        axios.get(`/api/v1/inventory/${id}/channels`),
      ]);
      setProduct(productRes.data);
      setInventory(inventoryRes.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateStock = async () => {
    if (!selectedChannel || !stockInput) return;

    try {
      await axios.put(`/api/v1/inventory/${id}/update`, {
        channel_id: selectedChannel,
        total_stock: parseInt(stockInput),
        reason: 'manual_update',
      });
      
      setStockInput('');
      fetchProduct();
    } catch (error) {
      console.error('Failed to update stock:', error);
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!product) return <div className="p-6">Product not found</div>;

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow p-8 mb-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">{product.name}</h1>
              <p className="text-gray-600 mt-2">{product.description}</p>
            </div>
            <span className={`px-4 py-2 rounded-full font-semibold ${
              product.is_active
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {product.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="border rounded-lg p-4">
              <p className="text-gray-600 text-sm">SKU</p>
              <p className="text-xl font-bold text-gray-800">{product.sku}</p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-gray-600 text-sm">Base Price</p>
              <p className="text-xl font-bold text-gray-800">₹{product.base_price}</p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-gray-600 text-sm">Current Price</p>
              <p className="text-xl font-bold text-green-600">₹{product.current_price}</p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-gray-600 text-sm">Cost</p>
              <p className="text-xl font-bold text-gray-800">₹{product.cost || '-'}</p>
            </div>
          </div>
        </div>

        {/* Inventory Management */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800 flex items-center gap-2">
            <Package size={24} /> Inventory Management
          </h2>

          <div className="grid grid-cols-3 gap-4 mb-6">
            {inventory.map((inv) => (
              <div key={inv.channel_id} className="border rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-3">{inv.channel_name}</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Available:</span>
                    <span className="font-bold text-gray-800">{inv.available}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Reserved:</span>
                    <span className="font-bold text-yellow-600">{inv.reserved}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="text-gray-600 font-semibold">Total:</span>
                    <span className="font-bold text-blue-600">{inv.total}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Update Stock Form */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h3 className="font-semibold text-gray-800 mb-4">Update Stock</h3>
            <div className="flex gap-4">
              <select
                value={selectedChannel}
                onChange={(e) => setSelectedChannel(e.target.value)}
                className="flex-1 border rounded-lg px-3 py-2 outline-none"
              >
                <option value="">Select Channel</option>
                {inventory.map((inv) => (
                  <option key={inv.channel_id} value={inv.channel_id}>
                    {inv.channel_name}
                  </option>
                ))}
              </select>
              <input
                type="number"
                value={stockInput}
                onChange={(e) => setStockInput(e.target.value)}
                placeholder="Total Stock"
                min="0"
                className="flex-1 border rounded-lg px-3 py-2 outline-none"
              />
              <button
                onClick={updateStock}
                disabled={!selectedChannel || !stockInput}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                Update
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductDetail;
