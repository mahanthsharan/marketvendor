import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle } from 'lucide-react';

function OrderConfirmation() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrder();
  }, [orderId]);

  const fetchOrder = async () => {
    try {
      const response = await axios.get(`/api/v1/orders/${orderId}`);
      setOrder(response.data);
    } catch (error) {
      console.error('Failed to fetch order:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!order) return <div className="p-6">Order not found</div>;

  return (
    <div className="p-6">
      <div className="max-w-2xl mx-auto text-center py-12">
        <CheckCircle size={80} className="mx-auto text-green-500 mb-6" />
        
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Order Confirmed!</h1>
        <p className="text-gray-600 mb-8">Thank you for your purchase</p>

        <div className="bg-white rounded-lg shadow p-8 mb-8 text-left">
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <p className="text-gray-600 text-sm mb-1">Order Number</p>
              <p className="text-xl font-bold text-gray-800">{order.order_number}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm mb-1">Order Total</p>
              <p className="text-xl font-bold text-blue-600">₹{order.total_amount}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm mb-1">Order Status</p>
              <p className="text-lg font-semibold text-green-600 capitalize">{order.status}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm mb-1">Payment Status</p>
              <p className="text-lg font-semibold text-green-600 capitalize">{order.payment_status}</p>
            </div>
          </div>

          <div className="border-t pt-6">
            <h2 className="text-lg font-bold mb-4 text-gray-800">Order Details</h2>
            <div className="space-y-3">
              <p className="text-gray-600"><strong>Email:</strong> {order.buyer_email}</p>
              <p className="text-gray-600"><strong>Subtotal:</strong> ₹{order.subtotal.toFixed(2)}</p>
              <p className="text-gray-600"><strong>Tax (18%):</strong> ₹{order.tax.toFixed(2)}</p>
              <p className="text-gray-600"><strong>Shipping:</strong> ₹{order.shipping.toFixed(2)}</p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <p className="text-sm text-gray-700">
            <strong>✓ Real-time Inventory Synced:</strong> Your purchase has updated inventory across all channels instantly. 
            Thank you for being part of our multi-vendor ecosystem!
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => navigate('/products')}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition"
          >
            Continue Shopping
          </button>
          <button
            onClick={() => navigate('/')}
            className="w-full border border-gray-300 text-gray-700 py-3 rounded-lg font-bold hover:bg-gray-50 transition"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default OrderConfirmation;
