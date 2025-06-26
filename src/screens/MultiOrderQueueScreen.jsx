import { useState } from 'react'

const MultiOrderQueueScreen = () => {
  // Static progress for visual only (no animation)
  const progress = 65

  // Mock data for multiple orders (static design)
  const [orders] = useState([
    { position: 1, orderNumber: '9630', color: 'purple', isMain: true },
    { position: 2, orderNumber: '5533', color: 'pink', isMain: false },
    { position: 3, orderNumber: '2211', color: 'cyan', isMain: false },
    { position: 4, orderNumber: '3690', color: 'green', isMain: false }
  ])

  const getPositionText = (position) => {
    const ordinals = { 1: '1ST', 2: '2ND', 3: '3RD', 4: '4TH' }
    return ordinals[position] || `${position}TH`
  }

  const getColorClasses = (color, isMain = false) => {
    const colors = {
      purple: {
        border: 'border-purple-200',
        iconBg: 'bg-purple-200',
      },
      pink: {
        border: 'border-pink-200',
        iconBg: 'bg-pink-200',
      },
      cyan: {
        border: 'border-cyan-200',
        iconBg: 'bg-cyan-200',
      },
      green: {
        border: 'border-green-200',
        iconBg: 'bg-green-200',
      }
    }
    return colors[color] || colors.purple
  }

  const PhoneCaseIcon = ({ color, isMain }) => {
    const colorClasses = getColorClasses(color)
    const wrapperSize = isMain ? 'w-32 h-20' : 'w-20 h-12'
    const slotSize = isMain ? 'w-16 h-3' : 'w-10 h-2'
    return (
      <div className={`${wrapperSize} ${colorClasses.iconBg} rounded-[42px] flex items-center justify-center`}>
        <div className={`${slotSize} bg-white rounded-full opacity-90`}></div>
      </div>
    )
  }

  const OrderCard = ({ order }) => {
    const colorClasses = getColorClasses(order.color, order.isMain)

    // Dynamic sizing based on whether it's the main card
    const outerBorder = order.isMain ? 'border-[48px]' : 'border-[24px]'
    const outerRadius = order.isMain ? 'rounded-[60px]' : 'rounded-[32px]'
    const cardPadding = order.isMain ? 'p-6' : 'p-3'
    const titleSize = order.isMain ? 'text-5xl' : 'text-xl'
    const subtitleSize = order.isMain ? 'text-lg' : 'text-sm'
    const numberSize = order.isMain ? 'text-8xl' : 'text-5xl'

    return (
      <div className={`bg-white ${outerBorder} ${outerRadius} ${colorClasses.border} ${cardPadding} text-center mx-auto ${order.isMain ? 'max-w-[640px]' : ''}`}>
        <h2 className={`font-bold ${titleSize} text-gray-800 mb-2 tracking-tight text-left`} style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}>
          HANG TIGHT!
        </h2>
        <p className={`${subtitleSize} text-gray-600 mb-6 font-light text-left`} style={{ fontFamily: 'Poppins, sans-serif' }}>
          YOUR CASE IS <span className="font-black">{getPositionText(order.position)}</span> IN THE QUEUE
        </p>

        <div className={`flex items-center ${order.isMain ? 'w-full justify-between pr-4' : 'justify-center'} space-x-8 mb-2`}>
          <PhoneCaseIcon color={order.color} isMain={order.isMain} />
          <div className={`font-bold ${numberSize} text-gray-800 leading-none`} style={{ fontFamily: 'Redminer9360, Redminer, Cubano, Arial Black, sans-serif' }}>
            {order.orderNumber}
          </div>
        </div>
      </div>
    )
  }

  const mainOrder = orders.find(order => order.isMain)
  const otherOrders = orders.filter(order => !order.isMain)

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      {/* Static pastel blobs – green top-left, pink top-right (pushed further into corners) */}
      <div className="absolute top-[-200px] left-[-180px] w-[450px] h-[300px] bg-[#D4EFC1] rounded-[70%_30%_60%_40%/45%_65%_35%_55%] opacity-70"></div>
      <div className="absolute top-[-200px] right-[-180px] w-[450px] h-[300px] bg-[#FFD6E2] rounded-[65%_35%_55%_45%/60%_50%_65%_40%] opacity-70"></div>
      
      {/* Header */}
      <div className="relative z-10 pt-12 pb-6">
        <h1 className="text-center text-5xl font-black text-gray-800 tracking-tight" style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}>
          ORDERS IN QUEUE
        </h1>
      </div>

      {/* Main Order Card */}
      <div className="relative z-10 px-6 mb-8">
        <OrderCard order={mainOrder} />
      </div>

      {/* Progress Bar */}
      <div className="relative z-10 flex justify-center mb-8 px-6">
        <div className="w-[260px] h-6 bg-white border-2 border-gray-300 rounded-full overflow-hidden">
          <div className="h-full bg-green-300" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      {/* Other Orders Grid */}
      <div className="relative z-10 px-6 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {otherOrders.map((order, index) => (
            <OrderCard key={order.orderNumber} order={order} />
          ))}
        </div>
      </div>

      {/* Footer spacing */}
      <div className="h-10" />
    </div>
  )
}

export default MultiOrderQueueScreen 