import { useState, useRef } from 'react'
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

const FunnyToonScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage: initialImage, transform: initialTransform } = location.state || {}

  const [uploadedImage, setUploadedImage] = useState(initialImage || null)
  const [toonStyle, setToonStyle] = useState('') // no style selected initially
  const [transform, setTransform] = useState(initialTransform || { x: 0, y: 0, scale: 2 })
  const fileInputRef = useRef(null)

  /* Image transform helpers */
  const moveLeft = () => setTransform((p) => ({ ...p, x: Math.max(p.x - 5, -50) }))
  const moveRight = () => setTransform((p) => ({ ...p, x: Math.min(p.x + 5, 50) }))
  const moveUp = () => setTransform((p) => ({ ...p, y: Math.max(p.y - 5, -50) }))
  const moveDown = () => setTransform((p) => ({ ...p, y: Math.min(p.y + 5, 50) }))
  const zoomIn = () => setTransform((p) => ({ ...p, scale: Math.min(p.scale + 0.1, 5) }))
  const zoomOut = () => setTransform((p) => ({ ...p, scale: Math.max(p.scale - 0.1, 0.5) }))
  const resetTransform = () => setTransform({ x: 0, y: 0, scale: 2 })

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

  const openFilePicker = () => {
    if (fileInputRef.current) fileInputRef.current.click()
  }

  const handleBack = () => {
    navigate('/phone-preview', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        transform
      }
    })
  }

  const handleNext = () => {
    navigate('/funny-toon-generate', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        toonStyle,
        transform
      }
    })
  }

  const resetInputs = () => {
    setUploadedImage(initialImage || null)
    setToonStyle('')
    resetTransform()
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
          className="w-12 h-12 rounded-full bg-white/90 border-4 border-pink-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
        >
          <ArrowLeft size={20} className="text-pink-400" />
        </button>
        <h1 className="text-lg font-semibold text-gray-800">Funny Toon</h1>
        <div className="w-12 h-12"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            {/* User's uploaded image */}
            <div className="phone-case-content">
              {uploadedImage ? (
                <img
                  src={uploadedImage}
                  alt="Uploaded design"
                  className="phone-case-image"
                  style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50 cursor-pointer" onClick={openFilePicker}>
                  <div className="text-center text-gray-400">
                    <Upload size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Tap to add image</p>
                  </div>
                </div>
              )}
            </div>
            {/* Phone Template Overlay */}
            <div className="absolute inset-0">
              <img
                src="/phone-template.png"
                alt="Phone template overlay"
                className="w-full h-full object-contain pointer-events-none"
              />
            </div>
          </div>
        </div>

        {/* Control Buttons Row – placeholder reuse (optional) */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[
            { Icon: ZoomOut, action: zoomOut },
            { Icon: ZoomIn, action: zoomIn },
            { Icon: RefreshCw, action: resetTransform },
            { Icon: ArrowRight, action: moveRight },
            { Icon: ArrowLeft, action: moveLeft },
            { Icon: ArrowDown, action: moveDown },
            { Icon: ArrowUp, action: moveUp },
          ].map(({ Icon, action }, idx) => (
            <button
              key={idx}
              onClick={action}
              disabled={!uploadedImage}
              className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${uploadedImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
            >
              <Icon size={20} className={uploadedImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
          ))}
        </div>

        {/* Navigation Arrows with Toon Style options between */}
        <div className="flex items-center w-full max-w-xs mb-6 px-2">
          {/* Left Arrow */}
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>

          {/* Style buttons */}
          <div className="flex flex-col flex-grow mx-2 space-y-2">
            {[
              { id: 'wild-wacky', label: 'Wild & Wacky' },
              { id: 'smooth-funny', label: 'Smooth & Funny' }
            ].map((option) => (
              <button
                key={option.id}
                onClick={() => setToonStyle(option.id)}
                className={`w-full py-2 rounded-full text-sm font-medium shadow-md transition-transform active:scale-95 ${
                  toonStyle === option.id
                    ? 'bg-blue-200 text-blue-800 ring-2 ring-blue-400'
                    : 'bg-white border border-gray-300 text-gray-700'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>

          {/* Right Arrow */}
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Upload Image Button */}
        {/* Note: image already uploaded in previous screen */}

        {/* Reset Inputs Button */}
        {toonStyle && (
          <button
            onClick={resetInputs}
            className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
          >
            Reset Inputs
          </button>
        )}

        {/* Hidden file input */}
        <input type="file" accept="image/*" ref={fileInputRef} onChange={handleImageUpload} style={{ display:'none' }} />
      </div>

      {/* Submit Button */}
      <div className="relative z-10 p-6 flex justify-center">
        {toonStyle ? (
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

export default FunnyToonScreen 