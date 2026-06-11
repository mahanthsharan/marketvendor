import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { TrendingUp } from 'lucide-react';

function PricingRules() {
  const [products, setProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [productsRes, recommendationsRes] = await Promise.all([
        axios.get('/api/v1/products/seller/products'),
        axios.get('/api/v1/pricing/recommendations'),
      ]);
      setProducts(productsRes.data);
      setRecommendations(recommendationsRes.data.recommendations);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyRecommendation = async (productId: string) => {
    try {
      await axios.post(`/api/v1/pricing/${productId}/recalculate-price`);
      fetchData();
    } catch (error) {
      console.error('Failed to apply recommendation:', error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800 flex items-center gap-2">
        <TrendingUp size={32} /> Dynamic Pricing
      </h1>

      {loading ? (
        <div>Loading...</div>
      ) : recommendations.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">No pricing recommendations available yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec: any) => (
            <div key={rec.product_id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-800">{rec.product_name}</h3>
                  <p className="text-sm text-gray-600">Demand Score: {rec.demand_score}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  rec.action === 'increase'
                    ? 'bg-green-100 text-green-800'
                    : rec.action === 'decrease'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {rec.action.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-gray-600 text-sm">Current Price</p>
                  <p className="text-2xl font-bold text-gray-800">₹{rec.current_price}</p>
                </div>
                <div className="flex items-center justify-center">
                  <div className="text-3xl text-gray-400">→</div>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Recommended Price</p>
                  <p className="text-2xl font-bold text-blue-600">₹{rec.recommended_price.toFixed(2)}</p>
                </div>
              </div>

              <button
                onClick={() => applyRecommendation(rec.product_id)}
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Apply Recommendation
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PricingRules;
