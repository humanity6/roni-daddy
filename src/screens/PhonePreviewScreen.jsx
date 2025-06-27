import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { 
  ArrowLeft, 
  ArrowRight, 
  Upload, 
  ZoomIn, 
  ZoomOut, 
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
    if (template?.id === 'funny-toon') {
      navigate('/funny-toon', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage
        }
      })
    } else if (template?.id?.startsWith('film-strip')) {
      navigate('/film-strip', {
        state: {
          brand,
          model,
          color,
          template
        }
      })
    } else {
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
        {/* Back Arrow – outlined pastel-pink circle */}
        <button 
          onClick={handleBack}
          className="w-12 h-12 rounded-full bg-white/90 border-4 border-pink-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
        >
          <ArrowLeft size={20} className="text-pink-400" />
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

        {/* Control Buttons Row – pastel-green squares */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[{Icon: ZoomOut}, {Icon: ZoomIn}, {Icon: RefreshCw}, {Icon: ArrowRight}, {Icon: ArrowLeft}, {Icon: ArrowDown}, {Icon: ArrowUp}].map(({Icon}, idx) => (
            <button
              key={idx}
              className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform"
            >
              <Icon size={20} className="text-gray-700" />
            </button>
          ))}
        </div>

        {/* Navigation Arrows below – square white buttons */}
        <div className="flex items-center justify-between w-full max-w-xs mb-6 px-2">
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform">
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
            <div className="w-full bg-blue-100 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform cursor-pointer shadow-lg">
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

      {/* Submit Button – pink outer ring, white inner ring, pink core */}
      <div className="relative z-10 p-6 flex justify-center">
        {template?.id?.startsWith('film-strip') || uploadedImage ? (
          <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
            <div className="rounded-full bg-white p-[6px]">
              <button
                onClick={handleNext}
                className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold"
              >
                <span className="text-sm">Submit</span>
              </button>
            </div>
          </div>
        ) : (
          <button
            disabled
            className="w-16 h-16 rounded-full flex items-center justify-center bg-gray-300 text-gray-500 shadow-xl cursor-not-allowed"
          >
            <span className="text-sm">Submit</span>
          </button>
        )}
      </div>
    </div>
  )
}

export default PhonePreviewScreen 