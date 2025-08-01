import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { ShoppingBag, Clock, CheckCircle, XCircle, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [recentOrders, setRecentOrders] = useState([])
  const [templateAnalytics, setTemplateAnalytics] = useState([])
  const [loading, setLoading] = useState(true)
  const [health, setHealth] = useState(null)
  const [dbStats, setDbStats] = useState(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load stats, orders, template analytics, and database stats in parallel
      const [statsResponse, ordersResponse, healthResponse, templateAnalyticsResponse, dbStatsResponse] = await Promise.all([
        adminApi.getStats(),
        adminApi.getOrders(10), // Get last 10 orders
        adminApi.getHealth(),
        adminApi.getTemplateAnalytics().catch(err => {
          console.warn('Template analytics not available:', err)
          return { data: { analytics: [] } }
        }),
        adminApi.getDatabaseStats().catch(err => {
          console.warn('Database stats not available:', err)
          return { data: { stats: null } }
        })
      ])
      
      setStats(statsResponse.data.stats)
      setRecentOrders(ordersResponse.data.orders)
      setHealth(healthResponse.data)
      setTemplateAnalytics(templateAnalyticsResponse.data.analytics || [])
      setDbStats(dbStatsResponse.data.stats)
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, icon: Icon, color = 'primary' }) => {
    const colorClasses = {
      primary: 'bg-primary-100 text-primary-600',
      orange: 'bg-orange-100 text-orange-600', 
      green: 'bg-green-100 text-green-600',
      red: 'bg-red-100 text-red-600'
    }
    
    return (
      <div className="stat-card group hover:shadow-md transition-all duration-200 border-l-4 border-l-gray-200 hover:border-l-primary-500">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 group-hover:text-primary-700 transition-colors">{value || 0}</p>
          <div className="mt-2">
            <span className="text-xs text-gray-500">Total count</span>
          </div>
        </div>
        <div className={`p-4 rounded-xl ${colorClasses[color]} group-hover:scale-110 transition-transform duration-200`}>
          <Icon className="h-8 w-8" />
        </div>
      </div>
    )
  }

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

  // Use real template analytics data or fallback to empty array
  const chartData = templateAnalytics.length > 0 ? templateAnalytics.map(item => ({
    name: item.template_name || item.name,
    orders: item.order_count || item.orders || 0
  })) : []

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
      {stats ? (
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
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1,2,3,4].map(i => (
            <div key={i} className="stat-card animate-pulse">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-8 bg-gray-300 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-20"></div>
              </div>
              <div className="w-16 h-16 bg-gray-200 rounded-xl"></div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Template Usage Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Template Usage Analytics</h3>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-primary-500 rounded"></div>
              <span className="text-sm text-gray-600">Orders</span>
            </div>
          </div>
          
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar 
                  dataKey="orders" 
                  fill="#3B82F6" 
                  radius={[4, 4, 0, 0]}
                  maxBarSize={60}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium text-gray-900 mb-2">No Analytics Data</p>
                <p className="text-sm text-gray-500 mb-4">Template usage analytics will appear here once orders are placed.</p>
                <button 
                  onClick={loadDashboardData}
                  className="btn-secondary"
                >
                  Refresh Data
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Recent Orders */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Recent Orders</h3>
            <span className="text-sm text-gray-500">Last 10 orders</span>
          </div>
          <div className="space-y-3">
            {recentOrders.length > 0 ? (
              recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg border border-transparent hover:border-gray-200 transition-all duration-200">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-medium text-gray-900 truncate">
                        {order.brand} {order.model}
                      </span>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${getStatusColor(order.status)}`}>
                        {order.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mb-1">
                      {order.template} • <span className="font-medium text-green-600">£{order.total_amount}</span>
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatDate(order.created_at)}
                    </div>
                  </div>
                  {order.queue_number && (
                    <div className="ml-4 flex-shrink-0">
                      <div className="text-sm font-mono text-gray-700 bg-white px-3 py-1 rounded-md border border-gray-200">
                        Q: {order.queue_number}
                      </div>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-gray-500">
                <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No recent orders found</p>
                <p className="text-sm mt-1">New orders will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard