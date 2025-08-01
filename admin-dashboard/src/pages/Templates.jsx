import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { Palette, Edit3, Save, X } from 'lucide-react'
import toast from 'react-hot-toast'

const Templates = () => {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingTemplate, setEditingTemplate] = useState(null)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      setLoading(true)
      const response = await adminApi.getTemplates(true)
      setTemplates(response.data.templates)
    } catch (error) {
      console.error('Failed to load templates:', error)
      toast.error('Failed to load templates')
    } finally {
      setLoading(false)
    }
  }

  const updatePrice = async (templateId, newPrice) => {
    try {
      await adminApi.updateTemplatePrice(templateId, parseFloat(newPrice))
      toast.success('Template price updated successfully')
      loadTemplates() // Refresh templates
    } catch (error) {
      console.error('Failed to update template price:', error)
      toast.error('Failed to update template price')
    }
  }

  const startEditing = (template) => {
    setEditingTemplate({
      id: template.id,
      price: template.price
    })
  }

  const saveEditing = () => {
    if (editingTemplate) {
      updatePrice(editingTemplate.id, editingTemplate.price)
      setEditingTemplate(null)
    }
  }

  const cancelEditing = () => {
    setEditingTemplate(null)
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'basic': return 'text-blue-700 bg-blue-100'
      case 'ai': return 'text-purple-700 bg-purple-100'
      case 'film': return 'text-green-700 bg-green-100'
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Templates Management</h1>
        <button onClick={loadTemplates} className="btn-primary">
          Refresh Data
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
        {templates.map((template) => {
          const isEditing = editingTemplate?.id === template.id
          return (
            <div key={template.id} className="card hover:shadow-md transition-shadow duration-200">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <Palette className="h-6 w-6 text-primary-500 mr-3" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCategoryColor(template.category)}`}>
                      {template.category}
                    </span>
                  </div>
                </div>
                <div className="flex items-center">
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
                      onClick={() => startEditing(template)}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      <Edit3 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">{template.description}</p>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-600">Price:</span>
                  {isEditing ? (
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={editingTemplate.price}
                      onChange={(e) => setEditingTemplate({
                        ...editingTemplate,
                        price: parseFloat(e.target.value) || 0
                      })}
                      className="w-24 px-2 py-1 text-sm border border-gray-300 rounded"
                    />
                  ) : (
                    <span className="text-lg font-bold text-gray-900">{template.display_price}</span>
                  )}
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-600">Image Count:</span>
                  <span className="text-sm text-gray-900">{template.image_count}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-600">Status:</span>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    template.is_active ? 'text-green-700 bg-green-100' : 'text-red-700 bg-red-100'
                  }`}>
                    {template.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                {template.features && template.features.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-gray-600 block mb-2">Features:</span>
                    <div className="space-y-1">
                      {template.features.map((feature, index) => (
                        <div key={index} className="text-xs text-gray-500 flex items-center">
                          <div className="w-1 h-1 bg-gray-400 rounded-full mr-2"></div>
                          {feature}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {templates.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No templates found
        </div>
      )}
    </div>
  )
}

export default Templates