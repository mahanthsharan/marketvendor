import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Package, ShoppingCart, DollarSign, TrendingUp } from 'lucide-react';

function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    revenue: 0,
    pendingOrders: 0,
  });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [productsRes, ordersRes] = await Promise.all([
        axios.get('/api/v1/products/seller/products?limit=1'),
        axios.get('/api/v1/orders/'),
      ]);

      // Calculate stats
      const orders = ordersRes.data;
      const pendingCount = orders.filter((o: any) => o.status === 'pending').length;
      const totalRevenue = orders
        .filter((o: any) => o.payment_status === 'completed')
        .reduce((sum: number, o: any) => sum + o.total_amount, 0);

      setStats({
        totalProducts: productsRes.data.length,
        totalOrders: orders.length,
        revenue: totalRevenue,
        pendingOrders: pendingCount,
      });

      // Mock chart data
      setChartData([
        { name: 'Mon', sales: 4000, orders: 24 },
        { name: 'Tue', sales: 3000, orders: 13 },
        { name: 'Wed', sales: 2000, orders: 9 },
        { name: 'Thu', sales: 2780, orders: 39 },
        { name: 'Fri', sales: 1890, orders: 23 },
        { name: 'Sat', sales: 2390, orders: 22 },
        { name: 'Sun', sales: 3490, orders: 29 },
      ]);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Products</p>
              <p className="text-3xl font-bold text-gray-800">{stats.totalProducts}</p>
            </div>
            <Package size={40} className="text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Orders</p>
              <p className="text-3xl font-bold text-gray-800">{stats.totalOrders}</p>
            </div>
            <ShoppingCart size={40} className="text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Revenue</p>
              <p className="text-3xl font-bold text-gray-800">₹{(stats.revenue).toLocaleString()}</p>
            </div>
            <DollarSign size={40} className="text-yellow-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Pending Orders</p>
              <p className="text-3xl font-bold text-gray-800">{stats.pendingOrders}</p>
            </div>
            <TrendingUp size={40} className="text-red-500" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-bold mb-4 text-gray-800">Weekly Sales</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sales" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-bold mb-4 text-gray-800">Order Status</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Completed', value: 40 },
                  { name: 'Pending', value: 25 },
                  { name: 'Cancelled', value: 15 },
                  { name: 'Processing', value: 20 },
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                <Cell fill="#3b82f6" />
                <Cell fill="#10b981" />
                <Cell fill="#ef4444" />
                <Cell fill="#f59e0b" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
