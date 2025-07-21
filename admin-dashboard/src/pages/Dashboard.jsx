import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { ShoppingBag, Clock, CheckCircle, XCircle, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [recentOrders, setRecentOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load stats and orders in parallel
      const [statsResponse, ordersResponse, healthResponse] = await Promise.all([
        adminApi.getStats(),
        adminApi.getOrders(10), // Get last 10 orders
        adminApi.getHealth()
      ])
      
      setStats(statsResponse.data.stats)
      setRecentOrders(ordersResponse.data.orders)
      setHealth(healthResponse.data)
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, icon: Icon, color = 'primary' }) => (
    <div className="stat-card">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
      <div className={`p-3 rounded-full bg-${color}-100`}>
        <Icon className={`h-6 w-6 text-${color}-600`} />
      </div>
    </div>
  )

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'failed': return 'text-red-600 bg-red-100'
      case 'paid': case 'generating': case 'sent_to_chinese': return 'text-blue-600 bg-blue-100'
      case 'printing': return 'text-orange-600 bg-orange-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Mock chart data for template usage
  const chartData = [
    { name: 'Classic', orders: 45 },
    { name: 'Funny Toon', orders: 38 },
    { name: 'Retro Remix', orders: 32 },
    { name: 'Cover Shoot', orders: 28 },
    { name: 'Glitch Pro', orders: 24 },
    { name: 'Footy Fan', orders: 20 },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={loadDashboardData}
          className="btn-primary"
        >
          Refresh Data
        </button>
      </div>

      {/* Health Status */}
      {health && (
        <div className={`p-4 rounded-lg ${health.status === 'healthy' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <div className="flex items-center">
            {health.status === 'healthy' ? (
              <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            ) : (
              <XCircle className="h-5 w-5 text-red-500 mr-2" />
            )}
            <span className={`font-medium ${health.status === 'healthy' ? 'text-green-800' : 'text-red-800'}`}>
              System Status: {health.status === 'healthy' ? 'All systems operational' : 'Issues detected'}
            </span>
          </div>
          {health.status !== 'healthy' && (
            <div className="mt-2 text-sm text-red-700">
              OpenAI: {health.openai?.status}, Database: {health.database?.status}
            </div>
          )}
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Orders"
            value={stats.total_orders}
            icon={ShoppingBag}
            color="primary"
          />
          <StatCard
            title="Pending Orders"
            value={stats.pending_orders}
            icon={Clock}
            color="orange"
          />
          <StatCard
            title="Completed Orders"
            value={stats.completed_orders}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            title="Failed Orders"
            value={stats.failed_orders}
            icon={XCircle}
            color="red"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Template Usage Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Template Usage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="orders" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Orders */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Orders</h3>
          <div className="space-y-3">
            {recentOrders.map((order) => (
              <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">
                      {order.brand} {order.model}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {order.template} • £{order.total_amount}
                  </div>
                  <div className="text-xs text-gray-400">
                    {formatDate(order.created_at)}
                  </div>
                </div>
                {order.queue_number && (
                  <div className="text-sm font-mono text-gray-600 bg-white px-2 py-1 rounded">
                    {order.queue_number}
                  </div>
                )}
              </div>
            ))}
          </div>
          {recentOrders.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No recent orders found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard