import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  Sparkles, 
  Upload, 
  RefreshCw,
  Wand2,
  Image as ImageIcon,
  Type,
  Palette
} from 'lucide-react'
import { useAppState } from '../contexts/AppStateContext'
import PastelBlobs from '../components/PastelBlobs'

const RetryScreen = () => {
  const navigate = useNavigate()
  const { state, actions } = useAppState()
  const [modificationPrompt, setModificationPrompt] = useState('')
  const [selectedModification, setSelectedModification] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const modificationOptions = [
    {
      id: 'ai-enhance',
      title: 'AI Enhancement',
      description: 'Improve image quality and colors',
      icon: <Sparkles className="text-purple-500" size={24} />,
      color: 'bg-purple-50 border-purple-200'
    },
    {
      id: 'style-change',
      title: 'Style Transformation',
      description: 'Apply artistic filters and effects',
      icon: <Wand2 className="text-pink-500" size={24} />,
      color: 'bg-pink-50 border-pink-200'
    },
    {
      id: 'text-edit',
      title: 'Text Modifications',
      description: 'Change text, font, or positioning',
      icon: <Type className="text-blue-500" size={24} />,
      color: 'bg-blue-50 border-blue-200'
    },
    {
      id: 'color-adjust',
      title: 'Color Adjustments',
      description: 'Modify colors and brightness',
      icon: <Palette className="text-green-500" size={24} />,
      color: 'bg-green-50 border-green-200'
    },
    {
      id: 'image-replace',
      title: 'Replace Images',
      description: 'Upload new images',
      icon: <Upload className="text-orange-500" size={24} />,
      color: 'bg-orange-50 border-orange-200'
    }
  ]

  const handleBack = () => {
    navigate('/phone-back-preview')
  }

  const handleModificationSelect = (modification) => {
    setSelectedModification(modification)
    if (modification.id === 'image-replace') {
      // Handle image replacement
      document.getElementById('image-upload').click()
    } else if (modification.id === 'text-edit') {
      // Navigate to text editing
      navigate('/text-input')
    }
  }

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        actions.addImage(e.target.result)
        setSelectedModification(null)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleApplyModification = async () => {
    if (!selectedModification && !modificationPrompt.trim()) return
    
    setIsProcessing(true)
    actions.setLoading(true)

    try {
      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      // Update design state
      actions.setDesignComplete(true)
      
      // Navigate to payment screen
      navigate('/payment')
    } catch (error) {
      actions.setError('Failed to apply modifications. Please try again.')
    } finally {
      setIsProcessing(false)
      actions.setLoading(false)
    }
  }

  const handleProceedToPayment = () => {
    actions.setDesignComplete(true)
    navigate('/payment')
  }

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="flex items-center justify-between p-4">
          <button 
            onClick={handleBack}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ArrowLeft size={24} className="text-gray-600" />
          </button>
          <h1 className="text-lg font-semibold text-gray-800">Modify Design</h1>
          <div className="w-8 h-8"></div>
        </div>
      </div>

      {/* Current Design Preview */}
      <div className="relative z-10 p-6 bg-white/80 backdrop-blur-sm">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Current Design</h2>
        <div className="bg-white rounded-2xl p-4 shadow-lg">
          <div className="relative mx-auto max-w-xs">
            <img 
              src="/phone-template.png" 
              alt="Phone template" 
              className="w-full h-auto"
            />
            <div className="phone-case-preview">
              {state.uploadedImages.length > 0 && (
                <img 
                  src={state.uploadedImages[0]} 
                  alt="Current design" 
                  className="phone-case-image"
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modification Options */}
      <div className="relative z-10 flex-1 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Modification Options</h2>
        
        <div className="space-y-3 mb-6">
          {modificationOptions.map((option) => (
            <button
              key={option.id}
              onClick={() => handleModificationSelect(option)}
              className={`w-full p-4 rounded-2xl border-2 transition-all ${
                selectedModification?.id === option.id 
                  ? 'border-pink-500 bg-pink-50' 
                  : `${option.color} hover:border-gray-300`
              }`}
            >
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  {option.icon}
                </div>
                <div className="flex-1 text-left">
                  <h3 className="font-semibold text-gray-800">{option.title}</h3>
                  <p className="text-sm text-gray-600">{option.description}</p>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Custom Prompt */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Or describe your changes:
          </label>
          <textarea
            value={modificationPrompt}
            onChange={(e) => setModificationPrompt(e.target.value)}
            placeholder="e.g., Make the colors more vibrant, add a vintage filter, adjust the brightness..."
            className="w-full p-4 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-pink-500 focus:border-pink-500 resize-none"
            rows={3}
          />
        </div>

        {/* Hidden file input */}
        <input
          id="image-upload"
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
      </div>

      {/* Action Buttons */}
      <div className="relative z-10 p-6 bg-white/80 backdrop-blur-sm space-y-3">
        <button
          onClick={handleApplyModification}
          disabled={!selectedModification && !modificationPrompt.trim()}
          className="w-full btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? (
            <>
              <RefreshCw size={20} className="animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Sparkles size={20} />
              <span>Apply Changes</span>
            </>
          )}
        </button>
        
        <button
          onClick={handleProceedToPayment}
          className="w-full btn-secondary"
        >
          Keep Current Design & Continue
        </button>
      </div>
    </div>
  )
}

export default RetryScreen 