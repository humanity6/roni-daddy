import { ArrowLeft, CreditCard, Clock } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAppState } from '../contexts/AppStateContext'

const VendingPaymentWaitingScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { state } = useAppState()
  const [timeElapsed, setTimeElapsed] = useState(0)
  const [paymentStatus, setPaymentStatus] = useState('waiting') // waiting, processing, completed, failed
  const [error, setError] = useState(null)

  const { orderData, price } = location.state || {}

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Real payment status checking via API polling
  useEffect(() => {
    const pollPaymentStatus = async () => {
      try {
        // Get vending session info
        const sessionId = state.vendingMachineSession?.sessionId
        const sessionStatus = state.vendingMachineSession?.sessionStatus
        if (sessionStatus === 'registration_failed') {
          console.warn('Skipping payment status polling: vending session registration failed')
          setPaymentStatus('failed')
          setError('Vending session not established. Please rescan the QR code to try again.')
          return
        }
        if (!sessionId) {
          console.error('No vending session ID available')
          setPaymentStatus('failed')
          setError('No vending session found')
          return
        }

        // Poll the vending machine session status
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/session/${sessionId}/status`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        })

        if (!response.ok) {
          if (response.status === 404) {
            // Session status not yet initialized on backend; keep waiting silently
            setPaymentStatus(prev => (prev === 'failed' ? 'waiting' : prev))
            return
          }
          throw new Error('Failed to check payment status')
        }

        const statusData = await response.json()
        
        // Update status based on API response
        if (statusData.status === 'payment_completed') {
          setPaymentStatus('completed')
          // Navigate to vending payment success screen
          setTimeout(() => {
            navigate('/vending-payment-success', {
              state: {
                orderData,
                paymentMethod: 'vending_machine',
                vendingSession: state.vendingMachineSession,
                transactionId: statusData.transaction_id
              }
            })
          }, 2000)
        } else if (statusData.status === 'payment_pending') {
          setPaymentStatus('processing')
        } else if (statusData.status === 'payment_failed') {
          setPaymentStatus('failed')
        } else {
          setPaymentStatus('waiting')
        }
        
      } catch (error) {
        console.error('Payment status polling error:', error)
        // Network / transient errors: stay in waiting to avoid scaring user
        setPaymentStatus(prev => prev === 'completed' ? prev : 'waiting')
      }
    }

    // Initial status check
    pollPaymentStatus()

    // Set up polling interval every 3 seconds
  const pollInterval = setInterval(pollPaymentStatus, 3000)

    // Cleanup interval on unmount
    return () => clearInterval(pollInterval)
  }, [navigate, orderData, state.vendingMachineSession])

  const handleBack = () => {
    navigate(-1)
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusColor = () => {
    switch (paymentStatus) {
      case 'waiting': return 'text-yellow-600'
      case 'processing': return 'text-blue-600'
      case 'completed': return 'text-green-600'
      case 'failed': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusMessage = () => {
    switch (paymentStatus) {
      case 'waiting': return 'Waiting for payment...'
      case 'processing': return 'Processing payment...'
      case 'completed': return 'Payment completed!'
      case 'failed': return 'Payment failed. Please try again.'
      default: return 'Checking payment status...'
    }
  }

  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      {/* Content wrapper */}
      <div className="relative z-10 flex flex-col items-center px-6 py-8 min-h-screen">
        {/* Back Arrow */}
        <div className="w-full flex justify-start mb-6">
          <button
            onClick={handleBack}
            className="w-12 h-12 rounded-full bg-white border-4 border-blue-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
          >
            <ArrowLeft size={20} className="text-blue-500" />
          </button>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col items-center justify-center text-center space-y-8">
          {/* Payment icon */}
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-2xl">
            <CreditCard size={64} className="text-white" />
          </div>

          {/* Title */}
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Vending Machine Payment
            </h1>
            <p className="text-xl text-gray-600">
              {getStatusMessage()}
            </p>
          </div>

          {/* Payment details */}
          <div className="bg-gray-50 rounded-2xl p-6 w-full max-w-sm">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Amount:</span>
                <span className="text-2xl font-bold text-gray-800">£{price?.toFixed(2) || '19.99'}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Status:</span>
                <span className={`font-semibold ${getStatusColor()}`}>
                  {paymentStatus.charAt(0).toUpperCase() + paymentStatus.slice(1)}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Time:</span>
                <span className="font-mono text-gray-800 flex items-center">
                  <Clock size={16} className="mr-2" />
                  {formatTime(timeElapsed)}
                </span>
              </div>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-red-50 rounded-2xl p-6 w-full max-w-sm">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-3">
                  <span className="text-red-500 text-xl">✕</span>
                </div>
                <h3 className="font-semibold text-red-800 mb-2">Payment Error</h3>
                <p className="text-red-700 text-sm">{error}</p>
                <button
                  onClick={handleBack}
                  className="mt-3 px-4 py-2 bg-red-100 text-red-800 rounded-full font-semibold text-sm hover:bg-red-200 transition-colors"
                >
                  Go Back
                </button>
              </div>
            </div>
          )}

          {/* Instructions */}
          <div className="bg-blue-50 rounded-2xl p-6 w-full max-w-sm">
            <h3 className="font-semibold text-blue-800 mb-3">Instructions:</h3>
            <ul className="text-blue-700 space-y-2 text-left">
              <li>• Insert cash or card into the vending machine</li>
              <li>• Follow the payment prompts on the machine display</li>
              <li>• Wait for payment confirmation</li>
              <li>• Your order will be processed automatically</li>
            </ul>
          </div>

          {/* Progress indicator */}
          <div className="w-full max-w-sm">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  paymentStatus === 'waiting' ? 'bg-yellow-400 w-1/3' :
                  paymentStatus === 'processing' ? 'bg-blue-400 w-2/3' :
                  paymentStatus === 'completed' ? 'bg-green-400 w-full' :
                  'bg-red-400 w-1/4'
                }`}
              />
            </div>
            <p className="text-sm text-gray-500 mt-2">
              {paymentStatus === 'completed' ? 'Redirecting to confirmation...' : 'Payment in progress'}
            </p>
          </div>
        </div>

        {/* Cancel button */}
        <div className="mt-8">
          <button
            onClick={handleBack}
            className="px-8 py-3 bg-gray-200 text-gray-700 rounded-full font-semibold hover:bg-gray-300 transition-colors"
          >
            Cancel & Go Back
          </button>
        </div>
      </div>
    </div>
  )
}

export default VendingPaymentWaitingScreen