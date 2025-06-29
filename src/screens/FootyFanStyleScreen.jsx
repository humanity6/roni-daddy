import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  Upload,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const PRESET_STYLES = [
  'In team colours with fireworks',
  'Retro stadium poster style',
  'Pop-art comic style',
  'Minimal outline illustration',
  'Custom…'
]

const FootyFanStyleScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    brand,
    model,
    color,
    template,
    uploadedImage,
    team,
    transform: initialTransform
  } = location.state || {}

  // Selected preset or custom text
  const [styleChoice, setStyleChoice] = useState(PRESET_STYLES[0])
  const [customText, setCustomText] = useState('')

  const [transform] = useState(initialTransform || { x: 0, y: 0, scale: 2 })

  const isCustom = styleChoice === 'Custom…'
  const chosenStyle = isCustom ? customText : styleChoice

  const handleBack = () => {
    navigate('/footy-fan', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        team,
        transform
      }
    })
  }

  const handleNext = () => {
    navigate('/footy-fan-generate', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        team,
        style: chosenStyle,
        aiCredits: 4, // initial credits like other flow
        transform,
      }
    })
  }

  const resetInputs = () => {
    setStyleChoice(PRESET_STYLES[0])
    setCustomText('')
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
        <h1 className="text-lg font-semibold text-gray-800">Footy Fan</h1>
        <div className="w-12 h-12" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone preview */}
        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            <div className="phone-case-content">
              {uploadedImage ? (
                <img src={uploadedImage} alt="Upload" className="phone-case-image" style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }} />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <Upload size={48} className="text-gray-400" />
                </div>
              )}
            </div>
            <div className="absolute inset-0 pointer-events-none">
              <img src="/phone-template.png" className="w-full h-full object-contain" />
            </div>
          </div>
        </div>

        {/* Control buttons row */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[ZoomOut, ZoomIn, RefreshCw, ArrowRight, ArrowLeft, ArrowDown, ArrowUp].map((Icon, idx) => (
            <button
              key={idx}
              className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95"
            >
              <Icon size={20} className="text-gray-700" />
            </button>
          ))}
        </div>

        {/* Question banner */}
        <div className="w-full max-w-md mb-4 py-3 px-4 rounded-full text-center font-bold border-2 border-black" style={{ background: '#D8ECF4', color: '#1F2937' }}>
          what do you want to see on your case?
        </div>

        {/* Dropdown & optional custom text */}
        <div className="flex items-center w-full max-w-xs mb-6 px-2">
          {/* Left arrow placeholder */}
          <button className="w-12 h-12 rounded-md bg-white border-2 border-black flex-shrink-0 flex items-center justify-center shadow-md">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>

          <div className="flex flex-col flex-grow mx-2 space-y-2">
            <select
              value={styleChoice}
              onChange={(e) => setStyleChoice(e.target.value)}
              className="w-full py-2 rounded-full text-sm font-medium shadow-md bg-white border border-black text-gray-700 focus:outline-none text-center"
            >
              {PRESET_STYLES.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
            {isCustom && (
              <input
                type="text"
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                placeholder="Describe your idea..."
                className="w-full py-2 rounded-full text-sm font-medium shadow-md bg-white border border-black text-gray-700 focus:outline-none px-4 text-center"
              />
            )}
          </div>

          {/* Right arrow placeholder */}
          <button className="w-12 h-12 rounded-md bg-white border-2 border-black flex-shrink-0 flex items-center justify-center shadow-md">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Reset Button */}
        {chosenStyle && (
          <button
            onClick={resetInputs}
            className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 shadow-lg mb-4"
          >
            Reset Inputs
          </button>
        )}
      </div>

      {/* Generate / Submit Button */}
      <div className="relative z-10 p-6 flex justify-center">
        {chosenStyle ? (
          <div className="rounded-full bg-pink-400 p-[6px] shadow-xl active:scale-95 transition-transform">
            <div className="rounded-full bg-white p-[6px]">
              <button
                onClick={handleNext}
                className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold"
              >
                <span className="text-sm">Generate</span>
              </button>
            </div>
          </div>
        ) : (
          <button
            disabled
            className="w-16 h-16 rounded-full flex items-center justify-center bg-gray-300 text-gray-500 shadow-xl cursor-not-allowed"
          >
            <span className="text-sm">Generate</span>
          </button>
        )}
      </div>
    </div>
  )
}

export default FootyFanStyleScreen 