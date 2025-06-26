import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { 
  ArrowLeft, 
  ArrowRight, 
  Upload, 
  RotateCcw, 
  ZoomIn, 
  ZoomOut, 
  Move,
  RotateCw,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const PhonePreviewScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template } = location.state || {}
  
  const [uploadedImage, setUploadedImage] = useState(null)

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleBack = () => {
    navigate('/template-selection', { 
      state: { 
        brand, 
        model, 
        color 
      } 
    })
  }

  const handleNext = () => {
    navigate('/text-input', { 
      state: { 
        brand, 
        model, 
        color, 
        template,
        uploadedImage 
      } 
    })
  }

  const resetInputs = () => {
    setUploadedImage(null)
  }

  const getColorClass = (colorId) => {
    const colorMap = {
      black: 'bg-gray-900',
      white: 'bg-gray-100',
      blue: 'bg-blue-500',
      pink: 'bg-pink-400',
      green: 'bg-green-600'
    }
    return colorMap[colorId] || 'bg-gray-900'
  }

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 flex items-center justify-between p-4">
        <button 
          onClick={handleBack}
          className="w-12 h-12 rounded-full bg-cyan-400 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
        >
          <ArrowLeft size={20} className="text-white" />
        </button>
        <div className="w-12 h-12"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-8">
          {/* Phone Case Container */}
          <div className="relative w-72 h-[480px]">
            {/* User's uploaded image - positioned to fit exactly within phone template boundaries */}
            <div className="phone-case-content">
              {uploadedImage ? (
                <img 
                  src={uploadedImage} 
                  alt="Uploaded design" 
                  className="phone-case-image"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-400">
                    <Upload size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Your design here</p>
                  </div>
                </div>
              )}
            </div>
            
            {/* Phone Template Overlay - camera holes and edges on top */}
            <div className="absolute inset-0">
              <img 
                src="/phone-template.png" 
                alt="Phone template overlay" 
                className="w-full h-full object-contain pointer-events-none"
              />
            </div>
          </div>
        </div>

        {/* Control Buttons Row */}
        <div className="flex items-center justify-center space-x-4 mb-6">
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ZoomOut size={20} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ZoomIn size={20} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <RefreshCw size={20} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ArrowRight size={20} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ArrowLeft size={20} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ArrowDown size={20} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ArrowUp size={20} className="text-gray-600" />
          </button>
        </div>

        {/* Navigation Arrows */}
        <div className="flex items-center justify-between w-full max-w-xs mb-6">
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Upload Image Button */}
        <div className="w-full max-w-xs mb-4">
          <label className="block">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            <div className="w-full bg-blue-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform cursor-pointer shadow-lg">
              <div className="flex items-center justify-center space-x-2">
                <Upload size={20} />
                <span>Upload Image</span>
              </div>
            </div>
          </label>
        </div>

        {/* Reset Inputs Button */}
        {uploadedImage && (
          <button 
            onClick={resetInputs}
            className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
          >
            Reset Inputs
          </button>
        )}
      </div>

      {/* Submit Button */}
      <div className="relative z-10 p-6">
        <button 
          onClick={handleNext}
          disabled={!uploadedImage}
          className={`
            w-16 h-16 rounded-full mx-auto flex items-center justify-center shadow-xl transition-all duration-200
            ${uploadedImage 
              ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white active:scale-95' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          <span className="font-bold text-sm">Submit</span>
        </button>
      </div>
    </div>
  )
}

export default PhonePreviewScreen 