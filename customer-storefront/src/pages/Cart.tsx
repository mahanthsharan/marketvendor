import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, ArrowLeft, ShoppingCart } from 'lucide-react';
import useCartStore from '../store/cartStore';

function Cart() {
  const navigate = useNavigate();
  const { items, removeFromCart, clearCart } = useCartStore();

  const subtotal = items.reduce((sum, item) => sum + item.current_price, 0);
  const tax = subtotal * 0.18;
  const shipping = 50;
  const total = subtotal + tax + shipping;

  if (items.length === 0) {
    return (
      <div className="p-6">
        <div className="max-w-2xl mx-auto text-center py-12">
          <ShoppingCart size={64} className="mx-auto text-gray-300 mb-4" />
          <h1 className="text-3xl font-bold text-gray-800 mb-4">Your Cart is Empty</h1>
          <p className="text-gray-600 mb-8">Add some products to get started!</p>
          <button
            onClick={() => navigate('/products')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700"
          >
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-6"
        >
          <ArrowLeft size={20} /> Back
        </button>

        <h1 className="text-3xl font-bold mb-8 text-gray-800">Shopping Cart</h1>

        <div className="grid grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="col-span-2">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Product</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Price</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item: any, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <p className="font-medium text-gray-800">{item.name}</p>
                        <p className="text-sm text-gray-600">{item.sku}</p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-semibold text-gray-800">₹{item.current_price}</p>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => removeFromCart(index)}
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

            <button
              onClick={clearCart}
              className="mt-4 text-red-600 hover:text-red-800 font-medium"
            >
              Clear Cart
            </button>
          </div>

          {/* Order Summary */}
          <div>
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-xl font-bold mb-6 text-gray-800">Order Summary</h2>

              <div className="space-y-3 mb-6 pb-6 border-b">
                <div className="flex justify-between">
                  <span className="text-gray-600">Items ({items.length})</span>
                  <span className="font-medium text-gray-800">₹{subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax (18%)</span>
                  <span className="font-medium text-gray-800">₹{tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span className="font-medium text-gray-800">₹{shipping.toFixed(2)}</span>
                </div>
              </div>

              <div className="flex justify-between mb-6 text-lg font-bold">
                <span className="text-gray-800">Total</span>
                <span className="text-blue-600">₹{total.toFixed(2)}</span>
              </div>

              <button
                onClick={() => navigate('/checkout')}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition"
              >
                Proceed to Checkout
              </button>

              <button
                onClick={() => navigate('/products')}
                className="w-full mt-3 border border-gray-300 text-gray-700 py-3 rounded-lg font-bold hover:bg-gray-50 transition"
              >
                Continue Shopping
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Cart;
