import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { Search, Filter, Eye, Send, RotateCcw, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const Orders = () => {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [viewOrderModal, setViewOrderModal] = useState(false)
  const [imageLoadErrors, setImageLoadErrors] = useState(new Set())

  useEffect(() => {
    loadOrders()
  }, [])

  const loadOrders = async () => {
    try {
      setLoading(true)
      const response = await adminApi.getOrders(100)
      setOrders(response.data.orders)
    } catch (error) {
      console.error('Failed to load orders:', error)
      toast.error('Failed to load orders')
    } finally {
      setLoading(false)
    }
  }

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await adminApi.updateOrderStatus(orderId, newStatus)
      toast.success('Order status updated')
      loadOrders() // Refresh the list
    } catch (error) {
      console.error('Failed to update order status:', error)
      toast.error('Failed to update order status')
    }
  }

  const submitToChinese = async (orderId) => {
    try {
      await adminApi.submitOrderToChinese(orderId)
      toast.success('Order submitted to Chinese API')
      loadOrders()
    } catch (error) {
      console.error('Failed to submit order:', error)
      toast.error('Failed to submit order to Chinese API')
    }
  }

  const viewOrderDetails = async (order) => {
    try {
      const response = await adminApi.getOrder(order.id)
      setSelectedOrder(response.data.order)
      setViewOrderModal(true)
    } catch (error) {
      console.error('Failed to load order details:', error)
      toast.error('Failed to load order details')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-700 bg-green-100'
      case 'failed': return 'text-red-700 bg-red-100'
      case 'paid': case 'generating': case 'sent_to_chinese': return 'text-blue-700 bg-blue-100'
      case 'printing': return 'text-orange-700 bg-orange-100'
      default: return 'text-gray-700 bg-gray-100'
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

  const handleImageError = (imageId) => {
    setImageLoadErrors(prev => new Set([...prev, imageId]))
  }

  const handleImageLoad = (imageId) => {
    setImageLoadErrors(prev => {
      const newSet = new Set(prev)
      newSet.delete(imageId)
      return newSet
    })
  }

  // Filter orders based on search term and status
  const filteredOrders = orders.filter(order => {
    const matchesSearch = 
      order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.brand?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.model?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.template?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'created', label: 'Created' },
    { value: 'paid', label: 'Paid' },
    { value: 'generating', label: 'Generating' },
    { value: 'sent_to_chinese', label: 'Sent to Chinese' },
    { value: 'printing', label: 'Printing' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
  ]

  const actionOptions = [
    { value: 'paid', label: 'Mark as Paid' },
    { value: 'generating', label: 'Mark as Generating' },
    { value: 'sent_to_chinese', label: 'Mark as Sent to Chinese' },
    { value: 'printing', label: 'Mark as Printing' },
    { value: 'completed', label: 'Mark as Completed' },
    { value: 'failed', label: 'Mark as Failed' },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Orders Management</h1>
        <button onClick={loadOrders} className="btn-primary">
          <RotateCcw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search orders by ID, brand, model, or template..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="sm:w-48">
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Orders Table - Desktop View */}
      <div className="hidden lg:block card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Order Details
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredOrders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {order.id.substring(0, 8)}...
                      </div>
                      {order.queue_number && (
                        <div className="text-xs text-gray-500 font-mono">
                          Queue: {order.queue_number}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {order.brand} {order.model}
                      </div>
                      <div className="text-sm text-gray-500 truncate max-w-32">
                        {order.template}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    £{order.total_amount}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="text-sm">{formatDate(order.created_at).split(',')[0]}</div>
                    <div className="text-xs text-gray-400">{formatDate(order.created_at).split(',')[1]}</div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => viewOrderDetails(order)}
                        className="text-primary-600 hover:text-primary-900 p-1 hover:bg-primary-50 rounded"
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {order.status === 'paid' && (
                        <button
                          onClick={() => submitToChinese(order.id)}
                          className="text-green-600 hover:text-green-900 p-1 hover:bg-green-50 rounded"
                          title="Submit to Chinese API"
                        >
                          <Send className="h-4 w-4" />
                        </button>
                      )}
                      <select
                        onChange={(e) => {
                          if (e.target.value) {
                            updateOrderStatus(order.id, e.target.value)
                            e.target.value = '' // Reset selection
                          }
                        }}
                        className="text-xs border border-gray-300 rounded px-2 py-1 min-w-0 max-w-24"
                        defaultValue=""
                      >
                        <option value="">Status</option>
                        {actionOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label.replace('Mark as ', '')}
                          </option>
                        ))}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredOrders.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium text-gray-900 mb-2">No orders found</p>
            <p className="text-sm text-gray-500">No orders match your current filters</p>
          </div>
        )}
      </div>

      {/* Orders Cards - Mobile View */}
      <div className="lg:hidden space-y-4">
        {filteredOrders.length > 0 ? (
          filteredOrders.map((order) => (
            <div key={order.id} className="card">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      #{order.id.substring(0, 8)}
                    </span>
                    {order.queue_number && (
                      <span className="text-xs text-gray-500 font-mono bg-gray-100 px-2 py-1 rounded">
                        Q: {order.queue_number}
                      </span>
                    )}
                  </div>
                  <div className="text-lg font-semibold text-gray-900 mb-1">
                    {order.brand} {order.model}
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    {order.template}
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="text-lg font-bold text-gray-900 mb-1">
                    £{order.total_amount}
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(order.status)}`}>
                    {order.status}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                  {formatDate(order.created_at)}
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => viewOrderDetails(order)}
                    className="btn-secondary text-xs py-1 px-2"
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View
                  </button>
                  {order.status === 'paid' && (
                    <button
                      onClick={() => submitToChinese(order.id)}
                      className="text-xs bg-green-100 text-green-700 py-1 px-2 rounded hover:bg-green-200 transition-colors"
                    >
                      <Send className="h-3 w-3 mr-1 inline" />
                      Submit
                    </button>
                  )}
                  <select
                    onChange={(e) => {
                      if (e.target.value) {
                        updateOrderStatus(order.id, e.target.value)
                        e.target.value = ''
                      }
                    }}
                    className="text-xs border border-gray-300 rounded px-2 py-1"
                    defaultValue=""
                  >
                    <option value="">Update</option>
                    {actionOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label.replace('Mark as ', '')}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="card text-center py-12 text-gray-500">
            <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium text-gray-900 mb-2">No orders found</p>
            <p className="text-sm text-gray-500">No orders match your current filters</p>
          </div>
        )}
      </div>

      {/* Order Details Modal */}
      {viewOrderModal && selectedOrder && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={() => setViewOrderModal(false)} />
            <div className="relative bg-white rounded-lg max-w-2xl w-full p-6 max-h-screen overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Order Details</h3>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Order ID</label>
                    <p className="text-sm text-gray-900 font-mono">{selectedOrder.id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Status</label>
                    <p className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedOrder.status)}`}>
                      {selectedOrder.status}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Product</label>
                    <p className="text-sm text-gray-900">{selectedOrder.brand} {selectedOrder.model}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Template</label>
                    <p className="text-sm text-gray-900">{selectedOrder.template}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Amount</label>
                    <p className="text-sm text-gray-900">£{selectedOrder.total_amount}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Payment Status</label>
                    <p className="text-sm text-gray-900">{selectedOrder.payment_status}</p>
                  </div>
                </div>

                {selectedOrder.images && selectedOrder.images.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-600 block mb-3">Generated Images ({selectedOrder.images.length})</label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {selectedOrder.images.map((image, index) => (
                        <div key={image.id} className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                          <div className="aspect-square mb-2 bg-white rounded overflow-hidden">
                            {imageLoadErrors.has(image.id) ? (
                              <div className="w-full h-full flex flex-col items-center justify-center text-gray-400">
                                <AlertCircle className="h-8 w-8 mb-2" />
                                <span className="text-xs text-center">Image not found</span>
                              </div>
                            ) : (
                              <img
                                src={adminApi.getImageUrl(image.image_path.split('/').pop())}
                                alt={`Generated image ${index + 1}`}
                                className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-pointer"
                                onError={() => handleImageError(image.id)}
                                onLoad={() => handleImageLoad(image.id)}
                                loading="lazy"
                              />
                            )}
                          </div>
                          <div className="flex items-center justify-between">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              image.image_type === 'generated' ? 'text-green-700 bg-green-100' :
                              image.image_type === 'uploaded' ? 'text-blue-700 bg-blue-100' :
                              image.image_type === 'final' ? 'text-purple-700 bg-purple-100' :
                              'text-gray-700 bg-gray-100'
                            }`}>
                              {image.image_type}
                            </span>
                            <span className="text-xs text-gray-500">#{index + 1}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-sm font-medium text-gray-600">Created At</label>
                  <p className="text-sm text-gray-900">{formatDate(selectedOrder.created_at)}</p>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setViewOrderModal(false)}
                  className="btn-secondary"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Orders