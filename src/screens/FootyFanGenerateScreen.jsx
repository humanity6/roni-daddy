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
import CircleSubmitButton from '../components/CircleSubmitButton'

const FootyFanGenerateScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    brand,
    model,
    color,
    template,
    uploadedImage,
    team,
    style,
    aiCredits: initialCredits = 4,
    transform: initialTransform
  } = location.state || {}

  const [aiCredits, setAiCredits] = useState(initialCredits)
  const [isGenerating, setIsGenerating] = useState(false)
  const [transform, setTransform] = useState(initialTransform || { x: 0, y: 0, scale: 2 })

  /* transform controls */
  const moveLeft = () => setTransform((p)=>({...p,x:Math.max(p.x-5,-50)}))
  const moveRight = () => setTransform((p)=>({...p,x:Math.min(p.x+5,50)}))
  const moveUp = () => setTransform((p)=>({...p,y:Math.max(p.y-5,-50)}))
  const moveDown = () => setTransform((p)=>({...p,y:Math.min(p.y+5,50)}))
  const zoomIn = () => setTransform((p)=>({...p,scale:Math.min(p.scale+0.1,5)}))
  const zoomOut = () => setTransform((p)=>({...p,scale:Math.max(p.scale-0.1,0.5)}))
  const resetTransform = () => setTransform({x:0,y:0,scale:2})

  const handleBack = () => {
    navigate('/footy-fan-style', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        team,
        style,
        aiCredits,
        transform
      }
    })
  }

  const handleRegenerate = () => {
    if (aiCredits <= 0) return
    setIsGenerating(true)
    setTimeout(() => {
      setIsGenerating(false)
      setAiCredits(prev => Math.max(0, prev - 1))
      // no image changing for demo
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
        team,
        style,
        transform
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
                <img src={uploadedImage} alt="Upload" className="phone-case-image" style={{ transform:`translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin:'center center' }} />
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
          {[
            {Icon:ZoomOut, action:zoomOut},
            {Icon:ZoomIn, action:zoomIn},
            {Icon:RefreshCw, action:resetTransform},
            {Icon:ArrowRight, action:moveRight},
            {Icon:ArrowLeft, action:moveLeft},
            {Icon:ArrowDown, action:moveDown},
            {Icon:ArrowUp, action:moveUp},
          ].map(({Icon,action},idx)=>(
            <button key={idx} onClick={action} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95">
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
            <button
              onClick={handleRegenerate}
              disabled={aiCredits === 0 || isGenerating}
              className={`w-full py-2 rounded-full text-sm font-semibold text-white shadow-md transition-all active:scale-95 ${
                aiCredits === 0 ? 'bg-gray-300 cursor-not-allowed' : 'bg-gradient-to-r from-blue-400 to-blue-600'
              }`}
            >
              {isGenerating ? 'Generating...' : 'RE-GENERATE IMAGE'}
            </button>
            <div className="w-full py-2 rounded-full text-xs font-semibold bg-white border border-gray-300 text-gray-800 text-center">
              AI CREDITS REMAINING: {aiCredits}
            </div>
          </div>

          {/* Right Arrow */}
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Reset to Style Screen */}
        <button
          onClick={handleBack}
          className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
        >
          Back to Styles
        </button>
      </div>

      {/* Generate button */}
      <div className="relative z-10 p-6 flex justify-center">
        <CircleSubmitButton onClick={handleGenerate} label="Generate" />
      </div>
    </div>
  )
}

export default FootyFanGenerateScreen 