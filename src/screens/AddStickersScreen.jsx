import { useState, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'

const AddStickersScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { selectedModelData, deviceId, imageMode, brand, model } = location.state || {}
  const { state: appState, actions } = useAppState()

  const [placedStickers, setPlacedStickers] = useState([])
  const [selectedPack, setSelectedPack] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedStickerForEdit, setSelectedStickerForEdit] = useState(null)
  const [draggedSticker, setDraggedSticker] = useState(null)
  const previewRef = useRef(null)

  // Detect if device has touch capability
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0

  // Draggable Sticker Component
  const DraggableSticker = ({ sticker, isSelected, onSelect, onMove, onResize, onRotate, onDelete }) => {
    const [isDragging, setIsDragging] = useState(false)
    const [isResizing, setIsResizing] = useState(false)
    const [isRotating, setIsRotating] = useState(false)
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
    const [initialScale, setInitialScale] = useState(1)
    const [initialRotation, setInitialRotation] = useState(0)
    const [baseDistance, setBaseDistance] = useState(0)
    const stickerRef = useRef(null)
    const updateTimeoutRef = useRef(null)

    // Touch gesture states
    const [lastTouchDistance, setLastTouchDistance] = useState(0)
    const [lastTouchAngle, setLastTouchAngle] = useState(0)
    const [isMultiTouch, setIsMultiTouch] = useState(false)

    // Direct CSS transform update for immediate visual feedback
    const updateStickerTransform = (x, y, scale, rotation) => {
      if (stickerRef.current) {
        stickerRef.current.style.transform =
          `translate(-50%, -50%) translate(${x}%, ${y}%) scale(${scale}) rotate(${rotation}deg)`
      }
    }

    // Debounced state update for final positioning
    const debouncedUpdate = (updateFn, delay = 16) => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }
      updateTimeoutRef.current = setTimeout(updateFn, delay)
    }

    const handleMouseDown = (e, action = 'drag') => {
      e.preventDefault()
      e.stopPropagation()
      onSelect(sticker.placedId)

      const rect = previewRef.current.getBoundingClientRect()
      const startX = ((e.clientX - rect.left) / rect.width) * 100
      const startY = ((e.clientY - rect.top) / rect.height) * 100

      if (action === 'drag') {
        setIsDragging(true)
        setDragStart({ x: startX - sticker.x, y: startY - sticker.y })
      } else if (action === 'resize') {
        setIsResizing(true)
        setInitialScale(sticker.scale)
        // Calculate base distance from sticker center to resize handle
        const centerX = sticker.x
        const centerY = sticker.y
        const distance = Math.sqrt(Math.pow(startX - centerX, 2) + Math.pow(startY - centerY, 2))
        setBaseDistance(distance)
        setDragStart({ x: startX, y: startY })
      } else if (action === 'rotate') {
        setIsRotating(true)
        setInitialRotation(sticker.rotation)
        const centerX = sticker.x
        const centerY = sticker.y
        const initialAngle = Math.atan2(startY - centerY, startX - centerX) * (180 / Math.PI)
        setDragStart({ x: startX, y: startY, angle: initialAngle })
      }
    }

    const handleMouseMove = (e) => {
      if (!isDragging && !isResizing && !isRotating) return
      e.preventDefault()

      const rect = previewRef.current?.getBoundingClientRect()
      if (!rect) return

      const currentX = ((e.clientX - rect.left) / rect.width) * 100
      const currentY = ((e.clientY - rect.top) / rect.height) * 100

      if (isDragging) {
        const newX = Math.max(10, Math.min(90, currentX - dragStart.x))
        const newY = Math.max(10, Math.min(90, currentY - dragStart.y))

        // Update CSS immediately for visual feedback
        updateStickerTransform(newX - 50, newY - 50, sticker.scale, sticker.rotation)

        // Debounce React state update
        debouncedUpdate(() => onMove(sticker.placedId, newX, newY))
      } else if (isResizing) {
        const centerX = sticker.x
        const centerY = sticker.y
        const currentDistance = Math.sqrt(Math.pow(currentX - centerX, 2) + Math.pow(currentY - centerY, 2))
        const scaleFactor = currentDistance / (baseDistance || 50)
        const newScale = Math.max(0.3, Math.min(2.5, initialScale * scaleFactor))

        // Update CSS immediately for visual feedback
        updateStickerTransform(sticker.x - 50, sticker.y - 50, newScale, sticker.rotation)

        // Debounce React state update
        debouncedUpdate(() => onResize(sticker.placedId, newScale))
      } else if (isRotating) {
        const centerX = sticker.x
        const centerY = sticker.y
        const currentAngle = Math.atan2(currentY - centerY, currentX - centerX) * (180 / Math.PI)
        let angleDiff = currentAngle - dragStart.angle

        // Handle angle wrapping
        if (angleDiff > 180) angleDiff -= 360
        if (angleDiff < -180) angleDiff += 360

        const newRotation = initialRotation + angleDiff

        // Update CSS immediately for visual feedback
        updateStickerTransform(sticker.x - 50, sticker.y - 50, sticker.scale, newRotation)

        // Debounce React state update
        debouncedUpdate(() => onRotate(sticker.placedId, newRotation))
      }
    }

    const handleMouseUp = () => {
      // Force final state update
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }

      setIsDragging(false)
      setIsResizing(false)
      setIsRotating(false)
      setIsMultiTouch(false)
      setLastTouchDistance(0)
      setLastTouchAngle(0)

      // Reset cursor for rotate handle
      const rotateHandle = document.querySelector(`[data-rotate="${sticker.placedId}"]`)
      if (rotateHandle) {
        rotateHandle.style.cursor = 'grab'
      }
    }

    const handleTouchStart = (e) => {
      e.preventDefault()

      const touches = e.touches
      if (!touches || touches.length === 0) return

      // Multi-touch for gestures on selected stickers
      if (touches.length === 2 && isSelected && isTouchDevice) {
        setIsMultiTouch(true)
        setLastTouchDistance(getTouchDistance(touches))
        setLastTouchAngle(getTouchAngle(touches))
        setInitialScale(sticker.scale)
        setInitialRotation(sticker.rotation)
        return
      }

      // Single touch - convert to mouse event for existing drag logic
      if (touches.length === 1 && !isMultiTouch) {
        const touch = touches[0]
        const mouseEvent = new MouseEvent('mousedown', {
          clientX: touch.clientX,
          clientY: touch.clientY,
          bubbles: true,
          cancelable: true
        })
        handleMouseDown(mouseEvent, 'drag')
      }
    }

    // Helper function to calculate distance between two touches
    const getTouchDistance = (touches) => {
      if (touches.length < 2) return 0
      const touch1 = touches[0]
      const touch2 = touches[1]
      return Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      )
    }

    // Helper function to calculate angle between two touches
    const getTouchAngle = (touches) => {
      if (touches.length < 2) return 0
      const touch1 = touches[0]
      const touch2 = touches[1]
      return Math.atan2(
        touch2.clientY - touch1.clientY,
        touch2.clientX - touch1.clientX
      ) * (180 / Math.PI)
    }

    const handleTouchMove = (e) => {
      e.preventDefault()

      const touches = e.touches
      if (!touches || touches.length === 0) return

      const rect = previewRef.current?.getBoundingClientRect()
      if (!rect) return

      // Multi-touch gestures for pinch and rotate
      if (touches.length === 2 && isSelected && isTouchDevice) {
        setIsMultiTouch(true)

        const currentDistance = getTouchDistance(touches)
        const currentAngle = getTouchAngle(touches)

        // Initialize base values if not set
        if (lastTouchDistance === 0) {
          setLastTouchDistance(currentDistance)
          setInitialScale(sticker.scale)
        }
        if (lastTouchAngle === 0) {
          setLastTouchAngle(currentAngle)
          setInitialRotation(sticker.rotation)
        }

        // Pinch to scale
        if (lastTouchDistance > 0 && currentDistance > 0) {
          const scaleFactor = currentDistance / lastTouchDistance
          const newScale = Math.max(0.3, Math.min(2.5, initialScale * scaleFactor))

          // Update CSS immediately for visual feedback
          updateStickerTransform(sticker.x - 50, sticker.y - 50, newScale, sticker.rotation)

          // Debounce React state update
          debouncedUpdate(() => onResize(sticker.placedId, newScale))
        }

        // Two-finger rotation
        if (lastTouchAngle !== 0) {
          let angleDiff = currentAngle - lastTouchAngle

          // Handle angle wrapping
          if (angleDiff > 180) angleDiff -= 360
          if (angleDiff < -180) angleDiff += 360

          const newRotation = initialRotation + angleDiff

          // Update CSS immediately for visual feedback
          updateStickerTransform(sticker.x - 50, sticker.y - 50, sticker.scale, newRotation)

          // Debounce React state update
          debouncedUpdate(() => onRotate(sticker.placedId, newRotation))
        }

        return
      }

      // Single touch handling for drag and existing controls
      if (!isDragging && !isResizing && !isRotating && !isMultiTouch) return

      const touch = touches[0]
      if (!touch) return

      const currentX = ((touch.clientX - rect.left) / rect.width) * 100
      const currentY = ((touch.clientY - rect.top) / rect.height) * 100

      if (isDragging && !isMultiTouch) {
        const newX = Math.max(10, Math.min(90, currentX - dragStart.x))
        const newY = Math.max(10, Math.min(90, currentY - dragStart.y))

        // Update CSS immediately for visual feedback
        updateStickerTransform(newX - 50, newY - 50, sticker.scale, sticker.rotation)

        // Debounce React state update
        debouncedUpdate(() => onMove(sticker.placedId, newX, newY))
      } else if (isResizing && !isMultiTouch) {
        const centerX = sticker.x
        const centerY = sticker.y
        const currentDistance = Math.sqrt(Math.pow(currentX - centerX, 2) + Math.pow(currentY - centerY, 2))
        const scaleFactor = currentDistance / (baseDistance || 50)
        const newScale = Math.max(0.3, Math.min(2.5, initialScale * scaleFactor))

        // Update CSS immediately for visual feedback
        updateStickerTransform(sticker.x - 50, sticker.y - 50, newScale, sticker.rotation)

        // Debounce React state update
        debouncedUpdate(() => onResize(sticker.placedId, newScale))
      } else if (isRotating && !isMultiTouch) {
        const centerX = sticker.x
        const centerY = sticker.y
        const currentAngle = Math.atan2(currentY - centerY, currentX - centerX) * (180 / Math.PI)
        let angleDiff = currentAngle - dragStart.angle

        // Handle angle wrapping
        if (angleDiff > 180) angleDiff -= 360
        if (angleDiff < -180) angleDiff += 360

        const newRotation = initialRotation + angleDiff

        // Update CSS immediately for visual feedback
        updateStickerTransform(sticker.x - 50, sticker.y - 50, sticker.scale, newRotation)

        // Debounce React state update
        debouncedUpdate(() => onRotate(sticker.placedId, newRotation))
      }
    }

    useEffect(() => {
      if (isDragging || isResizing || isRotating) {
        // Mouse events
        document.addEventListener('mousemove', handleMouseMove, { passive: false })
        document.addEventListener('mouseup', handleMouseUp, { passive: false })
        // Touch events
        document.addEventListener('touchmove', handleTouchMove, { passive: false })
        document.addEventListener('touchend', handleMouseUp, { passive: false })

        return () => {
          document.removeEventListener('mousemove', handleMouseMove)
          document.removeEventListener('mouseup', handleMouseUp)
          document.removeEventListener('touchmove', handleTouchMove)
          document.removeEventListener('touchend', handleMouseUp)
        }
      }
    }, [isDragging, isResizing, isRotating, dragStart, initialScale, initialRotation, baseDistance])

    // Cleanup timeout on unmount
    useEffect(() => {
      return () => {
        if (updateTimeoutRef.current) {
          clearTimeout(updateTimeoutRef.current)
        }
      }
    }, [])

    return (
      <div
        ref={stickerRef}
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          transform: `translate(-50%, -50%) translate(${sticker.x - 50}%, ${sticker.y - 50}%) scale(${sticker.scale}) rotate(${sticker.rotation}deg)`,
          fontSize: '24px',
          cursor: isDragging ? 'grabbing' : 'grab',
          userSelect: 'none',
          zIndex: sticker.zIndex,
          border: isSelected ? '2px dashed #FF7CA3' : 'none',
          borderRadius: '8px',
          padding: '4px',
          willChange: isDragging || isResizing || isRotating ? 'transform' : 'auto'
        }}
        onMouseDown={(e) => handleMouseDown(e, 'drag')}
        onTouchStart={handleTouchStart}
      >
        {sticker.emoji}

        {/* Touch-only delete button - double tap to delete */}
        {isSelected && isTouchDevice && (
          <div
            style={{
              position: 'absolute',
              top: '-20px',
              right: '-20px',
              width: '20px',
              height: '20px',
              backgroundColor: '#FF4757',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              color: 'white',
              border: '2px solid white',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
              zIndex: 1000
            }}
            onTouchEnd={(e) => {
              e.stopPropagation()
              onDelete(sticker.placedId)
            }}
          >
            ×
          </div>
        )}

        {/* Control handles - only show when selected and not on touch devices */}
        {isSelected && !isTouchDevice && (
          <>
            {/* Delete button */}
            <div
              style={{
                position: 'absolute',
                top: '-16px',
                right: '-16px',
                width: '28px',
                height: '28px',
                backgroundColor: '#FF4757',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                border: '2px solid white',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                transition: 'all 150ms ease-out',
                zIndex: 1000
              }}
              onClick={(e) => {
                e.stopPropagation()
                onDelete(sticker.placedId)
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#FF3742'
                e.target.style.transform = 'scale(1.1)'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#FF4757'
                e.target.style.transform = 'scale(1)'
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>

            {/* Resize handle */}
            <div
              style={{
                position: 'absolute',
                bottom: '-16px',
                right: '-16px',
                width: '28px',
                height: '28px',
                backgroundColor: '#3742FA',
                borderRadius: '50%',
                cursor: 'nw-resize',
                border: '2px solid white',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 150ms ease-out',
                zIndex: 1000
              }}
              onMouseDown={(e) => handleMouseDown(e, 'resize')}
              onTouchStart={(e) => {
                e.preventDefault()
                e.stopPropagation()
                const touch = e.touches[0]
                if (!touch) return
                const mouseEvent = new MouseEvent('mousedown', {
                  clientX: touch.clientX,
                  clientY: touch.clientY,
                  bubbles: true,
                  cancelable: true
                })
                handleMouseDown(mouseEvent, 'resize')
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#2D38E6'
                e.target.style.transform = 'scale(1.1)'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#3742FA'
                e.target.style.transform = 'scale(1)'
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15L15 21M21 8V15H14" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 9L9 3M3 16V9H10" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>

            {/* Rotate handle */}
            <div
              style={{
                position: 'absolute',
                bottom: '-16px',
                left: '-16px',
                width: '28px',
                height: '28px',
                backgroundColor: '#2ED573',
                borderRadius: '50%',
                cursor: 'grab',
                border: '2px solid white',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 150ms ease-out',
                zIndex: 1000
              }}
              data-rotate={sticker.placedId}
              onMouseDown={(e) => {
                e.target.style.cursor = 'grabbing'
                handleMouseDown(e, 'rotate')
              }}
              onTouchStart={(e) => {
                e.preventDefault()
                e.stopPropagation()
                const touch = e.touches[0]
                if (!touch) return
                const mouseEvent = new MouseEvent('mousedown', {
                  clientX: touch.clientX,
                  clientY: touch.clientY,
                  bubbles: true,
                  cancelable: true
                })
                handleMouseDown(mouseEvent, 'rotate')
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#26D366'
                e.target.style.transform = 'scale(1.1)'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#2ED573'
                e.target.style.transform = 'scale(1)'
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 4V10H7" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3.51 15A9 9 0 1 0 6 5L1 10" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </>
        )}
      </div>
    )
  }

  const handleBack = () => {
    navigate('/browse-designs', {
      state: {
        selectedModelData,
        deviceId,
        imageMode,
        brand,
        model
      }
    })
  }

  const handleUploadSticker = () => {
    // TODO: Implement file upload functionality
    console.log('Upload sticker clicked')
  }

  const handleBrowseStickers = () => {
    // TODO: Open sticker browser modal/interface
    console.log('Browse stickers clicked')
  }

  const handleStickerPackSelect = (packName) => {
    setSelectedPack(packName)
    console.log(`Selected sticker pack: ${packName}`)
  }

  const handleStickerSelect = (sticker) => {
    // Add sticker to the preview area with default positioning and size
    const newPlacedSticker = {
      ...sticker,
      placedId: Date.now() + Math.random(), // Unique ID for placed instance
      x: 50, // Default center position (percentage)
      y: 50,
      scale: 1.0,
      rotation: 0,
      zIndex: placedStickers.length + 1
    }

    setPlacedStickers(prev => [...prev, newPlacedSticker])
    setSelectedStickerForEdit(newPlacedSticker.placedId)
  }

  const handleStickerMove = (placedId, newX, newY) => {
    setPlacedStickers(prev =>
      prev.map(sticker =>
        sticker.placedId === placedId
          ? { ...sticker, x: newX, y: newY }
          : sticker
      )
    )
  }

  const handleStickerResize = (placedId, newScale) => {
    setPlacedStickers(prev =>
      prev.map(sticker =>
        sticker.placedId === placedId
          ? { ...sticker, scale: Math.max(0.5, Math.min(3, newScale)) }
          : sticker
      )
    )
  }

  const handleStickerRotate = (placedId, newRotation) => {
    setPlacedStickers(prev =>
      prev.map(sticker =>
        sticker.placedId === placedId
          ? { ...sticker, rotation: newRotation }
          : sticker
      )
    )
  }

  const handleStickerDelete = (placedId) => {
    setPlacedStickers(prev => prev.filter(sticker => sticker.placedId !== placedId))
    if (selectedStickerForEdit === placedId) {
      setSelectedStickerForEdit(null)
    }
  }

  const handleContinue = () => {
    console.log('Continue with placed stickers:', placedStickers)
    // Navigate to next screen (likely text customization or payment)
    navigate('/text-customization', {
      state: {
        selectedModelData,
        deviceId,
        imageMode,
        brand,
        model,
        placedStickers
      }
    })
  }

  // Sticker packs data
  const stickerPacks = [
    {
      name: "Emoji Pack",
      icon: "😀",
      stickers: [
        { id: 1, emoji: "😀", name: "Happy" },
        { id: 2, emoji: "😎", name: "Cool" },
        { id: 3, emoji: "🥳", name: "Party" },
        { id: 4, emoji: "😍", name: "Love" },
        { id: 5, emoji: "🤔", name: "Thinking" },
        { id: 6, emoji: "😂", name: "Laugh" },
        { id: 7, emoji: "🔥", name: "Fire" },
        { id: 8, emoji: "💯", name: "Perfect" }
      ]
    },
    {
      name: "Shapes Pack",
      icon: "⭐",
      stickers: [
        { id: 9, emoji: "⭐", name: "Star" },
        { id: 10, emoji: "❤️", name: "Heart" },
        { id: 11, emoji: "💎", name: "Diamond" },
        { id: 12, emoji: "🌟", name: "Sparkle" },
        { id: 13, emoji: "⚡", name: "Lightning" },
        { id: 14, emoji: "🔷", name: "Blue Diamond" },
        { id: 15, emoji: "🔸", name: "Orange Diamond" },
        { id: 16, emoji: "✨", name: "Sparkles" }
      ]
    },
    {
      name: "Retro Stickers Pack",
      icon: "📼",
      stickers: [
        { id: 17, emoji: "📼", name: "Cassette" },
        { id: 18, emoji: "📺", name: "TV" },
        { id: 19, emoji: "🕹️", name: "Joystick" },
        { id: 20, emoji: "💾", name: "Floppy Disk" },
        { id: 21, emoji: "📻", name: "Radio" },
        { id: 22, emoji: "🎮", name: "Game Controller" },
        { id: 23, emoji: "📞", name: "Phone" },
        { id: 24, emoji: "⏰", name: "Alarm Clock" }
      ]
    },
    {
      name: "Sports Stickers Pack",
      icon: "⚽",
      stickers: [
        { id: 25, emoji: "⚽", name: "Soccer Ball" },
        { id: 26, emoji: "🏀", name: "Basketball" },
        { id: 27, emoji: "🏈", name: "Football" },
        { id: 28, emoji: "⚾", name: "Baseball" },
        { id: 29, emoji: "🎾", name: "Tennis Ball" },
        { id: 30, emoji: "🏆", name: "Trophy" },
        { id: 31, emoji: "🥇", name: "Gold Medal" },
        { id: 32, emoji: "🏅", name: "Medal" }
      ]
    },
    {
      name: "Music Stickers Pack",
      icon: "🎵",
      stickers: [
        { id: 33, emoji: "🎵", name: "Musical Note" },
        { id: 34, emoji: "🎶", name: "Musical Notes" },
        { id: 35, emoji: "🎸", name: "Guitar" },
        { id: 36, emoji: "🎤", name: "Microphone" },
        { id: 37, emoji: "🥁", name: "Drum" },
        { id: 38, emoji: "🎧", name: "Headphones" },
        { id: 39, emoji: "🔊", name: "Speaker" },
        { id: 40, emoji: "💿", name: "CD" }
      ]
    },
    {
      name: "Text Stickers Pack",
      icon: "💬",
      stickers: [
        { id: 41, emoji: "💬", name: "Speech Bubble" },
        { id: 42, emoji: "💭", name: "Thought Bubble" },
        { id: 43, emoji: "❗", name: "Exclamation" },
        { id: 44, emoji: "❓", name: "Question" },
        { id: 45, emoji: "💯", name: "100" },
        { id: 46, emoji: "🔤", name: "ABC" },
        { id: 47, emoji: "🆒", name: "Cool" },
        { id: 48, emoji: "🆕", name: "New" }
      ]
    }
  ]

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#FFFFFF',
        padding: '20px',
        fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
      }}
    >
      {/* Back Arrow */}
      <button
        onClick={handleBack}
        style={{
          position: 'fixed',
          top: '20px',
          left: '20px',
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          backgroundColor: '#FFFFFF',
          border: '2px solid #E5E5E5',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 20,
          transition: 'all 150ms ease-out',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}
        onMouseEnter={(e) => {
          e.target.style.borderColor = '#111111'
          e.target.style.transform = 'scale(1.05)'
        }}
        onMouseLeave={(e) => {
          e.target.style.borderColor = '#E5E5E5'
          e.target.style.transform = 'scale(1)'
        }}
        aria-label="Go back to browse designs"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Header */}
      <div style={{ marginTop: '80px', marginBottom: '30px' }}>
        <h1
          style={{
            fontSize: '36px',
            fontWeight: '800',
            color: '#111111',
            textAlign: 'center',
            margin: '0 0 20px 0',
            lineHeight: '1.1',
            fontFamily: '"GT Walsheim", "Proxima Nova", "Avenir Next", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
            letterSpacing: '-0.02em'
          }}
        >
          Add Stickers
        </h1>
      </div>

      {/* Upload/Browse Buttons */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '30px',
        maxWidth: '400px',
        margin: '0 auto 30px auto'
      }}>
        <button
          onClick={handleUploadSticker}
          style={{
            flex: 1,
            padding: '16px 24px',
            borderRadius: '12px',
            border: '2px solid #E5E5E5',
            backgroundColor: '#FFFFFF',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '600',
            color: '#111111',
            transition: 'all 200ms ease-out',
            fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = '#111111'
            e.target.style.transform = 'translateY(-2px)'
            e.target.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = '#E5E5E5'
            e.target.style.transform = 'translateY(0px)'
            e.target.style.boxShadow = 'none'
          }}
        >
          Upload Sticker
        </button>
        <button
          onClick={handleBrowseStickers}
          style={{
            flex: 1,
            padding: '16px 24px',
            borderRadius: '12px',
            border: '2px solid #E5E5E5',
            backgroundColor: '#FFFFFF',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '600',
            color: '#111111',
            transition: 'all 200ms ease-out',
            fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = '#111111'
            e.target.style.transform = 'translateY(-2px)'
            e.target.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = '#E5E5E5'
            e.target.style.transform = 'translateY(0px)'
            e.target.style.boxShadow = 'none'
          }}
        >
          Browse Stickers
        </button>
      </div>

      {/* Phone Case Preview */}
      <div style={{
        maxWidth: '300px',
        margin: '0 auto 40px auto',
        padding: '20px',
        border: '2px solid #E5E5E5',
        borderRadius: '16px',
        backgroundColor: '#F8F9FA',
        textAlign: 'center'
      }}>
        {/* Model info */}
        <div style={{
          marginBottom: '10px',
          fontSize: '12px',
          color: '#666',
          fontWeight: '500'
        }}>
          {brand && model ? `${brand} ${model}` : 'Phone Case Preview'}
        </div>

        <div
          ref={previewRef}
          style={{
            width: '200px',
            height: '300px',
            backgroundColor: '#FFFFFF',
            border: '3px solid #333',
            borderRadius: '28px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            color: '#666',
            position: 'relative',
            overflow: 'hidden',
            boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
          }}
          onClick={() => setSelectedStickerForEdit(null)} // Deselect when clicking empty area
        >
          {/* Phone case cutouts */}
          <div style={{
            position: 'absolute',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '60px',
            height: '6px',
            backgroundColor: '#333',
            borderRadius: '3px',
            zIndex: 5
          }} />

          {/* Camera cutout */}
          <div style={{
            position: 'absolute',
            top: '15px',
            right: '15px',
            width: '40px',
            height: '40px',
            backgroundColor: '#333',
            borderRadius: '8px',
            zIndex: 5
          }} />

          {/* Show the design from previous screen */}
          {appState.uploadedImages.length > 0 && (
            <img
              src={appState.uploadedImages[0]}
              alt="Selected design"
              style={{
                width: 'calc(100% - 10px)',
                height: 'calc(100% - 10px)',
                objectFit: 'cover',
                borderRadius: '24px',
                position: 'absolute',
                top: '5px',
                left: '5px',
                zIndex: 1
              }}
            />
          )}

          {/* Interactive placed stickers */}
          {placedStickers.map((sticker) => (
            <DraggableSticker
              key={sticker.placedId}
              sticker={sticker}
              isSelected={selectedStickerForEdit === sticker.placedId}
              onSelect={setSelectedStickerForEdit}
              onMove={handleStickerMove}
              onResize={handleStickerResize}
              onRotate={handleStickerRotate}
              onDelete={handleStickerDelete}
            />
          ))}

          {appState.uploadedImages.length === 0 && placedStickers.length === 0 && (
            <div style={{ zIndex: 1, position: 'relative', textAlign: 'center' }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>📱</div>
              <div>Add stickers to your case</div>
            </div>
          )}
        </div>
      </div>

      {/* Sticker Packs */}
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          {stickerPacks.map((pack) => (
            <div
              key={pack.name}
              style={{
                border: selectedPack === pack.name ? '3px solid #FF7CA3' : '2px solid #E5E5E5',
                borderRadius: '16px',
                padding: '20px',
                backgroundColor: '#FFFFFF',
                cursor: 'pointer',
                transition: 'all 200ms ease-out'
              }}
              onClick={() => handleStickerPackSelect(pack.name)}
              onMouseEnter={(e) => {
                if (selectedPack !== pack.name) {
                  e.target.style.borderColor = '#111111'
                  e.target.style.transform = 'translateY(-2px)'
                  e.target.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.1)'
                }
              }}
              onMouseLeave={(e) => {
                if (selectedPack !== pack.name) {
                  e.target.style.borderColor = '#E5E5E5'
                  e.target.style.transform = 'translateY(0px)'
                  e.target.style.boxShadow = 'none'
                }
              }}
            >
              {/* Pack Header */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '16px'
              }}>
                <span style={{ fontSize: '32px' }}>{pack.icon}</span>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#111111',
                  margin: 0,
                  fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
                }}>
                  {pack.name}
                </h3>
              </div>

              {/* Pack Stickers */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '8px'
              }}>
                {pack.stickers.map((sticker) => (
                  <button
                    key={sticker.id}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleStickerSelect(sticker)
                    }}
                    style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '8px',
                      border: '1px solid #E5E5E5',
                      backgroundColor: '#FFFFFF',
                      cursor: 'pointer',
                      fontSize: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 150ms ease-out'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.transform = 'scale(1.1)'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'scale(1)'
                    }}
                    title={sticker.name}
                  >
                    {sticker.emoji}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Continue Button */}
      {placedStickers.length > 0 && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10
        }}>
          <button
            onClick={handleContinue}
            disabled={isLoading}
            style={{
              padding: '16px 32px',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: '#FF7CA3',
              color: '#FFFFFF',
              fontSize: '16px',
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 200ms ease-out',
              fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace',
              boxShadow: '0 4px 16px rgba(255, 124, 163, 0.3)'
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.target.style.backgroundColor = '#FF5A8B'
                e.target.style.transform = 'translateY(-2px)'
                e.target.style.boxShadow = '0 6px 20px rgba(255, 124, 163, 0.4)'
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.target.style.backgroundColor = '#FF7CA3'
                e.target.style.transform = 'translateY(0px)'
                e.target.style.boxShadow = '0 4px 16px rgba(255, 124, 163, 0.3)'
              }
            }}
          >
            Continue with {placedStickers.length} sticker{placedStickers.length !== 1 ? 's' : ''}
          </button>
        </div>
      )}

      {/* Instructions */}
      <div style={{
        textAlign: 'center',
        padding: '20px',
        color: '#666',
        fontSize: '14px',
        fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
      }}>
        <p style={{ margin: '0 0 8px 0' }}>Click stickers to add them to your case</p>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {isTouchDevice ? 'Touch to move' : 'Drag to move'}
          </span>
          {!isTouchDevice ? (
            <>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <div style={{ width: '16px', height: '16px', backgroundColor: '#3742FA', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <svg width="8" height="8" viewBox="0 0 24 24" fill="none">
                    <path d="M21 15L15 21M21 8V15H14" stroke="white" strokeWidth="3" strokeLinecap="round"/>
                    <path d="M3 9L9 3M3 16V9H10" stroke="white" strokeWidth="3" strokeLinecap="round"/>
                  </svg>
                </div>
                resize
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <div style={{ width: '16px', height: '16px', backgroundColor: '#2ED573', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <svg width="8" height="8" viewBox="0 0 24 24" fill="none">
                    <path d="M1 4V10H7" stroke="white" strokeWidth="3" strokeLinecap="round"/>
                    <path d="M3.51 15A9 9 0 1 0 6 5L1 10" stroke="white" strokeWidth="3" strokeLinecap="round"/>
                  </svg>
                </div>
                rotate
              </span>
            </>
          ) : (
            <>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                Pinch to resize
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                Two-finger rotate
              </span>
            </>
          )}
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '16px', height: '16px', backgroundColor: '#FF4757', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="8" height="8" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6L18 18" stroke="white" strokeWidth="3" strokeLinecap="round"/>
              </svg>
            </div>
            {isTouchDevice ? 'tap to delete' : 'delete'}
          </span>
        </div>
      </div>

      {/* Font Import */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');
      `}</style>
    </div>
  )
}

export default AddStickersScreen