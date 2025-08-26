/**
 * Final Image Composer - Creates the final composed image with all user customizations
 * This handles text overlay, background colors, and image transformations for all template types
 * Now supports dynamic canvas sizing based on phone case dimensions
 */

/**
 * Calculate canvas dimensions from phone case dimensions in millimeters
 * @param {number} widthMm - Width in millimeters
 * @param {number} heightMm - Height in millimeters  
 * @param {number} dpi - DPI for conversion (default 300 for print quality)
 * @returns {Object} Canvas dimensions {width, height}
 */
function calculateCanvasDimensions(widthMm, heightMm, dpi = 300) {
  // Convert mm to inches, then inches to pixels
  const mmToInch = 0.0393701
  const widthInches = widthMm * mmToInch
  const heightInches = heightMm * mmToInch
  
  const canvasWidth = Math.round(widthInches * dpi)
  const canvasHeight = Math.round(heightInches * dpi)
  
  console.log(`Canvas calculation: ${widthMm}mm x ${heightMm}mm -> ${canvasWidth}px x ${canvasHeight}px at ${dpi}DPI`)
  
  return { width: canvasWidth, height: canvasHeight }
}

/**
 * Get error canvas dimensions (should not be needed since Chinese API provides dimensions)
 * @returns {Object} Error fallback canvas dimensions
 */
function getErrorCanvasDimensions() {
  // ERROR: This should not be used since Chinese API should always provide dimensions
  console.error('❌ FALLBACK ERROR: Phone case dimensions missing! Chinese API should provide width/height.')
  return { width: 1390, height: 2542 }
}

export async function composeFinalImage(options) {
  const {
    template,
    uploadedImages = [], // Array of images for multi-image templates
    uploadedImage = null, // Single image for basic templates
    imageTransforms = [],
    inputText = '',
    selectedFont = 'Arial',
    fontSize = 30,
    selectedTextColor = '#ffffff',
    selectedBackgroundColor = '#ffffff',
    textPosition = { x: 50, y: 50 },
    transform = { x: 0, y: 0, scale: 1 },
    phoneCaseDimensions = null // {width: mm, height: mm}
  } = options

  // Calculate canvas dimensions based on phone case dimensions
  let canvasDimensions
  if (phoneCaseDimensions && phoneCaseDimensions.width && phoneCaseDimensions.height) {
    canvasDimensions = calculateCanvasDimensions(phoneCaseDimensions.width, phoneCaseDimensions.height)
    console.log('✅ Using dynamic canvas dimensions from phone case:', phoneCaseDimensions)
  } else {
    canvasDimensions = getErrorCanvasDimensions()
    console.error('⚠️ ERROR: No phone case dimensions provided - this indicates a system error!')
  }
  
  const CANVAS_WIDTH = canvasDimensions.width
  const CANVAS_HEIGHT = canvasDimensions.height

  // Create canvas with high-quality settings
  const canvas = document.createElement('canvas')
  canvas.width = CANVAS_WIDTH
  canvas.height = CANVAS_HEIGHT
  const ctx = canvas.getContext('2d')
  
  // Enable high-quality rendering
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  
  // Additional quality settings
  ctx.textRenderingOptimization = 'optimizeQuality'
  ctx.antialias = true
  
  console.log(`Canvas created: ${CANVAS_WIDTH}x${CANVAS_HEIGHT} (high resolution, quality optimized)`)

  // Set background color
  ctx.fillStyle = selectedBackgroundColor
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

  try {
    // Handle different template types
    if (template?.id === 'classic' || template?.id === 'basic') {
      // Single image template
      if (uploadedImage) {
        await drawSingleImage(ctx, uploadedImage, transform, CANVAS_WIDTH, CANVAS_HEIGHT)
      }
    } else if (template?.imageCount > 1) {
      // Multi-image templates (2-in-1, 3-in-1, 4-in-1, film-strip)
      await drawMultipleImages(ctx, template, uploadedImages, imageTransforms, CANVAS_WIDTH, CANVAS_HEIGHT)
    } else if (template?.id?.includes('film')) {
      // Film strip template
      await drawFilmStripImages(ctx, uploadedImages, imageTransforms, CANVAS_WIDTH, CANVAS_HEIGHT)
    }

    // Add text overlay if provided
    if (inputText && inputText.trim()) {
      drawTextOverlay(ctx, {
        text: inputText,
        font: selectedFont,
        fontSize: fontSize,
        color: selectedTextColor,
        position: textPosition,
        canvasWidth: CANVAS_WIDTH,
        canvasHeight: CANVAS_HEIGHT
      })
    }

    // Convert to data URL with maximum quality
    return canvas.toDataURL('image/png', 1.0)

  } catch (error) {
    console.error('Error composing final image:', error)
    throw new Error('Failed to compose final image: ' + error.message)
  }
}

