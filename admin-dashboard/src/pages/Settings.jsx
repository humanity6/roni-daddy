import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { Type, Palette, Users, Database, Wifi, X } from 'lucide-react'
import toast from 'react-hot-toast'

// Font Modal Component
const FontModal = ({ mode, font, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: font?.name || '',
    css_style: font?.css_style || '',
    font_weight: font?.font_weight || '400',
    is_google_font: font?.is_google_font || false,
    google_font_url: font?.google_font_url || '',
    display_order: font?.display_order || 0,
    is_active: font?.is_active ?? true
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (mode === 'create') {
        await adminApi.createFont(formData)
        toast.success('Font created successfully')
      } else {
        await adminApi.updateFont(font.id, formData)
        toast.success('Font updated successfully')
      }
      onSuccess()
    } catch (error) {
      console.error('Font operation failed:', error)
      toast.error(`Failed to ${mode} font`)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-25" onClick={onClose}></div>
        <div className="relative bg-white rounded-lg max-w-md w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{mode === 'create' ? 'Add New Font' : 'Edit Font'}</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Font Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">CSS Font Family</label>
              <input
                type="text"
                value={formData.css_style}
                onChange={(e) => setFormData({...formData, css_style: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Arial, sans-serif"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Font Weight</label>
              <select
                value={formData.font_weight}
                onChange={(e) => setFormData({...formData, font_weight: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="100">100 - Thin</option>
                <option value="200">200 - Extra Light</option>
                <option value="300">300 - Light</option>
                <option value="400">400 - Normal</option>
                <option value="500">500 - Medium</option>
                <option value="600">600 - Semi Bold</option>
                <option value="700">700 - Bold</option>
                <option value="800">800 - Extra Bold</option>
                <option value="900">900 - Black</option>
              </select>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_google_font"
                checked={formData.is_google_font}
                onChange={(e) => setFormData({...formData, is_google_font: e.target.checked})}
                className="mr-2"
              />
              <label htmlFor="is_google_font" className="text-sm font-medium text-gray-700">
                Google Font
              </label>
            </div>
            
            {formData.is_google_font && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Google Font URL</label>
                <input
                  type="url"
                  value={formData.google_font_url}
                  onChange={(e) => setFormData({...formData, google_font_url: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="https://fonts.googleapis.com/css2?family=..."
                />
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
              <input
                type="number"
                value={formData.display_order}
                onChange={(e) => setFormData({...formData, display_order: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                min="0"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                className="mr-2"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                Active
              </label>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
              >
                {mode === 'create' ? 'Create' : 'Update'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

// Color Modal Component
const ColorModal = ({ mode, color, colorType, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: color?.name || '',
    hex_value: color?.hex_value || '#000000',
    color_type: colorType,
    display_order: color?.display_order || 0,
    is_active: color?.is_active ?? true
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (mode === 'create') {
        await adminApi.createColor(formData)
        toast.success('Color created successfully')
      } else {
        await adminApi.updateColor(color.id, formData)
        toast.success('Color updated successfully')
      }
      onSuccess()
    } catch (error) {
      console.error('Color operation failed:', error)
      toast.error(`Failed to ${mode} color`)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this color?')) return
    
    try {
      await adminApi.deleteColor(color.id)
      toast.success('Color deleted successfully')
      onSuccess()
    } catch (error) {
      console.error('Failed to delete color:', error)
      toast.error('Failed to delete color')
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-25" onClick={onClose}></div>
        <div className="relative bg-white rounded-lg max-w-md w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              {mode === 'create' ? `Add New ${colorType} Color` : `Edit ${colorType} Color`}
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Color Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={formData.hex_value}
                  onChange={(e) => setFormData({...formData, hex_value: e.target.value})}
                  className="w-16 h-10 border border-gray-300 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={formData.hex_value}
                  onChange={(e) => setFormData({...formData, hex_value: e.target.value})}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                  pattern="^#[0-9A-Fa-f]{6}$"
                  required
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
              <input
                type="number"
                value={formData.display_order}
                onChange={(e) => setFormData({...formData, display_order: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                min="0"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="color_is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                className="mr-2"
              />
              <label htmlFor="color_is_active" className="text-sm font-medium text-gray-700">
                Active
              </label>
            </div>
            
            <div className="flex justify-between pt-4">
              {mode === 'edit' && (
                <button
                  type="button"
                  onClick={handleDelete}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md"
                >
                  Delete
                </button>
              )}
              <div className="flex space-x-3 ml-auto">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                >
                  {mode === 'create' ? 'Create' : 'Update'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

const Settings = () => {
  const [fonts, setFonts] = useState([])
  const [backgroundColors, setBackgroundColors] = useState([])
  const [textColors, setTextColors] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [fontModal, setFontModal] = useState({ open: false, mode: 'create', font: null })
  const [colorModal, setColorModal] = useState({ open: false, mode: 'create', color: null, type: 'background' })

  useEffect(() => {
    loadAllSettings()
  }, [])

  const loadAllSettings = async () => {
    try {
      setLoading(true)
      
      const [
        fontsResponse,
        backgroundColorsResponse,
        textColorsResponse,
        healthResponse
      ] = await Promise.all([
        adminApi.getFonts(true),
        adminApi.getColors('background', true),
        adminApi.getColors('text', true),
        adminApi.getHealth()
      ])

      setFonts(fontsResponse.data.fonts)
      setBackgroundColors(backgroundColorsResponse.data.colors)
      setTextColors(textColorsResponse.data.colors)
      setHealth(healthResponse.data)
      
    } catch (error) {
      console.error('Failed to load settings:', error)
      toast.error('Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  // Font management functions
  const toggleFontActivation = async (fontId) => {
    try {
      await adminApi.toggleFontActivation(fontId)
      toast.success('Font activation toggled')
      loadAllSettings()
    } catch (error) {
      console.error('Failed to toggle font:', error)
      toast.error('Failed to toggle font activation')
    }
  }

  const deleteFont = async (fontId) => {
    if (!confirm('Are you sure you want to delete this font?')) return
    
    try {
      await adminApi.deleteFont(fontId)
      toast.success('Font deleted successfully')
      loadAllSettings()
    } catch (error) {
      console.error('Failed to delete font:', error)
      toast.error('Failed to delete font')
    }
  }

  const openFontModal = (mode, font = null) => {
    setFontModal({ open: true, mode, font })
  }

  const closeFontModal = () => {
    setFontModal({ open: false, mode: 'create', font: null })
  }

  // Color management functions
  const toggleColorActivation = async (colorId) => {
    try {
      await adminApi.toggleColorActivation(colorId)
      toast.success('Color activation toggled')
      loadAllSettings()
    } catch (error) {
      console.error('Failed to toggle color:', error)
      toast.error('Failed to toggle color activation')
    }
  }

  const deleteColor = async (colorId) => {
    if (!confirm('Are you sure you want to delete this color?')) return
    
    try {
      await adminApi.deleteColor(colorId)
      toast.success('Color deleted successfully')
      loadAllSettings()
    } catch (error) {
      console.error('Failed to delete color:', error)
      toast.error('Failed to delete color')
    }
  }

  const openColorModal = (mode, color = null, type = 'background') => {
    setColorModal({ open: true, mode, color, type })
  }

  const closeColorModal = () => {
    setColorModal({ open: false, mode: 'create', color: null, type: 'background' })
  }

  const SettingsCard = ({ title, icon: Icon, children }) => (
    <div className="card">
      <div className="flex items-center mb-4">
        <Icon className="h-6 w-6 text-primary-500 mr-3" />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {children}
    </div>
  )

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
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <button onClick={loadAllSettings} className="btn-primary">
          Refresh Data
        </button>
      </div>

      {/* System Health */}
      <SettingsCard title="System Health" icon={Wifi}>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">Overall Status</div>
                <div className="text-sm text-gray-500">System health</div>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                health?.status === 'healthy' 
                  ? 'text-green-700 bg-green-100'
                  : 'text-red-700 bg-red-100'
              }`}>
                {health?.status}
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">OpenAI</div>
                <div className="text-sm text-gray-500">AI image generation</div>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                health?.openai?.status === 'healthy' 
                  ? 'text-green-700 bg-green-100'
                  : 'text-red-700 bg-red-100'
              }`}>
                {health?.openai?.status}
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">Database</div>
                <div className="text-sm text-gray-500">PostgreSQL connection</div>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                health?.database?.status === 'healthy' 
                  ? 'text-green-700 bg-green-100'
                  : 'text-red-700 bg-red-100'
              }`}>
                {health?.database?.status}
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">API Version</div>
                <div className="text-sm text-gray-500">Backend version</div>
              </div>
              <div className="px-3 py-1 rounded-full text-sm font-medium text-blue-700 bg-blue-100">
                v2.0.0
              </div>
            </div>
          </div>
        </div>
      </SettingsCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fonts */}
        <SettingsCard title="Font Management" icon={Type}>
          <div className="flex justify-between items-center mb-4">
            <div className="text-sm text-gray-500">
              Total fonts: {fonts.length} • Active: {fonts.filter(f => f.is_active).length}
            </div>
            <button 
              onClick={() => openFontModal('create')}
              className="btn-primary text-sm"
            >
              Add Font
            </button>
          </div>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {fonts.map((font) => (
              <div key={font.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <div 
                    className="text-lg mr-3"
                    style={{ fontFamily: font.css_style }}
                  >
                    Aa
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{font.name}</div>
                    <div className="text-sm text-gray-500">{font.css_style}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {font.is_google_font && (
                    <span className="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded">
                      Google Font
                    </span>
                  )}
                  <button
                    onClick={() => toggleFontActivation(font.id)}
                    className={`px-2 py-1 text-xs font-medium rounded cursor-pointer hover:opacity-80 ${
                      font.is_active ? 'text-green-700 bg-green-100' : 'text-red-700 bg-red-100'
                    }`}
                  >
                    {font.is_active ? 'Active' : 'Inactive'}
                  </button>
                  <button
                    onClick={() => openFontModal('edit', font)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteFont(font.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </SettingsCard>

        {/* Colors */}
        <SettingsCard title="Color Management" icon={Palette}>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-gray-900">Background Colors</h4>
                <button 
                  onClick={() => openColorModal('create', null, 'background')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Add Background Color
                </button>
              </div>
              <div className="grid grid-cols-6 gap-2">
                {backgroundColors.map((color) => (
                  <div key={color.id} className="group relative">
                    <div
                      className="w-8 h-8 rounded border-2 border-gray-200 cursor-pointer"
                      style={{ backgroundColor: color.hex_value }}
                      title={color.name}
                      onClick={() => openColorModal('edit', color, 'background')}
                    />
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap mb-1 z-10">
                      {color.name}
                    </div>
                    <button
                      onClick={() => toggleColorActivation(color.id)}
                      className={`absolute -top-1 -right-1 w-3 h-3 rounded-full text-xs ${
                        color.is_active ? 'bg-green-500' : 'bg-red-500'
                      }`}
                    />
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-gray-900">Text Colors</h4>
                <button 
                  onClick={() => openColorModal('create', null, 'text')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Add Text Color
                </button>
              </div>
              <div className="grid grid-cols-6 gap-2">
                {textColors.map((color) => (
                  <div key={color.id} className="group relative">
                    <div
                      className="w-8 h-8 rounded border-2 border-gray-200 cursor-pointer"
                      style={{ backgroundColor: color.hex_value }}
                      title={color.name}
                      onClick={() => openColorModal('edit', color, 'text')}
                    />
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap mb-1 z-10">
                      {color.name}
                    </div>
                    <button
                      onClick={() => toggleColorActivation(color.id)}
                      className={`absolute -top-1 -right-1 w-3 h-3 rounded-full text-xs ${
                        color.is_active ? 'bg-green-500' : 'bg-red-500'
                      }`}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SettingsCard>
      </div>


      {/* Database Info */}
      <SettingsCard title="Database Information" icon={Database}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">{fonts.length}</div>
            <div className="text-sm text-gray-500">Fonts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">{backgroundColors.length + textColors.length}</div>
            <div className="text-sm text-gray-500">Colors</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">0</div>
            <div className="text-sm text-gray-500">Teams</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">11</div>
            <div className="text-sm text-gray-500">Templates</div>
          </div>
        </div>
      </SettingsCard>

      {/* Font Modal */}
      {fontModal.open && (
        <FontModal 
          mode={fontModal.mode}
          font={fontModal.font}
          onClose={closeFontModal}
          onSuccess={() => {
            closeFontModal()
            loadAllSettings()
          }}
        />
      )}

      {/* Color Modal */}
      {colorModal.open && (
        <ColorModal 
          mode={colorModal.mode}
          color={colorModal.color}
          colorType={colorModal.type}
          onClose={closeColorModal}
          onSuccess={() => {
            closeColorModal()
            loadAllSettings()
          }}
        />
      )}
    </div>
  )
}

export default Settings