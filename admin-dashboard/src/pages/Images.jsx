import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { Image as ImageIcon, Download, Eye, X } from 'lucide-react'
import toast from 'react-hot-toast'

const Images = () => {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedImage, setSelectedImage] = useState(null)
  const [viewImageModal, setViewImageModal] = useState(false)
  const [imageTypeFilter, setImageTypeFilter] = useState('all')

  useEffect(() => {
    loadOrdersWithImages()
  }, [])

  const loadOrdersWithImages = async () => {
    try {
      setLoading(true)
      const response = await adminApi.getOrders(100)
      // Filter orders that have images
      const ordersWithImages = response.data.orders.filter(order => 
        order.images && order.images.length > 0
      )
      setOrders(ordersWithImages)
    } catch (error) {
      console.error('Failed to load orders with images:', error)
      toast.error('Failed to load images')
    } finally {
      setLoading(false)
    }
  }

  const viewImage = (image, order) => {
    setSelectedImage({ ...image, order })
    setViewImageModal(true)
  }

  const downloadImage = (imagePath) => {
    const filename = imagePath.split('/').pop()
    const imageUrl = adminApi.getImageUrl(filename)
    
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
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

  const getImageTypeColor = (type) => {
    switch (type) {
      case 'generated': return 'text-green-700 bg-green-100'
      case 'uploaded': return 'text-blue-700 bg-blue-100'
      case 'final': return 'text-purple-700 bg-purple-100'
      default: return 'text-gray-700 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Flatten all images from all orders
  const allImages = orders.flatMap(order => 
    (order.images || []).map(image => ({ ...image, order }))
  ).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

  // Filter images by type
  const filteredImages = imageTypeFilter === 'all' 
    ? allImages 
    : allImages.filter(image => image.image_type === imageTypeFilter)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Images Gallery</h1>
        <div className="flex items-center space-x-3">
          <select 
            value={imageTypeFilter} 
            onChange={(e) => setImageTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Images</option>
            <option value="generated">AI Generated</option>
            <option value="uploaded">Uploaded</option>
            <option value="final">Final</option>
          </select>
          <button onClick={loadOrdersWithImages} className="btn-primary">
            Refresh Images
          </button>
        </div>
      </div>

      <div className="card">
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            {imageTypeFilter === 'all' ? (
              <>
                Total images: {allImages.length} • 
                Generated: {allImages.filter(img => img.image_type === 'generated').length} • 
                Uploaded: {allImages.filter(img => img.image_type === 'uploaded').length} • 
                Final: {allImages.filter(img => img.image_type === 'final').length}
              </>
            ) : (
              <>Showing {filteredImages.length} {imageTypeFilter} images</>
            )}
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          {filteredImages.map((image) => {
            const filename = image.image_path.split('/').pop()
            const imageUrl = adminApi.getImageUrl(filename)
            
            return (
              <div key={image.id} className="group relative bg-gray-100 rounded-lg overflow-hidden">
                <div className="aspect-square">
                  <img
                    src={imageUrl}
                    alt={`Generated for ${image.order.template}`}
                    className="w-full h-full object-cover cursor-pointer"
                    onClick={() => viewImage(image, image.order)}
                  />
                </div>
                
                {/* Overlay with actions */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => viewImage(image, image.order)}
                      className="p-2 bg-white rounded-full text-gray-700 hover:text-primary-600"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => downloadImage(image.image_path)}
                      className="p-2 bg-white rounded-full text-gray-700 hover:text-green-600"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Image info */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
                  <div className="text-white text-xs">
                    <div className="font-medium truncate">{image.order.template}</div>
                    <div className="opacity-75">{image.order.brand} {image.order.model}</div>
                  </div>
                </div>

                {/* Image type badge */}
                <div className="absolute top-2 right-2">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getImageTypeColor(image.image_type)}`}>
                    {image.image_type}
                  </span>
                </div>
              </div>
            )
          })}
        </div>

        {filteredImages.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <ImageIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>
              {allImages.length === 0 
                ? "No images found" 
                : `No ${imageTypeFilter} images found`
              }
            </p>
          </div>
        )}
      </div>

      {/* Image Detail Modal */}
      {viewImageModal && selectedImage && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={() => setViewImageModal(false)} />
            <div className="relative bg-white rounded-lg max-w-4xl w-full p-6 max-h-screen overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Image Details</h3>
                <button
                  onClick={() => setViewImageModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Image */}
                <div>
                  <img
                    src={adminApi.getImageUrl(selectedImage.image_path.split('/').pop())}
                    alt="Full size image"
                    className="w-full rounded-lg shadow-lg"
                  />
                </div>

                {/* Details */}
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Order Information</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Order ID:</span> {selectedImage.order.id.substring(0, 8)}...</div>
                      <div><span className="font-medium">Product:</span> {selectedImage.order.brand} {selectedImage.order.model}</div>
                      <div><span className="font-medium">Template:</span> {selectedImage.order.template}</div>
                      <div><span className="font-medium">Amount:</span> £{selectedImage.order.total_amount}</div>
                      <div><span className="font-medium">Status:</span> {selectedImage.order.status}</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Image Information</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Type:</span> 
                        <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getImageTypeColor(selectedImage.image_type)}`}>
                          {selectedImage.image_type}
                        </span>
                      </div>
                      <div><span className="font-medium">Created:</span> {formatDate(selectedImage.created_at)}</div>
                      <div><span className="font-medium">File:</span> {selectedImage.image_path.split('/').pop()}</div>
                    </div>
                  </div>

                  {selectedImage.ai_params && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">AI Parameters</h4>
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                          {JSON.stringify(selectedImage.ai_params, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-3">
                    <button
                      onClick={() => downloadImage(selectedImage.image_path)}
                      className="btn-primary flex items-center"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Images