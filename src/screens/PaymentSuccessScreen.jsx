import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useAppState } from '../contexts/AppStateContext'

const PaymentSuccessScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { actions } = useAppState()
  const [isProcessing, setIsProcessing] = useState(true)
  const [orderData, setOrderData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const processPayment = async () => {
      try {
        // Get session ID from URL params
        const urlParams = new URLSearchParams(location.search)
        const sessionId = urlParams.get('session_id')
        
        if (!sessionId) {
          throw new Error('No session ID found')
        }

        // Get pending order data from localStorage
        const pendingOrderData = JSON.parse(localStorage.getItem('pendingOrder') || '{}')
        
        // Process payment success with backend
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/process-payment-success`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            order_data: {
              mobile_model_id: "MM020250701000001",
              pic: pendingOrderData.designImage
            }
          }),
        })

        if (!response.ok) {
          throw new Error('Payment processing failed')
        }

        const result = await response.json()
        
        // Combine order data with payment result
        const completeOrderData = {
          ...pendingOrderData,
          orderData: result
        }
        
        setOrderData(completeOrderData)
        
        // Clear pending order from localStorage
        localStorage.removeItem('pendingOrder')
        
        // Reset AI credits after successful payment
        actions.setAiCredits(4)
        
        // Skip payment success screen and go directly to order confirmed
        navigate('/order-confirmed', { 
          state: completeOrderData
        })
        return
        
      } catch (err) {
        console.error('Payment processing error:', err)
        setError(err.message)
      } finally {
        setIsProcessing(false)
      }
    }

    processPayment()
  }, [location.search])

  const handleContinue = () => {
    if (orderData) {
      navigate('/order-confirmed', { 
        state: orderData
      })
    }
  }

  const handleBack = () => {
    navigate('/')
  }

  if (isProcessing) {
    return (
      <div className="screen-container" style={{ background: '#FFFFFF' }}>
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-400 mx-auto mb-4"></div>
            <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Processing Payment...</h1>
            <p className="text-gray-600">Please wait while we confirm your payment</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="screen-container" style={{ background: '#FFFFFF' }}>
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-red-500 text-2xl">✕</span>
            </div>
            <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Payment Error</h1>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={handleBack}
              className="px-6 py-3 bg-pink-400 text-white rounded-full font-semibold"
            >
              Return Home
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
            <span className="text-green-500 text-2xl">✓</span>
          </div>
          <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Payment Successful!</h1>
          <p className="text-gray-600 mb-6">Your payment has been processed successfully</p>
          
          {orderData?.orderData && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left max-w-md mx-auto">
              <h3 className="font-semibold mb-2">Order Details</h3>
              <p className="text-sm text-gray-600">Order ID: {orderData.orderData.order_id}</p>
              <p className="text-sm text-gray-600">Payment ID: {orderData.orderData.payment_id}</p>
              <p className="text-sm text-gray-600">Amount: £{orderData.price?.toFixed(2)}</p>
            </div>
          )}
          
          <button
            onClick={handleContinue}
            className="px-6 py-3 bg-pink-400 text-white rounded-full font-semibold"
          >
            View Order Status
          </button>
        </div>
      </div>
    </div>
  )
}

export default PaymentSuccessScreen