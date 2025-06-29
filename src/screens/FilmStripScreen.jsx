import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  ArrowRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
// Film-strip rails overlay
// Using public filmstrip case image

const FilmStripScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  //  brand / model / colour / template passed from previous screens if needed
  const { brand, model, color, template } = location.state || {}

  // keep track of user flow
  const [stripCount, setStripCount] = useState(null) // 3 or 4

  const handleChooseStrip = (count) => {
    setStripCount(count)
    // Uploading will be done in next screen
  }

  const handleBack = () => {
    // go back to template selection
    navigate('/template-selection', {
      state: { brand, model, color }
    })
  }

  const handleNext = () => {
    navigate('/film-strip-upload', {
      state: {
        brand,
        model,
        color,
        template,
        stripCount
      }
    })
  }

  const resetInputs = () => {
    setStripCount(null)
  }

  const canSubmit = !!stripCount

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
        {/* Center placeholder to maintain spacing */}
        <div className="flex-1"></div>
        <div className="w-12 h-12" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-start px-6 mt-4">
        {/* Phone Case Preview */}
        <div className="relative mb-6">
          <div className="relative w-[525px] h-[525px]">
            <div className="phone-case-content mask-filmstrip">
              {/* Preview area for filmstrip layout */}
              <div className="absolute inset-0 flex flex-col justify-center items-center z-10 px-8 py-12">
                {Array.from({ length: stripCount || 3 }).map((_, idx) => (
                  <div 
                    key={idx} 
                    className="w-full mb-2 overflow-hidden bg-gray-200/50 border border-gray-300" 
                    style={{
                      height: `${100 / (stripCount || 3) - 2}%`,
                      aspectRatio: '4/3'
                    }}
                  >
                    <div className="w-full h-full flex items-center justify-center">
                      <span className="text-gray-400 text-xs">Frame {idx + 1}</span>
                    </div>
                  </div>
                ))}
              </div>

              <img
                src="/filmstrip-case.png"
                alt="Film strip phone case"
                className="absolute inset-0 w-full h-full object-contain pointer-events-none z-10"
              />
            </div>
          </div>
        </div>

        {/* Control Buttons Row */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[ZoomOut, ZoomIn, RefreshCw, ArrowRight, ArrowLeft, ArrowDown, ArrowUp].map((Icon, idx) => (
            <button
              key={idx}
              className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform"
            >
              <Icon size={20} className="text-gray-700" />
            </button>
          ))}
        </div>

        {/* Choose strip buttons */}
        <div className="flex flex-col w-full max-w-xs mb-6 space-y-3">
          <button
            onClick={() => handleChooseStrip(3)}
            className={`w-full py-3 rounded-full text-base font-extrabold shadow-md transition-transform active:scale-95 ${stripCount === 3 ? 'bg-blue-200 text-blue-800 ring-2 ring-blue-400' : 'bg-white border border-gray-300 text-gray-700'}`}
          >
            Choose 3 image strip
          </button>
          <button
            onClick={() => handleChooseStrip(4)}
            className={`w-full py-3 rounded-full text-base font-extrabold shadow-md transition-transform active:scale-95 ${stripCount === 4 ? 'bg-blue-200 text-blue-800 ring-2 ring-blue-400' : 'bg-white border border-gray-300 text-gray-700'}`}
          >
            Choose 4 image strip
          </button>
        </div>

        {/* Reset Inputs Button */}
        {stripCount && (
          <button
            onClick={resetInputs}
            className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
          >
            Reset Inputs
          </button>
        )}
      </div>

      {/* Submit Button */}
      <div className="relative z-10 p-6 flex justify-center">
        {canSubmit ? (
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
          <div className="rounded-full bg-pink-400/50 p-[6px] shadow-xl">
            <div className="rounded-full bg-white p-[6px]">
              <button disabled className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-300 text-white font-semibold cursor-not-allowed">
                <span className="text-sm">Submit</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FilmStripScreen 