import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useAppState } from '../contexts/AppStateContext'

const VendingPaymentSuccessScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { state: appState, actions } = useAppState()
  const [isProcessing, setIsProcessing] = useState(true)
  const [orderData, setOrderData] = useState(null)
  const [error, setError] = useState(null)

  // Get data passed from vending payment flow
  const { orderData: vendingOrderData, paymentMethod, vendingSession, transactionId } = location.state || {}

  useEffect(() => {
    const processVendingPayment = async () => {
      try {
        if (!vendingOrderData) {
          throw new Error('No vending payment data found')
        }

        // Get vending session info
        const { vendingMachineSession } = appState
        const sessionId = vendingSession?.sessionId || vendingMachineSession?.sessionId

        if (!sessionId) {
          throw new Error('No vending machine session found')
        }

        // Get order info from vending API
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/session/${sessionId}/order-info`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        })

        if (!response.ok) {
          throw new Error('Failed to retrieve order information')
        }

        const result = await response.json()
        
        // Combine vending order data with API result
        const completeOrderData = {
          ...vendingOrderData,
          orderInfo: result,
          paymentMethod: 'vending_machine',
          sessionId: sessionId,
          transactionId: transactionId || result.transaction_id
        }
        
        setOrderData(completeOrderData)
        
        // Clear any pending order from localStorage since vending payment is complete
        localStorage.removeItem('pendingOrder')
        
        // Reset AI credits after successful payment
        actions.setAiCredits(4)
        
        // Auto-navigate to order confirmed screen after 3 seconds
        setTimeout(() => {
          navigate('/order-confirmed', { 
            state: completeOrderData
          })
        }, 3000)
        
      } catch (err) {
        console.error('Vending payment processing error:', err)
        setError(err.message)
      } finally {
        setIsProcessing(false)
      }
    }

    processVendingPayment()
  }, [location.state, appState, actions, navigate])

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
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto mb-4"></div>
            <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Processing Vending Payment...</h1>
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
          <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Vending Payment Successful!</h1>
          <p className="text-gray-600 mb-6">Your payment has been processed at the vending machine</p>
          
          {/* Vending Machine Info */}
          <div className="bg-green-50 rounded-lg p-4 mb-6 max-w-md mx-auto">
            <div className="flex items-center justify-center space-x-2 mb-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <p className="text-green-800 font-semibold">Vending Machine Payment</p>
            </div>
            {orderData?.sessionId && (
              <p className="text-sm text-green-600 mb-2">Session: {orderData.sessionId}</p>
            )}
            {orderData?.transactionId && (
              <p className="text-sm text-green-600">Transaction: {orderData.transactionId}</p>
            )}
          </div>

          {/* Order Details */}
          {orderData?.orderInfo && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left max-w-md mx-auto">
              <h3 className="font-semibold mb-2">Order Details</h3>
              {orderData.orderInfo.order_id && (
                <p className="text-sm text-gray-600">Order ID: {orderData.orderInfo.order_id}</p>
              )}
              {orderData.price && (
                <p className="text-sm text-gray-600">Amount: £{orderData.price?.toFixed(2)}</p>
              )}
              <p className="text-sm text-gray-600">Payment: Vending Machine</p>
            </div>
          )}
          
          {/* Auto-redirect notice */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6 max-w-md mx-auto">
            <p className="text-blue-800 text-sm">
              Automatically redirecting to order status in 3 seconds...
            </p>
          </div>
          
          <button
            onClick={handleContinue}
            className="px-6 py-3 bg-green-400 text-white rounded-full font-semibold"
          >
            View Order Status
          </button>
        </div>
      </div>
    </div>
  )
}

export default VendingPaymentSuccessScreen