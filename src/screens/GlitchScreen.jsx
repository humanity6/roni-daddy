import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  Plus,
  Minus,
  RefreshCw
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const GlitchScreen = () => {
  const navigate = useNavigate()
  const { brand, model, color, template, uploadedImage } = (useLocation().state || {})

  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 2 })
  const [image, setImage] = useState(uploadedImage || null)
  const [mode, setMode] = useState('retro') // 'retro' | 'chaos'

  // transform helpers
  const move = (dx, dy) => setTransform((p) => ({ ...p, x: Math.max(Math.min(p.x + dx, 50), -50), y: Math.max(Math.min(p.y + dy, 50), -50) }))
  const zoom = (dz) => setTransform((p) => ({ ...p, scale: Math.max(1, Math.min(p.scale + dz, 3)) }))
  const reset = () => setTransform({ x: 0, y: 0, scale: 2 })

  const handleGenerate = () => {
    navigate('/ai-regenerate', {
      state: { brand, model, color, template, uploadedImage: image, transform, mode }
    })
  }

  return (
    <div className="screen-container">
      <PastelBlobs />

      {/* Back Arrow */}
      <button onClick={() => navigate(-1)} className="absolute top-4 left-4 w-12 h-12 rounded-full bg-white border-4 border-pink-400 flex items-center justify-center shadow-lg active:scale-95 transition-transform z-20">
        <ArrowLeft size={20} className="text-pink-400" />
      </button>

      <div className="relative z-10 flex flex-col items-center px-6 mt-2">
        {/* Phone preview */}
        <div className="relative w-72 h-[480px] mb-4">
          <div className="phone-case-content">
            {image && (
              <img src={image} alt="Uploaded" className="phone-case-image" style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }} />
            )}
          </div>
          <div className="absolute inset-0 pointer-events-none">
            <img src="/phone-template.png" alt="template" className="w-full h-full object-contain" />
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[{icon: Minus, act: () => zoom(-0.1)}, {icon: Plus, act: () => zoom(0.1)}, {icon: RefreshCw, act: reset}, {icon: ArrowRight, act: () => move(5,0)}, {icon: ArrowLeft, act: () => move(-5,0)}, {icon: ArrowDown, act: () => move(0,5)}, {icon: ArrowUp, act: () => move(0,-5)}].map(({icon: Icon, act}, idx) => (
            <button key={idx} onClick={act} disabled={!image} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${image ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <Icon size={20} className={image ? 'text-gray-700' : 'text-gray-400'} />
            </button>
          ))}
        </div>

        {/* Mode selector */}
        <div className="flex items-center w-full max-w-xs mb-1">
          <button className="flex-shrink-0 w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow">
            <ArrowLeft size={20} className="text-gray-600" />
          </button>
          <button onClick={() => setMode('retro')} className={`flex-1 mx-2 rounded-full py-2 text-sm font-bold shadow border-2 ${mode==='retro' ? 'bg-blue-100 border-black text-black' : 'bg-white border-gray-300 text-gray-700'}`}>Retro Mode</button>
          <button className="flex-shrink-0 w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow">
            <ArrowRight size={20} className="text-gray-600" />
          </button>
        </div>
        <button onClick={() => setMode('chaos')} className={`w-full max-w-xs mb-4 rounded-full py-2 text-sm font-bold shadow border-2 ${mode==='chaos' ? 'bg-blue-100 border-black text-black' : 'bg-white border-gray-300 text-gray-700'}`}>Chaos Mode</button>

        <button onClick={() => { setTransform({ x:0,y:0,scale:2}) }} disabled={!image} className={`mb-6 bg-green-200 text-gray-800 font-medium py-2 px-10 rounded-full active:scale-95 transition-transform shadow ${image?'':'opacity-40 cursor-not-allowed'}`}>Reset Inputs</button>
      </div>

      {/* Generate ring */}
      <div className="relative z-10 pb-8 flex justify-center">
        <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
          <div className="rounded-full bg-white p-[6px]">
            <button onClick={handleGenerate} disabled={!image} className={`w-20 h-20 rounded-full flex items-center justify-center font-semibold transition-all bg-pink-400 text-white ${image?'':'opacity-40 cursor-not-allowed'}`}>Generate</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GlitchScreen 