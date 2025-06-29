import { Wifi } from 'lucide-react';

const ReadyToPayScreen = () => {
  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      {/* Static pastel blobs – green top-right, blue bottom-left */}
      <div className="absolute top-[-140px] right-[-120px] w-[520px] h-[360px] bg-[#D4EFC1] rounded-[70%_30%_60%_40%/45%_65%_35%_55%] opacity-70"></div>
      <div className="absolute bottom-[-160px] left-[-140px] w-[500px] h-[340px] bg-[#CBE8F4] rounded-[80%_20%_50%_50%/70%_30%_60%_40%] opacity-70"></div>

      <div className="relative z-10 flex-1 flex flex-col items-center justify-between px-6 py-12">
        {/* Header */}
        <div className="text-center mt-8">
          <h1 
            className="text-5xl md:text-6xl font-black text-[#2F3842] mb-8 outline-none"
            style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}
          >
            READY TO PAY?
          </h1>
        </div>

        {/* Main Content Area */}
        <div className="flex w-full max-w-2xl mx-auto items-center justify-center">
          {/* Outer card with thick pink border */}
          <div className="flex flex-col items-center justify-center gap-6 w-full bg-white rounded-[80px] border-[48px] border-[#FFD6E2] p-6 relative">
            
            {/* Instructions Text */}
            <div className="w-full text-left pl-4">
              <p className="text-[#374151] text-lg md:text-xl leading-snug font-light" style={{ fontFamily: 'Poppins, sans-serif' }}>
                TAP YOUR <span className="font-extrabold">CARD</span> OR PHONE TO THE<br/>
                CARD READER NOW.
              </p>
            </div>

            {/* Payment Interface */}
            <div className="grid grid-cols-2 w-full items-end">
              {/* Card Reader – bottom-left */}
              <div className="flex items-end justify-start h-full pl-4">
                <div className="w-44 h-28 bg-[#FFD6E2] rounded-full flex items-center justify-center">
                  <div className="w-24 h-7 bg-white rounded-full"></div>
                </div>
              </div>

              {/* Wifi icon with total underneath */}
              <div className="flex flex-col items-center justify-start gap-4">
                <Wifi size={128} strokeWidth={4} color="#FFD6E2" />
                <p className="text-[#2F3842] text-3xl md:text-4xl font-black" style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}>
                  TOTAL: £16.99
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Status Messages */}
        <div className="text-center space-y-2">
          <p
            className="text-[#6B7280] text-2xl font-light"
            style={{ fontFamily: 'Poppins, sans-serif' }}
          >
            Secure payment in progress...
          </p>
          <p
            className="text-[#9CA3AF] text-xl font-light"
            style={{ fontFamily: 'Poppins, sans-serif' }}
          >
            Waiting for payment... 55 seconds
          </p>
          <p
            className="text-[#9CA3AF] text-lg font-light"
            style={{ fontFamily: 'Poppins, sans-serif' }}
          >
            Didn't go through? Cancel on your phone and try again
          </p>
        </div>
      </div>
    </div>
  )
}

export default ReadyToPayScreen 