import { useState } from 'react'

const MultiOrderQueueScreen = () => {
  // Static progress for visual only (no animation)
  const progress = 65

  // Mock data for multiple orders (static design)
  const [orders] = useState([
    { position: 1, orderNumber: '9630', color: 'lavender', isMain: true },
    { position: 2, orderNumber: '5533', color: 'coral',    isMain: false },
    { position: 3, orderNumber: '2211', color: 'cyan',     isMain: false },
    { position: 4, orderNumber: '3690', color: 'lime',     isMain: false }
  ])

  const getPositionText = (position) => {
    const ordinals = { 1: '1ST', 2: '2ND', 3: '3RD', 4: '4TH' }
    return ordinals[position] || `${position}TH`
  }

  const getColorClasses = (color) => {
    const palette = {
      lavender: { border: 'border-[#E6DFF4]', iconBg: 'bg-[#E6DFF4]' }, // lighter lavender
      coral:    { border: 'border-[#F9DADA]', iconBg: 'bg-[#F9DADA]' }, // lighter coral
      cyan:     { border: 'border-[#DAF2FA]', iconBg: 'bg-[#DAF2FA]' }, // lighter cyan
      lime:     { border: 'border-[#E4F3DA]', iconBg: 'bg-[#E4F3DA]' }, // lighter lime
    }
    return palette[color] || palette.lavender
  }

  const PhoneCaseIcon = ({ color, isMain }) => {
    const colorClasses = getColorClasses(color)
    const wrapperSize = isMain ? 'w-40 h-28' : 'w-24 h-16'
    const slotSize = isMain ? 'w-16 h-5' : 'w-10 h-3'
    return (
      <div className={`${wrapperSize} ${colorClasses.iconBg} rounded-full flex items-center justify-center ${isMain ? 'ml-6' : 'ml-0'}`}>
        <div className={`${slotSize} bg-white rounded-full opacity-90`}></div>
      </div>
    )
  }

  const OrderCard = ({ order }) => {
    const colorClasses = getColorClasses(order.color)

    // Border & radius per spec
    const outerBorder = order.isMain ? 'border-[60px]' : 'border-[30px]'
    const outerRadius = order.isMain ? 'rounded-[80px]' : 'rounded-[48px]'
    const cardPadding = order.isMain ? 'p-7' : 'p-4'
    const titleSize = order.isMain ? 'text-5xl' : 'text-2xl'
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

        <div className={`flex items-center w-full ${order.isMain ? 'justify-between pr-4' : 'justify-between px-4'} space-x-8 mb-2`}>
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
      {/* Decorative blobs with EXACT colours */}
      <div className="absolute top-[-160px] left-[-140px] w-[380px] h-[260px] bg-[#E8F5E8] rounded-[65%_35%_60%_40%/60%_40%_60%_40%] opacity-80"></div>
      <div className="absolute top-[-160px] right-[-140px] w-[380px] h-[260px] bg-[#F5E8F0] rounded-[40%_60%_45%_55%/55%_45%_60%_40%] opacity-80"></div>
      <div className="absolute bottom-[-160px] left-[-140px] w-[380px] h-[260px] bg-[#F5E8F0] rounded-[60%_40%_55%_45%/45%_55%_40%_60%] opacity-80"></div>
      <div className="absolute bottom-[-160px] right-[-140px] w-[380px] h-[260px] bg-[#E8F0F5] rounded-[50%_50%_60%_40%/60%_50%_40%_60%] opacity-80"></div>

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
        <div className="w-[260px] h-4 bg-white border-2 border-[#E0E0E0] rounded-full overflow-hidden">
          <div className="h-full bg-[#C5E8D4] rounded-full" style={{ width: `${progress}%` }}></div>
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