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

const FunnyToonGenerateScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    brand,
    model,
    color,
    template,
    uploadedImage,
    toonStyle,
    aiCredits: initialCredits = 4
  } = location.state || {}

  const [aiCredits, setAiCredits] = useState(initialCredits)
  const [isGenerating, setIsGenerating] = useState(false)

  const handleBack = () => {
    navigate('/funny-toon', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        toonStyle,
        aiCredits
      }
    })
  }

  const handleRegenerate = () => {
    if (aiCredits <= 0) return
    // Fake regen process (could call an API)
    setIsGenerating(true)
    setTimeout(() => {
      setIsGenerating(false)
      setAiCredits((prev) => Math.max(0, prev - 1))
      // In a real flow we'd set a new uploadedImage here
    }, 1500)
  }

  const handleGenerate = () => {
    navigate('/text-input', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        toonStyle
      }
    })
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
        <div className="w-12 h-12" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone preview */}
        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            <div className="phone-case-content">
              {uploadedImage ? (
                <img src={uploadedImage} alt="Uploaded design" className="phone-case-image" />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-400">
                    <Upload size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Your design here</p>
                  </div>
                </div>
              )}
            </div>

            {/* Overlay */}
            <div className="absolute inset-0 pointer-events-none">
              <img src="/phone-template.png" alt="Phone template" className="w-full h-full object-contain" />
            </div>
          </div>
        </div>

        {/* Placeholder controls row */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[ZoomOut, ZoomIn, RefreshCw, ArrowRight, ArrowLeft, ArrowDown, ArrowUp].map((Icon, idx) => (
            <button key={idx} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
              <Icon size={20} className="text-gray-700" />
            </button>
          ))}
        </div>

        {/* Arrow row with credits & regenerate */}
        <div className="flex items-center w-full max-w-xs mb-6 px-2">
          {/* Left Arrow */}
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>

          {/* Info & regenerate buttons */}
          <div className="flex flex-col flex-grow mx-2 space-y-2">
            <div className="w-full py-2 rounded-full text-sm font-semibold font-display bg-white border border-gray-300 text-gray-800 text-center">
              AI CREDITS REMAINING: {aiCredits}
            </div>
            <button
              onClick={handleRegenerate}
              disabled={aiCredits === 0 || isGenerating}
              className={`w-full py-2 rounded-full text-sm font-semibold font-display text-white shadow-md transition-all active:scale-95 ${
                aiCredits === 0 ? 'bg-gray-300 cursor-not-allowed' : 'bg-gradient-to-r from-blue-400 to-blue-600'
              }`}
            >
              {isGenerating ? 'Generating...' : 'RE-GENERATE IMAGE'}
            </button>
          </div>

          {/* Right Arrow */}
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Reset Inputs (reusing functionality) */}
        <button
          onClick={handleBack}
          className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
        >
          Back to Styles
        </button>
      </div>

      {/* Generate button - always pink */}
      <div className="relative z-10 p-6 flex justify-center">
        <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
          <div className="rounded-full bg-white p-[6px]">
            <button
              onClick={handleGenerate}
              className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold font-display"
            >
              <span className="text-sm">Generate</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FunnyToonGenerateScreen 