async function drawSingleImage(ctx, imageDataUrl, transform, canvasWidth, canvasHeight) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      try {
        // Calculate position and size based on transform (USER'S CROPPING CHOICES)
        const { x = 0, y = 0, scale = 1 } = transform
        
        // Calculate how to fit the image within the canvas (object-fit: contain logic)
        const imageAspect = img.width / img.height
        const canvasAspect = canvasWidth / canvasHeight
        
        let baseWidth, baseHeight
        if (imageAspect > canvasAspect) {
          // Image is wider - fit to canvas width
          baseWidth = canvasWidth
          baseHeight = canvasWidth / imageAspect
        } else {
          // Image is taller - fit to canvas height
          baseHeight = canvasHeight
          baseWidth = canvasHeight * imageAspect
        }
        
        console.log(`Image scaling: ${img.width}x${img.height} -> ${baseWidth}x${baseHeight} (aspect: ${imageAspect.toFixed(2)})`)
        console.log(`User transform: scale=${scale}, x=${x}, y=${y}`)
        
        // Apply transform
        ctx.save()
        
        // Enable high-quality image rendering
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        
        // Move to center for scaling and positioning
        const centerX = canvasWidth / 2
        const centerY = canvasHeight / 2
        ctx.translate(centerX, centerY)
        
        // Apply user's scale factor on top of the base fit-to-canvas scaling
        ctx.scale(scale, scale)
        
        // Apply user's position offset (convert from percentage to pixels)
        const offsetX = (x / 100) * canvasWidth
        const offsetY = (y / 100) * canvasHeight
        ctx.translate(offsetX, offsetY)
        
        // Draw image centered with calculated dimensions (WITH user transforms applied)
        ctx.drawImage(img, -baseWidth / 2, -baseHeight / 2, baseWidth, baseHeight)
        
        ctx.restore()
        resolve()
      } catch (error) {
        reject(error)
      }
    }
    img.onerror = reject
    img.src = imageDataUrl
  })
}

async function drawMultipleImages(ctx, template, images, transforms, canvasWidth, canvasHeight) {
  const imageCount = template.imageCount || images.length
  
  // Calculate grid layout
  let cols, rows
  switch (imageCount) {
    case 2:
      cols = 1; rows = 2
      break
    case 3:
      cols = 1; rows = 3
      break
    case 4:
      cols = 2; rows = 2
      break
    default:
      cols = Math.ceil(Math.sqrt(imageCount))
      rows = Math.ceil(imageCount / cols)
  }

  const cellWidth = canvasWidth / cols
  const cellHeight = canvasHeight / rows

  // Draw each image in its cell
  for (let i = 0; i < Math.min(images.length, imageCount); i++) {
    if (!images[i] || !images[i].src) continue

    const col = i % cols
    const row = Math.floor(i / cols)
    const cellX = col * cellWidth
    const cellY = row * cellHeight

    await drawImageInCell(ctx, images[i].src, transforms[i] || {}, cellX, cellY, cellWidth, cellHeight)
  }
}

