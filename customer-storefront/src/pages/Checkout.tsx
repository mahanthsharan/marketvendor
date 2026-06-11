import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { Mail, MapPin } from 'lucide-react';
import useCartStore from '../store/cartStore';

function Checkout() {
  const navigate = useNavigate();
  const stripe = useStripe();
  const elements = useElements();
  const { items, clearCart } = useCartStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    shipping_address: '',
  });

  const subtotal = items.reduce((sum, item) => sum + item.current_price, 0);
  const tax = subtotal * 0.18;
  const shipping = 50;
  const total = subtotal + tax + shipping;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setLoading(true);
    setError('');

    try {
      // Create order first
      const orderResponse = await axios.post(`/api/v1/orders/`, {
        items: items.map((item) => ({
          product_id: item.id,
          quantity: 1,
        })),
        buyer_email: formData.email,
        shipping_address: formData.shipping_address,
      }, {
        params: { channel_id: 'own_store' }
      });

      const orderId = orderResponse.data.id;
      const totalAmount = orderResponse.data.total_amount;

      // Create payment intent
      const paymentResponse = await axios.post(`/api/v1/orders/${orderId}/payment-intent`);
      const clientSecret = paymentResponse.data.client_secret;

      // Confirm payment with Stripe
      const cardElement = elements.getElement(CardElement);
      if (!cardElement) return;

      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            email: formData.email,
          },
        },
      });

      if (result.error) {
        setError(result.error.message || 'Payment failed');
      } else {
        // Confirm payment on backend
        await axios.post(`/api/v1/orders/${orderId}/confirm-payment`);
        clearCart();
        navigate(`/order-confirmation/${orderId}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">Checkout</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <div className="grid grid-cols-3 gap-8">
          {/* Checkout Form */}
          <form onSubmit={handleSubmit} className="col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Delivery Information</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Email</label>
                  <div className="flex items-center border rounded-lg px-3 py-2">
                    <Mail size={20} className="text-gray-400 mr-2" />
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="your@email.com"
                      required
                      className="w-full outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-700 font-medium mb-2">Shipping Address</label>
                  <div className="flex gap-3 items-start">
                    <MapPin size={20} className="text-gray-400 mt-3 flex-shrink-0" />
                    <textarea
                      name="shipping_address"
                      value={formData.shipping_address}
                      onChange={handleChange}
                      placeholder="Street, City, State, Postal Code"
                      required
                      rows={3}
                      className="w-full border rounded-lg px-3 py-2 outline-none"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Payment Information</h2>

              <div className="border rounded-lg p-4 bg-gray-50 mb-6">
                <CardElement
                  options={{
                    style: {
                      base: {
                        fontSize: '16px',
                        color: '#424770',
                        '::placeholder': {
                          color: '#aab7c4',
                        },
                      },
                      invalid: {
                        color: '#9e2146',
                      },
                    },
                  }}
                />
              </div>

              <p className="text-xs text-gray-600 mb-6">
                🔒 Your payment information is secure and encrypted. Using Stripe Sandbox for testing.
              </p>

              <button
                type="submit"
                disabled={loading || !stripe}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 disabled:bg-gray-400 transition"
              >
                {loading ? 'Processing...' : `Pay ₹${total.toFixed(2)}`}
              </button>
            </div>
          </form>

          {/* Order Summary */}
          <div>
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-xl font-bold mb-6 text-gray-800">Order Summary</h2>

              <div className="space-y-2 mb-6 pb-6 border-b max-h-64 overflow-y-auto">
                {items.map((item: any, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="text-gray-600 truncate">{item.name}</span>
                    <span className="font-medium text-gray-800 flex-shrink-0">₹{item.current_price}</span>
                  </div>
                ))}
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">₹{subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax (18%)</span>
                  <span className="font-medium">₹{tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span className="font-medium">₹{shipping.toFixed(2)}</span>
                </div>
              </div>

              <div className="flex justify-between border-t pt-3">
                <span className="font-bold text-gray-800">Total</span>
                <span className="text-2xl font-bold text-blue-600">₹{total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Checkout;
