import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ShoppingCart, Calendar, DollarSign } from 'lucide-react';
import { format } from 'date-fns';

function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchOrders();
  }, [statusFilter]);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`/api/v1/orders/${statusFilter ? `?status_filter=${statusFilter}` : ''}`);
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800 flex items-center gap-2">
        <ShoppingCart size={32} /> Order Management
      </h1>

      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setStatusFilter('')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            statusFilter === ''
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          All Orders
        </button>
        {['pending', 'processing', 'confirmed', 'shipped', 'delivered', 'cancelled'].map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium transition capitalize ${
              statusFilter === status
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {status}
          </button>
        ))}
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : orders.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-600">No orders found.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order: any) => (
            <div key={order.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-800">{order.order_number}</h3>
                  <p className="text-sm text-gray-600">{order.buyer_email}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-800">₹{order.total_amount}</p>
                  <p className="text-sm text-gray-600 flex items-center gap-1 justify-end">
                    <Calendar size={14} /> {format(new Date(order.created_at), 'MMM dd, yyyy')}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 rounded">
                <div>
                  <p className="text-gray-600 text-sm">Order Status</p>
                  <p className={`font-semibold capitalize ${
                    order.status === 'delivered' ? 'text-green-600' : 'text-blue-600'
                  }`}>
                    {order.status}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Payment Status</p>
                  <p className={`font-semibold capitalize ${
                    order.payment_status === 'completed' ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {order.payment_status}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Items</p>
                  <p className="font-semibold text-gray-800">{order.items?.length || 0} items</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default OrderManagement;
