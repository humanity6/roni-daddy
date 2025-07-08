import { useState, useEffect, useRef, useCallback } from 'react'
import { fonts, DEFAULT_FONT_SIZE } from './fontManager'

// Constants for container dimensions
const CONTAINER_DIMENSIONS = {
  PHONE_CASE: { width: 230, height: 380 }, // w-72 = 288px, h-[480px] = 480px
  FILM_STRIP: { width: 525, height: 525 },
  // Safe zones to keep text well within bounds
  SAFE_MARGIN: 20 // pixels from edge
}

// Enhanced text boundary management hook
const useTextBoundaries = (template, inputText, fontSize, selectedFont) => {
  const [textDimensions, setTextDimensions] = useState({ width: 0, height: 0 })
  const [containerDimensions, setContainerDimensions] = useState(CONTAINER_DIMENSIONS.PHONE_CASE)
  const [safeBoundaries, setSafeBoundaries] = useState({ minX: 10, maxX: 90, minY: 10, maxY: 90 })
  const measureRef = useRef(null)

  // Get font style for consistent rendering using the central font manager
  const getFontStyle = useCallback(() => {
    return {
      fontFamily: fonts.find((f) => f.name === selectedFont)?.style || 'Arial, sans-serif',
      fontSize: `${fontSize || DEFAULT_FONT_SIZE}px`,
      fontWeight: '500',
      lineHeight: '1.2',
      whiteSpace: 'nowrap'
    }
  }, [selectedFont, fontSize])

  // Set container dimensions based on template
  useEffect(() => {
    if (template?.id?.startsWith('film-strip')) {
      setContainerDimensions(CONTAINER_DIMENSIONS.FILM_STRIP)
    } else {
      setContainerDimensions(CONTAINER_DIMENSIONS.PHONE_CASE)
    }
  }, [template])

  // Measure text dimensions accurately
  const measureTextDimensions = useCallback(() => {
    if (!inputText?.trim()) {
      setTextDimensions({ width: 0, height: 0 })
      return
    }

    // Create a temporary element to measure text
    const tempElement = document.createElement('div')
    tempElement.style.position = 'absolute'
    tempElement.style.visibility = 'hidden'
    tempElement.style.whiteSpace = 'nowrap'
    tempElement.style.fontSize = `${fontSize}px`
    tempElement.style.fontFamily = getFontStyle().fontFamily
    tempElement.style.fontWeight = '500'
    tempElement.style.lineHeight = '1.2'
    tempElement.textContent = inputText
    
    document.body.appendChild(tempElement)
    const rect = tempElement.getBoundingClientRect()
    document.body.removeChild(tempElement)
    
    setTextDimensions({
      width: Math.ceil(rect.width),
      height: Math.ceil(rect.height)
    })
  }, [inputText, fontSize, getFontStyle])

  // Calculate safe boundaries
  useEffect(() => {
    if (!inputText?.trim() || textDimensions.width === 0 || textDimensions.height === 0) {
      setSafeBoundaries({ minX: 10, maxX: 90, minY: 10, maxY: 90 })
      return
    }

    const { width: containerWidth, height: containerHeight } = containerDimensions
    const { width: textWidth, height: textHeight } = textDimensions
    
    // Calculate minimum safe distances from edges (in pixels)
    const minXPixels = Math.max(CONTAINER_DIMENSIONS.SAFE_MARGIN * 1.5, textWidth / 2 + 5) // Added extra padding for smaller fonts
    const minYPixels = Math.max(CONTAINER_DIMENSIONS.SAFE_MARGIN, textHeight / 2)
    
    // Convert to percentages
    const minXPercent = (minXPixels / containerWidth) * 100
    const maxXPercent = 100 - minXPercent
    const minYPercent = (minYPixels / containerHeight) * 100
    const maxYPercent = 100 - minYPercent
    
    // Ensure we have valid boundaries - tighter left/right constraints
    const safeMinX = Math.max(10, Math.min(55, minXPercent)) // Increased from 2 to 10, and from 35 to 55
    const safeMaxX = Math.min(90, Math.max(45, maxXPercent)) // Decreased from 98 to 90, and from 65 to 45
    const safeMinY = Math.max(5, Math.min(45, minYPercent))
    const safeMaxY = Math.min(95, Math.max(55, maxYPercent))
    
    setSafeBoundaries({
      minX: safeMinX,
      maxX: safeMaxX,
      minY: safeMinY,
      maxY: safeMaxY
    })
  }, [textDimensions, containerDimensions, inputText])

  // Re-measure when dependencies change
  useEffect(() => {
    measureTextDimensions()
  }, [measureTextDimensions])

  // Constrain position to safe boundaries
  const constrainPosition = useCallback((position) => {
    return {
      x: Math.max(safeBoundaries.minX, Math.min(safeBoundaries.maxX, position.x)),
      y: Math.max(safeBoundaries.minY, Math.min(safeBoundaries.maxY, position.y))
    }
  }, [safeBoundaries])

  // Validate if text would fit at current settings
  const validateTextFit = useCallback(() => {
    if (!inputText?.trim()) return true
    
    const { width: containerWidth, height: containerHeight } = containerDimensions
    const { width: textWidth, height: textHeight } = textDimensions
    
    // Check if text dimensions plus safe margins exceed container
    const requiredWidth = textWidth + (CONTAINER_DIMENSIONS.SAFE_MARGIN * 2)
    const requiredHeight = textHeight + (CONTAINER_DIMENSIONS.SAFE_MARGIN * 2)
    
    return requiredWidth <= containerWidth && requiredHeight <= containerHeight
  }, [inputText, textDimensions, containerDimensions])

  // Calculate maximum safe character count for current font/size
  const getMaxSafeCharacters = useCallback(() => {
    const { width: containerWidth } = containerDimensions
    const availableWidth = containerWidth - (CONTAINER_DIMENSIONS.SAFE_MARGIN * 2)
    
    // Estimate character width based on font and size
    const estimatedCharWidth = fontSize * 0.6 // Rough estimate
    const maxChars = Math.floor(availableWidth / estimatedCharWidth)
    
    return Math.max(15, Math.min(50, maxChars)) // Between 10-50 chars
  }, [fontSize, containerDimensions])

  return {
    textDimensions,
    containerDimensions,
    safeBoundaries,
    constrainPosition,
    validateTextFit,
    getMaxSafeCharacters,
    getFontStyle,
    measureRef
  }
}

