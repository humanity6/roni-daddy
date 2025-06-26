import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, CreditCard, Smartphone } from 'lucide-react'
import { useAppState } from '../contexts/AppStateContext'
import PastelBlobs from '../components/PastelBlobs'

const PaymentScreen = () => {
  const navigate = useNavigate()
  const { state, actions } = useAppState()
  const [isProcessing, setIsProcessing] = useState(false)

  const handleBack = () => {
    navigate('/retry')
  }

  const handlePayment = async () => {
    setIsProcessing(true)
    actions.setLoading(true)
    actions.setOrderStatus('payment')

    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Generate order number
      const orderNumber = Math.floor(Math.random() * 9000) + 1000
      actions.setOrderNumber(orderNumber)
      actions.setOrderStatus('queue')
      
      // Navigate to queue screen
      navigate('/queue')
    } catch (error) {
      actions.setError('Payment failed. Please try again.')
    } finally {
      setIsProcessing(false)
      actions.setLoading(false)
    }
  }

  const getColorClass = (colorId) => {
    const colorMap = {
      black: 'bg-gray-900',
      white: 'bg-gray-100',
      blue: 'bg-blue-500',
      pink: 'bg-pink-400',
      green: 'bg-green-600'
    }
    return colorMap[colorId] || 'bg-gray-900'
  }

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="flex items-center justify-between p-4">
          <button 
            onClick={handleBack}
            className="p-3 bg-blue-500 hover:bg-blue-600 rounded-full transition-colors"
          >
            <ArrowLeft size={20} className="text-white" />
          </button>
          <div className="w-8 h-8"></div>
        </div>
      </div>

      {/* Phone Case Preview */}
      <div className="relative z-10 flex-1 flex items-center justify-center p-6">
        <div className="relative max-w-sm w-full">
          {/* Phone case container */}
          <div className="relative bg-white rounded-3xl p-6 shadow-2xl">
            {/* Phone case image */}
            <div className="relative mx-auto" style={{ width: '200px', height: '400px' }}>
              {/* Phone case frame */}
              <div 
                className={`absolute inset-0 rounded-3xl ${getColorClass(state.color)}`}
                style={{
                  boxShadow: 'inset 0 0 0 8px rgba(0,0,0,0.1)'
                }}
              />
              
              {/* Camera cutout */}
              <div className="absolute top-6 left-6 w-16 h-12 bg-black rounded-2xl flex items-center justify-center space-x-2">
                <div className="w-4 h-4 bg-gray-800 rounded-full border border-gray-600"></div>
                <div className="w-3 h-3 bg-gray-800 rounded-full border border-gray-600"></div>
              </div>
              
              {/* Case content area */}
              <div 
                className="absolute rounded-3xl overflow-hidden"
                style={{
                  top: '20px',
                  left: '20px',
                  right: '20px',
                  bottom: '20px'
                }}
              >
                {state.uploadedImages.length > 0 ? (
                  <img 
                    src={state.uploadedImages[0]} 
                    alt="Case design" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                    <Smartphone size={40} className="text-gray-400" />
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Price badge */}
          <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2">
            <div className="bg-gradient-to-r from-blue-400 to-blue-500 text-white px-6 py-3 rounded-2xl shadow-lg">
              <span className="text-2xl font-bold">£17.99</span>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Button */}
      <div className="relative z-10 p-6 bg-white/80 backdrop-blur-sm">
        <div className="mb-6">
          <div className="bg-gradient-to-r from-pink-500 to-pink-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span className="text-white text-2xl font-bold">PAY</span>
          </div>
          
          <div className="text-center">
            <p className="text-gray-600 mb-2">Please <strong>Scan</strong> Your</p>
            <p className="text-gray-600"><strong>Card on the Card Reader.</strong></p>
          </div>
        </div>

        <button
          onClick={handlePayment}
          disabled={isProcessing}
          className="w-full btn-primary flex items-center justify-center space-x-3 text-xl py-6 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? (
            <>
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              <span>Processing Payment...</span>
            </>
          ) : (
            <>
              <CreditCard size={24} />
              <span>PAY £17.99</span>
            </>
          )}
        </button>
        
        {/* Payment info */}
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500">
            Secure payment • Your case will be printed immediately
          </p>
        </div>
      </div>
    </div>
  )
}

export default PaymentScreen 