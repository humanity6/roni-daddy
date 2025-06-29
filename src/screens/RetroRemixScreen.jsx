import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ZoomIn,
  ZoomOut,
  RefreshCw,
  ArrowRight,
  ArrowLeft,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const RetroRemixScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage, transform: initialTransform } = location.state || {}

  /* --------------------------------------------------------------------
   * UI STATE
   * ------------------------------------------------------------------*/
  const [keyword, setKeyword] = useState('')
  const [optionalText, setOptionalText] = useState('')

  /* --------------------------------------------------------------------
   * IMAGE TRANSFORM STATE
   * ------------------------------------------------------------------*/
  const [transform, setTransform] = useState(initialTransform || { x: 0, y: 0, scale: 2 })

  const moveLeft = () => setTransform((p) => ({ ...p, x: Math.max(p.x - 5, -50) }))
  const moveRight = () => setTransform((p) => ({ ...p, x: Math.min(p.x + 5, 50) }))
  const moveUp = () => setTransform((p) => ({ ...p, y: Math.max(p.y - 5, -50) }))
  const moveDown = () => setTransform((p) => ({ ...p, y: Math.min(p.y + 5, 50) }))
  const zoomIn = () => setTransform((p) => ({ ...p, scale: Math.min(p.scale + 0.1, 5) }))
  const zoomOut = () => setTransform((p) => ({ ...p, scale: Math.max(p.scale - 0.1, 0.5) }))
  const resetTransform = () => setTransform({ x: 0, y: 0, scale: 2 })

  /* --------------------------------------------------------------------
   * NAVIGATION HANDLERS
   * ------------------------------------------------------------------*/
  const handleBack = () => {
    navigate('/phone-preview', { state: { brand, model, color, template, uploadedImage, transform } })
  }

  const handleSubmit = () => {
    // For now just console log – further flow TBD
    /* eslint-disable no-console */
    console.log('SUBMIT RETRO REMIX', { brand, model, color, keyword, optionalText, transform })
  }

  /* --------------------------------------------------------------------
   * RENDER HELPERS
   * ------------------------------------------------------------------*/
  const ControlButton = ({ Icon, action }) => (
    <button
      onClick={action}
      disabled={!uploadedImage}
      className={`w-10 h-10 rounded-md flex items-center justify-center shadow active:scale-95 transition-all ${uploadedImage ? 'bg-green-200 hover:bg-green-300' : 'bg-gray-100 cursor-not-allowed'}`}
    >
      <Icon size={18} className={uploadedImage ? 'text-gray-700' : 'text-gray-400'} />
    </button>
  )

  return (
    <div className="screen-container font-[PoppinsLight]">
      <PastelBlobs />

      {/* Back arrow */}
      <button
        onClick={handleBack}
        className="absolute top-4 left-4 w-12 h-12 rounded-full bg-white border-4 border-pink-400 flex items-center justify-center shadow-lg active:scale-95 transition-transform z-20"
      >
        <ArrowLeft size={20} className="text-pink-400" />
      </button>

      {/* MAIN CONTENT */}
      <div className="relative z-10 flex flex-col items-center px-6 mt-2">
        {/* PHONE PREVIEW */}
        <div className="relative w-72 h-[480px] mb-4">
          <div className="phone-case-content">
            {uploadedImage ? (
              <img
                src={uploadedImage}
                alt="Uploaded"
                className="phone-case-image"
                style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gray-50" />
            )}
          </div>
          {/* Phone template overlay */}
          <div className="absolute inset-0 pointer-events-none">
            <img src="/phone-template.png" alt="template" className="w-full h-full object-contain" />
          </div>
        </div>

        {/* CONTROLS ROW */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[
            { icon: ZoomOut, action: zoomOut },
            { icon: ZoomIn, action: zoomIn },
            { icon: RefreshCw, action: resetTransform },
            { icon: ArrowRight, action: moveRight },
            { icon: ArrowLeft, action: moveLeft },
            { icon: ArrowDown, action: moveDown },
            { icon: ArrowUp, action: moveUp },
          ].map(({ icon: Icon, action }, idx) => (
            <ControlButton key={idx} Icon={Icon} action={action} />
          ))}
        </div>

        {/* KEYWORD INPUT */}
        <div className="w-full flex flex-col items-center mb-3">
          <div className="flex items-center w-72 justify-center mx-auto">
            <button className="flex-shrink-0 w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow active:scale-95 transition-transform mr-2">
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Enter a keyword"
              className="flex-1 bg-gray-100 backdrop-blur-sm border-2 border-gray-400 rounded-full px-4 py-3 text-center text-base font-semibold text-black shadow-lg focus:outline-none focus:border-pink-500 transition-colors"
            />
            <button className="flex-shrink-0 w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow active:scale-95 transition-transform ml-2">
              <ArrowRight size={20} className="text-gray-600" />
            </button>
          </div>
          <p className="text-center text-[11px] text-gray-500 mt-1 w-72">e.g. 'Y2K Chrome', '80s Neon', '90s Grunge'</p>
        </div>

        {/* OPTIONAL TEXT INPUT */}
        <div className="w-full flex flex-col items-center mb-3">
          <div className="w-72 relative">
            <input
              type="text"
              value={optionalText}
              onChange={(e) => setOptionalText(e.target.value)}
              placeholder="Enter Text (Optional)"
              className="w-full bg-gray-100 backdrop-blur-sm border-2 border-gray-400 rounded-full px-4 py-3 text-center text-base font-semibold text-black shadow-lg focus:outline-none focus:border-pink-500 transition-colors"
            />
          </div>
          <p className="text-center text-[11px] text-gray-500 mt-2">Optional</p>
        </div>

        {/* RESET + AI BADGE ROW */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          <button
            onClick={() => {
              setKeyword('')
              setOptionalText('')
            }}
            className="bg-green-200 text-gray-800 font-medium py-2 px-8 rounded-full active:scale-95 transition-transform shadow"
          >
            Reset Inputs
          </button>
          <span className="text-[11px] bg-blue-100 text-blue-800 px-3 py-1 rounded-full shadow whitespace-nowrap">5 AI uploads left</span>
        </div>
      </div>

      {/* SUBMIT BUTTON AT BOTTOM */}
      <div className="relative z-10 pb-8 flex justify-center">
        <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
          <div className="rounded-full bg-white p-[6px]">
            <button
              onClick={handleSubmit}
              className="w-20 h-20 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold"
            >
              <span className="text-sm">Submit</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RetroRemixScreen 