import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { Smartphone, Package, Edit3, Save, X } from 'lucide-react'
import toast from 'react-hot-toast'

const Brands = () => {
  const [brands, setBrands] = useState([])
  const [selectedBrand, setSelectedBrand] = useState(null)
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingModel, setEditingModel] = useState(null)

  useEffect(() => {
    loadBrands()
  }, [])

  useEffect(() => {
    if (selectedBrand) {
      loadModels(selectedBrand.id)
    }
  }, [selectedBrand])

  const loadBrands = async () => {
    try {
      setLoading(true)
      const response = await adminApi.getBrands(true)
      setBrands(response.data.brands)
      if (response.data.brands.length > 0) {
        setSelectedBrand(response.data.brands[0])
      }
    } catch (error) {
      console.error('Failed to load brands:', error)
      toast.error('Failed to load brands')
    } finally {
      setLoading(false)
    }
  }

  const loadModels = async (brandId) => {
    try {
      const response = await adminApi.getModels(brandId, true)
      setModels(response.data.models)
    } catch (error) {
      console.error('Failed to load models:', error)
      toast.error('Failed to load models')
    }
  }

  const updateStock = async (modelId, newStock) => {
    try {
      await adminApi.updateModelStock(modelId, newStock)
      toast.success('Stock updated successfully')
      loadModels(selectedBrand.id) // Refresh models
    } catch (error) {
      console.error('Failed to update stock:', error)
      toast.error('Failed to update stock')
    }
  }


  const handleStockChange = (modelId, value) => {
    const stock = parseInt(value)
    if (stock >= 0) {
      updateStock(modelId, stock)
    }
  }


  const startEditing = (model) => {
    setEditingModel({
      id: model.id,
      stock: model.stock
    })
  }

  const saveEditing = () => {
    if (editingModel) {
      updateStock(editingModel.id, editingModel.stock)
      setEditingModel(null)
    }
  }

  const cancelEditing = () => {
    setEditingModel(null)
  }

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
        <h1 className="text-2xl font-bold text-gray-900">Brands & Models Management</h1>
        <button onClick={loadBrands} className="btn-primary">
          Refresh Data
        </button>
      </div>

      {/* Mobile Brand Selector */}
      <div className="lg:hidden mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select Brand</label>
        <select
          value={selectedBrand?.id || ''}
          onChange={(e) => {
            const brand = brands.find(b => b.id === e.target.value)
            setSelectedBrand(brand)
          }}
          className="w-full input-field"
        >
          <option value="">Choose a brand...</option>
          {brands.map((brand) => (
            <option key={brand.id} value={brand.id}>
              {brand.display_name} ({brand.is_available ? 'Available' : 'Unavailable'})
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Brands Sidebar - Desktop Only */}
        <div className="hidden lg:block lg:col-span-1">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Phone Brands</h3>
            <div className="space-y-2">
              {brands.map((brand) => (
                <button
                  key={brand.id}
                  onClick={() => setSelectedBrand(brand)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedBrand?.id === brand.id
                      ? 'bg-primary-100 text-primary-700 border border-primary-200'
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center">
                    <Smartphone className="h-5 w-5 mr-3" />
                    <div>
                      <div className="font-medium">{brand.display_name}</div>
                      <div className="text-sm opacity-75">
                        {brand.is_available ? 'Available' : 'Unavailable'}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Models Management */}
        <div className="lg:col-span-3">
          {selectedBrand ? (
            <div className="card">
              <div className="flex items-center mb-6">
                <div 
                  className="w-4 h-4 rounded-full mr-3" 
                  style={{ backgroundColor: selectedBrand.frame_color }}
                ></div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {selectedBrand.display_name} Models
                </h3>
                <span className="ml-auto text-sm text-gray-500">
                  {models.length} models
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Model
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Chinese Model ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Stock
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {models.map((model) => {
                      const isEditing = editingModel?.id === model.id
                      return (
                        <tr key={model.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <Package className="h-5 w-5 text-gray-400 mr-3" />
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {model.display_name}
                                </div>
                                <div className="text-sm text-gray-500">
                                  ID: {model.id}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                            {model.chinese_model_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {isEditing ? (
                              <input
                                type="number"
                                min="0"
                                value={editingModel.stock}
                                onChange={(e) => setEditingModel({
                                  ...editingModel,
                                  stock: parseInt(e.target.value) || 0
                                })}
                                className="w-16 px-2 py-1 text-sm border border-gray-300 rounded"
                              />
                            ) : (
                              <span className={`text-sm font-medium ${
                                model.stock > 10 ? 'text-green-600' :
                                model.stock > 0 ? 'text-orange-600' : 'text-red-600'
                              }`}>
                                {model.stock}
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              model.is_available && model.stock > 0
                                ? 'text-green-700 bg-green-100'
                                : 'text-red-700 bg-red-100'
                            }`}>
                              {model.is_available && model.stock > 0 ? 'Available' : 'Unavailable'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            {isEditing ? (
                              <div className="flex space-x-2">
                                <button
                                  onClick={saveEditing}
                                  className="text-green-600 hover:text-green-900"
                                >
                                  <Save className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={cancelEditing}
                                  className="text-red-600 hover:text-red-900"
                                >
                                  <X className="h-4 w-4" />
                                </button>
                              </div>
                            ) : (
                              <button
                                onClick={() => startEditing(model)}
                                className="text-primary-600 hover:text-primary-900"
                              >
                                <Edit3 className="h-4 w-4" />
                              </button>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              {models.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  No models found for this brand
                </div>
              )}
            </div>
          ) : (
            <div className="card">
              <div className="text-center py-12 text-gray-500">
                Select a brand to view its models
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Brands