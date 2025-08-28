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
  const [pollCount, setPollCount] = useState(0)
  const [recoveryAttempted, setRecoveryAttempted] = useState(false)

  const { orderData, price } = location.state || {}

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Enhanced payment status checking with exponential backoff and recovery
  useEffect(() => {
    let localPollCount = 0
    const maxPolls = 60 // Maximum 3 minutes of polling
    const baseInterval = 3000 // Base interval: 3 seconds
    const maxInterval = 10000 // Max interval: 10 seconds
    
    const getPollingInterval = (count) => {
      // Exponential backoff: 3s, 4s, 5s, 6s, 8s, 10s, then stay at 10s
      return Math.min(baseInterval + (count * 500), maxInterval)
    }
    
    const pollPaymentStatus = async () => {
      try {
        // Stop polling after maximum attempts to prevent infinite loops
        localPollCount++
        setPollCount(localPollCount)
        
        if (localPollCount > maxPolls) {
          console.warn('Payment status polling timed out after 3 minutes')
          // Attempt recovery before giving up
          if (!recoveryAttempted) {
            console.log('Attempting payment status recovery...')
            setRecoveryAttempted(true)
            await attemptPaymentRecovery()
            return
          }
          setPaymentStatus('failed')
          setError('Payment status check timed out. If you completed payment, please contact support with your order details.')
          return
        }
        
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
          
          // Extract error details from session data
          const chineseApiError = statusData.session_data?.chinese_api_error
          const paymentData = statusData.session_data?.payment_data
          
          if (chineseApiError) {
            if (chineseApiError.message?.includes('payment') && paymentData?.third_id) {
              setError(`Payment completed but order processing failed. Order ID: ${paymentData.third_id}. Please contact support.`)
            } else {
              setError(`Processing Error: ${chineseApiError.message || 'Order processing failed'}`)
            }
          } else {
            setError('Payment processing failed. Please try again or contact support.')
          }
          
          // Stop polling when payment has failed
          return
        } else {
          setPaymentStatus('waiting')
        }
        
      } catch (error) {
        console.error('Payment status polling error:', error)
        
        // On network errors after many attempts, try recovery
        if (localPollCount > 20 && !recoveryAttempted) {
          console.log('Network errors detected, attempting recovery...')
          setRecoveryAttempted(true)
          await attemptPaymentRecovery()
          return
        }
        
        // Network / transient errors: stay in waiting to avoid scaring user
        setPaymentStatus(prev => prev === 'completed' ? prev : 'waiting')
      }
    }
    
    // Payment recovery mechanism for stuck payments
    const attemptPaymentRecovery = async () => {
      try {
        setPaymentStatus('processing')
        setError(null)
        
        // Get session data to extract payment info
        const sessionId = state.vendingMachineSession?.sessionId
        if (!sessionId) return
        
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/session/${sessionId}/status`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          const statusData = await response.json()
          const paymentData = statusData.session_data?.payment_data
          
          if (paymentData?.third_id) {
            console.log(`Recovery: Found payment data with third_id: ${paymentData.third_id}`)
            
            // Check Chinese API directly for this payment
            const chineseResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/chinese/order/payStatus`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                third_id: paymentData.third_id,
                device_id: state.vendingMachineSession?.deviceId,
                status: 3  // Check for successful payment
              })
            })
            
            if (chineseResponse.ok) {
              const chineseResult = await chineseResponse.json()
              if (chineseResult.code === 200) {
                console.log('Recovery successful: Payment confirmed by Chinese API')
                setPaymentStatus('completed')
                setTimeout(() => {
                  navigate('/vending-payment-success', {
                    state: {
                      orderData,
                      paymentMethod: 'vending_machine',
                      vendingSession: state.vendingMachineSession,
                      recoveredPayment: true
                    }
                  })
                }, 2000)
                return
              }
            }
          }
        }
        
        // Recovery failed, show helpful error
        setPaymentStatus('failed')
        setError('Unable to verify payment status. If payment was completed, please contact support with your payment reference.')
        
      } catch (recoveryError) {
        console.error('Payment recovery failed:', recoveryError)
        setPaymentStatus('failed')
        setError('Payment verification failed. Please contact support if payment was completed.')
      }
    }

    // Initial status check
    pollPaymentStatus()

    // Set up polling with exponential backoff
    let pollInterval
    const scheduleNextPoll = () => {
      const interval = getPollingInterval(localPollCount)
      pollInterval = setTimeout(() => {
        pollPaymentStatus().then(() => {
          if (localPollCount <= maxPolls && paymentStatus !== 'completed' && paymentStatus !== 'failed') {
            scheduleNextPoll()
          }
        })
      }, interval)
    }
    
    scheduleNextPoll()

    // Cleanup timeout on unmount
    return () => {
      if (pollInterval) {
        clearTimeout(pollInterval)
      }
    }
  }, [navigate, orderData, state.vendingMachineSession?.sessionId, state.vendingMachineSession?.deviceId, paymentStatus, recoveryAttempted])

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
              
              {pollCount > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Checks:</span>
                  <span className="text-sm text-gray-600">
                    {pollCount}/60 {recoveryAttempted && '(Recovery attempted)'}
                  </span>
                </div>
              )}
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