import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, Users, Printer, CheckCircle } from 'lucide-react'
import { useAppState } from '../contexts/AppStateContext'
import PastelBlobs from '../components/PastelBlobs'

const QueueScreen = () => {
  const navigate = useNavigate()
  const { state, actions } = useAppState()
  const [queuePosition, setQueuePosition] = useState(3)
  const [estimatedTime, setEstimatedTime] = useState(5)
  const [currentStatus, setCurrentStatus] = useState('queue')

  useEffect(() => {
    // Simulate queue progression
    const interval = setInterval(() => {
      setQueuePosition(prev => {
        if (prev > 1) {
          return prev - 1
        } else {
          setCurrentStatus('printing')
          setEstimatedTime(2)
          return 0
        }
      })
    }, 3000) // Move up in queue every 3 seconds

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Simulate printing completion
    if (currentStatus === 'printing') {
      const printingTimer = setTimeout(() => {
        actions.setOrderStatus('completed')
        navigate('/completion')
      }, 6000) // 6 seconds of printing

      return () => clearTimeout(printingTimer)
    }
  }, [currentStatus, actions, navigate])

  useEffect(() => {
    // Update global queue position
    actions.setQueuePosition(queuePosition)
  }, [queuePosition, actions])

  const getStatusMessage = () => {
    if (currentStatus === 'printing') {
      return {
        title: 'Printing Your Case',
        subtitle: 'Almost done!',
        icon: <Printer size={40} className="text-green-500" />
      }
    } else {
      return {
        title: 'In Queue',
        subtitle: `${queuePosition} ${queuePosition === 1 ? 'person' : 'people'} ahead of you`,
        icon: <Users size={40} className="text-blue-500" />
      }
    }
  }

  const status = getStatusMessage()

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="flex items-center justify-center p-4">
          <h1 className="text-lg font-semibold text-gray-800">Order Status</h1>
        </div>
      </div>

      {/* Order Info */}
      <div className="relative z-10 p-6 bg-white/80 backdrop-blur-sm">
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">Order Number</p>
          <p className="text-2xl font-bold text-gray-800">#{state.orderNumber}</p>
        </div>
      </div>

      {/* Status Display */}
      <div className="relative z-10 flex-1 flex items-center justify-center p-6">
        <div className="text-center max-w-sm">
          {/* Status Icon */}
          <div className="mb-8">
            <div className="mx-auto w-24 h-24 bg-white rounded-full shadow-xl flex items-center justify-center mb-4">
              {status.icon}
            </div>
            {currentStatus === 'printing' && (
              <div className="flex justify-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            )}
          </div>

          {/* Status Text */}
          <h2 className="text-3xl font-bold text-gray-800 mb-3">{status.title}</h2>
          <p className="text-lg text-gray-600 mb-8">{status.subtitle}</p>

          {/* Progress Steps */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3 text-left">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                <CheckCircle size={16} className="text-white" />
              </div>
              <div>
                <p className="font-semibold text-gray-800">Payment Received</p>
                <p className="text-sm text-gray-600">£17.99 processed successfully</p>
              </div>
            </div>

            <div className={`flex items-center space-x-3 text-left ${currentStatus === 'printing' ? 'opacity-100' : 'opacity-50'}`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                currentStatus === 'printing' ? 'bg-green-500' : 'bg-gray-300'
              }`}>
                {currentStatus === 'printing' ? (
                  <CheckCircle size={16} className="text-white" />
                ) : (
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                )}
              </div>
              <div>
                <p className="font-semibold text-gray-800">Design Processing</p>
                <p className="text-sm text-gray-600">Preparing your custom case</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 text-left opacity-50">
              <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                <div className="w-3 h-3 bg-white rounded-full"></div>
              </div>
              <div>
                <p className="font-semibold text-gray-800">Ready for Pickup</p>
                <p className="text-sm text-gray-600">Collection available</p>
              </div>
            </div>
          </div>

          {/* Estimated Time */}
          <div className="mt-8 p-4 bg-blue-50 rounded-2xl border border-blue-200">
            <div className="flex items-center justify-center space-x-2 text-blue-700">
              <Clock size={20} />
              <span className="font-semibold">
                Estimated time: ~{estimatedTime} {estimatedTime === 1 ? 'minute' : 'minutes'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Message */}
      <div className="relative z-10 p-6 bg-white/80 backdrop-blur-sm">
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Please stay nearby. We'll notify you when your case is ready!
          </p>
        </div>
      </div>
    </div>
  )
}

export default QueueScreen 