async function drawImageInCell(ctx, imageDataUrl, transform, cellX, cellY, cellWidth, cellHeight) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      try {
        ctx.save()
        
        // Enable high-quality image rendering
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        
        // Clip to cell boundaries
        ctx.beginPath()
        ctx.rect(cellX, cellY, cellWidth, cellHeight)
        ctx.clip()
        
        // Calculate how to fit the image within the cell (object-fit: contain logic)
        const imageAspect = img.width / img.height
        const cellAspect = cellWidth / cellHeight
        
        let drawWidth, drawHeight
        if (imageAspect > cellAspect) {
          // Image is wider - fit to cell width
          drawWidth = cellWidth
          drawHeight = cellWidth / imageAspect
        } else {
          // Image is taller - fit to cell height
          drawHeight = cellHeight
          drawWidth = cellHeight * imageAspect
        }
        
        // Center the image in the cell without user transforms for consistency
        const centerX = cellX + cellWidth / 2
        const centerY = cellY + cellHeight / 2
        
        // Draw image centered in cell with calculated dimensions (no user transforms)
        ctx.drawImage(img, centerX - drawWidth / 2, centerY - drawHeight / 2, drawWidth, drawHeight)
        
        ctx.restore()
        resolve()
      } catch (error) {
        reject(error)
      }
    }
    img.onerror = reject
    img.src = imageDataUrl
  })
}

async function drawFilmStripImages(ctx, images, transforms, canvasWidth, canvasHeight) {
  // Film strip layout - vertical strips with film perforations
  const stripCount = images.length
  const stripHeight = canvasHeight / stripCount
  const perfWidth = 20 // Width of film perforations
  const imageWidth = canvasWidth - (perfWidth * 2)

  // Draw film background
  ctx.fillStyle = '#2a2a2a'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  for (let i = 0; i < images.length; i++) {
    if (!images[i] || !images[i].src) continue

    const stripY = i * stripHeight
    
    // Draw perforations
    drawFilmPerforations(ctx, stripY, stripHeight, perfWidth, canvasWidth)
    
    // Draw image in strip
    await drawImageInCell(ctx, images[i].src, transforms[i] || {}, perfWidth, stripY, imageWidth, stripHeight)
  }
}

function drawFilmPerforations(ctx, stripY, stripHeight, perfWidth, canvasWidth) {
  ctx.fillStyle = '#000'
  
  // Left perforations
  const perfHeight = 8
  const perfSpacing = 12
  const perfsPerStrip = Math.floor(stripHeight / perfSpacing)
  
  for (let j = 0; j < perfsPerStrip; j++) {
    const perfY = stripY + (j * perfSpacing)
    // Left side
    ctx.fillRect(5, perfY, perfWidth - 10, perfHeight)
    // Right side
    ctx.fillRect(canvasWidth - perfWidth + 5, perfY, perfWidth - 10, perfHeight)
  }
}

function drawTextOverlay(ctx, options) {
  const { text, font, fontSize, color, position, canvasWidth, canvasHeight } = options
  
  ctx.save()
  
  // Scale font size for high-resolution canvas (1390x2542)
  // The UI uses 30px as base, but the canvas is much larger than typical preview
  // Scale factor based on canvas width (1390px is about 5.4x larger than typical 256px preview)
  const scaleFactor = Math.max(4.5, canvasWidth / 300) // Minimum 4.5x scaling for high-res canvas
  const scaledFontSize = fontSize * scaleFactor
  
  console.log(`Text rendering: original ${fontSize}px -> scaled ${scaledFontSize}px (factor: ${scaleFactor})`)
  
  // Set font with scaled size
  ctx.font = `${scaledFontSize}px ${font}, sans-serif`
  ctx.fillStyle = color
  ctx.textAlign = 'left'
  ctx.textBaseline = 'top'
  
  // Enable text stroke for better visibility (also scale stroke width)
  ctx.strokeStyle = color === '#ffffff' ? '#000000' : '#ffffff'
  ctx.lineWidth = Math.max(2, scaleFactor * 0.5) // Scale stroke width
  
  // Calculate text position (percentage to pixel conversion)
  const textX = (position.x / 100) * canvasWidth
  const textY = (position.y / 100) * canvasHeight
  
  // Handle multi-line text with scaled line height
  const lines = text.split('\n')
  const lineHeight = scaledFontSize * 1.2
  
  lines.forEach((line, index) => {
    const y = textY + (index * lineHeight)
    if (y < canvasHeight - scaledFontSize) { // Don't draw text outside canvas
      // Draw stroke first (outline)
      ctx.strokeText(line, textX, y)
      // Draw fill text on top
      ctx.fillText(line, textX, y)
    }
  })
  
  ctx.restore()
}