import { useNavigate } from 'react-router-dom'
import { QrCode, Smartphone, ArrowRight } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const WelcomeScreen = () => {
  const navigate = useNavigate()

  const handleStart = () => {
    navigate('/phone-brand')
  }

  return (
    <div className="screen-container">
      <PastelBlobs />
      {/* Header */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-8">
        {/* QR Code Icon */}
        <div className="mb-8 p-6 bg-white rounded-3xl shadow-xl">
          <QrCode size={80} className="text-gray-700" />
        </div>

        {/* Welcome Content */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Welcome to
          </h1>
          <div className="mb-6">
            <h2 className="text-5xl font-black text-gray-900 mb-2">PIMP MY</h2>
            <h2 className="text-5xl font-black text-gray-900">CASE®</h2>
          </div>
          <p className="text-lg text-gray-600 max-w-sm mx-auto leading-relaxed">
            Create your custom phone case in minutes. 
            Choose your design, upload your photos, and get printing!
          </p>
        </div>

        {/* Features */}
        <div className="flex items-center space-x-4 mb-12 bg-white/50 backdrop-blur-sm rounded-2xl p-4">
          <div className="flex items-center space-x-2">
            <Smartphone className="text-pink-500" size={20} />
            <span className="text-sm font-medium text-gray-700">Custom Design</span>
          </div>
          <div className="h-4 w-px bg-gray-300"></div>
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 bg-gradient-to-r from-pink-500 to-rose-500 rounded-full"></div>
            <span className="text-sm font-medium text-gray-700">Instant Print</span>
          </div>
        </div>
      </div>

      {/* Start Button */}
      <div className="relative z-10 p-6 bg-white/80 backdrop-blur-sm">
        <button 
          onClick={handleStart}
          className="w-full btn-primary flex items-center justify-center space-x-3 text-lg"
        >
          <span>Get Started</span>
          <ArrowRight size={20} />
        </button>
        <p className="text-center text-xs text-gray-500 mt-3">
          Scan QR code or tap to begin
        </p>
      </div>
    </div>
  )
}

export default WelcomeScreen 