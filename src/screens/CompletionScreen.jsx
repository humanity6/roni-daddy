import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle, Gift, Smartphone, Home } from 'lucide-react'
import { useAppState } from '../contexts/AppStateContext'
import PastelBlobs from '../components/PastelBlobs'

const CompletionScreen = () => {
  const navigate = useNavigate()
  const { state, actions } = useAppState()
  const [showConfetti, setShowConfetti] = useState(true)

  useEffect(() => {
    // Hide confetti after animation
    const timer = setTimeout(() => {
      setShowConfetti(false)
    }, 3000)

    return () => clearTimeout(timer)
  }, [])

  const handleNewOrder = () => {
    actions.resetState()
    navigate('/welcome')
  }

  const handleGoHome = () => {
    navigate('/welcome')
  }

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Confetti Animation */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-pink-500 rounded-full animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${2 + Math.random() * 2}s`
              }}
            />
          ))}
        </div>
      )}

      {/* Header */}
      <div className="relative z-10 flex-1 flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          {/* Success Message */}
          <div className="mb-8">
            <div className="bg-gradient-to-r from-blue-400 to-blue-500 text-white px-8 py-6 rounded-3xl shadow-2xl mx-auto max-w-xs">
              <h1 className="text-2xl font-black">ORDER</h1>
              <h1 className="text-2xl font-black">CONFIRMED!</h1>
            </div>
          </div>

          {/* Order Number */}
          <div className="mb-8">
            <div className="bg-gradient-to-r from-green-400 to-green-500 text-white px-8 py-4 rounded-3xl shadow-lg mx-auto max-w-xs">
              <p className="text-3xl font-black">{state.orderNumber || '9630'}</p>
            </div>
          </div>

          {/* Phone Case Illustration */}
          <div className="mb-8">
            <div className="bg-gradient-to-r from-pink-300 to-pink-400 text-white px-8 py-12 rounded-3xl shadow-lg mx-auto max-w-xs">
              <div className="text-center">
                <div className="mb-4">
                  <div className="w-16 h-16 bg-white rounded-2xl mx-auto flex items-center justify-center shadow-lg">
                    <Smartphone size={32} className="text-pink-500" />
                  </div>
                </div>
                <h2 className="text-xl font-black mb-2">HANG TIGHT!</h2>
                <p className="text-white text-lg">Your</p>
                <p className="text-white text-lg font-bold">case <span className="font-normal">is</span></p>
                <p className="text-white text-lg font-normal">being</p>
                <p className="text-white text-lg font-bold">printed!</p>
              </div>
            </div>
          </div>

          {/* Success Icon */}
          <div className="mb-6">
            <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto shadow-xl">
              <CheckCircle size={40} className="text-white" />
            </div>
          </div>

          {/* Completion Message */}
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Case Ready!</h3>
            <p className="text-lg text-gray-600 mb-4">
              Your custom phone case has been printed successfully.
            </p>
            <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
              <div className="flex items-center justify-center space-x-2 text-green-700">
                <Gift size={20} />
                <span className="font-semibold">Ready for collection!</span>
              </div>
            </div>
          </div>

          {/* Order Details */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 mb-8 shadow-lg">
            <h4 className="font-semibold text-gray-800 mb-4">Order Summary</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Order #:</span>
                <span className="font-semibold text-gray-800">#{state.orderNumber || '9630'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Phone Model:</span>
                <span className="font-semibold text-gray-800">{state.brand} {state.model}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Case Color:</span>
                <span className="font-semibold text-gray-800 capitalize">{state.color}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Template:</span>
                <span className="font-semibold text-gray-800">{state.template?.name || 'Custom'}</span>
              </div>
              <div className="border-t border-gray-200 pt-2 mt-2">
                <div className="flex justify-between font-semibold">
                  <span className="text-gray-800">Total Paid:</span>
                  <span className="text-green-600">£17.99</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="relative z-10 p-6 bg-white/80 backdrop-blur-sm space-y-3">
        <button
          onClick={handleNewOrder}
          className="w-full btn-primary flex items-center justify-center space-x-2"
        >
          <Smartphone size={20} />
          <span>Create Another Case</span>
        </button>
        
        <button
          onClick={handleGoHome}
          className="w-full btn-secondary flex items-center justify-center space-x-2"
        >
          <Home size={20} />
          <span>Back to Home</span>
        </button>

        <div className="text-center pt-4">
          <p className="text-sm text-gray-500">
            Thank you for using PIMP MY CASE®!
          </p>
        </div>
      </div>
    </div>
  )
}

export default CompletionScreen 