// Enhanced text input validation
const validateTextInput = (text, maxLength) => {
  // Remove any characters that could cause issues (newlines, tabs, but keep spaces)
  const cleanText = text.replace(/[\n\r\t]/g, '')
  
  // Limit length
  if (cleanText.length > maxLength) {
    return cleanText.substring(0, maxLength)
  }
  
  return cleanText
}

// Enhanced position movement with boundary checking
const createPositionHandlers = (currentPosition, safeBoundaries, setPosition) => {
  const moveStep = 3 // Smaller steps for more precise control
  
  return {
    moveLeft: () => {
      const newX = Math.max(safeBoundaries.minX, currentPosition.x - moveStep)
      setPosition(prev => ({ ...prev, x: newX }))
    },
    moveRight: () => {
      const newX = Math.min(safeBoundaries.maxX, currentPosition.x + moveStep)
      setPosition(prev => ({ ...prev, x: newX }))
    },
    moveUp: () => {
      const newY = Math.max(safeBoundaries.minY, currentPosition.y - moveStep)
      setPosition(prev => ({ ...prev, y: newY }))
    },
    moveDown: () => {
      const newY = Math.min(safeBoundaries.maxY, currentPosition.y + moveStep)
      setPosition(prev => ({ ...prev, y: newY }))
    }
  }
}

// Font size validation – simplified.  We no longer auto-shrink the text.  The
// size is clamped between a sensible range but otherwise left unchanged.
const validateFontSize = (newSize /* ignoredArgs */) => {
  const minSize = 12
  const maxSize = 30
  return Math.max(minSize, Math.min(maxSize, newSize))
}

export {
  useTextBoundaries,
  validateTextInput,
  createPositionHandlers,
  validateFontSize,
  CONTAINER_DIMENSIONS
} 