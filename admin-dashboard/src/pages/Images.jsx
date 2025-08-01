import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { Image as ImageIcon, Download, Eye, X, AlertCircle, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'

const Images = () => {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedImage, setSelectedImage] = useState(null)
  const [viewImageModal, setViewImageModal] = useState(false)
  const [imageTypeFilter, setImageTypeFilter] = useState('all')
  const [imageLoadErrors, setImageLoadErrors] = useState(new Set())

  useEffect(() => {
    loadImages()
  }, [])

  useEffect(() => {
    if (imageTypeFilter) {
      loadImages()
    }
  }, [imageTypeFilter])

  const loadImages = async () => {
    try {
      setLoading(true)
      // Use dedicated images API if available, fallback to orders method
      const response = await adminApi.getImages(200, imageTypeFilter)
        .catch(async (error) => {
          console.warn('Dedicated images API not available, falling back to orders method:', error)
          // Fallback to the old method if the new endpoint doesn't exist
          const ordersResponse = await adminApi.getOrders(100)
          const ordersWithImages = ordersResponse.data.orders.filter(order => 
            order.images && order.images.length > 0
          )
          // Transform orders data to match images format
          const allImagesFromOrders = ordersWithImages.flatMap(order => 
            (order.images || []).map(image => ({ ...image, order }))
          )
          return { data: { images: allImagesFromOrders } }
        })
      
      setImages(response.data.images || [])
    } catch (error) {
      console.error('Failed to load images:', error)
      toast.error('Failed to load images')
    } finally {
      setLoading(false)
    }
  }

  const viewImage = (image, order) => {
    setSelectedImage({ ...image, order })
    setViewImageModal(true)
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

  // Sort images by creation date
  const allImages = images.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

  // Filter images by type (if not already filtered by API)
  const filteredImages = imageTypeFilter === 'all' 
    ? allImages 
    : allImages.filter(image => image.image_type === imageTypeFilter)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Images Gallery</h1>
          <p className="text-sm text-gray-600">Browse and manage all generated images</p>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <select 
            value={imageTypeFilter} 
            onChange={(e) => setImageTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
          >
            <option value="all">All Images</option>
            <option value="generated">AI Generated</option>
            <option value="uploaded">Uploaded</option>
            <option value="final">Final</option>
          </select>
          <button onClick={loadImages} className="btn-primary whitespace-nowrap">
            <RotateCcw className="h-4 w-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      <div className="card">
        <div className="mb-6">
          <div className="flex flex-wrap items-center gap-4 p-4 bg-gray-50 rounded-lg border">
            {imageTypeFilter === 'all' ? (
              <>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-600 rounded"></div>
                  <span className="text-sm font-medium text-gray-700">Total: {allImages.length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span className="text-sm text-gray-600">Generated: {allImages.filter(img => img.image_type === 'generated').length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded"></div>
                  <span className="text-sm text-gray-600">Uploaded: {allImages.filter(img => img.image_type === 'uploaded').length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-purple-500 rounded"></div>
                  <span className="text-sm text-gray-600">Final: {allImages.filter(img => img.image_type === 'final').length}</span>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded ${
                  imageTypeFilter === 'generated' ? 'bg-green-500' :
                  imageTypeFilter === 'uploaded' ? 'bg-blue-500' :
                  imageTypeFilter === 'final' ? 'bg-purple-500' : 'bg-gray-500'
                }`}></div>
                <span className="text-sm font-medium text-gray-700">Showing {filteredImages.length} {imageTypeFilter} images</span>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
          {filteredImages.map((image) => {
            const filename = image.image_path ? image.image_path.split('/').pop() : 'unknown'
            const imageUrl = adminApi.getImageUrl(filename)
            const orderInfo = image.order || { 
              template: image.template || 'Unknown Template', 
              brand: image.brand || 'Unknown Brand', 
              model: image.model || 'Unknown Model' 
            }
            
            return (
              <div key={image.id} className="group relative bg-gray-100 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
                <div className="aspect-square">
                  {imageLoadErrors.has(image.id) ? (
                    <div className="w-full h-full flex flex-col items-center justify-center text-gray-400 bg-gray-50">
                      <AlertCircle className="h-8 w-8 mb-2" />
                      <span className="text-xs text-center px-2">Image not found</span>
                    </div>
                  ) : (
                    <img
                      src={imageUrl}
                      alt={`Generated for ${orderInfo.template}`}
                      className="w-full h-full object-cover cursor-pointer transition-transform duration-200 group-hover:scale-105"
                      onClick={() => viewImage(image, orderInfo)}
                      onError={() => handleImageError(image.id)}
                      onLoad={() => handleImageLoad(image.id)}
                      loading="lazy"
                    />
                  )}
                </div>
                
                {/* Overlay with actions - only show if image loaded successfully */}
                {!imageLoadErrors.has(image.id) && (
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => viewImage(image, image.order)}
                        className="p-2 bg-white rounded-full text-gray-700 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                        title="View image"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => downloadImage(image.image_path)}
                        className="p-2 bg-white rounded-full text-gray-700 hover:text-green-600 hover:bg-green-50 transition-colors"
                        title="Download image"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}

                {/* Image info */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/50 to-transparent p-2">
                  <div className="text-white text-xs">
                    <div className="font-medium truncate">{orderInfo.template}</div>
                    <div className="opacity-90 text-gray-200">{orderInfo.brand} {orderInfo.model}</div>
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
          <div className="text-center py-16 text-gray-500">
            <div className="max-w-sm mx-auto">
              <ImageIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {allImages.length === 0 ? "No images found" : `No ${imageTypeFilter} images`}
              </h3>
              <p className="text-sm text-gray-500">
                {allImages.length === 0 
                  ? "Images will appear here once orders with generated images are created." 
                  : `Try selecting a different image type or refresh the gallery.`
                }
              </p>
              {allImages.length === 0 && (
                <button 
                  onClick={loadImages}
                  className="mt-4 btn-secondary inline-flex items-center"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Refresh Gallery
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Image Detail Modal */}
      {viewImageModal && selectedImage && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={() => setViewImageModal(false)} />
            <div className="relative bg-white rounded-lg max-w-5xl w-full p-6 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Image Details</h3>
                <button
                  onClick={() => setViewImageModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                {/* Image */}
                <div className="flex justify-center">
                  {imageLoadErrors.has(selectedImage.id) ? (
                    <div className="w-full max-w-md h-64 flex flex-col items-center justify-center text-gray-400 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                      <AlertCircle className="h-12 w-12 mb-4" />
                      <span className="text-sm text-center">Image could not be loaded</span>
                      <span className="text-xs text-gray-500 mt-1">File: {selectedImage.image_path.split('/').pop()}</span>
                    </div>
                  ) : (
                    <img
                      src={adminApi.getImageUrl(selectedImage.image_path.split('/').pop())}
                      alt="Full size image"
                      className="w-full max-w-lg rounded-lg shadow-lg border border-gray-200"
                      onError={() => handleImageError(selectedImage.id)}
                      onLoad={() => handleImageLoad(selectedImage.id)}
                    />
                  )}
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