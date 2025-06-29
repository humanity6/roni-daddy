import { useState, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft, Upload, ZoomIn, ZoomOut, RefreshCw, ChevronLeft, ChevronRight, ArrowUp, ArrowDown, ArrowRight
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const LEAGUES = {
  'Premier League (ENG)': [
    'Arsenal','Aston Villa','Bournemouth','Brentford','Brighton','Burnley','Chelsea','Crystal Palace','Everton','Fulham','Liverpool','Luton Town','Manchester City','Manchester United','Newcastle United','Nottingham Forest','Sheffield United','Tottenham Hotspur','West Ham','Wolves'
  ],
  'La Liga (ESP)': ['Barcelona','Real Madrid','Atlético Madrid','Real Sociedad','Sevilla','Valencia'],
  'Serie A (ITA)': ['Juventus','Inter Milan','AC Milan','Roma','Napoli','Lazio'],
  'Bundesliga (GER)': ['Bayern Munich','Borussia Dortmund','RB Leipzig','Bayer Leverkusen','Eintracht Frankfurt'],
  'Ligue 1 (FRA)': ['Paris Saint-Germain','Marseille','Lyon','Monaco','Lille']
}

const FootyFanScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage: initialImage, transform: initialTransform } = location.state || {}

  const [uploadedImage, setUploadedImage] = useState(initialImage || null)
  const [transform, setTransform] = useState(initialTransform || { x: 0, y: 0, scale: 2 })
  const fileInputRef = useRef(null)

  const TEAMS = Object.values(LEAGUES).flat()
  const [team, setTeam] = useState('Liverpool')

  const handleBack = () => {
    navigate('/phone-preview', { state: { brand, model, color, template, uploadedImage, transform } })
  }

  const handleNext = () => {
    navigate('/footy-fan-style', { state: { brand, model, color, template, uploadedImage, team, transform } })
  }

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (ev) => setUploadedImage(ev.target.result)
      reader.readAsDataURL(file)
    }
  }

  const openFilePicker = () => {
    fileInputRef.current && fileInputRef.current.click()
  }

  const resetInputs = () => {
    setTeam('Liverpool')
    resetTransform()
  }

  /* Transform helpers */
  const moveLeft = () => setTransform((p) => ({ ...p, x: Math.max(p.x - 5, -50) }))
  const moveRight = () => setTransform((p) => ({ ...p, x: Math.min(p.x + 5, 50) }))
  const moveUp = () => setTransform((p) => ({ ...p, y: Math.max(p.y - 5, -50) }))
  const moveDown = () => setTransform((p) => ({ ...p, y: Math.min(p.y + 5, 50) }))
  const zoomIn = () => setTransform((p) => ({ ...p, scale: Math.min(p.scale + 0.1, 5) }))
  const zoomOut = () => setTransform((p) => ({ ...p, scale: Math.max(p.scale - 0.1, 0.5) }))
  const resetTransform = () => setTransform({ x: 0, y: 0, scale: 2 })

  return (
    <div className="screen-container">
      <PastelBlobs />

      {/* Header */}
      <div className="relative z-10 flex items-center justify-between p-4">
        <button onClick={handleBack} className="w-12 h-12 rounded-full bg-white/90 border-4 border-pink-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg">
          <ArrowLeft size={20} className="text-pink-400" />
        </button>
        <h1 className="text-lg font-semibold text-gray-800">Footy Fan</h1>
        <div className="w-12 h-12"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone preview */}
        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            <div className="phone-case-content">
              {uploadedImage ? <img src={uploadedImage} alt="Upload" className="phone-case-image" style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }} /> : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50 cursor-pointer" onClick={openFilePicker}>
                  <Upload size={48} className="text-gray-400" />
                </div>
              )}
            </div>
            <div className="absolute inset-0 pointer-events-none"><img src="/phone-template.png" className="w-full h-full object-contain" /></div>
          </div>
        </div>

        {/* Control buttons row */}
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

        {/* Selection bar */}
        <div className="flex items-center w-full max-w-xs mb-6 px-2">
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md"><ChevronLeft size={24} className="text-gray-600"/></button>

          <div className="flex flex-col flex-grow mx-2 space-y-2 items-center">
            {/* Heading */}
            <div className="w-full py-2 rounded-full text-sm font-bold text-center font-poppins shadow-md" style={{background:'#D8ECF4', color:'#1F2937'}}>PICK A TEAM</div>

            {/* Searchable team input */}
            <input
              list="teams-list"
              value={team}
              onChange={(e)=>setTeam(e.target.value)}
              placeholder="Start typing..."
              className="w-full py-2 rounded-full text-sm font-medium shadow-md bg-white border border-gray-300 text-gray-700 focus:outline-none px-4 text-center"
            />
            <datalist id="teams-list">
              {TEAMS.map(t=>(<option key={t} value={t} />))}
            </datalist>
          </div>

          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md"><ChevronRight size={24} className="text-gray-600"/></button>
        </div>

        {/* Reset */}
        {team && (
          <button onClick={resetInputs} className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 shadow-lg mb-4">Reset Inputs</button>
        )}

        {/* Hidden upload input */}
        <input type="file" accept="image/*" ref={fileInputRef} onChange={handleImageUpload} style={{ display:'none' }} />
      </div>

      {/* Submit */}
      <div className="relative z-10 p-6 flex justify-center">
        {team ? (
          <div className="rounded-full bg-pink-400 p-[6px] shadow-xl active:scale-95 transition-transform">
            <div className="rounded-full bg-white p-[6px]">
              <button onClick={handleNext} className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold">
                <span className="text-sm">Submit</span>
              </button>
            </div>
          </div>
        ) : (
          <button disabled className="w-16 h-16 rounded-full flex items-center justify-center bg-gray-300 text-gray-500 shadow-xl cursor-not-allowed"><span className="text-sm">Submit</span></button>
        )}
      </div>
    </div>
  )
}

export default FootyFanScreen 