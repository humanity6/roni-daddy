import React from 'react'

const CircleSubmitButton = ({ label = 'Submit', onClick, disabled = false }) => {
  return (
    <div
      className={`rounded-full ${disabled ? 'bg-gray-300' : 'bg-pink-400'} p-[6px] shadow-xl ${
        disabled ? '' : 'active:scale-95 transition-transform'
      }`}
    >
      <div className="rounded-full bg-white p-[6px]">
        <button
          onClick={onClick}
          disabled={disabled}
          className={`w-16 h-16 rounded-full flex items-center justify-center font-semibold text-[10px] ${
            disabled
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-pink-400 text-white'
          }`}
        >
          {label}
        </button>
      </div>
    </div>
  )
}

export default CircleSubmitButton 