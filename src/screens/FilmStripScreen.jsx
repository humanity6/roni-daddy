import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  Upload,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  ArrowRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

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
    // go back to phone preview
    navigate('/phone-preview', {
      state: { brand, model, color, template }
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
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            <div className="phone-case-content relative flex flex-col justify-between p-1">
              {/* Internal film strip edges */}
              <div className="absolute inset-y-0 left-0 w-3 bg-black flex flex-col justify-between py-2">
                {Array.from({ length: 11 }).map((_, i) => (
                  <div key={i} className="w-2 h-2 bg-white mx-auto my-1 rounded-sm"></div>
                ))}
              </div>
              <div className="absolute inset-y-0 right-0 w-3 bg-black flex flex-col justify-between py-2">
                {Array.from({ length: 11 }).map((_, i) => (
                  <div key={i} className="w-2 h-2 bg-white mx-auto my-1 rounded-sm"></div>
                ))}
              </div>
              {stripCount ? (
                Array.from({ length: stripCount }).map((_, idx) => (
                  <div
                    key={idx}
                    className="flex-1 mb-1 last:mb-0 overflow-hidden bg-gray-50 flex items-center justify-center"
                  >
                    <Upload size={24} className="text-gray-300" />
                  </div>
                ))
              ) : (
                // empty placeholder before user chooses option
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-400">
                    <Upload size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Choose strip option</p>
                  </div>
                </div>
              )}
            </div>
            {/* Template overlay */}
            <div className="absolute inset-0 pointer-events-none">
              <img src="/phone-template.png" alt="Phone template" className="w-full h-full object-contain" />
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